#!/usr/bin/env python3
"""Teach the hand by moving it, then play it back.

Usage: teach.py record [--seconds 300] [--torque 10,30,30,40,40,25,25]
       teach.py replay [take.json | last] [--full] [--dry-run]
       teach.py label [take.json | last]  prints (and with --save, sets) the take's auto-label
       teach.py list                      one JSON line per take, newest first (the app's list)
       teach.py rename <take.json | last> <name>
       teach.py delete <take.json>        moves it to TAKES/deleted, not gone
       teach.py audio <take.json> <sidecar.json>  attaches the app's recording of the mic (below)

record: transparent mode. Every servo gets a small constant pull (CTRL_TOR) that just keeps its cord
taut against the return spring, so the fingers can be moved by hand (or a glove) both ways. All 7
actuations are logged at ~100 Hz with timestamps until Stop (SIGINT) or --seconds, then the hand
relaxes and the take is saved to TAKES, named from its motion ("Index finger curled in, index finger
extended"; rename overrides it). About 10 times a second it prints "pos" and each servo's place in its
range, 0 (open) to 100, which the app draws as live bars. See plans/aero-hand-glove-teaching.md.

audio: the app records the mic for the whole take (it owns the mic permission), transcribes it on the
device, and hands both over with `audio`. The take keeps "audio" (the .m4a next to it, and "offset", the
seconds of audio before the take's t=0, from both clocks' wall time), "transcript", and "words" on the
take's clock. Narration names the take instead of the motion label, unless it was already renamed.

replay: position mode. Every take is cleaned first (clean): smoothed, and a servo that travelled less
than DEADBAND_DEG is held still at its middle value, so read noise and slow drift aren't replayed.
  motion (default): the key poses only (each moving servo's turning points, and places it paused),
    driven between as smooth moves at the speed cap (AERO_SPEED_PCT, 50% by default).
  --full: the recorded timing, slowed down only where a servo would beat the speed cap. With audio, it
    prints "audio <file> <seconds in> <rate>" as the first frame goes out, and the app plays it from there.
Moving servos run at MOVE_TORQUE, still ones at STILL_TORQUE. Commands go out at SEND_HZ, not 100 Hz:
flooding the bus starved the firmware's position reads and left the servos hunting. Glides to the first
pose first and holds the last one low-power (hold.py). Stops and relaxes at TEMP_HOT. --dry-run prints.
"""
import glob, json, math, os, signal, sys, time
from aero_open_sdk.aero_hand import AeroHand
import hand_speed, hold

NAMES = ["thumb_abd", "thumb_flex", "thumb_tendon", "index", "middle", "ring", "pinky"]
# Transparent-mode pull per servo. Bench test 1 (2026-10-17, torque 50 everywhere): index and middle
# followed both ways but rested a bit curled, ring and pinky stayed curled, so all are lowered.
# Lowered about a quarter again after take-20261017-170553 rested 8-15% curled and the thumb tendon crept
# closed (82 vs 38). But a release test (fingers curled to 60%, then the pull at 1x, 0.75x, 0.5x and 0.35x
# of the old values) found every finger stayed at 60% for 3 s: the springs don't back-drive the spools, so
# fingers rest where they're left and less pull mostly helps the thumb's creep.
TORQUE = [8, 22, 20, 30, 30, 18, 18]
HZ = 100
TEMP_HOT = 60.0         # °C: relax and stop, like performance.py
TEMP_EVERY_S = 1.0
GLIDE_S = 1.0           # to the take's first frame before playing
DEG_S_PER_UNIT = 0.732 * 6  # SET_SPE unit is 0.732 RPM (hand_speed.py)
TAKES = os.path.expanduser("~/HelpingHands-tools/aero/takes")
LIVE_EVERY_S = 0.1
SEND_HZ = 25            # replay command rate; 100 Hz CTRL_POS hogs the servo bus
SMOOTH_S = 0.15         # moving-average window
DEADBAND_DEG = 20.0     # a servo that travelled less than this (smoothed) didn't really move
SWING_FRAC = 0.25       # a turning point counts if it swings back this much of the servo's travel...
SWING_MIN_DEG = 30.0    # ...and at least this many degrees
SETTLE_S = 0.5          # the start of a recording, while the pull takes up the slack
PAUSE_S, PAUSE_DEG = 0.6, 5.0  # a pause partway through a move: this long within this many degrees
MERGE_S = 0.3           # key points closer than this are one key pose
KEY_HOLD_S = 0.25       # motion mode rests this long on each key pose
MOVE_TORQUE, STILL_TORQUE = 500, 200  # replay torque limits (SET_TOR) for moving and still servos
# What curling (actuation going up) and opening are called in labels; the two thumb servos are one thumb.
LABELS = {"thumb_abd": ("thumb", "swung across", "swung back"), "thumb_flex": ("thumb", "curled in", "extended"),
          "thumb_tendon": ("thumb", "curled in", "extended")}


