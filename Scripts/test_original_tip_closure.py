"""Original tips must meet by rigid blade positioning, never by adding a tip bridge."""
import os,json,unittest,subprocess,tempfile,sys
from pathlib import Path
import numpy as np,trimesh
from shapely.geometry import box
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from Scripts.check_finger_plane_constraints import projection,clipped
NEW=ROOT/'Two Finger Gripper/versions/v325_generalist_original_tip_closure'
class OriginalTips(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.f=Path(os.environ.get('ORIGINAL_TIP_FOLDER',NEW));sys.path.insert(0,str(cls.f))
  import check_geometry as c,params
  cls.c=c;cls.v=params.values()
 def posed(self,k,a=0):
  m=trimesh.load_mesh(self.f/f'exports/parts/{k}.stl');p,r=self.c.motion(k,self.v);m.vertices=self.c.rotated(m.vertices,p,(a-15)*r);return m
 def test_no_material_added_or_removed_from_original_blade(self):
  # Independent original finger() bypasses direct_finger() and all new tip helpers.
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp);scad=path/'oracle.scad';out=path/'oracle.stl'
   scad.write_text('include <'+str(self.f/'gripper.scad')+'>\npart="oracle";scale(scale_factor) mirror([0,1,0]) placed(1,15) mirror([0,1,0]) finger();')
   subprocess.run(['/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD','--backend','manifold','--export-format','binstl','-o',str(out),str(scad)],capture_output=True,check=True)
   actual=clipped(trimesh.load_mesh(self.f/'exports/parts/right.stl'),-2.999,2.999)
   oracle=clipped(trimesh.load_mesh(out),-2.999,2.999)
   import manifold3d as mf
   blade=mf.Manifold.cube((400,100,200)).translate((-200,-50,12))
   a=self.c.solid(actual)^blade;b=self.c.solid(oracle)^blade
   self.assertLess((a-b).volume()+(b-a).volume(),.0001,'Blade must be the original solid under a rigid transform; no nose, extension or trim')
 def test_original_rounded_tip_contacts_first(self):
  a,b=[projection(clipped(self.posed(k),-2.999,2.999)) for k in ['left','right']]
  self.assertLessEqual(a.distance(b),.00005)
  self.assertLessEqual(a.intersection(b).area,.00001)
  z=max(a.bounds[3],b.bounds[3]);tip=[s.intersection(box(-100,z-.3,100,100)) for s in [a,b]]
  self.assertLessEqual(tip[0].distance(tip[1]),.00005)
  body=[s.intersection(box(-100,12,100,z-3)) for s in [a,b]]
  self.assertGreaterEqual(body[0].distance(body[1]),.6-1e-5)
 def test_full_stroke_and_hardware_reports(self):
  import hashlib
  for name in ['geometry_checks.json','hardware_checks.json','closure_checks.json']:
   r=json.loads((self.f/name).read_text());self.assertTrue(r['passed'],name)
   for p,h in r['input_sha256'].items():self.assertEqual(hashlib.sha256((self.f/p).read_bytes()).hexdigest(),h,p)
  r=json.loads((self.f/'geometry_checks.json').read_text());self.assertEqual(r['full_stroke']['angles'],121);self.assertEqual(r['full_stroke']['pairs_per_angle'],78);self.assertGreaterEqual(r['rear_clearance']['minimum_gap_mm'],.8)
class OriginalTipGallery(unittest.TestCase):
 def test_published_version_lineage_and_pose(self):
  import tempfile
  from Scripts import publish_designs as pub
  row=next(r for r in pub.discover() if r['id']=='two-finger-gripper-v325-generalist-original-tip-closure')
  self.assertEqual((row['name'],row['fingers'],row['builds_on']),('Base 24','28','Base 23'))
  self.assertEqual(row['finger_lineage']['builds_on'],'Gripper 27')
  with tempfile.TemporaryDirectory() as tmp:
   data=pub.publish_entry(row,Path(tmp),build=False);self.assertEqual(data['export_status'],'ready');self.assertEqual(len(data['models']),12)
  js="import P from './cad/mobile_gallery/poses.js';console.log(JSON.stringify(P['two-finger-gripper-v325-generalist-original-tip-closure']));"
  pose=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=ROOT,text=True));self.assertEqual(pose['hinges'][0]['pivot'],[15,0,0]);self.assertEqual((pose['min'],pose['max']),(0,30))
if __name__=='__main__':unittest.main()
