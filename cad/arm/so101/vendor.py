#!/usr/bin/env python3
"""Bring The Robot Studio's SO-101 arm CAD into this folder (voice-790aa455). Downloads, at the pinned commit, the follower URDF
(Simulation/SO101/so101_new_calib.urdf), the meshes it names, the licence and the wrist STEPs, then decimates every mesh over
DECIMATE_OVER triangles to 20% (never under KEEP_AT_LEAST) so the folder stays small. The URDF is kept byte for byte and the
meshes keep its units (metres) and names under assets/, so so101_new_calib.urdf still loads as it is; assets_preview/ is a
lighter copy (5%) for the live preview. arm_pose.py turns either into mm STLs for OpenSCAD and the live preview.

    cad/blender/.venv/bin/python cad/arm/so101/vendor.py           # needs trimesh + fast_simplification
    cad/blender/.venv/bin/python cad/arm/so101/vendor.py --full    # the meshes as The Robot Studio ships them (~15 MB, not committed)
"""
from pathlib import Path
import argparse, json, re, urllib.request
HERE=Path(__file__).resolve().parent
REPO='TheRobotStudio/SO-ARM100'
SHA='a758567c3978dfeefe282ede0500085a48fe8f78'   # main on 2026-10-20
RAW=f'https://raw.githubusercontent.com/{REPO}/{SHA}/'
SIM='Simulation/SO101/'
URDF='so101_new_calib.urdf'
STEPS=['STEP/SO101/Wrist_Roll_Pitch_SO101.step',                       # holds the wrist-roll STS3215 (the collar round its horn)
       'STEP/SO101/Follower_Specific/Wrist_Roll_Follower_SO101.step']   # the stock fixed jaw on that horn, which Mount 2 replaces
DECIMATE_OVER=12000
KEEP_AT_LEAST=6000
PREVIEW_FRACTION=0.05   # assets_preview/: what the live preview draws (arm_pose.py lod='preview')
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
    urdf=get(SIM+URDF);(HERE/URDF).write_bytes(urdf)
    (HERE/'LICENSE').write_bytes(get('LICENSE'))
    (HERE/'interface').mkdir(exist_ok=True)
    for p in STEPS:(HERE/'interface'/Path(p).name).write_bytes(get(p))
    rows=[]
    for name in sorted(set(re.findall(r'filename="(assets/[^"]+\.stl)"',urdf.decode()))):
        out=HERE/name;out.parent.mkdir(parents=True,exist_ok=True)
        m=trimesh.load(io.BytesIO(get(SIM+name)),file_type='stl');n=len(m.faces)
        if n>DECIMATE_OVER and not a.full:
            v,f=fast_simplification.simplify(m.vertices.astype(np.float32),m.faces,target_count=max(KEEP_AT_LEAST,n//5))
            m=trimesh.Trimesh(v,f)
        m.export(out);rows.append(dict(mesh=name,source_triangles=n,triangles=len(m.faces)))
        lite=HERE/'assets_preview'/out.name;lite.parent.mkdir(parents=True,exist_ok=True)
        if len(m.faces)>PREVIEW_AT_LEAST:
            v,f=fast_simplification.simplify(m.vertices.astype(np.float32),m.faces,target_count=max(PREVIEW_AT_LEAST,int(n*PREVIEW_FRACTION)))
            m=trimesh.Trimesh(v,f)
        m.export(lite);rows[-1]['preview_triangles']=len(m.faces)
        print(f'{name}: {n} -> {rows[-1]["triangles"]} triangles (preview {len(m.faces)})')
    (HERE/'assets/decimation.json').write_text(json.dumps(dict(source=f'https://github.com/{REPO}/tree/{SHA}/{SIM}assets',rows=rows),indent=1)+'\n')


if __name__=='__main__':main()