def take_path(name):
    """A take by file name (the app passes those) or path; "last" or None is the newest."""
    if name in (None, "last"):
        takes = sorted(glob.glob(os.path.join(TAKES, "take-*.json")))
        if not takes:
            sys.exit(f"no takes in {TAKES}; record one first")
        return takes[-1]
    path = name if os.sep in name else os.path.join(TAKES, name)
    if not os.path.isfile(path):
        sys.exit(f"no take {name}")
    return path


def connect():
    ports = sorted(glob.glob("/dev/cu.usbmodem*"))
    if not ports:
        sys.exit("hand not connected; not moved")
    hand = AeroHand(port=ports[0])
    hand.ser.write_timeout = 0.05
    return hand


def too_hot(hand):
    temps = hand.get_actuator_temperatures()
    if temps and max(temps) >= TEMP_HOT:
        print(f"HOT: {NAMES[temps.index(max(temps))]} at {max(temps):.0f} °C, relaxing", flush=True)
        return True
    return False


def record(seconds, torque):
    hand = connect()
    samples, temps, t0, started_at = [], [], time.monotonic(), time.time()
    print("recording: move the fingers; Stop saves the take. torque", torque, flush=True)
    try:
        hand.ctrl_torque(torque)
        next_tick = next_torque = next_temp = next_live = t0
        lo, hi = hand.actuation_lower_limits, hand.actuation_upper_limits
        while (now := time.monotonic()) - t0 < seconds:
            if now >= next_torque:  # resend now and then, in case a frame was dropped
                hand.ctrl_torque(torque)
                next_torque = now + 0.5
            if now >= next_temp:
                t = hand.get_actuator_temperatures()
                if t:
                    temps.append([round(now - t0, 3)] + t)
                    if max(t) >= TEMP_HOT:
                        print(f"HOT: {max(t):.0f} °C, stopping", flush=True)
                        break
                next_temp = now + TEMP_EVERY_S
            a = hand.get_actuations()
            if a:
                samples.append([round(time.monotonic() - t0, 4)] + [round(x, 2) for x in a])
                if now >= next_live:
                    pct = [max(0, min(100, round(100 * (x - l) / (h - l)))) for x, l, h in zip(a, lo, hi)]
                    print("pos", *pct, flush=True)
                    next_live = now + LIVE_EVERY_S
            next_tick += 1 / HZ
            time.sleep(max(0.0, next_tick - time.monotonic()))
    except KeyboardInterrupt:
        pass
    finally:
        hand.ctrl_torque([0] * 7)
        hand.close()
    if len(samples) < 2:
        sys.exit("nothing recorded")
    os.makedirs(TAKES, exist_ok=True)
    path = os.path.join(TAKES, time.strftime("take-%Y%m%d-%H%M%S.json"))
    with open(path, "w") as f:
        json.dump({"names": NAMES, "torque": torque, "hz": HZ, "name": label(samples), "started_at": started_at,
                   "samples": samples, "temps": temps}, f)
    dur = samples[-1][0]
    print(f"saved {path}: {dur:.1f} s, {len(samples)} samples ({len(samples) / max(dur, 1e-3):.0f} Hz)", flush=True)


