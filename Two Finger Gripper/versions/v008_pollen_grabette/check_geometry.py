#!/usr/bin/env python3
"""Check that the gallery hinges reproduce each URDF and that each grip closes.

For Grabette and for Gripette:
1. For several openings, every finger part moved by its poses.js hinge (rotate about Y
   through the proximal pivot by sign*(angle-90)) must land where URDF forward kinematics
   puts it.
2. Closed (angle 0) the soft tips nearly meet; open (angle 90) they are tens of mm apart.
   Positive control: the open gap must be much larger."""
import json, math, re
import numpy as np
import export_models as m
POSES=m.HERE.parents[2]/'cad/mobile_gallery/poses.js'


def hinges():
    text=POSES.read_text();text=text[text.index('{'):text.rindex('}')+1]
    return json.loads(text)['two-finger-gripper-v008-pollen-grabette']['hinges']


def hinge(deg,pivot):
    c,s=math.cos(math.radians(deg)),math.sin(math.radians(deg))
    P=np.eye(4);P[:3,3]=pivot;R=np.eye(4);R[:3,:3]=[[c,0,s],[0,1,0],[-s,0,c]]
    return P@R@np.linalg.inv(P)


def tip_gap(name,angle):
    vs=m.visuals(name,{'proximal':m.ASSEMBLIES[name]['proximal'](angle)})
    pts=lambda prefix:np.concatenate([m.place(m.read_stl(m.ASSEMBLIES[name]['dir']/'assets'/f),T) for _,f,T,_ in vs if f.startswith(prefix)])
    a,b=pts('grip_soft_tip')[::5],pts('distal_soft_tip')[::5]
    return float(min(np.linalg.norm(a-p,axis=1).min() for p in b))


def main():
    checks=[];hs=hinges()
    for name,a in m.ASSEMBLIES.items():
        h=next(h for h in hs if re.match(h['match'],f'{name} finger — x'))
        assert not re.match(h['match'],f'{name} body — x')
        zero=m.visuals(name)
        for angle in (0,30,60,90):
            moved=m.visuals(name,{'proximal':a['proximal'](angle)})
            H=hinge(h['sign']*(angle-m.EXPORTED_DEG),h['pivot'])
            err=max(float(np.abs(H@A-B)[:3].max()) for (l,_,A,_),(_,_,B,_) in zip(zero,moved) if a['group'][l]!='body')
            checks.append(dict(check=f'{name}: hinge matches URDF at angle {angle}',max_error_mm=round(err,4),passed=err<0.01))
        closed,opened=tip_gap(name,0),tip_gap(name,90)
        checks.append(dict(check=f'{name}: closed soft tips nearly meet',gap_mm=round(closed,1),passed=closed<5))
        checks.append(dict(check=f'{name}: open gap is wide (positive control)',gap_mm=round(opened,1),passed=opened>50))
    (m.HERE/'geometry_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    for c in checks:print('PASS' if c['passed'] else 'FAIL',c)
    raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
if __name__=='__main__':main()
