#!/usr/bin/env python3
"""Relax every servo: zero torque, so the fingers go limp and the servos cool. The next pose re-engages them."""
import glob, sys, time
from aero_open_sdk.aero_hand import AeroHand
ports = sorted(glob.glob("/dev/cu.usbmodem*"))
if not ports:
    sys.exit("hand not connected")
hand = AeroHand(port=ports[0])
hand.ser.write_timeout = 0.05
for _ in range(3):
    hand.ctrl_torque([0] * 7)
    time.sleep(0.05)
time.sleep(0.5)
print("relaxed; currents", hand.get_actuator_currents(), "temps", hand.get_actuator_temperatures())
hand.close()
