#!/usr/bin/env python3
"""Re-export original CAD; inspect binary STL topology. No hardware operations. Generation 6."""
from pathlib import Path
from collections import Counter
import json, math, struct, subprocess
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
PARTS=[
 ('housing_base','Dorsal housing base — sits on the back of the hand','#2b313a',[0,25,-25]),
 ('housing_lid','Dorsal housing lid — holds the left axle, passes the servo drive','#3a424d',[0,50,-25]),
 ('left','Left finger — perforated crescent plate, mirror of the right','#efb83b',[-45,0,10]),
 ('right','Right finger — perforated crescent plate','#efb83b',[45,0,10]),
 ('left_gear','Left gear — half-tooth index','#8f969e',[-30,45,0]),
 ('right_gear','Right gear — servo driven','#8f969e',[30,45,0]),
 ('left_tip','Left black TPU tip','#15181c',[-55,0,40]),
 ('right_tip','Right black TPU tip','#15181c',[55,0,40]),
 ('motor','ONE servo envelope — unselected','#252e38',[0,70,-10])]


def mesh_check(path):
    raw=path.read_bytes();n=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+n*50, f'Not binary STL: {path}'
    ids={};parent=[];edges=Counter();directed=Counter();volume=0;area_min=float('inf');bounds=[]
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
        cross=((b[1]-a[1])*(c[2]-a[2])-(b[2]-a[2])*(c[1]-a[1]),(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]),(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
        area_min=min(area_min,math.sqrt(sum(v*v for v in cross))/2)
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    components=len({root(i) for i in range(len(parent))})
    watertight=all(v==2 for v in edges.values());winding=all(directed[(v,u)]==count for (u,v),count in directed.items())
    return dict(path=str(path.relative_to(HERE)),triangles=n,components=components,watertight=watertight,
      consistent_winding=winding,signed_volume_mm3=volume,min_triangle_area_mm2=area_min,
      bounds_mm=[[min(v[k] for v in bounds) for k in range(3)],[max(v[k] for v in bounds) for k in range(3)]],
      passed=watertight and winding and volume>0 and (components==1 or path.name=='assembly.stl'))

def main():
    logs=[];meshes=[];parts=[]
    specs=[('assembly',HERE/'exports/assembly.stl')]+[('viewer_'+p[0],HERE/'exports/parts'/f'{p[0]}.stl') for p in PARTS]+[(k,HERE/'exports/print'/f'{k}.stl') for k in ('left','right','left_gear','right_gear','left_tip','right_tip','housing_base','housing_lid')]
    for mode,path in specs:
        path.parent.mkdir(parents=True,exist_ok=True)
        p=subprocess.run([SCAD,'--export-format','binstl','-D',f'part="{mode}"','-o',str(path),str(HERE/'gripper.scad')],capture_output=True,text=True)
        log=p.stdout+p.stderr;ok=p.returncode==0 and 'NoError' in log and path.exists()
        logs.append(dict(part=mode,passed=ok,log=log.strip()))
        if ok:meshes.append(mesh_check(path))
    for key,name,color,explode in PARTS:parts.append(dict(path=f'exports/parts/{key}.stl',name=name,color=color,explode=explode))
    (HERE/'viewer_parts.json').write_text(json.dumps(dict(parts=parts),indent=2)+'\n')
    (HERE/'export_checks.json').write_text(json.dumps(logs,indent=2)+'\n')
    (HERE/'mesh_checks.json').write_text(json.dumps(meshes,indent=2)+'\n')
    for q in meshes:print(('PASS' if q['passed'] else 'FAIL')+f": {q['path']} / {q['components']} connected components / {q['triangles']} triangles")
    raise SystemExit(0 if all(q['passed'] for q in logs+meshes) else 1)
if __name__=='__main__':main()
