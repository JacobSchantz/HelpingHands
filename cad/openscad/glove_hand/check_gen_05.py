#!/usr/bin/env python3
# /// script
# dependencies = ["numpy", "manifold3d"]
# ///
"""Fail-closed geometric audit for gen05. Run: uv run check_gen_05.py.
Exports the actual CAD, transforms its rigid bodies over a pose grid, and
intersects watertight meshes with Manifold. A compiler error, missing STL,
invalid manifold, disconnected printable body or unexpected collision fails.
Not a strength, fit, tendon-friction, spring-rate or human-safety validation.
"""
import argparse, concurrent.futures, hashlib, itertools, json, math, os
from pathlib import Path
import re, struct, subprocess, tempfile
import numpy as np
import manifold3d as md

HERE=Path(__file__).resolve().parent
SRC=HERE/'gen_05_index_anatomical.scad'
SCAD=os.environ.get('OPENSCAD','/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD')
PARTS=['base','proximal','middle','distal','drum','lid']
COLORS=['#7d8c9d','#e3e4df','#e3e4df','#e3e4df','#527b9e','#8995a3']
OUT=HERE/'print'/'gen_05'
EXPORT=HERE/'export'
EPS=0.01  # cubic mm, numerical reporting threshold; no notion of safe contact


def read_stl(p):
    b=p.read_bytes()
    n=struct.unpack('<I',b[80:84])[0]
    if len(b)!=84+n*50: raise RuntimeError(f'Expected binary STL: {p}')
    rec=np.frombuffer(b[84:],dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]))
    return rec['v'].astype(float)

def write_stl(p,t):
    p.parent.mkdir(parents=True,exist_ok=True)
    t=np.asarray(t,dtype=np.float32); n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-12)
    rec=np.zeros(len(t),dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]))
    rec['n']=n;rec['v']=t
    p.write_bytes(b'Original gen05 index glove CAD'.ljust(80,b' ')+struct.pack('<I',len(t))+rec.tobytes())

def scad(code=None,**defs):
    with tempfile.TemporaryDirectory(prefix='gen05-') as tmp:
        out=Path(tmp)/'mesh.stl'; source=SRC
        if code is not None:
            source=Path(tmp)/'probe.scad';source.write_text(f'include <{SRC}>\n'+code)
        cmd=[SCAD,'--backend','Manifold','--export-format','binstl','-o',str(out)]
        if code is not None: cmd+=['-D','part="none"']
        for k,v in defs.items():cmd+=['-D',f'{k}={json.dumps(v)}']
        cmd.append(str(source))
        run=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        if run.returncode or not out.exists() or re.search(r'ERROR:|WARNING:',run.stderr):
            raise RuntimeError(f'OpenSCAD export failed ({defs}): {run.stderr[-2500:]}')
        return read_stl(out)

def metadata():
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'meta.echo'
        r=subprocess.run([SCAD,'-o',str(p),'-D','part="metadata"',str(SRC)],capture_output=True,text=True,timeout=30)
        if r.returncode or not p.exists():raise RuntimeError(r.stderr)
        s=p.read_text().removeprefix('ECHO: ').strip()
        # OpenSCAD echo values are JSON arrays/numbers. Parse each complete value.
        ans={};dec=json.JSONDecoder()
        while s:
            k,s=s.split(' = ',1);v,n=dec.raw_decode(s);ans[k]=v;s=s[n:].lstrip(', ')
        return ans

def manifold(tris):
    # Weld exported coincident vertices, never silently fill holes or drop faces.
    verts,ind=np.unique(np.round(tris.reshape(-1,3),5),axis=0,return_inverse=True)
    faces=ind.reshape(-1,3)
    mesh=md.Manifold(md.Mesh(np.asarray(verts,dtype=np.float32),np.asarray(faces,dtype=np.uint32)))
    if mesh.status()!=md.Error.NoError or mesh.is_empty():raise RuntimeError(f'Invalid/non-solid CAD mesh: {mesh.status()}')
    return mesh

def stats(t,m):
    lo=t.reshape(-1,3).min(0);hi=t.reshape(-1,3).max(0)
    n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);a=np.linalg.norm(n,axis=1)/2;n/=np.maximum(2*a[:,None],1e-12)
    onbed=(t[:,:,2].max(1)<.015)&(n[:,2]<-.99)
    over=(n[:,2]<-math.cos(math.pi/4))&~onbed&(t[:,:,2].min(1)>.2)
    return dict(bodies=len(m.decompose()),volume_mm3=m.volume(),size_mm=(hi-lo).tolist(),triangles=len(t),bed_mm2=float(a[onbed].sum()),overhang_mm2=float(a[over].sum()))

def trans(v):
    a=np.eye(4);a[:3,3]=v;return a

def rot(deg):
    a=math.radians(-deg);c,s=math.cos(a),math.sin(a)
    return np.array([[1,0,0,0],[0,c,-s,0],[0,s,c,0],[0,0,0,1.]])

def frames(pose,E):
    f=[]
    for k in range(3):f.append(rot(pose[k]) if k==0 else f[-1]@trans([0,E[k-1],0])@rot(pose[k]))
    return f

def xform(m,f):return m.transform(f[:3,:4])

def intersection(a,b):return max(0.,(a^b).volume())

def cord_points(meta,pose):
    f=frames(pose,meta['lengths']);gx=meta['groove_x'];r=4.05
    pts=[[gx,-r,28.]]
    pts.extend([gx,-r*math.cos(math.radians(a)),-r*math.sin(math.radians(a))] for a in np.linspace(0,90-pose[0],33))
    pts.extend((f[k]@np.r_[q,1])[:3].tolist() for k,g in enumerate(meta['guides']) for q in g)
    return np.asarray(pts)

