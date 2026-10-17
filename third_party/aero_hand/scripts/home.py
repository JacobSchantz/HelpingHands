#!/usr/bin/env python3
"""Home all seven servos (port auto-detected). Run with the aero venv, or via home.sh."""
import glob, sys, time
from aero_open_sdk.aero_hand import AeroHand
import hand_speed

ports = sorted(glob.glob("/dev/cu.usbmodem*"))
if not ports:
    sys.exit("hand not connected; not homed")
h = AeroHand(port=ports[0])
hand_speed.limit(h)  # 50% unless Jake asks for more
t = time.time(); r = h.send_homing(); print("homing returned", r, f"{time.time()-t:.1f}s", flush=True)
print("temps", h.get_actuator_temperatures())
h.close()
