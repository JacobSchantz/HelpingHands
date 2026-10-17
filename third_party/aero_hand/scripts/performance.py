#!/usr/bin/env python3
"""Hand performance: start a song, then dance to it.

Usage: performance.py [song] [--routine] [--dry-run]
  song       default: a random track from the "¿?" playlist (port auto-detected)
  --routine  play the old fixed routine instead of dancing
  --dry-run  listen and print tempo/energy, don't move the hand
Run with the aero venv: ~/HelpingHands-tools/aero/venv/bin/python performance.py

Dancing listens through the Mac's microphone (grant the terminal Microphone access), tracks
tempo and beat phase from spectral-flux onsets, and drives the hand from a beat clock: a move
changes every 8 bars, its size follows the song's loudness, and strong onsets add a flick.
All motion is low-passed and speed-limited, so nothing jerks. It stops when the track ends
(or Ctrl-C), easing back open. Servo temperatures are polled; the dance shrinks when warm
and stops when hot.
"""
import argparse, collections, glob, math, subprocess, sys, threading, time
import numpy as np

PLAYLIST = "¿?"
OPEN = [0.0] * 7

ROUTINE = [
    (OPEN, 1.0),
    # pinch each finger to the thumb
    ([100.0, 35.0, 23.0, 0.0, 0.0, 0.0, 50.0], 0.5), ([100.0, 35.0, 23.0, 0.0, 0.0, 0.0, 50.0], 0.25),
    ([100.0, 42.0, 23.0, 0.0, 0.0, 52.0, 0.0], 0.5), ([100.0, 42.0, 23.0, 0.0, 0.0, 52.0, 0.0], 0.25),
    ([83.0, 42.0, 23.0, 0.0, 50.0, 0.0, 0.0], 0.5), ([83.0, 42.0, 23.0, 0.0, 50.0, 0.0, 0.0], 0.25),
    ([75.0, 25.0, 30.0, 50.0, 0.0, 0.0, 0.0], 0.5), ([75.0, 25.0, 30.0, 50.0, 0.0, 0.0, 0.0], 0.25),
    (OPEN, 0.5), (OPEN, 0.5),
    # finger wave, index to pinky and back
    ([0.0, 0.0, 0.0, 90.0, 0.0, 0.0, 0.0], 0.3), ([0.0, 0.0, 0.0, 0.0, 90.0, 0.0, 0.0], 0.3),
    ([0.0, 0.0, 0.0, 0.0, 0.0, 90.0, 0.0], 0.3), ([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 90.0], 0.3),
    ([0.0, 0.0, 0.0, 0.0, 0.0, 90.0, 0.0], 0.3), ([0.0, 0.0, 0.0, 0.0, 90.0, 0.0, 0.0], 0.3),
    ([0.0, 0.0, 0.0, 90.0, 0.0, 0.0, 0.0], 0.3), (OPEN, 0.5),
    # peace sign
    ([90.0, 0.0, 0.0, 0.0, 0.0, 90.0, 90.0], 0.5), ([90.0, 45.0, 60.0, 0.0, 0.0, 90.0, 90.0], 0.5),
    ([90.0, 45.0, 60.0, 0.0, 0.0, 90.0, 90.0], 1.0), (OPEN, 0.5), (OPEN, 0.5),
    # rock on
    ([0.0, 0.0, 0.0, 0.0, 90.0, 90.0, 0.0], 0.5), ([0.0, 0.0, 0.0, 0.0, 90.0, 90.0, 0.0], 1.0),
    # fist, then open to finish
    ([90.0, 45.0, 60.0, 90.0, 90.0, 90.0, 90.0], 0.8), ([90.0, 45.0, 60.0, 90.0, 90.0, 90.0, 90.0], 1.0),
    (OPEN, 1.0),
]

# --- listening ---------------------------------------------------------------------------
SR, HOP = 22050, 512
FPS = SR / HOP              # onset frames per second (~43)
HISTORY_S = 8.0             # tempo is estimated from this much onset history
BPM_RANGE = (70.0, 180.0)
BANDS_HZ = (150.0, 2000.0)  # low (kick, bass) | mid (snare, voice) | high (hats, cymbals)
LOUD_HISTORY_S = 30.0       # loudness is ranked against this much of the song


