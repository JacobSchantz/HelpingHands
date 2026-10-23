"""Whole WebXR skin screening for Base 23 using the SAME scene/contacts as review animation.
No product hand solver modifications. Vertex containment is sampled and cannot prove clearance.
"""
from pathlib import Path
import json,shutil,subprocess,tempfile,sys,hashlib,os
import numpy as np
import trimesh
from Scripts.check_finger_plane_constraints import ROOT,load

FOLDER=ROOT/os.environ.get('HAND_CASE_FOLDER','Two Finger Gripper/versions/v324_generalist_contact_close')
CASE_MODULE=os.environ.get('HAND_CASE_MODULE','contact_case.js')
def pose(m,k,angle,contract):
 import math
 p=contract['pivot'];ratio=contract['ratio']
 if k.startswith('right'):c=np.array([p,0,0]);r=1
 elif k.startswith('left'):c=np.array([-p,0,0]);r=-1
 elif k in ('pinion','stock_plate','plate_screws','center_screw'):c=np.array(contract['pinion']);r=-ratio
 else:return m
 a=math.radians((angle-15)*r);R=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
 out=m.copy();out.vertices=(out.vertices-c)@R.T+c;return out
OUT=ROOT/os.environ.get('HAND_CASE_OUT','cad/validation/voice-550038ca-contact')
SCRIPT=r'''
import fs from 'node:fs';import * as THREE from 'three';import {STLLoader} from 'three/addons/loaders/STLLoader.js';
const root=process.argv[1],folder=process.argv[2];
globalThis.readGlb = side => {const b=fs.readFileSync(root+'/cad/mobile_gallery/reference/human_hand/'+side+'.glb');return b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength);};
const {makeCase,CASE}=await import('./contact_case.js');
const manifest=JSON.parse(fs.readFileSync(folder+'/viewer_parts.json'));
const meshes=manifest.parts.map(p=>{const b=fs.readFileSync(folder+'/'+p.path);const m=new THREE.Mesh(new STLLoader().parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)));m.userData.name=p.name;return m;});
let cases=[];
for(const length of [181.1,193.3]){
 const study=await makeCase(meshes,{length,station:50}),frames=[];let wrist;
 for(let angle=0;angle<=30;angle+=2.5){
  const fit=study.solve(angle);if(wrist&&JSON.stringify(fit.wrist)!==JSON.stringify(wrist))throw Error('Wrist moved');wrist=fit.wrist;
  const vertices=[],faces=[];study.hand.traverse(n=>{if(n.isSkinnedMesh){const base=vertices.length,p=new THREE.Vector3();for(let i=0;i<n.geometry.attributes.position.count;i++){n.getVertexPosition(i,p).applyMatrix4(n.matrixWorld);vertices.push(p.toArray());}const index=n.geometry.index;for(let i=0;i<index.count;i+=3)faces.push([base+index.getX(i),base+index.getX(i+1),base+index.getX(i+2)]);}});
  frames.push({angle,fit,vertices,faces});
 }
 cases.push({length_mm:length,side:'right',joint_names:Object.keys(study.hand.userData.bones),frames});
}
console.log(JSON.stringify({contract:CASE,cases}));
'''
def sample():
 with tempfile.TemporaryDirectory() as tmp:
  work=Path(tmp);three=work/'node_modules/three';(three/'addons').mkdir(parents=True)
  vendor=ROOT/'cad/compare/vendor'
  for n in ('three.module.min.js','three.core.min.js'):shutil.copy2(vendor/n,three/n)
  for n in ('loaders','utils'):shutil.copytree(vendor/n,three/'addons'/n)
  shutil.copy2(vendor/'STLLoader.js',three/'addons/loaders/STLLoader.js')
  (three/'package.json').write_text(json.dumps({'type':'module','exports':{'.':'./three.module.min.js','./addons/*':'./addons/*'}}));(work/'package.json').write_text('{"type":"module"}')
  gallery=ROOT/'cad/mobile_gallery'
  source=(gallery/'human_hand.js').read_text().replace("loader.loadAsync('reference/human_hand/' + side + '.glb')","loader.parseAsync(globalThis.readGlb(side), '')")
  (work/'human_hand.js').write_text(source);shutil.copy2(gallery/'contact_case.js',work/'contact_case.js')
  shutil.copy2(gallery/CASE_MODULE,work/'selected_case.js')
  run=subprocess.run(['node','--input-type=module','-e',SCRIPT,str(ROOT),str(FOLDER)],cwd=work,capture_output=True,text=True,timeout=180)
  if run.returncode:raise RuntimeError(run.stderr)
  return json.loads(run.stdout)
