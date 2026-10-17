#!/usr/bin/env python3
"""Transparent-mode bench test: small constant pull on every servo, print positions as you move fingers.
Usage: transparent_test.py [torque=50] [seconds=40]"""
import glob, sys, time
from aero_open_sdk.aero_hand import AeroHand
tq = int(sys.argv[1]) if len(sys.argv) > 1 else 50
secs = float(sys.argv[2]) if len(sys.argv) > 2 else 40
h = AeroHand(port=sorted(glob.glob("/dev/cu.usbmodem*"))[0]); h.ser.write_timeout = 0.05
names = ["th_abd", "th_flex", "th_tend", "index", "middle", "ring", "pinky"]
t0 = time.time(); last = None; temps_at = 0
try:
    while time.time() - t0 < secs:
        h.ctrl_torque([tq] * 7)
        a = h.get_actuations()
        if a:
            a = [round(x) for x in a]
            if last is None or max(abs(x - y) for x, y in zip(a, last)) >= 3:
                print(f"{time.time()-t0:5.1f}s " + " ".join(f"{n}={v}" for n, v in zip(names, a)), flush=True)
                last = a
        if time.time() > temps_at:
            temps_at = time.time() + 5
            print("   temps", h.get_actuator_temperatures(), flush=True)
        time.sleep(0.05)
finally:
    h.ctrl_torque([0] * 7)
    h.close()