class Listener:
    """Feed it audio blocks; it keeps a beat clock plus what the song sounds like right now:
    loudness, brightness, how busy the highs are, how hard the lows hit, and per-band hits."""

    def __init__(self):
        n = int(HISTORY_S * FPS)
        self.flux = collections.deque([0.0] * n, maxlen=n)
        self.prev_mag = np.zeros(HOP + 1)
        self.window = np.hanning(2 * HOP)
        self.tail = np.zeros(HOP)
        self.frames = 0
        freqs = np.fft.rfftfreq(2 * HOP, 1 / SR)
        self.freqs = freqs
        self.bands = [freqs < BANDS_HZ[0], (freqs >= BANDS_HZ[0]) & (freqs < BANDS_HZ[1]), freqs >= BANDS_HZ[1]]
        self.band_mean, self.power_mean = [0.0] * 3, 0.0
        self.band_was_hit = [False] * 3
        self.hits = [0.0] * 3              # decaying per-band onset accents (low, mid, high)
        self.onset_times = collections.deque(maxlen=200)  # high-band onset frames, for busyness
        self.db = -80.0
        self.db_hist = collections.deque(maxlen=int(LOUD_HISTORY_S * FPS / 4))
        self.loud_mid, self.loud_span, self.energy, self.level = -30.0, 8.0, 0.0, 0.0
        self.bright, self.punch, self.peak_db = 0.5, 0.0, -120.0
        self.bpm, self.beat, self.confident = 120.0, 0.0, False  # beat = beats elapsed (float)
        self.lock = threading.Lock()

    def feed(self, block):
        """One HOP-sample mono block."""
        frame = np.concatenate([self.tail, block])
        self.tail = block
        spec = np.abs(np.fft.rfft(frame * self.window))
        mag = np.log1p(100 * spec)
        diff = np.maximum(mag - self.prev_mag, 0)
        flux = float(diff.sum())
        self.prev_mag = mag
        rms_db = 20 * math.log10(float(np.sqrt(np.mean(block ** 2))) + 1e-9)
        centroid = float((self.freqs * spec).sum() / (spec.sum() + 1e-9))
        dt = 1 / FPS
        with self.lock:
            self.flux.append(flux)
            self.frames += 1
            self.beat += dt * self.bpm / 60
            self.peak_db = max(self.peak_db, rms_db)
            self.db += (rms_db - self.db) * (0.3 if rms_db > self.db else 0.05)
            if self.frames % 4 == 0:
                self.db_hist.append(self.db)
            if self.frames % int(FPS) == 0 and len(self.db_hist) > FPS / 4:
                # rank loudness against the song so far, not a fixed scale (mic level varies)
                lo, self.loud_mid, hi = np.percentile(np.fromiter(self.db_hist, float), [10, 50, 95])
                self.loud_span = max(hi - lo, 8.0)
            # the song's usual level reads 0.5; a quiet intro ~0, a drop well above its usual ~1
            self.energy = min(1.0, max(0.0, 0.5 + (self.db - self.loud_mid) / self.loud_span))
            if self.db < -60:
                self.energy = 0.0
            self.level += (self.energy - self.level) * dt / 2.0
            if rms_db > -60:
                b = min(1.0, max(0.0, math.log2(max(centroid, 1) / 400) / math.log2(5000 / 400)))
                self.bright += (b - self.bright) * dt / 1.5
            power = spec ** 2
            total = float(power.sum())
            self.power_mean += (total - self.power_mean) * dt / 2.0
            for k, mask in enumerate(self.bands):
                f = float(power[mask].sum())
                # a jump over the band's own recent power; a band that's nearly empty can't "hit"
                r = f / (self.band_mean[k] + 0.01 * self.power_mean + 1e-12)
                self.band_mean[k] += (f - self.band_mean[k]) * dt / 2.0
                hit = r > 1.8 and rms_db > -60
                if hit:
                    self.hits[k] = max(self.hits[k], min(1.0, (r - 1.8) / 2.0))
                    if (k == 2 and r > 2.2 and not self.band_was_hit[k]
                            and (not self.onset_times or self.frames - self.onset_times[-1] > 3)):
                        self.onset_times.append(self.frames)
                self.band_was_hit[k] = hit
                self.hits[k] *= math.exp(-dt / 0.12)
            self.punch += (self.hits[0] - self.punch) * dt / 2.0
            if self.frames % int(FPS / 2) == 0:
                self._track()

    def _track(self):
        """Re-estimate tempo (autocorrelation) and nudge the beat clock toward the onsets."""
        o = np.fromiter(self.flux, float)
        o = o - o.mean()
        if not o.any():
            self.confident = False
            return
        ac = np.correlate(o, o, "full")[len(o) - 1:]
        lo, hi = int(FPS * 60 / BPM_RANGE[1]), int(FPS * 60 / BPM_RANGE[0]) + 1
        lags = np.arange(lo, hi)
        bpms = FPS * 60 / lags
        score = ac[lo:hi] * np.exp(-0.5 * (np.log2(bpms / 120.0) / 0.9) ** 2)  # prefer ~120 BPM
        k = int(np.argmax(score))
        self.confident = score[k] > 0.15 * ac[0]
        if not self.confident:
            return
        lag = float(lags[k])
        if 0 < k < len(score) - 1:  # parabolic refine
            a, b, c = score[k - 1], score[k], score[k + 1]
            lag += 0.5 * (a - c) / (a - 2 * b + c + 1e-12)
        bpm = FPS * 60 / lag
        if abs(bpm - self.bpm) / self.bpm < 0.08:
            self.bpm += 0.3 * (bpm - self.bpm)
        else:
            self.bpm = bpm  # new tempo (or first lock): jump to it
        # phase: comb-sum the onsets at each candidate offset over the history
        period = FPS * 60 / self.bpm
        n = len(o)
        best, best_off = -1e9, 0.0
        for off in np.arange(0, period, 1.0):
            idx = (n - 1 - off - period * np.arange(int(n / period))).astype(int)
            s = o[idx[idx >= 0]].sum()
            if s > best:
                best, best_off = s, off
        measured = best_off / period  # the latest beat was best_off frames ago, so we're that far past it
        err = (measured - self.beat + 0.5) % 1.0 - 0.5
        self.beat += 0.25 * err

    def state(self, lead_s=0.0):
        """A snapshot of the beat clock and the song's character (all 0..1 except beat/bpm)."""
        with self.lock:
            window = 2 * 4 * 60 / self.bpm * FPS  # two bars of frames
            recent = sum(1 for t in self.onset_times if self.frames - t < window)
            busy = min(1.0, recent / 8 / 4.0)  # onsets per beat: ~1 sparse .. 4 = sixteenth hats
            return Feel(self.beat + lead_s * self.bpm / 60, self.bpm, self.confident, self.energy, self.level,
                        self.bright, busy, min(1.0, self.punch * 4), tuple(self.hits))


