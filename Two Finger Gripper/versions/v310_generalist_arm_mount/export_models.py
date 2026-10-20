#!/usr/bin/env python3
"""Export Base 10 (Base 9 on the reBot Arm B601-RS: a wrist hub on J6, a tool plate per tool, an L bracket from the motor's back face to the gripper's tool plate, and the Aero Hand's tool plate; the arm itself posed from Seeed's URDF by cad/arm/rebot_b601_rs/arm_pose.py). Base 9 (Base 8 with a top plate: three pillars on the base, a C-shaped ring round each pivot in a groove in its handle-gear). Base 8 (Base 7 with no separate Handle: each handle-gear is the handle, with two strap-loop slots). Base 7 (Base 4 made printable: Gripper 21's fingers; Handle 7's handle, strap tunnel and tail, each handle printed in one piece
with its side gear, every part one flat-bottomed extrusion; a centred pinion on the RobStride RS00 on 3 countersunk M3; the base plate on 3,
with a pivot post for each handle-gear): every piece its own STL (exports/print/: lying on the bed, z up), check the meshes, render
previews and the photo overlay. Writes params.scad and re-traces the outline from params.json first. No hardware operations."""
from pathlib import Path
from collections import Counter
import json, math, re, struct, subprocess
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
PHOTO=REPO/'cad/reference/generalist_gripper_gen6_two_hands.png'
PARTS=[('left','Left finger — Generalist yellow, mirror of the right','#efb83b',[-30,0,0]),
       ('right','Right finger — Generalist yellow','#efb83b',[30,0,0]),
       ('left_gear','Left handle-gear — black, the left handle: one print with its gear (both hooks, two strap-loop slots, tail fused into the hub), turns on the base’s left post','#26272b',[-30,-40,0]),   # "Left"/"Right" names swing with the finger (poses.js); "handle-gear" before ' — ' keeps it a Base part in the mix and drops the Handle picker (Base 8)
       ('right_gear','Right handle-gear — black, the right handle: one print with its gear (both hooks, two strap-loop slots, tail fused into the hub), driven by the pinion, turns on the right post','#26272b',[30,-40,0]),
       ('pinion','Pinion — black, centred, full-height teeth, 3 countersunk M3 to the motor flange','#26272b',[0,-40,-30]),
       ('base','Base — black flat plate with a pivot post for each handle-gear, 3 countersunk M3 to the motor','#26272b',[0,-65,0]),
       ('top_plate','Top plate — black, over the handle-gears and fingers on 3 pillars; a C-shaped ring round each pivot runs in its handle-gear’s groove, so each axle is held top and bottom','#26272b',[0,45,0]),
       ('bracket','Wrist bracket — black L: its leg bolts to the RS00’s back face (4 M3), its foot lies across the arm’s J6 axis and takes the tool plate; a zip-tie point for the motor’s cable','#26272b',[0,-30,-50]),
       ('tool_plate','Tool plate — the gripper’s side of the wrist interface (twin of Seeed’s Connector B): 4 M3 up into the bracket, slips over the hub, 3 radial M3','#3a3b40',[0,0,-80]),
       ('hub','Wrist hub — stays on the arm: bolted to J6’s RS00 output (twin of Seeed’s Connector A; Seeed’s aluminium one fits too)','#a3a8ad',[0,0,-110]),
       ('aero_plate','Aero Hand tool plate — the same tool plate plus an 8 mm spacer with a cable channel: 4 M3 straight into the Aero Hand’s wrist inserts','#3a3b40',[0,0,-40]),
       ('motor','Motor — RobStride RS00, reference only (not printed)','#a3a8ad',[0,-95,0])]
