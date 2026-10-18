#!/usr/bin/env python3
"""Assemble Pollen's Grabette and Gripette exactly as their URDFs do and export them for the gallery.

Grabette is the hand-held data-collection gripper and Gripette is the robot-side gripper
with the same finger. Every visual in each robot.urdf becomes one viewer part: the
upstream STL, unchanged in shape, moved by the URDF's own link/joint/visual transforms
(metres -> mm) and coloured with the URDF material. The parts that drive or measure the
finger (Gripette's two servos in magenta, Grabette's angle sensors and magnets in red)
are recoloured so they stand out. Gripette stands to the right of Grabette. Writes gripper.scad (the same
scene as OpenSCAD imports), exports/parts/*.stl + viewer_parts.json (with exploded-view
offsets), exports/assembly.stl, mesh_checks.json and previews/. Run fetch_grabette.py first."""
from pathlib import Path
import json, math, re, subprocess, xml.etree.ElementTree as ET
import numpy as np
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
# The gallery is Z-up and its hinges turn about Y, so URDF z (every finger joint axis)
# goes to world Y: URDF (x, y, z) -> world (-x, -z, -y), metres -> mm. That leaves each
# body on top and its finger hanging down.
WORLD=np.array([[-1,0,0,0],[0,0,-1,0],[0,-1,0,0],[0,0,0,1]],float)@np.diag([1000,1000,1000,1.0])
# Gallery 'angle' = finger opening in degrees: 0 closed, 90 wide open. Parts are exported
# at the URDF zero pose, which is wide open on both, i.e. angle 90. Only the proximal joint
# follows the slider; the distal joint stays at 0 (straight).
EXPORTED_DEG=90
GAP_X=320  # Gripette's offset to the right of Grabette, mm
# group: URDF link -> sub-assembly; proximal: gallery angle (deg) -> URDF proximal (rad).
# Grabette's proximal joint runs [-90, 0] deg (0 open); Gripette's runs [0, 90] (0 open).
# drive: (link, mesh prefix) -> label + highlight colour for the parts that move or read the finger.
ASSEMBLIES={
    'Grabette':dict(dir=HERE/'pollen',shift=0,proximal=lambda a:math.radians(a-90),
        group={'grip_r':'body','proximal_bend_r':'finger','distal_r':'finger tip'},
        drive={('grip_r','radial_magnet'):('SENSOR proximal-joint magnet','#e5322d'),
               ('proximal_bend_r','sensor'):('SENSOR AS5600L angle sensor','#e5322d'),
               ('distal_r','radial_magnet'):('SENSOR distal-joint magnet','#e5322d')}),
    'Gripette':dict(dir=HERE/'pollen/gripette',shift=GAP_X,proximal=lambda a:math.radians(90-a),
        group={'gripper_base_r':'body','proximal_bot_r':'finger','distal_r':'finger tip'},
        drive={('gripper_base_r','feetech_sts3215'):('DRIVE proximal servo STS3215 (ID 1)','#d81b9a'),
               ('proximal_bot_r','feetech_sts3215'):('DRIVE distal servo STS3215 (ID 2)','#d81b9a')}),
}
# The main printed frame of each gripper, kept (faint) in the drive-only preview.
FRAME={'grip_r','proximal_bend_r','pivot_bot_r','distal_r','gripper_base_r','proximal_bot_r','proximal_top_r','distal_part_r'}
DTYPE=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')])


def origin(el):
    xyz=[float(v) for v in el.get('xyz','0 0 0').split()] if el is not None else [0,0,0]
    r,p,y=[float(v) for v in el.get('rpy','0 0 0').split()] if el is not None else [0,0,0]
    cx,sx,cy,sy,cz,sz=math.cos(r),math.sin(r),math.cos(p),math.sin(p),math.cos(y),math.sin(y)
    T=np.eye(4)
    T[:3,:3]=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    T[:3,3]=xyz
    return T


def axis_rot(axis,q):
    a=np.array(axis,float);a/=np.linalg.norm(a);K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    T=np.eye(4);T[:3,:3]=np.eye(3)+math.sin(q)*K+(1-math.cos(q))*K@K
    return T


def place_world(shift):
    S=np.eye(4);S[0,3]=shift
    return S@WORLD