def main():
 data=sample();meshes=load(FOLDER)
 for k in ('pivot_screws','pivot_washers','pivot_nuts','plate_screws','case_screws','center_screw'):meshes[k]=trimesh.load_mesh(FOLDER/f'exports/reference/{k}.stl')
 report=dict(assumptions=dict(source='Unmodified WebXR generic-hand mesh, MIT; existing human_hand.js outside fingerContacts + fixed-wrist local IK',hand_length_mm=[181.1,193.3],breadth='Uniform scaling retains narrow generic mesh (~78 mm at 187.2 mm length), not Jake measured hand',station_percent=50,pad_radius_mm=8,stroke_positions=13,max_contact_miss_budget_mm=2,collision='Complete deformed skin vertices inside actual closed CAD meshes, no body exclusions; surface sampling may miss edge crossings',qualification='Exploratory right-hand reference; no continuous clearance, skin pressure or physical ergonomic/strength certification'),cases=[])
 for case in data['cases']:
  samples=[]
  for frame in case['frames']:
   points=np.array(frame['vertices']);hits={}
   for k,m in meshes.items():
    obj=pose(m,k,frame['angle'],data['contract']);bounds=obj.bounds;inside=np.all((points>bounds[0]+1e-5)&(points<bounds[1]-1e-5),axis=1)
    if inside.any():
     count=int(obj.contains(points[inside]).sum())
     if count:hits[k]=count
   samples.append(dict(angle=frame['angle'],contact_miss_mm=frame['fit']['miss'],skin_vertices_inside_cad=hits,passed=frame['fit']['miss']<=2 and not hits))
  report['cases'].append(dict(length_mm=case['length_mm'],joint_names=case['joint_names'],samples=samples,passed=all(s['passed'] for s in samples)))
 report['assumptions']['contact_selection']='Actual working-band triangles only for inherited fingerContacts raycaster; full physical solids retained in all collision screening. Conservative full-part boxes affect IK cost, especially integral jaw/gears.'
 report['input_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in list((FOLDER/'exports/parts').glob('*.stl'))+[FOLDER/f'exports/reference/{k}.stl' for k in ('pivot_screws','pivot_washers','pivot_nuts','plate_screws','case_screws','center_screw')]+[ROOT/'cad/mobile_gallery/human_hand.js',ROOT/'cad/mobile_gallery/contact_case.js',ROOT/('cad/mobile_gallery/'+CASE_MODULE),ROOT/'cad/mobile_gallery/reference/human_hand/right.glb']}
 report['passed']=all(c['passed'] for c in report['cases']);OUT.mkdir(parents=True,exist_ok=True)
 (OUT/'whole-hand.json').write_text(json.dumps(report,indent=2)+'\n')
 # Store actual skinned surfaces for the three review frames, independently of browser rendering.
 for case in data['cases']:case['frames']=[f for f in case['frames'] if f['angle'] in (0,15,30)]
 (OUT/'hand-frames.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
 print(json.dumps({**{k:v for k,v in report.items() if k not in ('cases','assumptions')},'cases':[dict(length_mm=c['length_mm'],worst_miss_mm=max(s['contact_miss_mm'] for s in c['samples']),collision_poses=sum(bool(s['skin_vertices_inside_cad']) for s in c['samples']),passed=c['passed']) for c in report['cases']]},indent=2))
 return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
