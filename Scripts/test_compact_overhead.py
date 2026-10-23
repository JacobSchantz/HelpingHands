"""Direct-contact compact drive: published parts, incompatible picks and saved CAD evidence."""
from pathlib import Path
import json,subprocess,tempfile,unittest
from Scripts import publish_designs as pub
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'Two Finger Gripper/versions/v321_generalist_compact_overhead'
ID='two-finger-gripper-v321-generalist-compact-overhead'
class CompactOverheadTests(unittest.TestCase):
 def test_catalog_and_independent_motion_without_handles(self):
  row=next(r for r in pub.discover() if r['id']==ID)
  self.assertEqual(row['name'],'Base 20');self.assertEqual(row['builds_on'],'Base 18')
  self.assertEqual(row['fingers'],'25');self.assertFalse(row.get('carries'))
  with tempfile.TemporaryDirectory() as tmp:
   result=pub.publish_entry(row,Path(tmp),build=False)
   self.assertEqual(result['export_status'],'ready');self.assertEqual(len(result['models']),9)
   self.assertFalse(any('handle' in m['name'].lower() for m in result['models']))
   self.assertEqual((Path(tmp)/result['preview']).read_bytes(),(FOLDER/'previews/comparison.png').read_bytes())
   result.update(project='Generalist Gripper',fingers='25',no_handles=True)
   cat=dict(designs=[result,dict(id='mount-test',name='Mount 2',project='Generalist Gripper',models=[dict(name='Wrist hub',path='hub.stl')],fits={'Arm':'2'},tool_plate='1')])
   path=Path(tmp)/'catalog.json';path.write_text(json.dumps(cat))
   script="""
import fs from 'node:fs';
import {MIX,buildMix} from './cad/mobile_gallery/model.js';
import POSES from './cad/mobile_gallery/poses.js';
const catalog=JSON.parse(fs.readFileSync(process.argv[1]));
const state={[MIX.id]:{base:'20',gripper:'25',arm:'none',mount:'2',handles:'7'}};
const mix=buildMix(catalog,state,MIX),pose=POSES[mix.pose];
console.log(JSON.stringify({names:mix.models.map(m=>m.name),missing:mix.models.filter(m=>/^(Left|Right|Pinion|Stock aluminum)/.test(m.name)&&!pose.hinges.some(h=>new RegExp(h.match).test(m.name))).map(m=>m.name),flags:mix.rows.flatMap(r=>r.notes),handles:mix.rows.find(r=>r.key==='handles')}));
"""
   r=subprocess.run(['node','--input-type=module','-e',script,str(path)],cwd=ROOT,capture_output=True,text=True,check=True)
   data=json.loads(r.stdout);self.assertFalse(data['missing']);self.assertIsNone(data['handles']['chosen'])
   self.assertTrue(any('no wrist bracket' in f['text'] for f in data['flags']))
 def test_motion_and_minimal_stack_evidence(self):
  d=json.loads((FOLDER/'geometry_checks.json').read_text())
  self.assertTrue(d['motion_collisions']['passed']);self.assertEqual(d['motion_collisions']['angles'],121)
  self.assertTrue(d['tool_access']['passed']);self.assertFalse(d['tool_access']['straight_case_access_passed'])
  self.assertTrue(d['clearances']['passed']);self.assertAlmostEqual(d['clearances']['gear_to_band_gap_mm'],.8,places=5)
  self.assertLess(d['overall_envelope']['width_depth_height_mm'][1],54)
  self.assertTrue(all(m['passed'] for m in d['meshes']+d['fidelity']))
  for key in ['hardware_controls','lattice','gear_phase_control','fasteners']:self.assertTrue(d[key]['passed'],key)
if __name__=='__main__':unittest.main()