def visuals(name,q=None):
    """[(link, mesh file, 4x4 world transform in mm, '#rrggbb')] for one assembly at joint angles q (radians)."""
    a=ASSEMBLIES[name];q=q or {}
    root=ET.parse(a['dir']/'robot.urdf').getroot()
    joints={j.find('child').get('link'):j for j in root.findall('joint')}
    def link_T(link):
        if link not in joints:return np.eye(4)
        j=joints[link];T=link_T(j.find('parent').get('link'))@origin(j.find('origin'))
        if j.get('type')=='revolute':T=T@axis_rot([float(v) for v in j.find('axis').get('xyz').split()],q.get(j.get('name'),0))
        return T
    out=[]
    for link in root.findall('link'):
        for v in link.findall('visual'):
            rgba=[float(c) for c in v.find('material/color').get('rgba').split()]
            out.append((link.get('name'),v.find('geometry/mesh').get('filename').split('/')[-1],
                        place_world(a['shift'])@link_T(link.get('name'))@origin(v.find('origin')),
                        '#'+''.join(f'{round(c*255):02x}' for c in rgba[:3])))
    return out


def joint_pivot(name):
    """World (x, z) of the proximal joint axis, for the gallery hinge."""
    a=ASSEMBLIES[name];root=ET.parse(a['dir']/'robot.urdf').getroot()
    j=next(j for j in root.findall('joint') if j.get('name')=='proximal')
    p=place_world(a['shift'])@origin(j.find('origin'))[:,3]
    return [round(float(p[0]),3),0,round(float(p[2]),3)]


def read_stl(path):
    raw=path.read_bytes();n=int(np.frombuffer(raw,'<u4',1,80)[0])
    assert len(raw)==84+50*n,f'Not binary STL: {path}'
    return np.frombuffer(raw,DTYPE,n,84)['v'].reshape(-1,3).astype(float)


def write_stl(path,v):
    t=v.reshape(-1,3,3);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-12)
    a=np.zeros(len(t),DTYPE);a['n']=n;a['v']=t.reshape(-1,9)
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'\0'*80+np.uint32(len(t)).tobytes()+a.tobytes())


def place(v,T):
    return v@T[:3,:3].T+T[:3,3]


def label(mesh):
    s=re.sub(r'\.stl$','',mesh);s=re.sub(r'_[0-9a-f]{32}$','',s);s=re.sub(r'__configuration.*$','',s)
    return s.replace('_',' ').strip()


def drive_of(name,link,mesh):
    return next((v for (l,prefix),v in ASSEMBLIES[name]['drive'].items() if l==link and mesh.startswith(prefix)),None)


def scad_source(parts):
    def mat(T):return '['+','.join('['+','.join(f'{x:.6g}' for x in row)+']' for row in T)+']'
    lines=['// GENERATED by export_models.py from pollen/robot.urdf and pollen/gripette/robot.urdf — do not edit by hand.',
           "// Pollen Robotics' Grabette and Gripette (right), Apache-2.0: the upstream meshes, placed by their URDFs.",
           '// Magenta = Gripette drive servos, red = Grabette angle sensors and magnets (recoloured to stand out).',
           f'angle={EXPORTED_DEG}; // finger opening, degrees: 0 closed, 90 = URDF zero pose (open)','part="assembly";',
           'explode=0; // 1 = exploded view, the same per-part offsets as viewer_parts.json',
           'drive_only=0; // 1 = only the drive/sensor parts, plus the main frame parts drawn faint and see-through',
           'function c(hex) = drive_only ? [0.6, 0.6, 0.6, 0.25] : hex;','']
    for name in ASSEMBLIES:
        for moving in (False,True):
            lines.append(f'module {name.lower()}_{"finger" if moving else "body"}() {{')
            for p in parts:
                if p['assembly']==name and (p['group']!='body')==moving:
                    sub=p['dir'].relative_to(HERE).as_posix()
                    col=f'"{p["color"]}"' if p['drive'] else f'c("{p["color"]}")'
                    hide='' if p['drive'] or p['mesh'][:-4] in FRAME else 'if (!drive_only) '
                    lines.append(f'  {hide}translate(explode*{p["explode"]}) color({col}) multmatrix({mat(p["T"])}) import("{sub}/assets/{p["mesh"]}");')
            lines.append('}')
    lines.append('')
    for name in ASSEMBLIES:
        x,_,z=joint_pivot(name)
        lines.append(f'{name.lower()}_body(); translate([{x},0,{z}]) rotate([0, (angle-{EXPORTED_DEG}), 0]) translate([{-x},0,{-z}]) {name.lower()}_finger();')
    return '\n'.join(lines)+'\n'


