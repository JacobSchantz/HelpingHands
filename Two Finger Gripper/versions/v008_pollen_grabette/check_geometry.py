#!/usr/bin/env python3
"""Check that the gallery hinge reproduces the URDF and that the grip closes.

1. For several openings, every finger part moved by the poses.js hinge (rotate about Y
   through the origin by angle-90) must land where URDF forward kinematics puts it.
2. Closed (angle 0, URDF proximal -90) the soft tips nearly meet; open (angle 90) they
   are tens of mm apart. Positive control: the open gap must be much larger."""
import json, math
import numpy as np
import export_models as m


def hinge(deg):
    c,s=math.cos(math.radians(deg)),math.sin(math.radians(deg))
    R=np.eye(4);R[:3,:3]=[[c,0,s],[0,1,0],[-s,0,c]]
    return R


def tip_gap(angle):
    vs=m.visuals({'proximal':math.radians(angle-90)})
    pts=lambda prefix:np.concatenate([m.place(m.read_stl(m.HERE/'pollen/assets'/f),T) for _,f,T,_ in vs if f.startswith(prefix)])
    a,b=pts('grip_soft_tip')[::5],pts('distal_soft_tip')[::5]
    return float(min(np.linalg.norm(a-p,axis=1).min() for p in b))


def main():
    zero=m.visuals();checks=[]
    for angle in (0,30,60,90):
        moved=m.visuals({'proximal':math.radians(angle-90)})
        err=max(float(np.abs(hinge(angle-m.EXPORTED_DEG)@A-B)[:3].max()) for (l,_,A,_),(_,_,B,_) in zip(zero,moved) if l!='grip_r')
        checks.append(dict(check=f'hinge matches URDF at angle {angle}',max_error_mm=round(err,4),passed=err<0.01))
    closed,opened=tip_gap(0),tip_gap(90)
    checks.append(dict(check='closed soft tips nearly meet',gap_mm=round(closed,1),passed=closed<5))
    checks.append(dict(check='open gap is wide (positive control)',gap_mm=round(opened,1),passed=opened>50))
    (m.HERE/'geometry_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    for c in checks:print('PASS' if c['passed'] else 'FAIL',c)
    raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
if __name__=='__main__':main()
