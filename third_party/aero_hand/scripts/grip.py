#!/usr/bin/env python3
"""Slowly close a gentle power grip around an object (e.g. a soda can), or release it.

Usage: grip.py [close|release] [--torque N] [--hold auto|medium|firm]   (port auto-detected)
The fingers close slowly with a reduced torque limit so they wrap the object and
stop against it instead of crushing it. Once closed, hold.py lowers each servo to what it needs:
a finger stopped on the object keeps half the grip torque, the rest drop to just above their springs.
--hold medium / firm (or AERO_HOLD) holds every servo at hold.py's fixed torque instead; firm also
closes at full force.
"""
import argparse, glob, sys, time
from aero_open_sdk.aero_hand import AeroHand
import hand_speed, hold

OPEN = [100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]          # thumb rotated across, fingers open
GRIP = [100.0, 55.0, 30.0, 70.0, 70.0, 70.0, 70.0]    # past the can, so torque does the stopping
TIGHT = [100.0, 55.0, 90.0, 90.0, 90.0, 90.0, 90.0]   # everything fully curled, thumb wrapped on (tools, e.g. a hammer)
CLOSE_S = 3.0

ap = argparse.ArgumentParser()
ap.add_argument("action", nargs="?", default="close", choices=["close", "release"])
ap.add_argument("--torque", type=int, default=300, help="0-1000; 300 holds a can without denting it")
ap.add_argument("--tight", action="store_true", help="full force (torque 1000), thumb wrapped on")
ap.add_argument("--hold", default=None, help="auto (default, or AERO_HOLD) | medium | firm, see hold.py")
a = ap.parse_args()
a.hold = hold.mode(a.hold) if a.action == "close" else "auto"  # a released hand just holds itself open
if a.hold == "firm":
    a.torque = 1000
if a.tight:
    a.torque, GRIP = 1000, TIGHT

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
start_torque = a.torque if a.action == "close" else 1000
held = hold.hold(hand, target, start=start_torque, stall_torque=start_torque // 2, how=a.hold)
print("grip:", a.action, "torque", start_torque, "hold", a.hold, "torque", held, "temps", hand.get_actuator_temperatures())
hand.close()
