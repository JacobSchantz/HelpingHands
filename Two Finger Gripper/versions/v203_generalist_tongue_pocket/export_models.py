#!/usr/bin/env python3
"""Export version 2.3 (2.2's handles, no lug: a tongue slides down into a pocket in each finger): two yellow fingers and two black handles, each its own STL, check the meshes,
render previews and the photo overlay. No hardware operations."""
from pathlib import Path
from collections import Counter
import json, math, re, struct, subprocess
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
PHOTO=REPO/'cad/reference/generalist_gripper_gen6_two_hands.png'
PARTS=[('left','Left finger — Generalist yellow, mirror of the right','#efb83b',[-30,0,0]),
       ('right','Right finger — Generalist yellow','#efb83b',[30,0,0]),
       ('left_slide','Left handle — black, tongue + two loop slots','#26272b',[-60,0,-20]),
       ('right_slide','Right handle — black, tongue + two loop slots','#26272b',[60,0,-20])]
VIEWS=[('top','angle=0','0,0,55,72,0,180,330'),        # dorsal (tilted 18 deg so pockets shade), closed: compare with the photos
       ('open','angle=15','0,0,55,72,0,180,380'),
       ('iso','angle=15','0,0,55,62,0,150,380'),
       ('finger','part="right"','-10,0,55,72,0,180,260'),
       ('edge','part="right"','0,0,55,90,0,90,260'),          # edge-on: thickness and the beak, like side.png
       ('jaw','part="right"','0,0,85,70,0,235,110'),          # the serrated inner face up close, like robot.png
       ('closed','angle=0','0,0,112,72,0,180,70'),          # the two points meeting, the gap opening behind them
       ('tip','angle=0','0,0,118,90,0,0,34'),           # plan view of the last ~14 mm, closed: point contact, V behind it
       ('slide','part="right_slide"','0,0,0,72,0,200,200'),   # Gen 17: the strap slide alone, its dovetail tongue and two slots
       ('slide_fit','angle=0','42,0,32,62,0,235,150'),         # Gen 17: the right slide in its lug, from the open tip end
       ('pocket','part="right"','70,45,25,-4,0,6'),          # 2.3: the keyhole pocket in the outer edge, up from the base hook
       ('handle_in','part="handle_in"','110,70,25,-3,0,8'),     # 2.3: the right handle seated, its foot behind the hook
       ('fingers','part="fingers"','0,0,55,72,0,180,380'),    # Gen 17: the two fingers alone
       ('slides','part="slides"','0,0,55,72,0,180,380')]      # Gen 17: the two slides alone, where they sit


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


def scad(out,*defs):
    p=subprocess.run([SCAD,'--export-format','binstl',*[a for d in defs for a in ('-D',d)],'-o',str(out),str(HERE/'gripper.scad')],capture_output=True,text=True)
    log=(p.stdout+p.stderr).strip()
    return dict(out=str(out.relative_to(HERE)),passed=p.returncode==0 and out.exists() and 'WARNING' not in log,log=log)


def overlay(path):
    """The traced outline, holes and slots drawn back on the source photo."""
    from PIL import Image, ImageDraw
    src=(HERE/'trace_px.scad').read_text()
    def points(name):
        body=re.search(name+r'=\[(.*?)\];',src,re.S).group(1)
        return [tuple(map(float,m.split(','))) for m in re.findall(r'\[([-\d., ]+)\]',body)]
    k=2;box=(290,300,880,640);X=lambda x:(x-box[0])*k;Y=lambda y:(y-box[1])*k
    img=Image.open(PHOTO).convert('RGB').crop(box);img=img.resize((img.width*k,img.height*k));d=ImageDraw.Draw(img)
    line=[(X(p[0]),Y(p[1])) for p in points('outline_px')]
    d.line(line+line[:1],fill=(0,230,255),width=3)
    for x,y,dia,*_ in points('holes_px')+points('dot_px'):
        r=max(1.8/0.2,dia)/2*k;d.ellipse([X(x)-r,Y(y)-r,X(x)+r,Y(y)+r],outline=(255,0,255),width=2)
    for x,y in points('slots_px'):d.ellipse([X(x)-4,Y(y)-4,X(x)+4,Y(y)+4],outline=(0,255,0),width=2)
    img.save(path)


