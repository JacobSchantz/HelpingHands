#!/usr/bin/env python3
"""Move the hand straight to a named pose.

Usage: pose.py <name>     e.g. pose.py peace, pose.py "surf's up"   (port auto-detected)
       pose.py --list
Run with the aero venv, or via pose.sh. To add a pose, add one line to POSES.
"""
import glob, re, sys, time
from aero_open_sdk.aero_hand import AeroHand

# joints: thumb abduction, thumb flex, thumb tendon, index, middle, ring, pinky (0 = open, 90 = curled)
THUMB_OUT = [0.0, 0.0, 0.0]
THUMB_IN = [90.0, 45.0, 60.0]  # tucked over the curled fingers, as in performance.py's peace sign
POSES = {
    "open":     (THUMB_OUT + [0.0, 0.0, 0.0, 0.0], ["open hand", "relax"]),
    "fist":     (THUMB_IN + [90.0, 90.0, 90.0, 90.0], ["close", "closed fist"]),
    "peace":    (THUMB_IN + [0.0, 0.0, 90.0, 90.0], ["peace sign", "victory"]),
    "flip off": (THUMB_IN + [90.0, 0.0, 90.0, 90.0], ["flip me off", "middle finger", "bird"]),
    "rock on":  (THUMB_IN + [0.0, 90.0, 90.0, 0.0], ["rock", "horns", "devil horns"]),
    "shaka":    (THUMB_OUT + [90.0, 90.0, 90.0, 0.0], ["surfs up", "hang loose"]),
    "i love you": (THUMB_OUT + [0.0, 90.0, 90.0, 0.0], ["ily", "love you"]),
    # half of a two-hand heart: four fingers bent together in a line, thumb all the way in
    "love":     ([100.0, 55.0, 90.0] + [40.0, 40.0, 40.0, 40.0], ["heart", "half heart"]),
}


def norm(s):
    return re.sub(r"[^a-z ]", "", s.lower()).strip()


def find(name):
    n = norm(name)
    for key, (joints, aliases) in POSES.items():
        if n in [norm(key)] + [norm(a) for a in aliases]:
            return key, joints
    return None, None


if len(sys.argv) < 2 or sys.argv[1] == "--list":
    for key, (_, aliases) in POSES.items():
        print(f"{key}: {', '.join(aliases)}")
    sys.exit(0)
key, joints = find(" ".join(sys.argv[1:]))
if not joints:
    sys.exit(f"unknown pose '{' '.join(sys.argv[1:])}'; known: {', '.join(POSES)}")
ports = sorted(glob.glob("/dev/cu.usbmodem*"))
if not ports:
    sys.exit("hand not connected; not moved")
hand = AeroHand(port=ports[0])
hand.ser.write_timeout = 0.05  # SDK default 10 ms drops a frame when USB stalls briefly
# glide from where the hand is now instead of snapping at full servo speed
MOVE_S = 0.7  # Jake: half speed (2026-10-17); full speed was too fast
start = hand.get_joint_positions_compact() or joints
hand.run_trajectory([(start, 0.0), (joints, MOVE_S)])
for _ in range(2):  # resend the target so a stalled frame can't leave the hand short
    hand.set_joint_positions(joints)
    time.sleep(0.02)
hand.close()
print("pose:", key)
