#!/usr/bin/env python3
"""Export Generation 15: every part placed (for the gallery, at the .scad's default angle) and every printed part in
its print orientation, check the meshes, render previews, write viewer_parts.json. No hardware operations."""
from pathlib import Path
from collections import Counter
import json, struct, subprocess
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
Y='#efb83b';D='#46464c';P='#2a2a2c';C='#26262a';S='#5a4632'
# gallery parts: (scad name, gallery name, colour, explode). Names starting Right/Left swing with that finger (poses.js).
PARTS=[('right_finger','Right finger (thumb side) — Gen 14 yellow',Y,[25,0,25]),
       ('left_finger','Left finger (index side) — Gen 14 yellow, mirrored',Y,[-25,0,25]),
       ('right_pad','Right tip pad — dark (prints merged unless two-material)',P,[30,0,45]),
       ('left_pad','Left tip pad — dark (prints merged unless two-material)',P,[-30,0,45]),
       ('right_carrier','Right carrier — rides on the thumb, holds the pivot nut',D,[25,25,0]),
       ('left_carrier','Left carrier — rides on the index finger, holds the pivot nut',D,[-25,25,0]),
       ('right_strap','Right thumb strap — 20 mm hook-and-loop or zip tie, not printed',S,[25,-15,0]),
       ('left_strap','Left index strap — 20 mm hook-and-loop or zip tie, not printed',S,[-25,-15,0]),
       ('pivot_plate','Pivot plate — both pivots, M4 bolts',D,[0,45,0]),
       ('hand_frame','Hand frame — back of the hand, wrist-strap slots',D,[0,75,-20]),
       ('camera_mount','Camera mount — Insta360 X4/X5 cradle, 1/4"-20 screw',D,[0,105,-20]),
       ('camera','Camera — Insta360 X4 size, lenses forward/back, not printed',C,[0,150,-20]),
       ('wrist_strap','Wrist strap — 25 mm hook-and-loop, not printed',S,[0,40,-40])]
PRINT=['right_finger','left_finger','right_carrier','left_carrier','pivot_plate','hand_frame','camera_mount']
TWO_MATERIAL=['right_finger_body','left_finger_body','right_pad','left_pad']
VIEWS=[('top','0,0,0,90,0,180,500'),('side','0,0,0,90,0,90,500'),('front','0,0,0,0,0,180,500'),('iso','0,0,0,60,0,145,500')]   # framed with --viewall


def mesh_check(path):
    raw=path.read_bytes();n=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+n*50, f'Not binary STL: {path}'
    ids={};parent=[];edges=Counter();directed=Counter();volume=0;bounds=[]
    def vid(v):
        if v not in ids:ids[v]=len(ids);parent.append(len(parent));bounds.append(v)
        return ids[v]
    def root(a):
        while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
        return a
    for i in range(n):
        q=struct.unpack_from('<12fH',raw,84+i*50);a,b,c=[tuple(q[j:j+3]) for j in (3,6,9)]
        ix=[vid(v) for v in (a,b,c)]
        for k in (1,2):parent[root(ix[k])]=root(ix[0])
        for u,v in zip(ix,ix[1:]+ix[:1]):edges[tuple(sorted((u,v)))]+=1;directed[(u,v)]+=1
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    components=len({root(i) for i in range(len(parent))})
    watertight=all(v==2 for v in edges.values());winding=all(directed[(v,u)]==count for (u,v),count in directed.items())
    return dict(path=str(path.relative_to(HERE)),triangles=n,components=components,watertight=watertight,
      consistent_winding=winding,signed_volume_mm3=volume,
      bounds_mm=[[min(v[k] for v in bounds) for k in range(3)],[max(v[k] for v in bounds) for k in range(3)]],
      passed=watertight and winding and volume>0 and (components==1 or path.name=='assembly.stl'))


def scad(out,define):
    p=subprocess.run([SCAD,'--export-format','binstl','-D',define,'-o',str(out),str(HERE/'gripper.scad')],capture_output=True,text=True)
    log=(p.stdout+p.stderr).strip()
    return dict(out=str(out.relative_to(HERE)),passed=p.returncode==0 and out.exists() and 'WARNING' not in log,log=log[-300:])


def render(name,camera,*defines,whole=True):
    out=HERE/'previews'/f'{name}.png'
    p=subprocess.run([SCAD,*[a for d in defines for a in ('-D',d)],*(['--viewall','--autocenter'] if whole else []),'--render','--projection=o','--imgsize=1000,1000','--colorscheme=Tomorrow',
                      '--camera='+camera,'-o',str(out),str(HERE/'gripper.scad')],capture_output=True,text=True)
    return dict(out=f'previews/{name}.png',passed=p.returncode==0,log=(p.stdout+p.stderr).strip()[-300:])


def main():
    jobs=[(HERE/'exports/assembly.stl','part="assembly"')]
    jobs+=[(HERE/'exports/parts'/f'{k}.stl',f'part="viewer_{k}"') for k,*_ in PARTS]
    jobs+=[(HERE/'exports/print'/f'{k}.stl',f'part="print_{k}"') for k in PRINT]
    jobs+=[(HERE/'exports/print/two_material'/f'{k}.stl',f'part="print_{k}"') for k in TWO_MATERIAL]
    for out,_ in jobs:out.parent.mkdir(parents=True,exist_ok=True)
    (HERE/'previews').mkdir(exist_ok=True)
    with ThreadPoolExecutor(6) as ex:
        logs=list(ex.map(lambda j:scad(*j),jobs))
        logs+=list(ex.map(lambda v:render(*v),VIEWS[:4]))
    logs.append(render('open','0,0,-10,90,0,180,330','angle=30',whole=False))     # top, both fingers fully open
    logs.append(render('closed','0,0,-10,90,0,180,330','angle=0',whole=False))
    for k in PRINT:logs.append(render(f'print_{k}','0,0,0,55,0,25,500',f'part="print_{k}"'))   # as it sits on the bed
    meshes=[mesh_check(out) for (out,_),r in zip(jobs,logs) if r['passed'] and out.name!='assembly.stl']   # the assembly is 3 bodies (washers not modelled) with touching faces: preview only
    printed=[m for m in meshes if '/print/' in m['path']]
    for m in printed:   # print orientation: sits on the bed (a 7 mm3 pad: the slicer drops it), fits a 220 mm bed
        lo,hi=m['bounds_mm'];m['on_bed']=abs(lo[2])<1e-3 or '_pad' in m['path'];m['fits_220_bed']=max(hi[0]-lo[0],hi[1]-lo[1])<=220
        m['passed']=m['passed'] and m['on_bed'] and m['fits_220_bed']
    parts=[dict(path=f'exports/parts/{k}.stl',name=n,color=c,explode=e) for k,n,c,e in PARTS]
    (HERE/'viewer_parts.json').write_text(json.dumps(dict(parts=parts),indent=2,ensure_ascii=False)+'\n')
    (HERE/'export_checks.json').write_text(json.dumps(logs,indent=2)+'\n')
    (HERE/'mesh_checks.json').write_text(json.dumps(meshes,indent=2)+'\n')
    for q in logs:
        if not q['passed']:print('FAIL:',q['out'],q['log'][-300:])
    for q in meshes:print(('PASS' if q['passed'] else 'FAIL')+f": {q['path']} / {q['components']} body / {round(q['signed_volume_mm3'])} mm3")
    raise SystemExit(0 if all(q['passed'] for q in logs+meshes) else 1)
if __name__=='__main__':main()
