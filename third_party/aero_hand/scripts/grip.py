#!/usr/bin/env python3
"""Slowly close a gentle power grip around an object (e.g. a soda can), or release it.

Usage: grip.py [close|release] [--torque N]   (port auto-detected)
The fingers close slowly with a reduced torque limit so they wrap the object and
stop against it instead of crushing it. Torque stays limited until release.
"""
import argparse, glob, sys, time
from aero_open_sdk.aero_hand import AeroHand
import hand_speed

OPEN = [100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]          # thumb rotated across, fingers open
GRIP = [100.0, 55.0, 30.0, 70.0, 70.0, 70.0, 70.0]    # past the can, so torque does the stopping
CLOSE_S = 3.0

ap = argparse.ArgumentParser()
ap.add_argument("action", nargs="?", default="close", choices=["close", "release"])
ap.add_argument("--torque", type=int, default=300, help="0-1000; 300 holds a can without denting it")
a = ap.parse_args()

ports = sorted(glob.glob("/dev/cu.usbmodem*"))
if not ports:
    sys.exit("hand not connected; not moved")
hand = AeroHand(port=ports[0])
hand.ser.write_timeout = 0.05
hand_speed.limit(hand, 25)  # slow grip, below the 50% default
for servo in range(7):
    hand.set_torque(servo, a.torque if a.action == "close" else 1000)
    time.sleep(0.01)
start = hand.get_joint_positions_compact() or (OPEN if a.action == "close" else GRIP)
target = GRIP if a.action == "close" else OPEN
hand.run_trajectory([(start, 0.0), (target, CLOSE_S)])
hand.set_joint_positions(target)
print("grip:", a.action, "torque", a.torque if a.action == "close" else 1000, "temps", hand.get_actuator_temperatures())
hand.close()
