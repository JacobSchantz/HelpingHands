"""Small drive must preserve wide jaw roots and original unmodified contact blades."""
import json,os,unittest,sys,hashlib
from pathlib import Path
import numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'Two Finger Gripper/versions/v325_generalist_original_tip_closure'
NEW=ROOT/'Two Finger Gripper/versions/v326_generalist_small_drive'
sys.path.insert(0,str(ROOT))
from Scripts.check_finger_plane_constraints import clipped
class SmallDrive(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.folder=Path(os.environ.get('SMALL_DRIVE_FOLDER',NEW));sys.path.insert(0,str(cls.folder))
  import check_geometry as c,params
  cls.c=c;cls.v=params.values()
 def test_gears_shrink_without_narrowing_jaws(self):
  v=self.v;s=v['scale_factor'];self.assertEqual(v['pivot_spacing']*s,30)
  m=v.get('drive_module',v['pivot_spacing']/v['gear_teeth']*s)
  n=v.get('drive_teeth',v['gear_teeth'])
  self.assertLessEqual(m*(n+2),21,'Shrink upper jaw gear independently of 30 mm jaw spacing')
  self.assertLessEqual(m*(v['pinion_teeth']+2),25,'Shrink pinion around real 18 mm spline plate')
  self.assertAlmostEqual(self.c.axes(v)[1][0],0,places=5)
 def test_original_finger_band_unchanged(self):
  for k in ['left','right']:
   a=clipped(trimesh.load_mesh(self.folder/f'exports/parts/{k}.stl'),-2.999,2.999)
   b=clipped(trimesh.load_mesh(OLD/f'exports/parts/{k}.stl'),-2.999,2.999)
   a,b=self.c.solid(a),self.c.solid(b)
   self.assertLess((a-b).volume()+(b-a).volume(),.0001)
 def test_verified_full_stroke_hardware_and_closure(self):
  for name in ['geometry_checks.json','hardware_checks.json','closure_checks.json','gear_checks.json']:
   r=json.loads((self.folder/name).read_text());self.assertTrue(r['passed'],name)
   for p,h in r['input_sha256'].items():self.assertEqual(hashlib.sha256((self.folder/p).read_bytes()).hexdigest(),h,p)
  r=json.loads((self.folder/'geometry_checks.json').read_text())
  self.assertEqual(r['full_stroke']['angles'],121);self.assertEqual(r['full_stroke']['pairs_per_angle'],78)
  self.assertLessEqual(r['support_band']['area_mm2'],12.8)
 def test_actual_drive_and_housing_envelope_reduction(self):
  old=json.loads((OLD/'geometry_checks.json').read_text())['swept_bounds']['per_part_bounds']
  new=json.loads((self.folder/'geometry_checks.json').read_text())['swept_bounds']['per_part_bounds']
  for k in ['pinion','base']:
   oldarea=(old[k][0][1]-old[k][0][0])*(old[k][2][1]-old[k][2][0])
   area=(new[k][0][1]-new[k][0][0])*(new[k][2][1]-new[k][2][0])
   self.assertLess(area,oldarea*.75,k+' must shrink by at least 25% in projected bounding area')

class SmallDriveGallery(unittest.TestCase):
 def test_lineage_published_and_correct_axes(self):
  from Scripts import publish_designs as pub
  import tempfile,subprocess
  row=next(r for r in pub.discover() if r['id']=='two-finger-gripper-v326-generalist-small-drive')
  self.assertEqual((row['name'],row['fingers'],row['builds_on']),('Base 25','29','Base 24'))
  self.assertEqual(row['finger_lineage']['builds_on'],'Gripper 28')
  with tempfile.TemporaryDirectory() as tmp:
   data=pub.publish_entry(row,Path(tmp),build=False)
   self.assertEqual(data['export_status'],'ready');self.assertEqual(len(data['models']),12)
  js="import P from './cad/mobile_gallery/poses.js';console.log(JSON.stringify(P['two-finger-gripper-v326-generalist-small-drive']));"
  pose=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=ROOT,text=True))
  self.assertEqual(pose['hinges'][0]['pivot'],[15,0,0])
  self.assertAlmostEqual(pose['hinges'][2]['pivot'][2],-10.6564534438)
  self.assertAlmostEqual(pose['hinges'][2]['sign'],-18/28)

if __name__=='__main__':unittest.main()
