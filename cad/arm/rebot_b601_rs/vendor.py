#!/usr/bin/env python3
"""Bring Seeed's reBot Arm B601-RS CAD into this folder (voice-3cd78d20). Downloads, at the pinned commit, Seeed's RS URDF,
its visual/collision meshes, the licence and the two stock gripper-connector STEPs, then decimates every mesh over
DECIMATE_OVER triangles to 20% (never under KEEP_AT_LEAST) so the folder stays small. The URDF is kept byte for byte and the
meshes keep its units (metres) and file names, so urdf/ReBot_Arm_RS.urdf still loads as it is; meshes_preview/ is a lighter
copy (5%) for the live preview. arm_pose.py turns either into mm STLs for OpenSCAD and the live preview.

    cad/blender/.venv/bin/python cad/arm/rebot_b601_rs/vendor.py           # needs trimesh + fast_simplification
    cad/blender/.venv/bin/python cad/arm/rebot_b601_rs/vendor.py --full     # the meshes as Seeed ships them (~70 MB, not committed)
"""
from pathlib import Path
import argparse, json, urllib.request
HERE=Path(__file__).resolve().parent
REPO='Seeed-Projects/reBot-DevArm'
SHA='9e8634ca0b20403c580903b771da952b17361c27'   # main on 2026-10-20
RAW=f'https://raw.githubusercontent.com/{REPO}/{SHA}/'
DESC='Rebot_Arm_description/RS/'
STEPS=['hardware/reBot_B601_RS/Metal_Parts/2-M6-ROTOR.step',    # Seeed's "Gripper Connector A": on the J6 output
       'hardware/reBot_B601_RS/Metal_Parts/2-M7-STATOR.step']   # Seeed's "Gripper Connector B": the stock gripper motor's back plate
DECIMATE_OVER=12000
KEEP_AT_LEAST=6000
PREVIEW_FRACTION=0.05   # meshes_preview/: what the live preview draws (arm_pose.py lod='preview')
PREVIEW_AT_LEAST=1500


def get(path,tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(RAW+path.replace(' ','%20'),timeout=60) as r:return r.read()
        except OSError:
            if i==tries-1:raise


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--full',action='store_true');a=ap.parse_args()
    import io, numpy as np, trimesh, fast_simplification
    tree=json.load(urllib.request.urlopen(f'https://api.github.com/repos/{REPO}/git/trees/{SHA}?recursive=1'))['tree']
    meshes=[t['path'] for t in tree if t['path'].startswith(DESC+'meshes/') and t['path'].endswith('.STL') and '/mujoco_collision/' not in t['path']]
    (HERE/'urdf').mkdir(exist_ok=True);(HERE/'interface').mkdir(exist_ok=True)
    (HERE/'urdf/ReBot_Arm_RS.urdf').write_bytes(get(DESC+'urdf/ReBot_Arm_RS.urdf'))
    (HERE/'LICENSE').write_bytes(get('LICENSE'))
    for p in STEPS:(HERE/'interface'/Path(p).name).write_bytes(get(p))
    rows=[]
    for p in meshes:
        out=HERE/'meshes'/p[len(DESC+'meshes/'):];out.parent.mkdir(parents=True,exist_ok=True)
        m=trimesh.load(io.BytesIO(get(p)),file_type='stl');n=len(m.faces)
        if n>DECIMATE_OVER and not a.full:
            v,f=fast_simplification.simplify(m.vertices.astype(np.float32),m.faces,target_count=max(KEEP_AT_LEAST,n//5))
            m=trimesh.Trimesh(v,f)
        m.export(out);rows.append(dict(mesh=str(out.relative_to(HERE)),seeed_triangles=n,triangles=len(m.faces)))
        lite=HERE/'meshes_preview'/out.relative_to(HERE/'meshes');lite.parent.mkdir(parents=True,exist_ok=True)
        if len(m.faces)>PREVIEW_AT_LEAST:
            v,f=fast_simplification.simplify(m.vertices.astype(np.float32),m.faces,target_count=max(PREVIEW_AT_LEAST,int(n*PREVIEW_FRACTION)))
            m=trimesh.Trimesh(v,f)
        m.export(lite);rows[-1]['preview_triangles']=len(m.faces)
        print(f'{out.relative_to(HERE)}: {n} -> {rows[-1]["triangles"]} triangles (preview {len(m.faces)})')
    (HERE/'meshes/decimation.json').write_text(json.dumps(dict(source=f'https://github.com/{REPO}/tree/{SHA}/{DESC}meshes',rows=rows),indent=1)+'\n')


if __name__=='__main__':main()
