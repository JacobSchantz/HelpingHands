#!/usr/bin/env python3
"""Pose Seeed's reBot Arm B601-RS (urdf/ReBot_Arm_RS.urdf) and write it as mm STLs, one per material, for OpenSCAD and the
live preview (voice-3cd78d20). Forward kinematics straight from the URDF's joint origins and axes; no ROS.

The output frame is a tool's own frame: give where J6's output boss top (link6's origin, its +z the roll axis pointing out of
the arm) sits in it, and every link is placed so that the tool is held there. The stock gripper (gripper_end and its fingers)
and link6's mesh (Seeed's Connector A + B stack) are left out: the tool brings its own.

    python3 arm_pose.py --out <dir> --flange 0,0,-96 --roll 0 --q 0,1.2,1.9,0,0.3,0
    import arm_pose; arm_pose.export(out_dir, flange=(0,0,-96), roll_deg=0, q=(...))

Writes <dir>/arm_<material>.stl (anodized_silver, motor_black, ...) and returns [(path, material, rgb)]. numpy only (no
trimesh), so the gripper versions' export_models.py can run it. lod='preview' (the default) reads meshes_preview/, a lighter
decimation made by vendor.py for the live preview; lod='full' reads meshes/, the set the URDF names."""
from pathlib import Path
import argparse, math, struct
import xml.etree.ElementTree as ET
import numpy as np
HERE=Path(__file__).resolve().parent
URDF=HERE/'urdf/ReBot_Arm_RS.urdf'
SKIP={'link6','gripper_end','gripper_left','gripper_right'}
# A pose with link6's +z straight up (the tool held upright, fingers +z, the way the gripper versions are drawn), the arm
# reaching forward from its base: joint1..joint6 in rad (fit_upright() finds it again).
UPRIGHT=(0.0,0.6,2.2,0.0,0.0,0.0)


def rpy(r,p,y):
    cr,sr,cp,sp,cy,sy=math.cos(r),math.sin(r),math.cos(p),math.sin(p),math.cos(y),math.sin(y)
    return np.array([[cy*cp,cy*sp*sr-sy*cr,cy*sp*cr+sy*sr],[sy*cp,sy*sp*sr+cy*cr,sy*sp*cr-cy*sr],[-sp,cp*sr,cp*cr]])


def frame(origin):
    T=np.eye(4)
    if origin is not None:
        T[:3,:3]=rpy(*map(float,origin.get('rpy','0 0 0').split()));T[:3,3]=list(map(float,origin.get('xyz','0 0 0').split()))
    return T


def axis_rot(axis,a):
    k=np.asarray(axis,float);k/=np.linalg.norm(k);K=np.array([[0,-k[2],k[1]],[k[2],0,-k[0]],[-k[1],k[0],0]])
    T=np.eye(4);T[:3,:3]=np.eye(3)+math.sin(a)*K+(1-math.cos(a))*K@K;return T


def model():
    root=ET.parse(URDF).getroot()
    colors={m.get('name'):tuple(map(float,m.find('color').get('rgba').split()[:3])) for m in root.findall('material') if m.find('color') is not None}
    joints=[dict(name=j.get('name'),type=j.get('type'),parent=j.find('parent').get('link'),child=j.find('child').get('link'),
                 T=frame(j.find('origin')),axis=list(map(float,(j.find('axis').get('xyz') if j.find('axis') is not None else '0 0 1').split())))
            for j in root.findall('joint')]
    visuals={L.get('name'):[(v.find('geometry/mesh').get('filename'),frame(v.find('origin')),v.find('material').get('name'))
                            for v in L.findall('visual')] for L in root.findall('link')}
    return joints,visuals,colors


