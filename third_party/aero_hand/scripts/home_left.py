import sys, subprocess, time
from aero_open_sdk.aero_hand import AeroHand
import hand_speed
h = AeroHand(port=sys.argv[1])
hand_speed.limit(h)  # 50% unless Jake asks for more
SONG = sys.argv[2] if len(sys.argv) > 2 else "Nausicaä Requiem"
# song first, confirmed playing, then move
subprocess.run(["osascript", "-e", f'tell application "Music" to play (first track of library playlist 1 whose name contains "{SONG}")'], check=True)
time.sleep(2)
t = time.time(); r = h.send_homing(); print("homing returned", r, f"{time.time()-t:.1f}s")
print("temps", h.get_actuator_temperatures())
h.close()
