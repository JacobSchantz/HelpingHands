#!/usr/bin/env python3
"""Non-moving solder-joint probe for the Aero Hand control board (firmware v0.2.0).

Resets the XIAO (non-power reset => firmware skips homing), captures boot text,
then sends read-only frames:
  GET_POS/GET_CURR/GET_TEMP  (0x22/0x24/0x25) - only populate when all 7 servos answer
No CTRL_POS / CTRL_TOR / HOMING / SET_ID / TRIM is sent.
"""
import struct, sys, time, serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/cu.usbmodem101"
BAUD = 921600

def frame(op, words=()):
    b = bytes([op, 0]) + b"".join(struct.pack("<H", w & 0xFFFF) for w in words)
    return b + bytes(16 - len(b))

def open_port():
    for _ in range(40):
        try:
            return serial.Serial(PORT, BAUD, timeout=0.05)
        except Exception:
            time.sleep(0.25)
    raise SystemExit("port did not come back")

def reset(s):
    s.dtr = False; s.rts = True; time.sleep(0.1); s.rts = False

def read_for(s, secs):
    buf = b""; end = time.time() + secs
    while time.time() < end:
        buf += s.read(4096)
    return buf

def query(s, op, words=(), wait=0.4):
    s.reset_input_buffer(); s.write(frame(op, words)); s.flush()
    data = read_for(s, wait)
    i = data.find(bytes([op, 0]))
    if i < 0 or len(data) - i < 16:
        return None, data
    return struct.unpack("<7H", data[i + 2:i + 16]), data

s = open_port()
if "--no-reset" not in sys.argv:
    reset(s); s.close(); s = open_port()
    boot = read_for(s, 4.0)
    print("BOOT>", boot.decode("latin-1").strip().replace("\r", ""))
    if b"homing" in boot and b"skipping" not in boot:
        print("!! homing started - resetting again to abort"); reset(s); s.close(); sys.exit(2)

for name, op in (("GET_POS", 0x22), ("GET_CURR", 0x24), ("GET_TEMP", 0x25), ("GET_VEL", 0x23)):
    v, raw = query(s, op)
    print(f"{name:8s} -> {v}  raw={raw.hex()}")

# Note: with fewer than 7 servos the firmware's SyncRead task never succeeds, so GET_* stay all-zero.
# Use setid_check.py (documented Set ID scan) to prove a single servo answers.
s.close()