# Base 10: reference models drawn beside the parts, not printed or mesh-checked (k, name, colour, explode)
REFS=[('aero_hand','Aero Hand (left) — reference: its palm only (third_party/aero_hand, guide meshes), standing on its tool plate beside the arm','#d9dce1',[0,0,40])]
ARM_COLORS={'anodized_silver':'#b8c2ba','motor_black':'#2b2f2e','base_black':'#1d2120','pla_black':'#2f3533','seeed_green':'#b9d51e','wordmark_black':'#111311'}
VIEWS=[('top','angle=0','0,0,55,72,0,180,330'),        # dorsal (tilted 18 deg so pockets shade), closed: compare with the photos
       ('open','angle=15','0,0,55,72,0,180,380'),
       ('iso','angle=15','0,0,55,62,0,150,380'),
       ('finger','part="right"','-10,0,55,72,0,180,260'),
       ('edge','part="right"','0,0,55,90,0,90,260'),          # edge-on: thickness and the beak, like side.png
       ('jaw','part="right"','0,0,85,70,0,235,110'),          # the serrated inner face up close, like robot.png
       ('closed','angle=0','0,0,112,72,0,180,70'),          # the two points meeting, the gap opening behind them
       ('tip','angle=0','0,0,118,90,0,0,34'),           # plan view of the last ~14 mm, closed: point contact, V behind it
       ('hooks','part="right"','-9,0,34,80,0,180,185'),          # 1.20: plan view of the outer edge, the two hooks facing each other (2.6: framed out to the top step)
       ('handle_in','part="handle_in"','-9,0,34,80,0,180,185'),  # 2.5: the right handle seated, a foot in each notch
       ('handle_gear','part="handle_gear"','0,10,10,60,0,200,260'),   # Base 4: the finger above its handle-gear, the way it drops in
       ('fingers','part="fingers"','0,0,55,72,0,180,380'),    # the two fingers alone
       ('drive_iso','angle=15','0,-30,0,60,0,210,420'),     # 3.1-3.3: the whole thing from below-behind: gears, pinion, base, motor
       ('front','part="inplane"','0,0,10,270,180,0,330'),   # 3.3: from the dorsal side, square on, base and motor hidden: the gears in the finger plane, the centred pinion
       ('strap_zones','part="strap_zones"','0,-30,0,60,0,210,420'),   # 3.2/3.3: the strap keep-outs (red), nothing else inside them
       ('gears','part="gears"','0,0,-20,270,180,0,200'),       # 3.3: side gears and pinion, seen from the dorsal side
       ('drive','part="drive"','0,-40,0,60,0,150,400'),         # the drive without fingers or handles
       ('cradle','part="cradle"','0,0,5,60,0,200,160'),     # the right finger seated in its handle-gear
       ('gear','part="right_gear"','0,0,0,60,0,200,200'),   # Base 4: one handle-gear: plate, strap boss, tail, hub pocket, teeth, web, axle
       ('base_plate','part="base"','0,0,0,90,0,0,250'),        # the base plate from below: posts, motor ring
       ('top_plate','part="print_top_plate"','0,0,0,50,0,20,250'),   # Base 9: the top plate as it prints (underside up): the two C rings, the pillars, the pinion access hole
       ('top_ring','part="top_ring"','0,0,0,270,180,0,90'),   # Base 9: the right pivot from the dorsal side, plate hidden: the groove (handle-gear) and the ring (red) in it
       ('print_bed','part="print_bed"','0,0,0,50,0,20,500'),    # Base 7: the printed parts as they lie on the bed (Base 10: + the four mount parts)
       ('mount_side','part="assembly"','0,0,0,90,0,90,500'),         # Base 10: from +x: the L bracket on the motor's back face, the foot over the tool plate and hub
       ('mount_iso','part="assembly"','0,0,0,62,0,230,500'),         # Base 10: from below-behind: leg, gussets, cable tie slots, tool plate
       ('bracket','part="print_bracket"','0,0,0,55,0,140,300'),      # Base 10: the bracket as it prints, foot down
       ('tool_plate','part="print_tool_plate"','0,0,0,40,0,20,150'), # Base 10: the tool plate as it prints: socket up, head pockets, radial holes
       ('aero_plate','part="print_aero_plate"','0,0,0,140,0,20,150'),# Base 10: the Aero plate from below (its hand face): the cable channel
       ('hub','part="print_hub"','0,0,0,40,0,20,120'),               # Base 10: the hub: 6 J6 screws, scallops, radial pilots
       ('aero_station','part="aero_station"','0,0,0,70,0,220,400'),  # Base 10: the Aero Hand's palm on its tool plate
       ('arm_view','part="arm_view"','0,0,0,72,0,35,1600'),          # Base 10: the reBot Arm holding the gripper, the Aero Hand beside it
       ('arm_wrist','part="arm_view"','0,-20,-90,68,0,215,600')]     # Base 10: the wrist close up: J6, hub, tool plate, bracket
PREVIEW_ONLY={'aero_station','arm_view','arm_wrist'}   # Base 10: these draw Seeed's/Aero's open meshes, which --render would drop


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
    p=subprocess.run([SCAD,'--backend','manifold','--export-format','binstl',*[a for d in defs for a in ('-D',d)],'-o',str(out),str(HERE/'gripper.scad')],capture_output=True,text=True)
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
    o,h,dot,slots,pivot,angle,plate,tip_thick,taper_z,tip_z,taper_power,rail,slide,strap_slots=json.loads(line.split(' = ',1)[1])
    path.write_text(json.dumps(dict(outline=[[round(x,3),round(z,3)] for x,z in o],holes=h+[dot],slots=slots,pivot=pivot,
        angle=angle,plate=plate,tip_thick=tip_thick,taper_z=taper_z,tip_z=tip_z,taper_power=taper_power,rail=rail,slide=slide,strap_slots=strap_slots))+'\n')


