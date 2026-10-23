"""Base 19's published mixed assembly preserves its unchanged interfaces and motion."""
from pathlib import Path
import json,subprocess,tempfile,unittest
from Scripts import publish_designs as pub
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'Two Finger Gripper/versions/v320_generalist_overhead_drive'
ID='two-finger-gripper-v320-generalist-overhead-drive'
class OverheadTests(unittest.TestCase):
 def test_catalog_lineage_and_side_comparison(self):
  row=next(r for r in pub.discover() if r['id']==ID)
  self.assertEqual(row['name'],'Base 19');self.assertEqual(row['builds_on'],'Base 15')
  self.assertEqual(row['fingers'],'22');self.assertEqual(row['carries'],{'Arm':'2','Mount':'2'})
  with tempfile.TemporaryDirectory() as tmp:
   result=pub.publish_entry(row,Path(tmp),build=False)
   self.assertEqual(result['export_status'],'ready')
   self.assertEqual((Path(tmp)/result['preview']).read_bytes(),(FOLDER/'previews/side_comparison.png').read_bytes())
   self.assertGreater(len(result['models']),14)
   with patch.object(pub,'run_scad',side_effect=AssertionError('Declared geometry/preview must not rerender')):
    normal=pub.publish_entry(row,Path(tmp),build=True)
   self.assertEqual(normal['preview'],result['preview'])
 def test_mixed_assembly_keeps_drivers_and_pinions_moving(self):
  cat=Path.home()/'HelpingHands-tools/design-gallery/catalog.json'
  script="""
import fs from 'node:fs';
import {MIX,buildMix} from './cad/mobile_gallery/model.js';
import POSES from './cad/mobile_gallery/poses.js';
const catalog=JSON.parse(fs.readFileSync(process.argv[1]));
const state={[MIX.id]:{base:'19',gripper:'22',arm:'2',mount:'2',handles:'none'}};
const mix=buildMix(catalog,state,MIX);
const pose=POSES[mix.pose];
const moving=mix.models.filter(m=>/^(Left|Right|Pinion)/.test(m.name));
console.log(JSON.stringify({name:mix.name,missing:moving.filter(m=>!pose.hinges.some(h=>new RegExp(h.match).test(m.name))).map(m=>m.name),names:mix.models.map(m=>m.name),notes:mix.rows.flatMap(r=>r.notes)}));
"""
  r=subprocess.run(['node','--input-type=module','-e',script,str(cat)],cwd=ROOT,capture_output=True,text=True,check=True)
  out=json.loads(r.stdout);self.assertIn('Base 19',out['name']);self.assertFalse(out['missing']);self.assertFalse(out['notes'])
  for name in ['Left_Driver','Right_Driver','Left Washer','Right Washer']:
   self.assertTrue(any(n.startswith(name) for n in out['names']),name)
 def test_saved_motion_certificate(self):
  d=json.loads((FOLDER/'geometry_checks.json').read_text())
  self.assertTrue(d['collisions']['passed']);self.assertEqual(d['collisions']['angles'],121)
  self.assertEqual(d['finger_band_y_mm'],[-6,6]);self.assertGreaterEqual(min(d['overhead_gap_mm'].values()),7.999)
  self.assertTrue(d['phase_positive_control']['passed'])
if __name__=='__main__':unittest.main()
