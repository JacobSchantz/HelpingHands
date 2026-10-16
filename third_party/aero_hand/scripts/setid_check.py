import sys, time
from aero_open_sdk.aero_hand import AeroHand
port, new_id, lim = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
h = AeroHand(port=port)
t = time.time()
ack = h.set_id(new_id, lim)
print(f"SET_ID ack after {time.time()-t:.2f}s: {ack}")
print("GET_TEMP:", h.get_actuator_temperatures())
h.close()