class Feel(collections.namedtuple("Feel", "beat bpm confident energy level bright busy punch hits")):
    """What the song sounds like at one instant (energy is now, level is the last few seconds)."""


# --- choreography ------------------------------------------------------------------------
# joints: thumb abduction (0-100), thumb flex (0-55), thumb tendon (0-90), index, middle, ring, pinky
LIMITS = [100.0, 55.0, 90.0, 90.0, 90.0, 90.0, 90.0]
PINCHES = [  # from ROUTINE: thumb tip to each finger
    [75.0, 25.0, 30.0, 50.0, 0.0, 0.0, 0.0], [83.0, 42.0, 23.0, 0.0, 50.0, 0.0, 0.0],
    [100.0, 42.0, 23.0, 0.0, 0.0, 52.0, 0.0], [100.0, 35.0, 23.0, 0.0, 0.0, 0.0, 50.0],
]
THUMB_IN = [90.0, 45.0, 60.0]
POSES = [THUMB_IN + [0.0, 0.0, 90.0, 90.0],    # peace
         THUMB_IN + [0.0, 90.0, 90.0, 0.0],    # rock on
         [0.0] * 3 + [90.0, 90.0, 90.0, 0.0],  # shaka
         [0.0] * 3 + [0.0, 90.0, 90.0, 0.0]]   # i love you
