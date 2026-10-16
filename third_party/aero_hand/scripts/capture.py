import serial, time, sys
P="/dev/cu.usbmodem101"; secs=float(sys.argv[1]) if len(sys.argv)>1 else 15
s=serial.Serial(P,921600,timeout=0.01)
if "--reset" in sys.argv:
    s.dtr=False; s.rts=True; time.sleep(0.1); s.rts=False
    try: s.close()
    except Exception: pass
    s=None
t0=time.time(); buf=b""
while time.time()-t0<secs:
    if s is None:
        try: s=serial.Serial(P,921600,timeout=0.01)
        except Exception: time.sleep(0.005); continue
    try: buf+=s.read(4096)
    except Exception: s=None
sys.stdout.write(buf.decode('latin-1').replace('\r',''))
