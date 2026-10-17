import sys, subprocess, time
from aero_open_sdk.aero_hand import AeroHand
h = AeroHand(port=sys.argv[1])
subprocess.Popen(["osascript", "-e", 'tell application "Music" to play track "Nausicaä Requiem"'])
t = time.time(); r = h.send_homing(); print("homing returned", r, f"{time.time()-t:.1f}s")
print("temps", h.get_actuator_temperatures())
h.close()
