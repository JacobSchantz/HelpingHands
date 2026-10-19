#!/usr/bin/env python3
"""Create an explicitly generated, once-per-finger variant; never replace the demonstration.

Example: curate_take.py take-20261017-170553.json --thumb-anchors 10.58,12.78,15.46
The anchors explicitly select open, opposition, and flexed thumb poses on the source clock.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import teach

METHOD = 'once-per-finger-v1'


def prepare(take, thumb_times, speed_pct=50):
    times, rows, _ = teach.clean(take['samples'])
    def nearest(t):
        return min(range(len(times)), key=lambda k: abs(times[k] - t))
    anchors = [nearest(t) for t in thumb_times]
    if len(anchors) != 3 or not anchors[0] < anchors[1] < anchors[2]:
        raise ValueError('choose three increasing thumb anchor times: open, opposition, flexed')
    thumb = [rows[k][:3] for k in anchors]
    if not thumb[0][2] < thumb[1][2] < thumb[2][2]:
        raise ValueError('thumb tendon anchors must increase from open through opposition to flexed')
    baseline = list(rows[anchors[0]])
    poses = [baseline]
    for pose in (thumb[1], thumb[2], thumb[1], thumb[0]):
        poses.append(list(pose) + baseline[3:])
    finger_anchors = []
    for i in range(3, 7):
        peak = max(range(len(rows)), key=lambda k: rows[k][i])
        if rows[peak][i] - baseline[i] < teach.DEADBAND_DEG:
            raise ValueError(f'{teach.NAMES[i]} has no clear curl to preserve')
        pose = list(baseline)
        pose[i] = rows[peak][i]
        poses.extend((pose, list(baseline)))
        finger_anchors.append(dict(finger=teach.NAMES[i], source_time=times[peak]))
    cap = teach.hand_speed.FULL * speed_pct / 100 * teach.DEG_S_PER_UNIT
    frames = teach.smooth_frames(poses, cap)
    samples = [[round(t, 6)] + row for t, row in frames]
    return dict(names=teach.NAMES, name='Smooth thumb, index, middle, ring and pinky — once each',
                hz=teach.SEND_HZ, samples=samples,
                derivation=dict(method=METHOD, generated=True, measured=False, speed_pct=speed_pct,
                                speed_cap_deg_s=cap, acceleration_cap_deg_s2=cap / .5,
                                thumb_anchor_times=[times[k] for k in anchors], finger_anchors=finger_anchors,
                                key_poses=poses, source_name=take.get('name'),
                                policy='One curl/release per finger; reverse the observed thumb opposition/flexion path; preserve original five-finger order'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('take')
    parser.add_argument('--thumb-anchors', required=True)
    parser.add_argument('--output')
    args = parser.parse_args()
    source = Path(teach.take_path(args.take)).resolve()
    prepared = prepare(json.loads(source.read_text()), [float(t) for t in args.thumb_anchors.split(',')])
    prepared['derivation'].update(source_take=str(source), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                                  created_at=time.time())
    output = Path(args.output) if args.output else source.parent / time.strftime('take-%Y%m%d-%H%M%S.json')
    with output.open('x') as stream:
        json.dump(prepared, stream)
    print(json.dumps(dict(derived_take=str(output.resolve()), source_take=str(source),
                         duration=prepared['samples'][-1][0], measured=False)))


if __name__ == '__main__':
    main()
