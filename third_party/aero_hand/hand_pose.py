#!/usr/bin/env python3
"""Pose the left Aero Hand (guide/anim41/left.urdf, the guide's CAD meshes) and write it as mm STLs, one per separable part:
the palm and each finger (thumb, index, middle, ring, pinky), for OpenSCAD and the live preview (voice-c0e340c7). Forward
kinematics straight from the URDF's joint origins and axes, the same as cad/arm/rebot_b601_rs/arm_pose.py (whose helpers it
uses); no ROS.

The output frame is the palm's (left_base_link: the wrist pad at z 0, the fingers up +z), in mm, moved by `origin`.
A pose is three angles in degrees: `curl` on every finger joint (MCP, PIP, DIP of index..pinky; the thumb's MCP and IP),
`thumb_abd` on the thumb's CMC abduction (0 = beside the palm, 100 = across it) and `thumb_flex` on its CMC flexion. Each is
clamped to the URDF's limits.

    python3 hand_pose.py --out <dir> --origin 0,0,0 --curl 15 --thumb-abd 60 --thumb-flex 10
    import hand_pose; hand_pose.export(out_dir, origin=(x,y,z), curl=15, thumb_abd=60, thumb_flex=10)

Writes <dir>/aero_<part>.stl and returns [(path, part)]. numpy only."""
from pathlib import Path
import argparse, math, sys
import numpy as np
HERE=Path(__file__).resolve().parent
URDF=HERE/'guide/anim41/left.urdf'
sys.path.insert(0,str(HERE.parents[1]/'cad/arm/rebot_b601_rs'))
from arm_pose import frame, axis_rot, read_stl, write_stl   # noqa: E402
import xml.etree.ElementTree as ET   # noqa: E402
PARTS=('palm','thumb','index','middle','ring','pinky')


def part_of(link):
    """left_index_middle_link -> index; left_t_link (the thumb's CMC block) -> thumb; left_base_link -> palm"""
    k=link.removeprefix('left_').split('_')[0]
    return {'base':'palm','t':'thumb'}.get(k,k)


def angles(curl,thumb_abd,thumb_flex):
    """joint name -> angle (deg) for the pose; the rest stay at 0"""
    a={}
    for f in ('index','middle','ring','pinky'):
        for j in ('mcp_flex','pip','dip'):a[f'left_{f}_{j}']=curl
    a.update(left_thumb_cmc_abd=thumb_abd,left_thumb_cmc_flex=thumb_flex,left_thumb_mcp=curl,left_thumb_ip=curl)
    return a


def export(out,origin=(0,0,0),curl=0.0,thumb_abd=0.0,thumb_flex=0.0):
    root=ET.parse(URDF).getroot();want=angles(curl,thumb_abd,thumb_flex)
    T={'left_base_link':np.eye(4)}
    for j in root.findall('joint'):   # the URDF lists parents before children
        q=0.0
        if j.get('type')=='revolute':
            lim=j.find('limit');q=min(max(math.radians(want.get(j.get('name'),0.0)),float(lim.get('lower'))),float(lim.get('upper')))
        axis=list(map(float,j.find('axis').get('xyz').split()))
        T[j.find('child').get('link')]=T[j.find('parent').get('link')]@frame(j.find('origin'))@(axis_rot(axis,q) if any(axis) else np.eye(4))
    groups={}
    for L in root.findall('link'):
        for v in L.findall('visual'):
            M=np.diag([1000,1000,1000,1])@T[L.get('name')]@frame(v.find('origin'));M[:3,3]+=origin   # metres -> mm, then moved
            src=URDF.parent/Path(v.find('geometry/mesh').get('filename')).name
            groups.setdefault(part_of(L.get('name')),[]).append(read_stl(src)@M[:3,:3].T+M[:3,3])
    out=Path(out);out.mkdir(parents=True,exist_ok=True);rows=[]
    for k in PARTS:
        p=out/f'aero_{k}.stl';write_stl(p,np.concatenate(groups[k]));rows.append((p,k))
    return rows


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out',required=True);ap.add_argument('--origin',default='0,0,0')
    ap.add_argument('--curl',type=float,default=0);ap.add_argument('--thumb-abd',type=float,default=0);ap.add_argument('--thumb-flex',type=float,default=0)
    a=ap.parse_args()
    for p,k in export(a.out,tuple(map(float,a.origin.split(','))),a.curl,a.thumb_abd,a.thumb_flex):print(p,k)