def sheet(path):
    """Photo beside the closed model, same scale feel, for the reviewer."""
    from PIL import Image
    tiles=[Image.open(p).convert('RGB') for p in (REPO/'cad/reference/generalist_gripper_gen6_two_hands.png',
           HERE/'previews/overlay.png',HERE/'previews/top.png',HERE/'previews/iso.png')]
    h=520;tiles=[t.resize((round(t.width*h/t.height),h)) for t in tiles]
    out=Image.new('RGB',(sum(t.width for t in tiles)+10*(len(tiles)-1),h),'white');x=0
    for t in tiles:out.paste(t,(x,0));x+=t.width+10
    out.save(path)


def concept_data(path):
    """The plan outline, holes and taper numbers for web/concept.js, echoed by gripper.scad part="concept"."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        echo=Path(tmp)/'concept.echo'
        subprocess.run([SCAD,'-D','part="concept"','-o',str(echo),str(HERE/'gripper.scad')],capture_output=True)
        line=next(l for l in echo.read_text().splitlines() if l.startswith('ECHO: concept = '))
    o,h,dot,slots,pivot,angle,plate,rail,tongue,slide,strap_slots=json.loads(line.split(' = ',1)[1])
    path.write_text(json.dumps(dict(outline=[[round(x,3),round(z,3)] for x,z in o],holes=h+[dot],slots=slots,pivot=pivot,
        angle=angle,plate=plate,rail=rail,tongue=tongue,slide=slide,strap_slots=strap_slots))+'\n')


def main():
    logs=[];meshes=[]
    concept_data(HERE/'web/concept.json')
    specs=[(HERE/'exports/assembly.stl','part="assembly"')]
    specs+=[(HERE/'exports/parts'/f'{k}.stl',f'part="viewer_{k}"') for k,*_ in PARTS]
    specs+=[(HERE/'exports/print'/f'{k}.stl',f'part="{k}"') for k,*_ in PARTS]
    for out,define in specs:
        out.parent.mkdir(parents=True,exist_ok=True)
        r=scad(out,define);logs.append(r)
        if r['passed']:meshes.append(mesh_check(out))
    (HERE/'previews').mkdir(exist_ok=True)
    for name,define,camera in VIEWS:
        p=subprocess.run([SCAD,'-D',define,'--render','--projection=o','--imgsize=1000,1200','--colorscheme=Tomorrow',
                          '--camera='+camera,*([] if name in ('closed','tip','slide_fit','pocket','handle_in') else ['--viewall','--autocenter']),'-o',str(HERE/'previews'/f'{name}.png'),str(HERE/'gripper.scad')],capture_output=True,text=True)
        logs.append(dict(out=f'previews/{name}.png',passed=p.returncode==0,log=(p.stdout+p.stderr).strip()[-300:]))
    overlay(HERE/'previews/overlay.png');sheet(HERE/'previews/compare_target.png')
    parts=[dict(path=f'exports/parts/{k}.stl',name=n,color=c,explode=e) for k,n,c,e in PARTS]
    (HERE/'viewer_parts.json').write_text(json.dumps(dict(parts=parts),indent=2)+'\n')
    (HERE/'export_checks.json').write_text(json.dumps(logs,indent=2)+'\n')
    (HERE/'mesh_checks.json').write_text(json.dumps(meshes,indent=2)+'\n')
    for q in logs:
        if not q['passed']:print('FAIL:',q['out'],q['log'][-300:])
    for q in meshes:print(('PASS' if q['passed'] else 'FAIL')+f": {q['path']} / {q['components']} components / {q['triangles']} triangles")
    raise SystemExit(0 if all(q['passed'] for q in logs+meshes) else 1)
if __name__=='__main__':main()
