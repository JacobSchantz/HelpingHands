#!/usr/bin/env python3
"""Base 11: record the gripper's joint position from its STS3215 while a hand works it (data collection).

The servo's torque is switched off, so the fingers back-drive it and it is read as an encoder: Present_Position (4096 counts a
turn) through LeRobot's Feetech bus, the same bus the SO-101 uses. The pinion sits on the horn and turns gear_teeth/pinion_teeth
times per finger turn (params.json), so every finger degree is 4096/360 x that ratio counts (11.4 at 34:34). Each row:

    t_s, raw, servo_deg, finger_deg        (finger_deg: each finger's swing from closed, 0 to max_angle; 30 open)

Close the fingers when asked: that reading is finger 0. Run it in the lerobot env (see robot_config.md), from a native terminal:

    conda activate lerobot
    python3 record_grip.py --port /dev/tty.usbmodemXXXX --id 1            # Ctrl+C stops; writes recordings/grip_<time>.csv
    python3 record_grip.py --fake --duration 3                             # no hardware: a synthetic open/close, to try the pipeline

A new STS3215 ships as ID 1; an SO-101 gripper motor is ID 6. Nothing is written to the servo but Torque_Enable (off)."""
from pathlib import Path
import argparse, csv, json, math, sys, time
HERE=Path(__file__).resolve().parent
COUNTS=4096   # STS3215 counts per output turn


def ratio():
    """Servo (pinion) turns per finger (side gear) turn, and the swing range, from params.json."""
    v={p['name']:p['value'] for g in json.loads((HERE/'params.json').read_text())['groups'] for p in g['params']}
    return v['gear_teeth']/v['pinion_teeth'],v['max_angle']


def finger_deg(raw,zero,pin_ratio,sign=1):
    """Each finger's swing in degrees from closed. raw and zero are 0..4095; the shortest way round from zero is taken, so
    crossing the counter's wrap is fine as long as the servo turns under half a turn (the 30 deg swing is 30 x pin_ratio deg)."""
    d=(raw-zero+COUNTS//2)%COUNTS-COUNTS//2
    return sign*d*360/COUNTS/pin_ratio


class FakeBus:
    """A servo opening and closing about once a second, for --fake."""
    def __init__(self,pin_ratio,max_angle):self.t0=time.monotonic();self.k=COUNTS/360*pin_ratio;self.max=max_angle
    def read(self):
        t=time.monotonic()-self.t0
        return round(2000+self.k*self.max*(0.5-0.5*math.cos(2*math.pi*t)))%COUNTS
    def close(self):pass


class ServoBus:
    """One STS3215 on a Feetech bus, read raw (no LeRobot calibration needed)."""
    def __init__(self,port,motor_id):
        from lerobot.motors import Motor, MotorNormMode
        from lerobot.motors.feetech import FeetechMotorsBus
        self.bus=FeetechMotorsBus(port,{'gripper':Motor(motor_id,'sts3215',MotorNormMode.RANGE_0_100)})
        self.bus.connect(handshake=True)
        self.bus.disable_torque('gripper')   # back-drivable: the hand moves it
    def read(self):return int(self.bus.read('Present_Position','gripper',normalize=False))
    def close(self):self.bus.disconnect(disable_torque=True)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--port',help='the bus adapter, e.g. /dev/tty.usbmodem5AAF2627031 (lerobot-find-port)')
    ap.add_argument('--id',type=int,default=1,help='servo ID (new STS3215: 1; SO-101 gripper: 6)')
    ap.add_argument('--hz',type=float,default=100,help='samples a second')
    ap.add_argument('--duration',type=float,help='seconds to record (default: until Ctrl+C)')
    ap.add_argument('--out',type=Path,help='CSV to write (default recordings/grip_<time>.csv here)')
    ap.add_argument('--zero',type=int,help='raw count with the fingers closed (default: read it now, after you close them)')
    ap.add_argument('--invert',action='store_true',help='opening reads negative: flip the sign (depends on which way the horn went on)')
    ap.add_argument('--fake',action='store_true',help='no hardware: a synthetic servo')
    a=ap.parse_args(argv)
    if not a.fake and not a.port:ap.error('--port is required (or --fake)')
    pin_ratio,max_angle=ratio()
    bus=FakeBus(pin_ratio,max_angle) if a.fake else ServoBus(a.port,a.id)
    out=a.out or HERE/'recordings'/time.strftime('grip_%Y%m%d_%H%M%S.csv');out.parent.mkdir(parents=True,exist_ok=True)
    try:
        if a.zero is None and not a.fake:input('Close the fingers fully, then press Enter: ')
        zero=a.zero if a.zero is not None else bus.read()
        sign=-1 if a.invert else 1
        print(f'zero {zero} counts; {COUNTS/360*pin_ratio:.2f} counts per finger degree; recording at {a.hz:g} Hz to {out} (Ctrl+C stops)',file=sys.stderr)
        n=0;t0=time.monotonic();period=1/a.hz;lo=hi=0.0
        with out.open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['t_s','raw','servo_deg','finger_deg'])
            try:
                while a.duration is None or time.monotonic()-t0<a.duration:
                    t=time.monotonic()-t0;raw=bus.read();fd=finger_deg(raw,zero,pin_ratio,sign)
                    w.writerow([f'{t:.4f}',raw,f'{fd*pin_ratio:.3f}',f'{fd:.3f}']);n+=1;lo=min(lo,fd);hi=max(hi,fd)
                    time.sleep(max(0,t0+n*period-time.monotonic()))
            except KeyboardInterrupt:
                pass
        dt=time.monotonic()-t0
        print(f'{n} samples in {dt:.1f} s ({n/max(dt,1e-9):.0f} Hz); finger {lo:.1f} to {hi:.1f} deg (designed 0 to {max_angle}) -> {out}',file=sys.stderr)
        if hi>max_angle+2 or lo<-2:print('warning: past the designed swing: check --zero / --invert',file=sys.stderr)
    finally:
        bus.close()
    return out


if __name__=='__main__':main()
