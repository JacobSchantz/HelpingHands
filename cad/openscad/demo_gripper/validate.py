#!/usr/bin/env python3
"""Geometry contracts; no app build and no hardware-performance claims."""
import concurrent.futures
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import zipfile
import numpy as np
from export import ROOT, SCAD, SOURCE

def triangles(data):
    n = struct.unpack_from('<I', data, 80)[0]
    assert len(data) == 84 + 50*n
    dtype = np.dtype([('normal','<f4',3),('v','<f4',(3,3)),('attr','<u2')])
    return np.frombuffer(data, dtype=dtype, offset=84)['v'].astype(float)

def mesh_contract(t):
    ids = {}
    edges = {}
    neighbors = [set() for _ in t]
    for face, tri in enumerate(t):
        vi = [ids.setdefault(tuple(v),len(ids)) for v in tri]
        assert len(set(vi)) == 3, 'degenerate face'
        for a,b in zip(vi,vi[1:]+vi[:1]):
            edges.setdefault(tuple(sorted((a,b))),[]).append((face,a<b))
    for connected in edges.values():
        assert len(connected)==2, 'not watertight'
        (a,da),(b,db)=connected
        assert da != db, 'inconsistent winding'
        neighbors[a].add(b); neighbors[b].add(a)
    reached={0}; pending=[0]
    while pending:
        for nxt in neighbors[pending.pop()]-reached:
            reached.add(nxt); pending.append(nxt)
    assert len(reached)==len(t), 'disconnected printed solids'
    volume = np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6
    assert volume>0, 'nonpositive volume'
    return volume

def collision(case):
    variant, angle, part, skew, expected_empty = case
    with tempfile.TemporaryDirectory(prefix='gripper-check-') as tmp:
        p=subprocess.run([SCAD,'--export-format','binstl','-o',tmp+'/clash.stl',
            '-D',f'variant="{variant}"','-D',f'angle={angle}',
            '-D',f'part="{part}"','-D',f'skew={skew}',str(SOURCE)],capture_output=True,text=True)
        output=p.stdout+p.stderr
        assert 'WARNING:' not in output and 'ERROR:' not in output, output
        empty='top level object is empty' in output
        assert empty or p.returncode==0, output
        assert empty==expected_empty, (case,output)
    return case

def main():
    parts=json.loads((ROOT/'export/parts.json').read_text())['parts']
    assert len(parts)==8 and len({p['file'] for p in parts})==8
    volumes={}
    for p in parts:
        volumes[p['file']]=round(mesh_contract(triangles((ROOT/'export'/p['file']).read_bytes()))/1000,2)
    with zipfile.ZipFile(ROOT/'jaws_print_ready.zip') as z:
        assert set(z.namelist())=={'a_left.stl','a_right.stl','b_left.stl','b_right.stl'}
        for name in z.namelist():
            t=triangles(z.read(name))
            mesh_contract(t)
            assert abs(t[:,:,2].min())<1e-5, (name,'not on bed')
            # At least half the X/Y footprint exists as real flat bed contact.
            base=t[np.all(abs(t[:,:,2])<1e-5,axis=1)]
            area=np.linalg.norm(np.cross(base[:,1]-base[:,0],base[:,2]-base[:,0]),axis=1).sum()/2
            assert area>300, (name,'insufficient bed contact',area)
    cases=[]
    for v in ['A','B']:
        for a in range(0,30,2):
            cases += [(v,a,'clash',0,True),(v,a,'gearclash',0,True)]
        for a in [0,14,29.5]:
            cases += [(v,a,'gearclash',3,False)] # engaged teeth, not vacuous clearance
        cases += [(v,31.5,'gearclash',0,False)] # mechanical stop
    cases += [('A',0,'insertclash',0,True),('A',0,'fitclash',0,True)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(collision,cases))
    repo=ROOT.parents[2]
    spec=importlib.util.spec_from_file_location('stage',repo/'Scripts/stage_cad_models.py')
    stage=importlib.util.module_from_spec(spec); spec.loader.exec_module(stage)
    assert str(ROOT) in stage.find_designs(str(repo/'cad'))
    key='openscad-demo_gripper'
    models=[{'id':f'{key}/{p["file"]}'} for p in parts]
    staged=stage.assembly_parts([str(ROOT/'export')],key,models)
    assert len(staged)==8
    assert stage.title(str(ROOT),str(repo))[0]=='Demo gripper · two jaw pairs, one interface'
    print(json.dumps({'watertight_single_solid_meshes':8,'bed_oriented_jaws':4,
        'collision_and_positive_control_cases':len(cases),'viewer_parts':len(staged),
        'solid_volume_cm3':volumes},indent=2))

if __name__=='__main__': main()