def main():
    meshes={};parts=[]
    for name,a in ASSEMBLIES.items():
        for link,mesh,T,color in visuals(name):
            if (name,mesh) not in meshes:meshes[name,mesh]=read_stl(a['dir']/'assets'/mesh)
            drive=drive_of(name,link,mesh)
            i=len(parts);tag=drive[0] if drive else label(mesh)
            parts.append(dict(assembly=name,dir=a['dir'],drive=bool(drive),group=a['group'][link],mesh=mesh,T=T,color=drive[1] if drive else color,
                              v=place(meshes[name,mesh],T),title=f'{name} {a["group"][link]} — {tag}',
                              path=f'exports/parts/{i:03d}_{name.lower()}_{re.sub(r"[^a-z0-9]+","_",label(mesh).lower())[:40]}.stl'))
    # Exploded view: each part slides away from the centre of its sub-assembly, and each
    # finger as a whole slides further out from its body, so screws and shells separate.
    centre={(p['assembly'],p['group']):None for p in parts}
    for k in centre:centre[k]=np.mean([p['v'].mean(0) for p in parts if (p['assembly'],p['group'])==k],0)
    for p in parts:
        c=(p['v'].min(0)+p['v'].max(0))/2
        e=0.9*(c-centre[p['assembly'],p['group']])
        if p['group']!='body':e+=0.6*(centre[p['assembly'],p['group']]-centre[p['assembly'],'body'])
        p['explode']=[round(float(x),1) for x in e]
    (HERE/'gripper.scad').write_text(scad_source(parts))
    for old in (HERE/'exports/parts').glob('*.stl'):old.unlink()
    for p in parts:write_stl(HERE/p['path'],p['v'])
    write_stl(HERE/'exports/assembly.stl',np.concatenate([p['v'] for p in parts]))
    (HERE/'viewer_parts.json').write_text(json.dumps(dict(parts=[dict(path=p['path'],name=p['title'],
        color=p['color'],explode=p['explode']) for p in parts]),indent=2)+'\n')
    checks={}
    for name in ASSEMBLIES:
        ps=[p for p in parts if p['assembly']==name];all_v=np.concatenate([p['v'] for p in ps])
        checks[name]=dict(parts=len(ps),upstream_meshes=sum(k[0]==name for k in meshes),triangles=len(all_v)//3,
                          bounds_mm=[all_v.min(0).round(2).tolist(),all_v.max(0).round(2).tolist()],
                          groups={g:sum(p['group']==g for p in ps) for g in ('body','finger','finger tip')},
                          highlighted=sorted({p['title'] for p in ps if drive_of(name,next(l for l,g in ASSEMBLIES[name]['group'].items() if g==p['group']),p['mesh'])}),
                          proximal_pivot_mm=joint_pivot(name))
    (HERE/'mesh_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    (HERE/'previews').mkdir(exist_ok=True)
    for name,angle,camera in (('exploded',f'{EXPORTED_DEG}; explode=1','0,0,0,65,0,35,900'),('front',EXPORTED_DEG,'0,0,0,90,0,0,700'),('iso',EXPORTED_DEG,'0,0,0,65,0,35,700'),
                              ('closed',0,'0,0,0,90,0,0,700'),('drive',f'{EXPORTED_DEG}; drive_only=1','0,0,0,60,0,20,700'),('side',EXPORTED_DEG,'0,0,0,90,0,90,700')):
        r=subprocess.run([SCAD,'-D',f'angle={angle}','--preview','--projection=o','--imgsize=1400,1000','--colorscheme=Tomorrow',
                          f'--camera={camera}','--viewall','--autocenter','-o',str(HERE/'previews'/f'{name}.png'),str(HERE/'gripper.scad')],
                         capture_output=True,text=True)
        if r.returncode:print('FAIL preview',name,r.stderr[-300:])
    print(json.dumps({k:{x:v[x] for x in ('parts','groups','proximal_pivot_mm')} for k,v in checks.items()}))
if __name__=='__main__':main()
