"""Closure and sourced HLS3606M fastening contracts, established before the new version."""
import json,os,unittest,math,hashlib,tempfile,subprocess
from pathlib import Path
import numpy as np
import trimesh
from Scripts.check_finger_plane_constraints import projection,clipped
from shapely.geometry import box
ROOT=Path(__file__).resolve().parents[1]
NEW=ROOT/'Two Finger Gripper/versions/v324_generalist_contact_close'
class ClosedTips(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.f=Path(os.environ.get('CLOSURE_FOLDER',NEW));cls.v={p['name']:p['value'] for g in json.loads((cls.f/'params.json').read_text())['groups'] for p in g['params']}
 def test_actual_tips_touch_at_zero_command(self):
  outlines=[];p=self.v['pivot_spacing']*self.v['scale_factor']/2
  for k,sign in [('left',-1),('right',1)]:
   m=trimesh.load_mesh(self.f/f'exports/parts/{k}.stl');c=np.array([sign*p,0,0]);a=math.radians(-15*sign);R=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]]);m.vertices=(m.vertices-c)@R.T+c
   outlines.append(projection(clipped(m,-2.999,2.999)).intersection(box(-100,40,100,100)))
  self.assertLessEqual(outlines[0].distance(outlines[1]),.00005)
  self.assertLessEqual(outlines[0].intersection(outlines[1]).area,.00001)
 def test_contact_is_at_the_distal_end(self):
  shapes=[];p=self.v['pivot_spacing']*self.v['scale_factor']/2
  for k,sign in [('left',-1),('right',1)]:
   m=trimesh.load_mesh(self.f/f'exports/parts/{k}.stl');c=np.array([sign*p,0,0]);a=math.radians(-15*sign);R=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]]);m.vertices=(m.vertices-c)@R.T+c
   q=projection(clipped(m,-2.999,2.999));shapes.append(q.intersection(box(-100,q.bounds[3]-.05,100,100)))
  self.assertLessEqual(shapes[0].distance(shapes[1]),.00005)
 def test_exact_hardware_and_new_center_stack(self):
  r=json.loads((self.f/'hardware_checks.json').read_text())
  self.assertEqual(r['plate']['hole_count'],8)
  self.assertEqual(r['plate']['used_screws'],2)
  self.assertTrue(r['alignment']['passed']);self.assertFalse(r['alignment']['sts_14mm_pcd_control_passed'])
  self.assertAlmostEqual(r['center_stack']['thread_engagement_mm'],2.8,places=4)
  self.assertGreaterEqual(r['center_stack']['bore_floor_clearance_mm'],.19)
  self.assertTrue(r['center_stack']['passed']);self.assertFalse(r['center_stack']['old_unseated_stack_passed'])
  self.assertEqual(r['case']['hole_count'],4)
 def test_closed_and_open_motion_contract(self):
  r=json.loads((self.f/'closure_checks.json').read_text())
  self.assertTrue(r['passed']);self.assertTrue(r['overclose_control_detected']);self.assertGreaterEqual(r['minimum_plan_ligament_mm'],.4)
  self.assertGreater(r['opening_at_point_one_degree_mm'],0)
  self.assertGreaterEqual(r['rear_minimum_mm'],.8)
  self.assertGreater(r['servo_index_margin_to_wrap_deg'],150)
  self.assertEqual(r['jaw_command_limits_deg'],[0,30])
  for p,h in r['input_sha256'].items():self.assertEqual(hashlib.sha256((self.f/p).read_bytes()).hexdigest(),h)
class ContactGallery(unittest.TestCase):
 def test_catalog_assembly_bom_and_pose(self):
  from Scripts import publish_designs as pub
  row=next(r for r in pub.discover() if r['id']=='two-finger-gripper-v324-generalist-contact-close')
  self.assertEqual((row['name'],row['fingers'],row['builds_on']),('Base 23','27','Base 22'))
  self.assertEqual(row['finger_lineage']['builds_on'],'Gripper 26')
  with tempfile.TemporaryDirectory() as tmp:
   data=pub.publish_entry(row,Path(tmp),build=False);self.assertEqual(data['export_status'],'ready');self.assertEqual(len(data['models']),12)
   path=Path(tmp)/'catalog.json';path.write_text(json.dumps({'designs':[data]}))
   script="""import fs from 'node:fs';import {MIX,buildMix} from './cad/mobile_gallery/model.js';import POSES from './cad/mobile_gallery/poses.js';const m=buildMix(JSON.parse(fs.readFileSync(process.argv[1])),{[MIX.id]:{base:'23',gripper:'27',arm:'none',mount:'none',handles:'none'}},MIX);console.log(JSON.stringify({pose:POSES[m.pose],count:m.models.length,flags:m.rows.flatMap(r=>r.notes)}));"""
   run=subprocess.run(['node','--input-type=module','-e',script,str(path)],cwd=ROOT,capture_output=True,text=True,check=True);d=json.loads(run.stdout);self.assertEqual(d['count'],12);self.assertFalse(d['flags']);self.assertEqual(d['pose']['hinges'][0]['pivot'],[10,0,0])
 def test_hardware_and_mechanical_reports_match_current_inputs(self):
  for name in ['hardware_checks.json','geometry_checks.json','closure_checks.json']:
   r=json.loads((NEW/name).read_text());self.assertTrue(r['passed'])
   for p,h in r['input_sha256'].items():self.assertEqual(hashlib.sha256((NEW/p).read_bytes()).hexdigest(),h,p)
  r=json.loads((NEW/'geometry_checks.json').read_text());self.assertEqual(r['bom']['manifest_discrete_count'],19)
  volume=sum(trimesh.load_mesh(p).volume for p in (NEW/'exports/parts').glob('*.stl'))
  volume+=sum(trimesh.load_mesh(NEW/f'exports/reference/{k}.stl').volume for k in ['plate_screws','case_screws','center_screw','pivot_screws','pivot_washers','pivot_nuts'])
  self.assertAlmostEqual(trimesh.load_mesh(NEW/'exports/assembly.stl').volume,volume,delta=.02)
if __name__=='__main__':unittest.main()
