"""Sample the actual large/compact/Aero-servo/overhead CAD with one fixed human wrist.
No CAD generation, build, publishing or load/comfort certification. Writes a reviewable report.
"""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import argparse

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / 'cad/mobile_gallery'
FOLDERS = ['v311_generalist_motor_choice', 'v312_generalist_compact_drive',
           'v319_generalist_hls3606m', 'v320_generalist_overhead_drive', 'v322_generalist_two_pivot_support']
SCRIPT = r'''
import fs from 'node:fs';
import * as THREE from 'three';
import {STLLoader} from 'three/addons/loaders/STLLoader.js';
import POSES from './poses.js';
globalThis.readGlb = side => {const b = fs.readFileSync(process.argv[1]+'/cad/mobile_gallery/reference/human_hand/'+side+'.glb'); return b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength);};
const {makeHand,sizeHand,gripHand,fingerContacts} = await import('./human_hand.js');
const {makeCase,CASE} = await import('./two_pivot_case.js');
const folders = JSON.parse(process.argv[2]), output = [];
for (const folder of folders) {
  const path=process.argv[1]+'/Two Finger Gripper/versions/'+folder;
  const parts=JSON.parse(fs.readFileSync(path+'/viewer_parts.json')).parts;
  const id='two-finger-gripper-'+folder.replaceAll('_','-'), pose=POSES[id];
  const meshes=parts.filter(p=>!p.name.match(/arm/i)).map(p=>{
    const b=fs.readFileSync(path+'/'+p.path), g=new STLLoader().parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));
    const m=new THREE.Mesh(g);m.userData.name=p.name;return m;
  });
  for (const side of ['right','left']) for (const length of [181.1,193.3]) {
    const hand=await makeHand(side);sizeHand(hand,length);
    const row={folder,side,length_mm:length,samples:[]}; output.push(row);
    const study=id===CASE.id ? await makeCase(meshes,{side,length}) : null;
    let wrist;
    for(let i=0;i<=12;i++) {
      const angle=pose.min+(pose.max-pose.min)*i/12;
      for(const m of meshes) {
        const h=pose.hinges.find(h=>new RegExp(h.match).test(m.userData.name));
        if(h) {m.rotation.y=THREE.MathUtils.degToRad(h.sign*(angle-pose.exported));const p=new THREE.Vector3(...h.pivot);m.position.copy(p).sub(p.clone().applyEuler(m.rotation));}
        m.updateMatrixWorld(true);
      }
      const [a,b]=fingerContacts(meshes,side,50)||[];
      if(!a||!b) {row.samples.push({angle,error:'No outer finger surface at 50% station'});continue;}
      const solids=meshes.filter(m=>!/arm/i.test(m.userData.name)).map(m=>new THREE.Box3().setFromObject(m));
      if(!study) gripHand(hand,a,b,solids,{indexOnly:true,lockWrist:true,radius:8,freeCurl:.8-.6*i/12});
      const fit=study ? study.solve(angle) : hand.userData.fit;
      const now=study ? fit.wrist : hand.userData.grip.slice(0,6);
      if(wrist&&JSON.stringify(wrist)!==JSON.stringify(now))throw Error('Wrist moved');
      wrist=now;
      if(![fit.miss,fit.penetration,fit.span].every(Number.isFinite))throw Error('Nonfinite diagnostic');
      row.samples.push({angle,...fit});
    }
  }
}
console.log(JSON.stringify({assumptions:{contact_surface:'outer finger; no handle or strap',sides:['right','left'],free_digit_curl:{open:.2,closed:.8},radius_mm:8,station_percent:50,positions:13,wrist:'fixed from first available contact',collision:'All posed skin triangles against conservative world tool boxes; joint spheres guide IK. No solid containment or pressure model',qualification:'Exploratory local IK only; missing contacts and box overlap require investigation, not comfort claims'},designs:output},null,2));
'''


def check():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        three = root / 'node_modules/three'
        (three / 'addons').mkdir(parents=True)
        vendor = ROOT / 'cad/compare/vendor'
        for name in ('three.module.min.js', 'three.core.min.js'):
            shutil.copy2(vendor / name, three / name)
        for name in ('loaders', 'utils'):
            shutil.copytree(vendor / name, three / 'addons' / name)
        (three / 'package.json').write_text(json.dumps({'type':'module','exports':{'.':'./three.module.min.js','./addons/*':'./addons/*'}}))
        shutil.copy2(vendor / 'STLLoader.js', three / 'addons/loaders/STLLoader.js')
        (root / 'package.json').write_text('{"type":"module"}')
        source = (GALLERY / 'human_hand.js').read_text().replace("loader.loadAsync('reference/human_hand/' + side + '.glb')", "loader.parseAsync(globalThis.readGlb(side), '')")
        (root / 'human_hand.js').write_text(source)
        shutil.copy2(GALLERY / 'poses.js', root / 'poses.js')
        shutil.copy2(GALLERY / 'two_pivot_case.js', root / 'two_pivot_case.js')
        run = subprocess.run(['node','--input-type=module','-e',SCRIPT,str(ROOT),json.dumps(FOLDERS)],cwd=root,capture_output=True,text=True,check=True,timeout=120)
        return json.loads(run.stdout)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = check()
    if args.output:
        args.output.write_text(json.dumps(report,indent=2)+'\n')
    for row in report['designs']:
        available=[s for s in row['samples'] if 'miss' in s]
        print(row['folder'],row['side'],row['length_mm'],f"{len(available)}/13 contacts",f"worst miss {max(s['miss'] for s in available):.1f} mm; box overlap {max(s['penetration'] for s in available):.1f} mm" if available else 'contact station unavailable')