FINGER_BAND = [2, 1, 1, 0]  # index follows the highs, middle/ring the mids, pinky the lows
MIN_CYCLE_S = 0.5           # at the 50% speed cap a finger can't swing much faster than this


def ease(x):
    """0..1 -> 0..1, smooth at both ends."""
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def blend(a, b, t):
    return [p + (q - p) * t for p, q in zip(a, b)]


def per_beat(f):
    """Beats per move cycle: 1, or 2 (half time) when one beat is too quick for the servos."""
    return 1 if 60 / f.bpm >= MIN_CYCLE_S * 0.9 else 2


def sway(f, amp):
    """Quiet parts: a slow curl drifts across the hand over two bars."""
    fingers = [amp * 55 * (0.5 - 0.5 * math.cos(2 * math.pi * (f.beat / 8 - i * 0.12))) for i in range(4)]
    return [amp * (20 + 20 * math.sin(math.pi * f.beat / 4)), 0.0, 0.0] + fingers


def wave(f, amp):
    """A curl rolls index -> pinky every two beats; the thumb sways with it."""
    fingers = [amp * 80 * (0.5 - 0.5 * math.cos(2 * math.pi * (f.beat / 2 - i * 0.18))) for i in range(4)]
    return [amp * (30 + 25 * math.sin(math.pi * f.beat)), 0.0, 0.0] + fingers


def flutter(f, amp):
    """Busy hats / fast flow: small quick ripples, as fast as the servos allow."""
    rate = 1.0 if 60 / f.bpm >= MIN_CYCLE_S else 0.5
    fingers = [amp * 40 * (0.5 - 0.5 * math.cos(2 * math.pi * (f.beat * rate - i * 0.25))) for i in range(4)]
    return [amp * 25, 0.0, 0.0] + fingers


def bounce(f, amp):
    """Heavy kicks: all fingers dip on the beat (or every other beat), quick down, slower release."""
    b = f.beat / per_beat(f)
    ph = b % 1.0
    d = ease(ph / 0.25) if ph < 0.25 else 1 - ease((ph - 0.25) / 0.75)
    return [amp * 40 * d, amp * 15 * d, amp * 20 * d] + [amp * 60 * d * (1 - 0.1 * i) for i in range(4)]


def pinch_walk(f, amp):
    """Bright, melodic parts: the thumb taps each fingertip, one per beat, index -> pinky and back."""
    order = [0, 1, 2, 3, 2, 1]
    b = f.beat / per_beat(f)
    i, ph = int(b) % len(order), b % 1.0
    a, c = PINCHES[order[i]], PINCHES[order[(i + 1) % len(order)]]
    pose = blend(a, c, ease((ph - 0.5) / 0.5))       # glide to the next finger in the back half
    return [v * (0.4 + 0.6 * amp) for v in pose]


