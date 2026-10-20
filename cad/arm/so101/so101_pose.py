#!/usr/bin/env python3
"""Pose The Robot Studio's SO-101 follower arm (so101_new_calib.urdf) and write it as mm STLs, one per material, for OpenSCAD
and the live preview (voice-790aa455). Forward kinematics straight from the URDF's joint origins and axes; no ROS. The maths
is the reBot's (cad/arm/rebot_b601_rs/arm_pose.py); only the arm and its tool interface differ.

The output frame is a tool's own frame: give where the wrist-roll servo's horn face sits in it (HORN, the stock fixed jaw's seat
on the horn, in gripper_link's frame), and every link is placed so that the tool is held there, the roll axis along the tool's
+z (the gripper_link's -z, the way the stock jaw points). The stock gripper (gripper_link: the fixed jaw and the gripper servo;
the moving jaw) is left out: the tool brings its own.

    python3 so101_pose.py --out <dir> --horn 0,0,-90 --roll 0
    import so101_pose; so101_pose.export(out_dir, horn=(0,0,-90), roll_deg=0)

Writes <dir>/arm_<material>.stl (printed, sts3215) and returns [(path, material, rgb)]. numpy only."""
from pathlib import Path
import argparse, math, sys
import xml.etree.ElementTree as ET
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'rebot_b601_rs'))
from arm_pose import frame, axis_rot, read_stl, write_stl   # the reBot's FK and STL helpers (this file is named apart from it)
URDF=HERE/'so101_new_calib.urdf'
SKIP={'gripper_link','moving_jaw_so101_v1_link','gripper_frame_link'}
TOOL='gripper_link'
# The horn's face, in gripper_link's frame (mm): the stock fixed jaw's flat seat (z -3.0, measured on its mesh), centred on its
# 4 horn screws on 14 (x -0.7: the URDF's roll axis runs 0.7 mm off the jaw's screw circle). The horn's screw face points -z.
HORN=(-0.7,0.0,-3.0)
# A pose with the roll axis straight up (the tool held upright, the way the gripper versions are drawn), the arm reaching
# forward from its base: shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll in rad (fit_upright() finds it again).
UPRIGHT=(0.0,0.6,-1.1,-1.0708,0.0)
NAMES={'3d_printed':'printed','sts3215':'sts3215'}


def model():
    root=ET.parse(URDF).getroot()
    colors={m.get('name'):tuple(map(float,m.find('color').get('rgba').split()[:3])) for m in root.findall('material') if m.find('color') is not None}
    joints=[dict(name=j.get('name'),type=j.get('type'),parent=j.find('parent').get('link'),child=j.find('child').get('link'),
                 T=frame(j.find('origin')),axis=list(map(float,(j.find('axis').get('xyz') if j.find('axis') is not None else '0 0 1').split())))
            for j in root.findall('joint')]
    order=[];done={'base_link'}   # onshape-to-robot lists children before parents: walk out from the base
    while len(order)<len(joints):
        for j in joints:
            if j not in order and j['parent'] in done:order.append(j);done.add(j['child'])
    visuals={L.get('name'):[(v.find('geometry/mesh').get('filename'),frame(v.find('origin')),v.find('material').get('name'))
                            for v in L.findall('visual')] for L in root.findall('link')}
    return order,visuals,colors


ARM=('shoulder_pan','shoulder_lift','elbow_flex','wrist_flex','wrist_roll')


def link_frames(q,joints):
    """world (base_link) <- link, for joint angles q (rad) in ARM order; the gripper joint at zero."""
    T={'base_link':np.eye(4)};angle=dict(zip(ARM,q))
    for j in joints:
        T[j['child']]=T[j['parent']]@j['T']@(axis_rot(j['axis'],angle.get(j['name'],0.0)) if j['type']=='revolute' else np.eye(4))
    return T


def fit_upright(lift=UPRIGHT[1],elbow=UPRIGHT[2],target=(0,0,1)):
    """The wrist_flex that turns gripper_link's -z along target for this shoulder_lift and elbow_flex (rad): (error, wrist_flex)."""
    joints,_,_=model()
    return min((np.linalg.norm(-link_frames((0,lift,elbow,q3,0),joints)[TOOL][:3,2]-target),q3) for q3 in np.linspace(-1.65,1.65,6601))


def export(out,horn=(0,0,0),roll_deg=0.0,q=UPRIGHT,skip=SKIP,lod='preview'):
    joints,visuals,colors=model();T=link_frames(q,joints)
    flip=np.diag([1.0,-1.0,-1.0,1.0])   # gripper_link -> tool: its -z (the jaw's way) becomes +z
    place=np.eye(4);place[:3,:3]=axis_rot((0,0,1),math.radians(roll_deg))[:3,:3];place[:3,3]=horn
    Tg=T[TOOL].copy();Tg[:3,3]*=1000   # world in mm
    seat=np.eye(4);seat[:3,3]=HORN     # gripper_link <- the horn face's frame
    to_tool=place@flip@np.linalg.inv(Tg@seat)   # tool frame <- world: the horn face lands on horn
    groups={}
    for link,vs in visuals.items():
        if link in skip:continue
        for fn,Tv,mat in vs:
            src=URDF.parent/(fn.replace('assets/','assets_preview/') if lod=='preview' else fn)
            M=T[link]@Tv;M=np.diag([1000,1000,1000,1])@M   # metres -> mm
            groups.setdefault(mat,[]).append(read_stl(src)@M[:3,:3].T+M[:3,3])
    out=Path(out);out.mkdir(parents=True,exist_ok=True);rows=[]
    for mat,ms in sorted(groups.items()):
        t=np.concatenate(ms)@to_tool[:3,:3].T+to_tool[:3,3]
        p=out/f'arm_{NAMES.get(mat,mat)}.stl';write_stl(p,t);rows.append((p,mat,colors.get(mat,(0.5,0.5,0.5))))
    return rows


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out');ap.add_argument('--horn',default='0,0,0');ap.add_argument('--roll',type=float,default=0)
    ap.add_argument('--q',default=','.join(map(str,UPRIGHT)));ap.add_argument('--fit',action='store_true',help='print the wrist_flex that holds the roll axis straight up');ap.add_argument('--lod',default='preview',choices=['preview','full'])
    a=ap.parse_args()
    if a.fit:print(fit_upright())
    if a.out:
        for p,mat,c in export(a.out,tuple(map(float,a.horn.split(','))),a.roll,tuple(map(float,a.q.split(','))),lod=a.lod):print(p,mat,c)