def arm(logs):
    """Base 10: the reBot Arm B601-RS from Seeed's URDF, posed so that J6's output boss top lands on the hub's arm face
    (gripper.scad echoes it as arm_flange), one STL per material in exports/parts/arm_*.stl. Needs trimesh + numpy
    (cad/blender/.venv); without them the committed arm STLs are kept as they are."""
    import sys
    sys.path.insert(0,str(REPO/'cad/arm/rebot_b601_rs'))
    import params
    with __import__('tempfile').TemporaryDirectory() as tmp:
        p=subprocess.run([SCAD,'-D','part="viewer_right"','-o',str(Path(tmp)/'x.echo'),str(HERE/'gripper.scad')],capture_output=True,text=True)
        flange=json.loads(re.search(r'ECHO: arm_flange = (\[.*?\])',(Path(tmp)/'x.echo').read_text()).group(1))
    try:
        import arm_pose
        rows=arm_pose.export(HERE/'exports/parts',flange=flange,roll_deg=params.values()['arm_roll_deg'])
        logs.append(dict(out='exports/parts/arm_*.stl',passed=True,log=f'arm posed at flange {flange}'))
    except ImportError as e:
        logs.append(dict(out='exports/parts/arm_*.stl',passed=True,log=f'kept the committed arm STLs ({e})'))
    names=[]
    for f in sorted((HERE/'exports/parts').glob('arm_*.stl')):
        k=f.stem.removeprefix('arm_')
        names.append(dict(path=f'exports/parts/{f.name}',name=f'reBot Arm B601-RS ({k.replace("_"," ")}) — reference, Seeed’s URDF and meshes (CERN-OHL-W-2.0), stock gripper removed',
                          color=ARM_COLORS.get(k,'#888888'),explode=[0,0,-160]))
    return names


def main():
    import params, trace_photo
    params.write_scad();trace_photo.configure(params.values());trace_photo.main()   # 2.4: params.json -> params.scad, trace_px.scad (2.5: with 1.20's top hook)
    logs=[];meshes=[]
    concept_data(HERE/'web/concept.json')
    specs=[(HERE/'exports/assembly.stl','part="assembly"')]
    specs+=[(HERE/'exports/parts'/f'{k}.stl',f'part="viewer_{k}"') for k,*_ in PARTS]
    specs+=[(HERE/'exports/print'/f'{k}.stl',f'part="print_{k}"') for k,*_ in PARTS]   # Base 7: on the bed, z up
    specs+=[(HERE/'exports/parts'/f'{k}.stl',f'part="viewer_{k}"') for k,*_ in REFS]
    for out,define in specs:
        out.parent.mkdir(parents=True,exist_ok=True)
        r=scad(out,define);logs.append(r)
        if r['passed'] and not any(out.name==f'{k}.stl' for k,*_ in REFS):meshes.append(mesh_check(out))
    (HERE/'previews').mkdir(exist_ok=True)
    for name,define,camera in VIEWS:
        p=subprocess.run([SCAD,'--backend','manifold','-D',define,*([] if name in PREVIEW_ONLY else ['--render']),'--projection=o','--imgsize=1000,1200','--colorscheme=Tomorrow',
                          '--camera='+camera,*([] if name in ('closed','tip','hooks','handle_in','drive_iso','strap_zones','arm_wrist') else ['--viewall','--autocenter']),'-o',str(HERE/'previews'/f'{name}.png'),str(HERE/'gripper.scad')],capture_output=True,text=True)
        logs.append(dict(out=f'previews/{name}.png',passed=p.returncode==0,log=(p.stdout+p.stderr).strip()[-300:]))
    overlay(HERE/'previews/overlay.png');sheet(HERE/'previews/compare_target.png')
    parts=[dict(path=f'exports/parts/{k}.stl',name=n,color=c,explode=e) for k,n,c,e in PARTS+REFS]
    parts+=arm(logs)
    (HERE/'viewer_parts.json').write_text(json.dumps(dict(parts=parts),indent=2)+'\n')
    (HERE/'export_checks.json').write_text(json.dumps(logs,indent=2)+'\n')
    (HERE/'mesh_checks.json').write_text(json.dumps(meshes,indent=2)+'\n')
    for q in logs:
        if not q['passed']:print('FAIL:',q['out'],q['log'][-300:])
    for q in meshes:print(('PASS' if q['passed'] else 'FAIL')+f": {q['path']} / {q['components']} components / {q['triangles']} triangles")
    raise SystemExit(0 if all(q['passed'] for q in logs+meshes) else 1)
if __name__=='__main__':main()
