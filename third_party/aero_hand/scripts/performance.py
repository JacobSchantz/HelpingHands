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


class Listener:
    """Feed it audio blocks; it keeps loudness, an onset accent, and a beat clock."""

    def __init__(self):
        n = int(HISTORY_S * FPS)
        self.flux = collections.deque([0.0] * n, maxlen=n)
        self.prev_mag = np.zeros(HOP + 1)
        self.window = np.hanning(2 * HOP)
        self.tail = np.zeros(HOP)
        self.frames = 0
        self.db, self.loud_hi, self.loud_lo = -80.0, -30.0, -60.0
        self.accent = 0.0
        self.bpm, self.beat, self.confident = 120.0, 0.0, False  # beat = beats elapsed (float)
        self.lock = threading.Lock()

    def feed(self, block):
        """One HOP-sample mono block."""
        frame = np.concatenate([self.tail, block])
        self.tail = block
        mag = np.log1p(100 * np.abs(np.fft.rfft(frame * self.window)))
        flux = float(np.maximum(mag - self.prev_mag, 0).sum())
        self.prev_mag = mag
        rms_db = 20 * math.log10(float(np.sqrt(np.mean(block ** 2))) + 1e-9)
        with self.lock:
            self.flux.append(flux)
            self.frames += 1
            dt = 1 / FPS
            self.beat += dt * self.bpm / 60
            # loudness: fast-attack/slow-release level against a slowly adapting range
            self.db += (rms_db - self.db) * (0.3 if rms_db > self.db else 0.05)
            self.loud_hi = max(self.db, self.loud_hi - dt * 0.5)
            self.loud_lo = min(self.db, self.loud_lo + dt * 0.5)
            recent = np.fromiter(self.flux, float)[-int(FPS):]
            mean = recent.mean() + 1e-6
            if flux > 2.0 * mean:
                self.accent = max(self.accent, min(1.0, (flux / mean - 2.0) / 2.0))
            self.accent *= math.exp(-dt / 0.15)
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
        with self.lock:
            span = max(self.loud_hi - self.loud_lo, 6.0)
            energy = min(1.0, max(0.0, (self.db - self.loud_lo) / span)) if self.db > -55 else 0.0
            return self.beat + lead_s * self.bpm / 60, self.bpm, energy, self.accent, self.confident


# --- choreography ------------------------------------------------------------------------
# joints: thumb abduction (0-100), thumb flex (0-55), thumb tendon (0-90), index, middle, ring, pinky
PINCHES = [  # from ROUTINE: thumb tip to each finger
    [75.0, 25.0, 30.0, 50.0, 0.0, 0.0, 0.0], [83.0, 42.0, 23.0, 0.0, 50.0, 0.0, 0.0],
    [100.0, 42.0, 23.0, 0.0, 0.0, 52.0, 0.0], [100.0, 35.0, 23.0, 0.0, 0.0, 0.0, 50.0],
]
THUMB_IN = [90.0, 45.0, 60.0]
POSES = [THUMB_IN + [0.0, 0.0, 90.0, 90.0],    # peace
         THUMB_IN + [0.0, 90.0, 90.0, 0.0],    # rock on
         [0.0] * 3 + [90.0, 90.0, 90.0, 0.0],  # shaka
         [0.0] * 3 + [0.0, 90.0, 90.0, 0.0]]   # i love you


def ease(x):
    """0..1 -> 0..1, smooth at both ends."""
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def blend(a, b, t):
    return [p + (q - p) * t for p, q in zip(a, b)]


def wave(beat, amp):
    """A curl rolls index -> pinky every two beats; the thumb sways with it."""
    fingers = [amp * 80 * (0.5 - 0.5 * math.cos(2 * math.pi * (beat / 2 - i * 0.18))) for i in range(4)]
    return [amp * (30 + 25 * math.sin(math.pi * beat)), 0.0, 0.0] + fingers


def bounce(beat, amp):
    """All fingers dip on every beat: quick down, slower release."""
    ph = beat % 1.0
    d = ease(ph / 0.25) if ph < 0.25 else 1 - ease((ph - 0.25) / 0.75)
    return [amp * 40 * d, amp * 15 * d, amp * 20 * d] + [amp * 60 * d * (1 - 0.1 * i) for i in range(4)]


def pinch_walk(beat, amp):
    """The thumb taps each fingertip, one per beat, index -> pinky and back."""
    order = [0, 1, 2, 3, 2, 1]
    i, ph = int(beat) % len(order), beat % 1.0
    a, b = PINCHES[order[i]], PINCHES[order[(i + 1) % len(order)]]
    pose = blend(a, b, ease((ph - 0.5) / 0.5))       # glide to the next finger in the back half
    return [v * (0.4 + 0.6 * amp) for v in pose]


def pose_hits(beat, amp):
    """Hit a pose on each bar's downbeat, hold it with a small groove, release before the next."""
    bar, ph = int(beat // 4), (beat % 4) / 4
    pose = POSES[bar % len(POSES)]
    t = ease(ph / 0.12) if ph < 0.85 else 1 - ease((ph - 0.85) / 0.15)
    groove = 0.08 * math.sin(2 * math.pi * beat)
    return [v * (t * (0.6 + 0.4 * amp) + groove * (v > 0)) for v in pose]


MOVES = [wave, bounce, pinch_walk, pose_hits]
BARS_PER_MOVE = 8
CROSSFADE_BEATS = 2.0


def choreograph(beat, energy, accent):
    """Joint targets at this beat: current move, crossfaded into the next at the boundary."""
    span = 4 * BARS_PER_MOVE
    n, pos = int(beat // span), beat % span
    amp = 0.35 + 0.65 * energy
    cur = MOVES[n % len(MOVES)](beat, amp)
    if pos > span - CROSSFADE_BEATS:
        cur = blend(cur, MOVES[(n + 1) % len(MOVES)](beat, amp), ease((pos - span + CROSSFADE_BEATS) / CROSSFADE_BEATS))
    flick = 15 * accent * energy  # onsets add a little curl on top
    return [v if j < 3 else v + flick for j, v in enumerate(cur)]


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
    scale, next_temp, last_print = 1.0, 0.0, 0.0
    t0 = time.monotonic()
    try:
        with sd.InputStream(samplerate=SR, blocksize=HOP, channels=1, callback=on_audio):
            while playing.is_set():
                now = time.monotonic()
                beat, bpm, energy, accent, confident = listener.state(LEAD_S)
                intro = ease((now - t0) / 3.0)  # fade in while the beat locks
                target = choreograph(beat, energy, accent) if confident else wave(beat, 0.3 * energy)
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
                    print(f"{bpm:5.1f} bpm {'lock' if confident else '....'}  energy {energy:.2f}"
                          f"  beat {beat:7.2f}  move {MOVES[int(beat // (4 * BARS_PER_MOVE)) % len(MOVES)].__name__}"
                          f"  scale {scale:.2f}", flush=True)
                time.sleep(max(0.0, 1 / RATE - (time.monotonic() - now)))
    except KeyboardInterrupt:
        pass
    finally:
        if hand:  # ease back open
            hand.run_trajectory([(smooth.q, 0.0), (OPEN, 1.0)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song", nargs="?", help='track name (default: random from the "¿?" playlist)')
    ap.add_argument("--routine", action="store_true", help="play the fixed routine instead of dancing")
    ap.add_argument("--dry-run", action="store_true", help="listen and print, don't move the hand")
    args = ap.parse_args()

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
