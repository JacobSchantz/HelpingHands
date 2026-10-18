#!/usr/bin/env python3
"""Fetch Pollen Robotics' Grabette and Gripette (right hand) URDFs and meshes, unchanged.

Grabette goes into pollen/, Gripette into pollen/gripette/. Pinned to one upstream
commit. The meshes live in Git LFS, so this clones without them and then runs
`git lfs pull` for the two URDF folders we use. The URDF, licence
files and SOURCE_MANIFEST.json are committed here; the STLs are not (the repo ignores
*.stl), and this script brings them back byte-for-byte, checked against the manifest."""
from pathlib import Path
import hashlib, json, shutil, subprocess, os
HERE=Path(__file__).resolve().parent
OUT=HERE/'pollen'
URL='https://github.com/pollen-robotics/grabette'
COMMIT='b5bacab06c19109b00acffefe38c3d3b3cb60bfc'
# upstream URDF folder -> local folder under pollen/
URDFS={'packages/grabette/urdf/grabette_right':'.','packages/gripette/urdf/gripette_right':'gripette'}
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
    git('lfs','pull','--include',','.join(u+'/**' for u in URDFS))
    files,dests={},{name:OUT/name for name in TOP}
    for urdf,local in URDFS.items():
        for p in sorted((CACHE/urdf).rglob('*')):
            if p.is_file() and p.name!='scene.xml':
                name=f'{urdf}/{p.relative_to(CACHE/urdf)}';files[name]=p;dests[name]=OUT/local/p.relative_to(CACHE/urdf)
    files.update({name:CACHE/name for name in TOP})
    manifest=OUT/'SOURCE_MANIFEST.json'
    expected=json.loads(manifest.read_text())['files'] if manifest.exists() else None
    for name,p in files.items():
        assert not p.read_bytes().startswith(b'version https://git-lfs'),f'LFS pointer, not a mesh: {name}'
        dest=dests[name]
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    got={name:sha(p) for name,p in files.items()}
    changed=sorted(k for k,v in (expected or {}).items() if got.get(k)!=v)
    if changed:raise SystemExit('Upstream files differ from SOURCE_MANIFEST.json: '+', '.join(changed))
    manifest.write_text(json.dumps(dict(source=URL,commit=COMMIT,folders=URDFS,license='Apache-2.0, Copyright 2026 Pollen Robotics',
                                        files=got),indent=2)+'\n')
    print(f'{len(files)} files from {URL}@{COMMIT[:7]} -> {OUT.relative_to(HERE)}/')
if __name__=='__main__':main()