def link_frames(q,joints):
    """world (base_link) <- link, for joint angles q (rad) in URDF joint order; fixed and prismatic joints at zero."""
    T={'base_link':np.eye(4)};revolute=[j for j in joints if j['type']=='revolute']
    angle={j['name']:(q[i] if i<len(q) else 0.0) for i,j in enumerate(revolute)}
    for j in joints:   # the URDF lists parents before children
        T[j['child']]=T[j['parent']]@j['T']@(axis_rot(j['axis'],angle[j['name']]) if j['type']=='revolute' else np.eye(4))
    return T


def fit_upright(target_z=(0,0,1)):
    """A pose (joint2, joint3, joint5) with link6's +z along target_z, by a coarse grid then a local refine."""
    joints,_,_=model();best=None
    for q2 in np.linspace(0.2,2.9,28):
        for q3 in np.linspace(0.2,2.9,28):
            for q5 in np.linspace(-1.5,1.5,13):
                z=link_frames((0,q2,q3,0,q5,0),joints)['link6'][:3,2];e=np.linalg.norm(z-target_z)
                if best is None or e<best[0]:best=(e,q2,q3,q5)
    return best


def read_stl(path):
    """triangles (n, 3, 3) of a binary or ASCII STL"""
    raw=Path(path).read_bytes();n=struct.unpack_from('<I',raw,80)[0] if len(raw)>=84 else 0
    if len(raw)==84+50*n:return np.frombuffer(raw,np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]),count=n,offset=84)['v'].reshape(n,3,3).astype(float)
    return np.array([float(x) for l in raw.decode(errors='replace').splitlines() if l.strip().startswith('vertex') for x in l.split()[1:4]]).reshape(-1,3,3)


def write_stl(path,tris):
    tris=np.asarray(tris,np.float32);n=len(tris);rec=np.zeros(n,np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))
    c=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);L=np.linalg.norm(c,axis=1,keepdims=True);rec['n']=c/np.where(L>0,L,1);rec['v']=tris.reshape(n,9)
    Path(path).write_bytes(b'arm_pose.py'.ljust(80,b' ')+struct.pack('<I',n)+rec.tobytes())


def export(out,flange=(0,0,0),roll_deg=0.0,q=UPRIGHT,skip=SKIP,lod='preview'):
    joints,visuals,colors=model();T=link_frames(q,joints)
    place=np.eye(4);place[:3,:3]=axis_rot((0,0,1),math.radians(roll_deg))[:3,:3];place[:3,3]=flange
    T6=T['link6'].copy();T6[:3,3]*=1000   # world in mm
    to_tool=place@np.linalg.inv(T6)        # tool frame <- world: link6's origin lands on the flange
    groups={}
    for link,vs in visuals.items():
        if link in skip:continue
        for fn,Tv,mat in vs:
            src=URDF.parent/(fn.replace('../meshes/','../meshes_preview/') if lod=='preview' else fn)
            M=T[link]@Tv;M=np.diag([1000,1000,1000,1])@M   # metres -> mm
            groups.setdefault(mat,[]).append(read_stl(src)@M[:3,:3].T+M[:3,3])
    out=Path(out);out.mkdir(parents=True,exist_ok=True);rows=[]
    for mat,ms in sorted(groups.items()):
        t=np.concatenate(ms)@to_tool[:3,:3].T+to_tool[:3,3]
        p=out/f'arm_{mat.removeprefix("rs_")}.stl';write_stl(p,t);rows.append((p,mat,colors.get(mat,(0.5,0.5,0.5))))
    return rows


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out',required=True);ap.add_argument('--flange',default='0,0,0');ap.add_argument('--roll',type=float,default=0)
    ap.add_argument('--q',default=','.join(map(str,UPRIGHT)));ap.add_argument('--fit',action='store_true',help='print a pose with link6 +z straight up');ap.add_argument('--lod',default='preview',choices=['preview','full'])
    a=ap.parse_args()
    if a.fit:print(fit_upright())
    for p,mat,c in export(a.out,tuple(map(float,a.flange.split(','))),a.roll,tuple(map(float,a.q.split(','))),lod=a.lod):print(p,mat,c)