def stretch_for(samples, cap_deg_s):
    """How much slower than recorded the take has to play so no servo beats the speed cap.
    Speeds are measured over ~50 ms so read noise doesn't count as motion."""
    peak, j = 0.0, 0
    for i, s in enumerate(samples):
        while samples[i][0] - samples[j][0] > 0.05:
            j += 1
        if j and (dt := s[0] - samples[j - 1][0]) > 0:
            peak = max(peak, max(abs(a - b) for a, b in zip(s[1:], samples[j - 1][1:])) / dt)
    return max(1.0, peak / cap_deg_s), peak


def clean(samples):
    """The take resampled to SEND_HZ and smoothed; servos that barely moved are held at their median.
    The first SETTLE_S is skipped: that's the cords going taut, not a move. Returns (times on the take's
    clock, rows of 7, moving flags)."""
    if samples[-1][0] > 2 * SETTLE_S:
        samples = [s for s in samples if s[0] >= SETTLE_S]
    dt, t0 = 1 / SEND_HZ, samples[0][0]
    times = [t0 + k * dt for k in range(int((samples[-1][0] - t0) / dt) + 1)]
    rows, j = [], 0
    for t in times:  # linear interpolation onto the grid
        while j + 2 < len(samples) and samples[j + 1][0] <= t:
            j += 1
        a, b = samples[j], samples[min(j + 1, len(samples) - 1)]
        f = 0 if b[0] == a[0] else max(0.0, min(1.0, (t - a[0]) / (b[0] - a[0])))
        rows.append([x + (y - x) * f for x, y in zip(a[1:], b[1:])])
    half = max(1, round(SMOOTH_S * SEND_HZ / 2))
    smooth = []
    for k in range(len(rows)):
        win = rows[max(0, k - half):k + half + 1]
        smooth.append([sum(r[i] for r in win) / len(win) for i in range(7)])
    moving = []
    for i in range(7):
        col = [r[i] for r in smooth]
        moving.append(max(col) - min(col) >= DEADBAND_DEG)
        if not moving[i]:
            still = sorted(col)[len(col) // 2]
            for r in smooth:
                r[i] = still
    return times, smooth, moving


def key_points(col):
    """One servo's key points as indexes into col: the start, every turning point that swings back far
    enough (SWING_FRAC of its travel, at least SWING_MIN_DEG), and the places it paused for PAUSE_S on
    the way. A drift at the end smaller than a swing is dropped, so the take ends at the last real pose."""
    swing = max(SWING_MIN_DEG, SWING_FRAC * (max(col) - min(col)))
    points, ext, direction = [0], 0, 0
    for k in range(1, len(col)):
        if direction == 0:
            if abs(col[k] - col[0]) >= swing:
                direction, ext = (1 if col[k] > col[0] else -1), k
        elif (col[k] - col[ext]) * direction > 0:
            ext = k  # still going the same way
        elif abs(col[k] - col[ext]) >= swing:
            points.append(ext)  # turned around for real
            direction, ext = -direction, k
    if direction and abs(col[ext] - col[points[-1]]) >= swing:
        points.append(ext)
    # pauses partway through a move, far enough from both ends of it to be a pose of their own
    n, k = max(2, round(PAUSE_S * SEND_HZ)), points[0]
    for a, b in zip(points[:], points[1:]):
        k = a + 1
        while k + n <= b:
            win = col[k:k + n]
            if max(win) - min(win) <= PAUSE_DEG:
                mid = col[k + n // 2]
                if min(abs(mid - col[a]), abs(mid - col[b])) >= swing:
                    points.append(k + n // 2)
                k += n
            else:
                k += 1
    return sorted(points)


def key_poses(samples):
    """The take as key poses: rows of 7. Each moving servo goes from key point to key point (linear in
    time between its own points, flat after its last), sampled wherever any servo has one."""
    times, rows, moving = clean(samples)
    tracks = {i: key_points([r[i] for r in rows]) for i in range(7) if moving[i]}
    keys = sorted({0}.union(*tracks.values()))
    merged = [keys[0]]
    for k in keys[1:]:
        if times[k] - times[merged[-1]] < MERGE_S:
            merged[-1] = k  # the later point of a cluster: the moves have finished by then
        else:
            merged.append(k)

    def at(i, k):
        pts = tracks.get(i)
        if not pts:
            return rows[0][i]
        if k >= pts[-1]:
            return rows[pts[-1]][i]
        b = next(p for p in pts if p >= k)
        a = max([p for p in pts if p <= k], default=b)
        return rows[a][i] if a == b else rows[a][i] + (rows[b][i] - rows[a][i]) * (k - a) / (b - a)

    poses = []
    for k in merged:
        pose = [at(i, k) for i in range(7)]
        if not poses or max(abs(x - y) for x, y in zip(pose, poses[-1])) >= PAUSE_DEG:
            poses.append(pose)
    return poses, moving


def label(samples):
    """A plain-English summary of what moved, in time order: "Thumb curled and extended, then index,
    middle, ring and pinky each curled and extended". The thumb's three servos read as one thumb,
    described by whichever travelled furthest. A move is timed where it crosses halfway, so a finger
    that sat still before its turn isn't counted as moving from the start."""
    times, rows, moving = clean(samples)
    cols = [[r[i] for r in rows] for i in range(7)]
    travel = [max(c) - min(c) if m else 0 for c, m in zip(cols, moving)]
    thumb = max(range(3), key=lambda i: travel[i])
    events = []  # (halfway time, finger, verb)
    for i, name in enumerate(NAMES):
        if not moving[i] or i < 3 and i != thumb:
            continue
        finger, up, down = LABELS.get(name, (name + " finger", "curled in", "extended"))
        col, pts = cols[i], key_points(cols[i])
        swing = max(SWING_MIN_DEG, SWING_FRAC * travel[i])
        for a, b in zip(pts, pts[1:]):
            if abs(col[b] - col[a]) >= swing:
                half = (col[a] + col[b]) / 2
                k = next(k for k in range(a, b + 1) if (col[k] - half) * (col[b] - col[a]) >= 0)
                events.append((times[k], finger, up if col[b] > col[a] else down))
    events.sort()
    groups = []  # [fingers, verb]: fingers doing the same thing at about the same time
    last_t = None
    for t, finger, verb in events:
        g = groups[-1] if groups else None
        if g and g[1] == verb and t - last_t < 0.5:
            if finger not in g[0]:
                g[0].append(finger)
        elif g and g[0] == [finger] and g[1] == verb:
            continue  # a pause partway through the same move
        else:
            groups.append([[finger], verb])
        last_t = t
    runs = []  # [fingers, verbs]: one finger (or set) doing several things in a row
    for fingers, verb in groups:
        if runs and runs[-1][0] == fingers:
            runs[-1][1].append(verb)
        else:
            runs.append([fingers, [verb]])
    said = []  # [finger sets, verb text]: in turn, each doing the same thing
    for fingers, verbs in runs:
        text = verb_text(verbs)
        if said and said[-1][1] == text:
            said[-1][0].append(fingers)
        else:
            said.append([[fingers], text])
    if not said:
        return "Still"
    phrases = []
    for sets, text in said:
        names = [f for fs in sets for f in fs]
        if len(names) == 1:
            phrases.append(f"{names[0]} {text}")
        else:
            names = [f.replace(" finger", "") for f in names]
            each = " each" if len(sets) > 1 else ""
            phrases.append(f"{', '.join(names[:-1])} and {names[-1]}{each} {text}")
    if len(phrases) > 6:
        phrases = phrases[:5] + ["and more"]
    text = ", then ".join(phrases)
    return text[0].upper() + text[1:]


def verb_text(verbs):
    """["curled in", "extended", "curled in", "extended"] -> "curled and extended 2 times"."""
    times = 1
    for n in range(1, len(verbs) // 2 + 1):
        if len(verbs) % n == 0 and verbs == verbs[:n] * (len(verbs) // n):
            verbs, times = verbs[:n], len(verbs) // n
            break
    if len(verbs) > 1:
        verbs = [v.removesuffix(" in") for v in verbs]
    text = verbs[0] if len(verbs) == 1 else ", ".join(verbs[:-1]) + " and " + verbs[-1]
    return text + (f" {times} times" if times > 1 else "")


def list_takes():
    for path in sorted(glob.glob(os.path.join(TAKES, "take-*.json")), reverse=True):
        try:
            with open(path) as f:
                take = json.load(f)
            seconds = take["samples"][-1][0]
        except (OSError, ValueError, KeyError, IndexError):
            continue
        print(json.dumps({"file": os.path.basename(path), "name": take.get("name", ""),
                          "seconds": round(seconds, 1), "audio": "audio" in take,
                          "recorded": time.mktime(time.strptime(os.path.basename(path), "take-%Y%m%d-%H%M%S.json"))}))


def rename(name, new):
    path = take_path(name)
    with open(path) as f:
        take = json.load(f)
    take["name"] = new.strip()
    write_take(path, take)
    print(f"renamed {os.path.basename(path)}: {take['name']}")


def write_take(path, take):
    with open(path + ".tmp", "w") as f:
        json.dump(take, f)
    os.replace(path + ".tmp", path)


def attach_audio(name, sidecar):
    """The app's sidecar: {"file": the .m4a, "started_at": wall time the mic started, "transcript",
    "words": [[seconds into the audio, word], ...]}. Moves the audio next to the take and stores it."""
    path = take_path(name)
    with open(path) as f:
        take = json.load(f)
    with open(sidecar) as f:
        heard = json.load(f)
    audio = path.removesuffix(".json") + os.path.splitext(heard["file"])[1]
    os.replace(heard["file"], audio)
    offset = take.get("started_at", heard["started_at"]) - heard["started_at"]
    text = " ".join(heard.get("transcript", "").split())
    take["audio"] = {"file": os.path.basename(audio), "offset": round(offset, 3)}
    take["transcript"] = text
    take["words"] = [[round(t - offset, 2), w] for t, w in heard.get("words", [])]
    take.setdefault("motion", label(take["samples"]))
    if text and take.get("name") == take["motion"]:
        take["name"] = narration_name(text)
    write_take(path, take)
    os.remove(sidecar)
    print(f"audio {os.path.basename(audio)}: {take['name']!r}" + (f", heard {text!r}" if text else ", nothing said"))


def narration_name(text, most=80):
    """What was said, as a name: capitalised, cut at a word boundary."""
    text = text.strip().rstrip(".")
    if len(text) > most:
        text = text[:most].rsplit(" ", 1)[0] + "…"
    return text[0].upper() + text[1:]


def delete(name):
    path = take_path(name)
    os.makedirs(os.path.join(TAKES, "deleted"), exist_ok=True)
    os.replace(path, os.path.join(TAKES, "deleted", os.path.basename(path)))
    audio = path.removesuffix(".json") + ".m4a"
    if os.path.isfile(audio):
        os.replace(audio, os.path.join(TAKES, "deleted", os.path.basename(audio)))
    print(f"deleted {os.path.basename(path)} (kept in {TAKES}/deleted)")


def ease(a, b, f):
    f = (1 - math.cos(math.pi * f)) / 2
    return [x + (y - x) * f for x, y in zip(a, b)]


def replay(path, dry_run, full=False):
    path = take_path(path)
    with open(path) as f:
        take = json.load(f)
    samples = take["samples"]
    pct = float(os.environ.get("AERO_SPEED_PCT", hand_speed.DEFAULT_PCT))
    cap = hand_speed.FULL * min(pct, 100) / 100 * DEG_S_PER_UNIT
    if full:
        times, rows, moving = clean(samples)
        frames_t0 = times[0]
        stretch, peak = stretch_for([[t] + r for t, r in zip(times, rows)], cap)
        frames = [((t - times[0]) * stretch, r) for t, r in zip(times, rows)]
        print(f"replay full {os.path.basename(path)}: {samples[-1][0]:.1f} s recorded, peak {peak:.0f}°/s, "
              f"cap {cap:.0f}°/s at {pct:.0f}%, playing {frames[-1][0]:.1f} s (x{stretch:.2f})", flush=True)
    else:
        poses, moving = key_poses(samples)
        frames, t = [(0.0, poses[0])], 0.0
        for a, b in zip(poses, poses[1:]):
            # an eased move peaks at pi/2 times its average speed; keep that peak under the cap
            move = max(0.3, max(abs(x - y) for x, y in zip(a, b)) * math.pi / 2 / cap)
            steps = max(1, round(move * SEND_HZ))
            frames += [(t + move * k / steps, ease(a, b, k / steps)) for k in range(1, steps + 1)]
            t += move + KEY_HOLD_S
            frames.append((t, b))
        print(f"replay motion {os.path.basename(path)}: {len(poses)} key poses from {samples[-1][0]:.1f} s, "
              f"{pct:.0f}% speed, playing {t:.1f} s", flush=True)
    print("moving:", ", ".join(n for n, m in zip(NAMES, moving) if m) or "nothing", flush=True)
    if dry_run:
        if not full:
            for p in poses:
                print("  key", *(round(x) for x in p))
        return
    hand = connect()
    hand_speed.limit(hand, pct)
    lo, hi = hand.actuation_lower_limits, hand.actuation_upper_limits
    frames = [(at, [max(l, min(h, x)) for x, l, h in zip(row, lo, hi)]) for at, row in frames]
    finished = False
    try:
        for i in range(7):  # moving servos get move torque; still ones only enough to stay put
            hand.set_torque(i, MOVE_TORQUE if moving[i] else STILL_TORQUE)
        start = hand.get_actuations() or frames[0][1]
        steps = max(1, int(GLIDE_S * SEND_HZ))
        for k in range(1, steps + 1):
            hand.set_actuations(ease(start, frames[0][1], k / steps))
            time.sleep(1 / SEND_HZ)
        t0, next_temp = time.monotonic(), 0.0
        if full and "audio" in take:  # the app plays it: from the first frame's moment, slowed to match
            print(f"audio {os.path.join(TAKES, take['audio']['file'])} "
                  f"{take['audio']['offset'] + frames_t0:.3f} {1 / stretch:.3f}", flush=True)
        for at, row in frames:
            wait = t0 + at - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            hand.set_actuations(row)
            if time.monotonic() >= next_temp:
                if too_hot(hand):
                    return
                next_temp = time.monotonic() + TEMP_EVERY_S
        time.sleep(0.5)  # let the firmware's position read catch up before the hold measures
        joints = hand.get_joint_positions_compact()
        if joints:
            print("hold", hold.mode(), "torque", hold.hold(hand, joints, start=MOVE_TORQUE), flush=True)
        finished = True
    except KeyboardInterrupt:
        pass
    finally:
        if not finished:  # stopped or hot: go limp rather than push at move torque
            hand.ctrl_torque([0] * 7)
        hand.close()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal.default_int_handler)  # the app's fallback after SIGINT
    args = sys.argv[1:]
    opts = {}
    for flag in ("--seconds", "--torque"):
        if flag in args:
            i = args.index(flag)
            opts[flag] = args[i + 1]
            del args[i:i + 2]
    dry, full, save = "--dry-run" in args, "--full" in args, "--save" in args
    args = [a for a in args if a not in ("--dry-run", "--full", "--save")]
    if args[:1] == ["record"]:
        tq = [int(x) for x in opts["--torque"].split(",")] if "--torque" in opts else TORQUE
        if len(tq) != 7 or not all(0 <= t <= 1000 for t in tq):
            sys.exit("--torque needs 7 values 0..1000, thumb_abd..pinky")
        record(float(opts.get("--seconds", 300)), tq)
    elif args[:1] == ["replay"]:
        replay(args[1] if len(args) > 1 else None, dry, full)
    elif args[:1] == ["label"]:
        path = take_path(args[1] if len(args) > 1 else None)
        with open(path) as f:
            name = label(json.load(f)["samples"])
        if save:
            rename(path, name)
        else:
            print(name)
    elif args[:1] == ["list"]:
        list_takes()
    elif args[:1] == ["rename"] and len(args) == 3:
        rename(args[1], args[2])
    elif args[:1] == ["delete"] and len(args) == 2:
        delete(args[1])
    elif args[:1] == ["audio"] and len(args) == 3:
        attach_audio(args[1], args[2])
    else:
        sys.exit(__doc__)
