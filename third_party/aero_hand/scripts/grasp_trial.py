#!/usr/bin/env python3
"""Bounded, filmed bottle-grasp trial. Torque units are NOT measured contact force.

Usage: grasp_trial.py --torque 250 --hold-seconds 5 [--dry-run]
Starts from the current pose, closes slowly toward the existing bottle-grip
pose, holds briefly while logging feedback, returns to its starting pose, and
relaxes. Never persists squeezing after the process exits. This cannot lift a
fixed-base hand or prove payload capacity.
"""
import argparse
import json
import math
from pathlib import Path
import signal
import time
import uuid

import teach
import hold
import hand_speed
from take_video import TakeVideo

GRIP = [100., 55., 30., 70., 70., 70., 70.]
MAX_TORQUE = 500  # existing replay moving-servo limit, not a new hardware limit
MAX_TEMP = 55.
MAX_CURRENT = 1800.  # per-servo mA, conservative trial cutoff
MOVE_SECONDS = 4.


def feedback(hand):
    positions = hand.get_actuations()
    currents = hand.get_actuator_currents()
    temperatures = hand.get_actuator_temperatures()
    if not all(v is not None and len(v) == 7 for v in (positions, currents, temperatures)):
        raise RuntimeError('missing hand telemetry; ending trial')
    if not all(math.isfinite(x) for row in (positions, currents, temperatures) for x in row):
        raise RuntimeError('invalid hand telemetry; ending trial')
    if max(temperatures) >= MAX_TEMP:
        raise RuntimeError(f'temperature cutoff: {temperatures}')
    if max(abs(v) for v in currents) >= MAX_CURRENT:
        raise RuntimeError(f'current cutoff: {currents}')
    return dict(positions=positions, currents_ma=currents, temperatures_c=temperatures)


def recorded_target(take, at, squeeze):
    """A chosen demonstrated posture plus explicit flexion, never inferred force."""
    from aero_open_sdk.actuations_to_joints import ActuationsToJointsModelCompact
    if not 0 <= squeeze <= 30:
        raise ValueError('squeeze must be 0..30 joint degrees')
    path = teach.take_path(take)
    data = json.loads(Path(path).read_text())
    if not data['samples'][0][0] <= at <= data['samples'][-1][0]:
        raise ValueError('at must be within the recorded sample times')
    sample = min(data['samples'], key=lambda row: abs(row[0]-at))
    joints = [math.degrees(v) for v in ActuationsToJointsModelCompact().hand_joints(
        [math.radians(v) for v in sample[1:]])]
    # Keep thumb opposition; small thumb flex changes, larger finger flex.
    adjusted = [joints[0], joints[1] + squeeze/4, joints[2] + squeeze/2]
    adjusted += [v + squeeze for v in joints[3:]]
    return adjusted, dict(take=str(Path(path).resolve()), at=sample[0], squeeze_degrees=squeeze,
                          recorded_joints=joints)


def run(torque, seconds, target_joints=None, source=None):
    if not 30 <= torque <= MAX_TORQUE or not 0 < seconds <= 10:
        raise ValueError('torque must be 30..500; hold-seconds must be >0 and <=10')
    target_joints = target_joints or GRIP
    directory = Path(teach.TAKES) / 'grasp-trials'
    directory.mkdir(exist_ok=True)
    result = directory / (time.strftime('trial-%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8] + '.json')
    log = dict(torque_limit=torque, hold_seconds=seconds, target_joints=target_joints, source=source,
               status='failed', samples=[], payload_verified=False)
    hand = None
    try:
        with TakeVideo(directory, 'grasp-trial') as video:
            log['video'] = str(video.video)
            hand = teach.connect()
            try:
                initial = feedback(hand)
                start = initial['positions']
                target = hold._target_actuations(hand, target_joints)
                log['start'], log['target'] = start, target
                hand_speed.limit(hand, 25)
                hold.engage(hand, torque)
                begun = time.monotonic()
                next_read = 0.

                def tick(phase, command):
                    nonlocal next_read
                    video.check()
                    now = time.monotonic()
                    if now >= next_read:
                        row = dict(t=round(now-begun, 4), phase=phase, command=command, **feedback(hand))
                        log['samples'].append(row)
                        next_read = now + .1
                        # Durable measurements survive a later exception or interruption.
                        result.write_text(json.dumps(log))
                    hand.set_actuations(command)

                def glide(phase, a, b):
                    t0 = time.monotonic()
                    for k in range(101):
                        tick(phase, teach.ease(a, b, k/100))
                        time.sleep(max(0, t0+(k+1)*MOVE_SECONDS/100-time.monotonic()))

                glide('close', start, target)
                until = time.monotonic() + seconds
                while time.monotonic() < until:
                    tick('hold', target)
                    time.sleep(.04)
                current = feedback(hand)['positions']
                glide('return', current, start)
            finally:
                try:
                    hand.ctrl_torque([0]*7)
                finally:
                    hand.close()
                    hand = None
        log['status'] = 'completed'
    except BaseException as exc:
        log['error'] = str(exc) or type(exc).__name__
        raise
    finally:
        if hand is not None:
            try:
                hand.ctrl_torque([0]*7)
            finally:
                hand.close()
        result.write_text(json.dumps(log, indent=2))
        print('grasp_result ' + json.dumps({'result': str(result), 'status': log['status'],
                                           'error': log.get('error'), 'video': log.get('video'),
                                           'payload_verified': False}), flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--torque',type=int,default=250)
    p.add_argument('--hold-seconds',type=float,default=5)
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--take',help='take filename or last; requires --at')
    p.add_argument('--at',type=float,help='seconds into the take containing the desired grasp')
    p.add_argument('--squeeze',type=float,default=20,help='extra finger joint flexion, 0..30 degrees')
    a=p.parse_args()
    target, source = GRIP, None
    if a.take:
        if a.at is None: p.error('--take requires --at')
        target, source = recorded_target(a.take,a.at,a.squeeze)
    elif a.at is not None: p.error('--at requires --take')
    if not 30 <= a.torque <= MAX_TORQUE or not 0 < a.hold_seconds <= 10:
        p.error('torque must be 30..500; hold-seconds must be >0 and <=10')
    signal.signal(signal.SIGTERM,signal.default_int_handler)
    if a.dry_run:
        print(json.dumps(dict(target_joints=target,source=source,torque_limit=a.torque,hold_seconds=a.hold_seconds,
                              max_temperature=MAX_TEMP,max_current_ma=MAX_CURRENT)))
    else:
        run(a.torque,a.hold_seconds,target,source)
