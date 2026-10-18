#!/usr/bin/env python3
"""Fetch Pollen Robotics' Grabette (right hand) URDF and meshes, unchanged, into pollen/.

Pinned to one upstream commit. The meshes live in Git LFS, so this clones without
them and then runs `git lfs pull` for the one URDF folder we use. The URDF, licence
files and SOURCE_MANIFEST.json are committed here; the STLs are not (the repo ignores
*.stl), and this script brings them back byte-for-byte, checked against the manifest."""
from pathlib import Path
import hashlib, json, shutil, subprocess, os
HERE=Path(__file__).resolve().parent
OUT=HERE/'pollen'
URL='https://github.com/pollen-robotics/grabette'
COMMIT='b5bacab06c19109b00acffefe38c3d3b3cb60bfc'
URDF='packages/grabette/urdf/grabette_right'
CACHE=Path.home()/'HelpingHands-tools/cache/grabette'
TOP=['LICENSE','NOTICE','THIRD_PARTY_NOTICES.md']


def git(*args,**kw):
    subprocess.run(['git','-C',str(CACHE),*args],check=True,**kw)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if not (CACHE/'.git').exists():
        CACHE.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['git','clone','--no-checkout',URL,str(CACHE)],check=True,env=dict(os.environ,GIT_LFS_SKIP_SMUDGE='1'))
    env=dict(os.environ,GIT_LFS_SKIP_SMUDGE='1')
    git('fetch','--quiet','origin',COMMIT,env=env)
    git('checkout','--quiet','--force',COMMIT,env=env)
    git('lfs','pull','--include',URDF+'/**')
    src=CACHE/URDF
    files={f'{URDF}/{p.relative_to(src)}':p for p in sorted(src.rglob('*')) if p.is_file() and p.name!='scene.xml'}
    files.update({name:CACHE/name for name in TOP})
    manifest=OUT/'SOURCE_MANIFEST.json'
    expected=json.loads(manifest.read_text())['files'] if manifest.exists() else None
    for name,p in files.items():
        assert not p.read_bytes().startswith(b'version https://git-lfs'),f'LFS pointer, not a mesh: {name}'
        dest=OUT/(name if name in TOP else Path(name).relative_to(URDF))
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    got={name:sha(p) for name,p in files.items()}
    if expected is not None and expected!=got:
        raise SystemExit('Upstream files differ from SOURCE_MANIFEST.json: '+', '.join(sorted(set(expected.items())^set(got.items()))))
    manifest.write_text(json.dumps(dict(source=URL,commit=COMMIT,folder=URDF,license='Apache-2.0, Copyright 2026 Pollen Robotics',
                                        files=got),indent=2)+'\n')
    print(f'{len(files)} files from {URL}@{COMMIT[:7]} -> {OUT.relative_to(HERE)}/')
if __name__=='__main__':main()