def cord_mesh(pts,r=.25):
    # Swept capsules match SCAD route(), including end knots, not zero-width lines.
    sphere=md.Manifold.sphere(r,12)
    return md.Manifold.batch_boolean([md.Manifold.batch_hull([sphere.translate(a),sphere.translate(b)]) for a,b in zip(pts,pts[1:])],md.OpType.Add)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--quick',action='store_true');ap.add_argument('--export-only',action='store_true');ap.add_argument('--probe',action='store_true');args=ap.parse_args()
    meta=metadata();print('metadata',json.dumps(meta),flush=True)
    meshes={};printed={};report={};OUT.mkdir(parents=True,exist_ok=True);EXPORT.mkdir(exist_ok=True)
    # Independent CAD exports can run concurrently. Failure in any future propagates.
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        fut={pool.submit(scad,part=p,local_part=True):p for p in PARTS}
        for f in concurrent.futures.as_completed(fut):
            p=fut[f];t=f.result();m=manifold(t);meshes[p]=m;printed[p]=t
            print(p,'bodies',len(m.decompose()),'volume',round(m.volume(),2),flush=True)
    if args.probe:
        # Development report still uses actual CAD and fails on invalid geometry.
        pass
    for p in PARTS:
        t=scad(part='print',piece=p);t-=np.r_[(t.reshape(-1,3).min(0)[:2]+t.reshape(-1,3).max(0)[:2])/2,t[:,:,2].min()]
        m=manifold(t);report[p]=stats(t,m);write_stl(OUT/f'gen_05_{p}.stl',t)
        # Workbench files in their assembled zero pose. Interactive view reverses this translation.
        idx={'proximal':0,'middle':1,'distal':2}.get(p)
        shift=np.array(meta['origin'])+np.array([0,sum(meta['lengths'][:idx]) if idx is not None else 0,0])
        write_stl(EXPORT/f'gen_05_{p}.stl',printed[p]+shift)
    t=scad(part='print',piece='coupon'); t[:,:,2]-=t[:,:,2].min();m=manifold(t);report['coupon']=stats(t,m);write_stl(OUT/'gen_05_coupon.stl',t)
    meta['source_sha256']=hashlib.sha256(SRC.read_bytes()).hexdigest();meta['parts']=PARTS
    (OUT/'geometry.json').write_text(json.dumps(meta,indent=2)+'\n')
    (OUT/'meshes.json').write_text(json.dumps(report,indent=2)+'\n')
    if args.export_only:return
    failures=[]
    for p,s in report.items():
        want=3 if p=='coupon' else 1
        if s['bodies']!=want:failures.append(f'{p}: {s["bodies"]} bodies, expected {want}')
    # Hand/collision proxies are also generated by the CAD, not guessed boxes.
    hand=[manifold(scad(code=f'segment({k},0);')) for k in range(3)]
    palm=manifold(scad(code='palm(1.5);'))
    hparts=[manifold(scad(code=f'hardware({k});')) for k in range(3)]
    poses=[[0,0,0],[45,45,30],[90,95,65],[90,0,0],[0,95,0],[0,0,65]] if args.quick else [list(x) for x in itertools.product([0,30,60,90],[0,30,60,95],[0,22,44,65])]
    thumb_yaws=[22,30,45,70];thumbs={yaw:manifold(scad(code=f'thumb(0);',thumb_yaw=yaw)) for yaw in thumb_yaws}
    # use-import keeps definition scope; pass arguments explicitly for neighbour poses.
    thumbs={yaw:manifold(scad(code=f'translate(-hand_mcp(0)) hand_thumb(0,0,{yaw},[0,0]);\n', **{})) for yaw in []} if False else thumbs
    maximum={};details=[]
    for pose in poses:
        fs=frames(pose,meta['lengths']);parts={p:(xform(meshes[p],fs[{'proximal':0,'middle':1,'distal':2}[p]]) if p in ['proximal','middle','distal'] else meshes[p]) for p in PARTS}
        skin=md.Manifold.batch_boolean([xform(h,f) for h,f in zip(hand,fs)],md.OpType.Add)
        full=md.Manifold.batch_boolean(list(parts.values()),md.OpType.Add)
        checks={f'{a} x {b}':intersection(parts[a],parts[b]) for a,b in itertools.combinations(PARTS,2)}
        checks.update({f'{p} x finger':intersection(m,skin) for p,m in parts.items()})
        checks.update({f'{p} x palm comfort':intersection(m,palm) for p,m in parts.items()})
        for yaw,th in thumbs.items():checks[f'printed x thumb {yaw}']=intersection(full,th)
        for k,f in enumerate(fs):checks[f'pin {k} x skin']=intersection(xform(hparts[k],f),skin)
        cord=cord_mesh(cord_points(meta,pose));checks['cord x finger']=intersection(cord,skin)
        for yaw,th in thumbs.items():checks[f'cord x thumb {yaw}']=intersection(cord,th)
        for key,v in checks.items():
            maximum[key]=max(maximum.get(key,0),v)
            if v>EPS:details.append({'pose':pose,'pair':key,'mm3':round(v,4)})
        print('pose',pose,'collisions',[(k,round(v,3)) for k,v in checks.items() if v>EPS],flush=True)
    audit=dict(source_sha256=meta['source_sha256'],pose_count=len(poses),max_overlaps_mm3=maximum,collisions=details,mesh_failures=failures)
    (OUT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print('GEOMETRY PASS' if not details and not failures else 'GEOMETRY FAIL',flush=True)
    raise SystemExit(1 if details or failures else 0)

if __name__=='__main__':main()
