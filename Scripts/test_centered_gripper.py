"""Tests-first contract for voice-550038ca's centered compact revision.
Run this against Base 21 first: it must fail centered axis, part count and spacing.
"""
import json, os, unittest, hashlib, tempfile, subprocess, sys
from pathlib import Path
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'Two Finger Gripper/versions/v323_generalist_centered_drive'
class CenteredRevision(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.folder=Path(os.environ.get('GRIPPER_CONTRACT_FOLDER',DEFAULT))
  cls.v={p['name']:p['value'] for g in json.loads((cls.folder/'params.json').read_text())['groups'] for p in g['params']}
 def test_report_matches_actual_source_and_meshes(self):
  r=json.loads((self.folder/'geometry_checks.json').read_text())
  for path,want in r['input_sha256'].items():
   self.assertEqual(hashlib.sha256((self.folder/path).read_bytes()).hexdigest(),want,path)
  self.assertTrue(r['wrong_phase_control']['passed'])
  self.assertEqual(len(r['wrong_phase_control']['controls']),3)
 def test_motor_output_axis_on_symmetry_plane(self):
  v=self.v;p=v['pivot_spacing']*v['scale_factor']/2
  theta=np.deg2rad(v['pinion_mesh_deg']);ratio=v['pinion_teeth']/v['gear_teeth']
  self.assertAlmostEqual(p-(p+p*ratio)*np.cos(theta),0,places=5)
 def test_four_actual_prints_with_integral_jaw_gears(self):
  parts=list((self.folder/'exports/print').glob('*.stl'))
  self.assertEqual(sorted(p.stem for p in parts),['base','left','pinion','right'])
  for p in parts:
   m=trimesh.load_mesh(p);self.assertTrue(m.is_watertight and len(m.split())==1,p.name)
 def test_close_pivots(self):
  self.assertLessEqual(self.v['pivot_spacing']*self.v['scale_factor'],20)
 def test_assembly_includes_all_physical_hardware(self):
  f=self.folder
  parts=[f/'exports/parts'/name for name in ['left.stl','right.stl','pinion.stl','base.stl','motor.stl','stock_plate.stl']]
  parts += [f/'exports/reference'/name for name in ['plate_screws.stl','case_screws.stl','center_screw.stl','pivot_screws.stl','pivot_washers.stl','pivot_nuts.stl']]
  volume=sum(trimesh.load_mesh(p).volume for p in parts)
  self.assertAlmostEqual(trimesh.load_mesh(f/'exports/assembly.stl').volume,volume,delta=.02)
 def test_full_stroke_rear_gap_with_positive_controls(self):
  r=json.loads((self.folder/'geometry_checks.json').read_text())
  self.assertTrue(r['rear_clearance']['passed'])
  self.assertGreaterEqual(r['rear_clearance']['minimum_gap_mm'],.8-1e-4)
  self.assertFalse(r['rear_clearance']['tighter_candidate_passed'])
  self.assertTrue(r['full_stroke']['passed'])
 def test_no_hidden_parts_and_exact_bom(self):
  r=json.loads((self.folder/'geometry_checks.json').read_text())
  self.assertEqual(r['bom']['before_total'],22)
  self.assertEqual(r['bom']['after_total'],20)
  self.assertEqual(r['bom']['after_printed'],4)
  self.assertEqual(r['bom']['manifest_discrete_count'],20)
 def test_retention_tools_and_band_symmetry(self):
  r=json.loads((self.folder/'geometry_checks.json').read_text())
  for k in ['retention','tool_access','finger_band_symmetry','support_band','outside_contacts']:
   self.assertTrue(r[k]['passed'],(k,r[k]))
class CenteredGallery(unittest.TestCase):
 def test_tune_gap_moves_drive_without_scaling_bought_motor(self):
  with tempfile.TemporaryDirectory() as tmp:
   run=subprocess.run([sys.executable,str(DEFAULT/'live_render.py'),'--values','{"drive_gap":1.2}','--out',tmp],cwd=ROOT,capture_output=True,text=True,check=True)
   self.assertTrue(json.loads(run.stdout)['ok'])
   old=trimesh.load_mesh(DEFAULT/'exports/parts/motor.stl');new=trimesh.load_mesh(Path(tmp)/'motor.stl')
   np.testing.assert_allclose(old.extents,new.extents,atol=1e-5)
   np.testing.assert_allclose(new.bounds[:,1]-old.bounds[:,1],.4,atol=1e-5)
   jaw=trimesh.load_mesh(Path(tmp)/'right.stl');self.assertAlmostEqual(jaw.bounds[0,1],-3,places=4)
 def test_catalog_mix_and_motion(self):
  from Scripts import publish_designs as pub
  row=next(r for r in pub.discover() if r['id']=='two-finger-gripper-v323-generalist-centered-drive')
  self.assertEqual((row['name'],row['builds_on'],row['fingers']),('Base 22','Base 21','26'))
  self.assertEqual(row['finger_lineage']['builds_on'],'Gripper 25')
  with tempfile.TemporaryDirectory() as tmp:
   item=pub.publish_entry(row,Path(tmp),build=False)
   self.assertEqual(item['export_status'],'ready');self.assertEqual(len(item['models']),12)
   path=Path(tmp)/'catalog.json';path.write_text(json.dumps(dict(designs=[item])))
   script="""
import fs from 'node:fs';import {MIX,buildMix} from './cad/mobile_gallery/model.js';import POSES from './cad/mobile_gallery/poses.js';
const c=JSON.parse(fs.readFileSync(process.argv[1]));const m=buildMix(c,{[MIX.id]:{base:'22',gripper:'26',arm:'none',mount:'none',handles:'none'}},MIX);
const pose=POSES[m.pose];console.log(JSON.stringify({count:m.models.length,pose:m.pose,names:m.models.map(x=>x.name),moving:m.models.filter(x=>/^(Left|Right|Pinion|Stock aluminum|Plate screws|Center screw)/.test(x.name)).map(x=>({name:x.name,matched:pose.hinges.some(h=>new RegExp(h.match).test(x.name))})),gripper:m.rows.find(r=>r.key==='gripper').chosen.models.length,flags:m.rows.flatMap(r=>r.notes)}));
"""
   run=subprocess.run(['node','--input-type=module','-e',script,str(path)],cwd=ROOT,capture_output=True,text=True,check=True)
   d=json.loads(run.stdout);self.assertEqual((d['count'],d['gripper']),(12,2));self.assertTrue(all(x['matched'] for x in d['moving']));self.assertEqual(len(d['moving']),6);self.assertFalse(d['flags'])
if __name__=='__main__':unittest.main()