def pose_hits(f, amp):
    """Big loud moments: hit a pose on each bar's downbeat, groove, release before the next."""
    bar, ph = int(f.beat // 4), (f.beat % 4) / 4
    pose = POSES[(bar + int(f.bright * 4)) % len(POSES)]
    t = ease(ph / 0.12) if ph < 0.85 else 1 - ease((ph - 0.85) / 0.15)
    groove = 0.08 * math.sin(2 * math.pi * f.beat)
    return [v * (t * (0.6 + 0.4 * amp) + groove * (v > 0)) for v in pose]


def pick_move(f):
    """Which move fits what the song is doing right now."""
    if f.level < 0.25:
        return sway
    if f.busy > 0.6:
        return flutter
    if f.level > 0.65 and f.punch > 0.5:
        return pose_hits
    if f.punch > 0.4:
        return bounce
    if f.bright > 0.55:
        return pinch_walk
    return wave


MIN_BARS = 2          # hold a move at least this long so it reads as a move
CROSSFADE_BEATS = 2.0


class Choreographer:
    """Picks a move at each bar line from what the music is doing, and crossfades between moves.
    On top of the move, each finger flicks with hits in its frequency band."""

    def __init__(self):
        self.move, self.prev, self.switched_at, self.bar, self.wanted = sway, None, -1e9, None, None

    def __call__(self, f):
        bar = int(f.beat // 4)
        if bar != self.bar:
            self.bar = bar
            want = pick_move(f)  # switch only when two bar lines in a row agree, so noise can't flip it
            if want is self.wanted and want is not self.move and f.beat - self.switched_at >= 4 * MIN_BARS:
                self.prev, self.move, self.switched_at = self.move, want, f.beat
            self.wanted = want
        amp = 0.25 + 0.75 * f.energy
        q = self.move(f, amp)
        fade = (f.beat - self.switched_at) / CROSSFADE_BEATS
        if self.prev and fade < 1:
            q = blend(self.prev(f, amp), q, ease(fade))
        for i, band in enumerate(FINGER_BAND):
            q[3 + i] += 25 * f.hits[band] * amp
        return [min(hi, max(0.0, v)) for v, hi in zip(q, LIMITS)]


# --- motion safety -----------------------------------------------------------------------
RATE = 50                     # control loop, Hz
SMOOTH_S = 0.06               # low-pass time constant
MAX_SPEED = 400.0             # deg/s per joint
LEAD_S = 0.10                 # move this early to cover mic + servo latency
TEMP_WARM, TEMP_HOT = 50.0, 60.0  # °C: shrink the dance above warm, stop at hot
TEMP_EVERY_S = 3.0


class Smoother:
    def __init__(self, start):
        self.q = list(start)

    def step(self, target, dt):
        a = 1 - math.exp(-dt / SMOOTH_S)
        lim = MAX_SPEED * dt
        self.q = [q + max(-lim, min(lim, (t - q) * a)) for q, t in zip(self.q, target)]
        return self.q


# --- Music.app ---------------------------------------------------------------------------
def osa(script):
    return subprocess.run(["osascript", "-e", script], capture_output=True, text=True).stdout.strip()


def start_song(name, started):
    """Start the track and return once Music reports it playing (polls every 50 ms)."""
    if name:
        osa(f'tell application "Music" to play (first track of library playlist 1 whose name contains "{name}")')
    else:
        osa(f'tell application "Music" to play some track of user playlist "{PLAYLIST}"')
    for _ in range(400):  # up to 20 s
        if osa('tell application "Music" to get player state') == "playing":
            started.set()
            return
        time.sleep(0.05)


def watch_song(track, playing):
    """Clear `playing` once Music stops or moves on from `track`."""
    while playing.is_set():
        time.sleep(1.0)
        if (osa('tell application "Music" to get player state') != "playing"
                or osa('tell application "Music" to get name of current track') != track):
            playing.clear()


def dance(hand, track):
    import sounddevice as sd
    listener = Listener()

    def on_audio(indata, frames, t, status):
        listener.feed(indata[:, 0].astype(np.float64))

    playing = threading.Event()
    playing.set()
    threading.Thread(target=watch_song, args=(track, playing), daemon=True).start()
    start = (hand.get_joint_positions_compact() if hand else None) or OPEN
    smooth = Smoother(start)
    choreo = Choreographer()
    scale, next_temp, last_print, warned = 1.0, 0.0, 0.0, False
    t0 = time.monotonic()
    try:
        with sd.InputStream(samplerate=SR, blocksize=HOP, channels=1, callback=on_audio):
            while playing.is_set():
                now = time.monotonic()
                f = listener.state(LEAD_S)
                if not warned and now - t0 > 4 and listener.peak_db < -70:
                    warned = True  # macOS hands a denied app silence, not an error
                    print("MICROPHONE IS SILENT: the hand can't hear the song. Allow Helping Hands (or the "
                          "terminal) in System Settings > Privacy & Security > Microphone.", flush=True)
                intro = ease((now - t0) / 3.0)  # fade in while the beat locks
                target = choreo(f) if f.confident else sway(f, 0.3 * f.energy)
                q = smooth.step([v * intro * scale for v in target], 1 / RATE)
                if hand:
                    hand.set_joint_positions(q)
                    if now >= next_temp:
                        next_temp = now + TEMP_EVERY_S
                        temps = hand.get_actuator_temperatures()
                        if temps:
                            hot = max(temps)
                            if hot >= TEMP_HOT:
                                print(f"servo at {hot:.0f} °C: stopping the dance")
                                break
                            scale = 1.0 if hot <= TEMP_WARM else 1 - 0.7 * (hot - TEMP_WARM) / (TEMP_HOT - TEMP_WARM)
                if now - last_print >= 1.0:
                    last_print = now
                    print(describe(f, choreo) + f"  scale {scale:.2f}", flush=True)
                time.sleep(max(0.0, 1 / RATE - (time.monotonic() - now)))
    except KeyboardInterrupt:
        pass
    finally:
        if hand:  # ease back open
            hand.run_trajectory([(smooth.q, 0.0), (OPEN, 1.0)])


def describe(f, choreo):
    return (f"{f.bpm:5.1f} bpm {'lock' if f.confident else '....'}  beat {f.beat:7.2f}  level {f.level:.2f}"
            f"  bright {f.bright:.2f}  busy {f.busy:.2f}  punch {f.punch:.2f}  move {choreo.move.__name__}")


def simulate(path):
    """Dance to an audio file offline (no hand, no mic): print the moves and the motion they make."""
    import scipy.io.wavfile, scipy.signal
    sr, x = scipy.io.wavfile.read(path)
    if x.dtype.kind in "iu":
        x = x / float(np.iinfo(x.dtype).max)
    x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != SR:
        x = scipy.signal.resample_poly(x, SR, sr)
    listener, choreo, smooth = Listener(), Choreographer(), Smoother(OPEN)
    trail, moves = [], []
    for i in range(0, len(x) - HOP, HOP):
        listener.feed(x[i:i + HOP])
        if listener.frames % max(1, int(FPS / RATE)) == 0:
            f = listener.state(LEAD_S)
            target = choreo(f) if f.confident else sway(f, 0.3 * f.energy)
            trail.append(smooth.step(target, 1 / RATE * max(1, int(FPS / RATE))))
            if not moves or moves[-1][1] != choreo.move.__name__:
                moves.append((i / SR, choreo.move.__name__))
        if listener.frames % int(FPS * 2) == 0:
            print(f"{i / SR:6.1f}s  " + describe(listener.state(), choreo))
    q = np.array(trail)
    print("moves:", ", ".join(f"{t:.0f}s {m}" for t, m in moves))
    print("joint mean:", np.round(q.mean(0)).astype(int).tolist(), " joint std:", np.round(q.std(0)).astype(int).tolist())
    return q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song", nargs="?", help='track name (default: random from the "¿?" playlist)')
    ap.add_argument("--routine", action="store_true", help="play the fixed routine instead of dancing")
    ap.add_argument("--dry-run", action="store_true", help="listen and print, don't move the hand")
    ap.add_argument("--wav", help="dance to this audio file offline (prints moves; no song, mic or hand)")
    args = ap.parse_args()
    if args.wav:
        simulate(args.wav)
        return

    hand = None
    ports = sorted(glob.glob("/dev/cu.usbmodem*"))
    if not args.dry_run and not ports:
        sys.exit("hand not connected; nothing played or moved (use --dry-run to just listen)")
    started = threading.Event()
    song = threading.Thread(target=start_song, args=(args.song, started))
    song.start()
    if not args.dry_run:
        from aero_open_sdk.aero_hand import AeroHand
        import hand_speed
        # open the hand's port while the song starts, so neither waits on the other
        hand = AeroHand(port=ports[0])
        hand_speed.limit(hand)  # 50% unless Jake asks for more
        hand.ser.write_timeout = 0.05  # SDK default 10 ms drops a frame when USB stalls briefly
    song.join()
    if not started.is_set():
        if hand:
            hand.close()
        sys.exit(f"song '{args.song}' did not start; hand not moved")
    track = osa('tell application "Music" to get name of current track')
    print("playing", track)
    try:
        if args.routine:
            hand and hand.run_trajectory(ROUTINE)
        else:
            dance(hand, track)
    finally:
        if hand:
            hand.close()
    print("performance done to", track)


if __name__ == "__main__":
    main()
