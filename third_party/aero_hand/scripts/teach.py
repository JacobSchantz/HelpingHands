#!/usr/bin/env python3
"""Teach the hand by moving it, then play it back.

Usage: teach.py record [--seconds 300] [--torque 10,30,30,40,40,25,25]
       teach.py replay [take.json | last] [--dry-run]
       teach.py list                      one JSON line per take, newest first (the app's list)
       teach.py rename <take.json> <name>
       teach.py delete <take.json>        moves it to TAKES/deleted, not gone

record: transparent mode. Every servo gets a small constant pull (CTRL_TOR) that just keeps its cord
taut against the return spring, so the fingers can be moved by hand (or a glove) both ways. All 7
actuations are logged at ~100 Hz with timestamps until Stop (SIGINT) or --seconds, then the hand
relaxes and the take is saved to TAKES. About 10 times a second it prints "pos" and each servo's
place in its range, 0 (open) to 100, which the app draws as live bars. See plans/aero-hand-glove-teaching.md.

replay: position mode at the recorded timing, slowed down only where a servo would have to move
faster than the speed cap (AERO_SPEED_PCT, 50% by default). Glides to the first frame first and
holds the last one low-power (hold.py). Stops and relaxes at TEMP_HOT. --dry-run only prints.
"""
import glob, json, os, signal, sys, time
from aero_open_sdk.aero_hand import AeroHand
import hand_speed, hold

NAMES = ["thumb_abd", "thumb_flex", "thumb_tendon", "index", "middle", "ring", "pinky"]
# Transparent-mode pull per servo. Bench test 1 (2026-10-17, torque 50 everywhere): index and middle
# followed both ways but rested a bit curled, ring and pinky stayed curled, so all are lowered.
# The thumb values are untested first guesses (abduction is a back-drivable linkage, so barely any).
TORQUE = [10, 30, 30, 40, 40, 25, 25]
HZ = 100
TEMP_HOT = 60.0         # °C: relax and stop, like performance.py
TEMP_EVERY_S = 1.0
GLIDE_S = 1.0           # to the take's first frame before playing
DEG_S_PER_UNIT = 0.732 * 6  # SET_SPE unit is 0.732 RPM (hand_speed.py)
TAKES = os.path.expanduser("~/HelpingHands-tools/aero/takes")
LIVE_EVERY_S = 0.1


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
    samples, temps, t0 = [], [], time.monotonic()
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
        json.dump({"names": NAMES, "torque": torque, "hz": HZ, "samples": samples, "temps": temps}, f)
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


def list_takes():
    for path in sorted(glob.glob(os.path.join(TAKES, "take-*.json")), reverse=True):
        try:
            with open(path) as f:
                take = json.load(f)
            seconds = take["samples"][-1][0]
        except (OSError, ValueError, KeyError, IndexError):
            continue
        print(json.dumps({"file": os.path.basename(path), "name": take.get("name", ""),
                          "seconds": round(seconds, 1),
                          "recorded": time.mktime(time.strptime(os.path.basename(path), "take-%Y%m%d-%H%M%S.json"))}))


def rename(name, new):
    path = take_path(name)
    with open(path) as f:
        take = json.load(f)
    take["name"] = new.strip()
    with open(path + ".tmp", "w") as f:
        json.dump(take, f)
    os.replace(path + ".tmp", path)
    print(f"renamed {os.path.basename(path)}: {take['name']}")


def delete(name):
    path = take_path(name)
    os.makedirs(os.path.join(TAKES, "deleted"), exist_ok=True)
    os.replace(path, os.path.join(TAKES, "deleted", os.path.basename(path)))
    print(f"deleted {os.path.basename(path)} (kept in {TAKES}/deleted)")


def replay(path, dry_run):
    path = take_path(path)
    with open(path) as f:
        samples = json.load(f)["samples"]
    pct = float(os.environ.get("AERO_SPEED_PCT", hand_speed.DEFAULT_PCT))
    cap = hand_speed.FULL * min(pct, 100) / 100 * DEG_S_PER_UNIT
    stretch, peak = stretch_for(samples, cap)
    dur = samples[-1][0] * stretch
    print(f"replay {os.path.basename(path)}: {samples[-1][0]:.1f} s recorded, peak {peak:.0f}°/s, "
          f"cap {cap:.0f}°/s at {pct:.0f}%, playing {dur:.1f} s (x{stretch:.2f})", flush=True)
    if dry_run:
        return
    hand = connect()
    hand_speed.limit(hand, pct)
    finished = False
    try:
        hold.engage(hand)  # CTRL_POS puts the servos back in position mode at move torque
        start = hand.get_actuations() or samples[0][1:]
        steps = max(1, int(GLIDE_S * HZ))
        for k in range(1, steps + 1):
            hand.set_actuations([a + (b - a) * k / steps for a, b in zip(start, samples[0][1:])])
            time.sleep(1 / HZ)
        t0, next_temp = time.monotonic(), 0.0
        for s in samples:
            wait = t0 + s[0] * stretch - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            hand.set_actuations(s[1:])
            if time.monotonic() >= next_temp:
                if too_hot(hand):
                    return
                next_temp = time.monotonic() + TEMP_EVERY_S
        time.sleep(0.5)  # let the firmware's position read (skipped while we hog the bus) catch up
        joints = hand.get_joint_positions_compact()
        if joints:
            print("hold", hold.mode(), "torque", hold.hold(hand, joints), flush=True)
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
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    if args[:1] == ["record"]:
        tq = [int(x) for x in opts["--torque"].split(",")] if "--torque" in opts else TORQUE
        if len(tq) != 7 or not all(0 <= t <= 1000 for t in tq):
            sys.exit("--torque needs 7 values 0..1000, thumb_abd..pinky")
        record(float(opts.get("--seconds", 300)), tq)
    elif args[:1] == ["replay"]:
        replay(args[1] if len(args) > 1 else None, dry)
    elif args[:1] == ["list"]:
        list_takes()
    elif args[:1] == ["rename"] and len(args) == 3:
        rename(args[1], args[2])
    elif args[:1] == ["delete"] and len(args) == 2:
        delete(args[1])
    else:
        sys.exit(__doc__)
