#!/usr/bin/env python3
"""Move the hand straight to a named pose.

Usage: pose.py <name> [--hold auto|medium|firm]   e.g. pose.py peace, pose.py "surf's up", pose.py seven
       pose.py count to ten   (Chinese one-hand counting 1..10, about a second on each)
       pose.py --list
Run with the aero venv, or via pose.sh. To add a pose, add one line to POSES.
"""
import glob, os, re, sys, time
from aero_open_sdk.aero_hand import AeroHand
import hand_speed, hold

# joints: thumb abduction, thumb flex, thumb tendon, index, middle, ring, pinky (0 = open, 90 = curled)
THUMB_OUT = [0.0, 0.0, 0.0]
THUMB_IN = [90.0, 45.0, 60.0]  # tucked over the curled fingers, as in performance.py's peace sign
POSES = {  # the Poses buttons in the Mac app, in order (relax.sh is added there as the last one)
    "open":     (THUMB_OUT + [0.0, 0.0, 0.0, 0.0], ["open hand"]),
    "fist":     (THUMB_IN + [90.0, 90.0, 90.0, 90.0], ["close", "closed fist"]),
    "peace":    (THUMB_IN + [0.0, 0.0, 90.0, 90.0], ["peace sign", "victory"]),
    "flip off": (THUMB_IN + [90.0, 0.0, 90.0, 90.0], ["flip me off", "middle finger", "bird"]),
    "rock on":  (THUMB_IN + [0.0, 90.0, 90.0, 0.0], ["rock", "horns", "devil horns", "i love you", "ily", "love you"]),
    # Chinese 666 (liù liù liù, "that's cool"): thumb and pinky up, the same shape as shaka and six
    "666":      (THUMB_OUT + [90.0, 90.0, 90.0, 0.0],
                 ["six six six", "liu liu liu", "lululil", "lulu", "shaka", "surfs up", "hang loose"]),
}
# Chinese one-hand counting (common mainland forms), for "count to ten"; no buttons, but `pose.py seven` works.
# Pinches use performance.py's thumb-to-fingertip values.
NUMBERS = {
    "one":      (THUMB_IN + [0.0, 90.0, 90.0, 90.0], ["1", "yi"]),
    "two":      (THUMB_IN + [0.0, 0.0, 90.0, 90.0], ["2", "er"]),
    "three":    ([75.0, 25.0, 30.0] + [50.0, 0.0, 0.0, 0.0], ["3", "san"]),  # OK-style: thumb on index tip
    "four":     (THUMB_IN + [0.0, 0.0, 0.0, 0.0], ["4", "si"]),
    "five":     (THUMB_OUT + [0.0, 0.0, 0.0, 0.0], ["5", "wu"]),
    "six":      (THUMB_OUT + [90.0, 90.0, 90.0, 0.0], ["6", "liu"]),
    "seven":    ([80.0, 33.0, 27.0] + [50.0, 50.0, 90.0, 90.0], ["7", "qi"]),  # thumb, index, middle tips pinched
    "eight":    (THUMB_OUT + [0.0, 90.0, 90.0, 90.0], ["8", "ba", "pistol"]),
    "nine":     (THUMB_IN + [50.0, 90.0, 90.0, 90.0], ["9", "jiu"]),  # index hooked
    "ten":      (THUMB_IN + [90.0, 90.0, 90.0, 90.0], ["10", "shi"]),  # fist (crossed index fingers needs two hands)
}
COUNT = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
COUNT_ALIASES = ["count to ten", "count to 10", "count", "count in chinese"]
HOLD_S = 1.0  # Jake: pause about a second on each number


def norm(s):
    return " ".join(re.sub(r"[^a-z0-9 ]", "", s.lower()).split())


def find(name):
    n = norm(name)
    for key, (joints, aliases) in {**POSES, **NUMBERS}.items():
        if n in [norm(key)] + [norm(a) for a in aliases]:
            return key, joints
    return None, None


args = sys.argv[1:]
if "--hold" in args:  # auto | medium | firm, see hold.py; the app sets AERO_HOLD instead
    i = args.index("--hold")
    os.environ["AERO_HOLD"] = args[i + 1] if i + 1 < len(args) else ""
    del args[i:i + 2]
hold.mode()  # a bad --hold exits here, before the hand moves
if not args or args[0] == "--list":  # --list prints the button poses only; the numbers are for counting
    for key, (_, aliases) in POSES.items():
        print(f"{key}: {', '.join(aliases)}")
    sys.exit(0)
said = " ".join(args)
if norm(said) in COUNT_ALIASES:
    steps = [(k, NUMBERS[k][0]) for k in COUNT]
else:
    key, joints = find(said)
    steps = [(key, joints)]
if not steps[0][1]:
    sys.exit(f"unknown pose '{said}'; known: {', '.join(POSES)}, one..ten")
ports = sorted(glob.glob("/dev/cu.usbmodem*"))
if not ports:
    sys.exit("hand not connected; not moved")
hand = AeroHand(port=ports[0])
hand_speed.limit(hand)  # 50% unless Jake asks for more
hand.ser.write_timeout = 0.05  # SDK default 10 ms drops a frame when USB stalls briefly
# glide from where the hand is now instead of snapping at full servo speed
MOVE_S = 0.7  # Jake: half speed (2026-10-17); full speed was too fast
for i, (key, joints) in enumerate(steps):
    hold.engage(hand)  # move torque back up; the last hold may have lowered it
    start = hand.get_joint_positions_compact() or joints
    hand.run_trajectory([(start, 0.0), (joints, MOVE_S)])
    for _ in range(2):  # resend the target so a stalled frame can't leave the hand short
        hand.set_joint_positions(joints)
        time.sleep(0.02)
    if i < len(steps) - 1:
        print("pose:", key, flush=True)
        time.sleep(HOLD_S)
    else:  # only the pose that stays gets the hold (auto's low-power search takes ~2 s)
        print("pose:", key, "hold", hold.mode(), "torque", hold.hold(hand, joints), flush=True)
hand.close()
