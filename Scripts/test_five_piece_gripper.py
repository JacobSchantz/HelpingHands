"""Physical manufacturing/assembly contracts for voice-550038ca's five-piece iteration.
Run: PYTHONPATH=. cad/blender/.venv/bin/python -m unittest Scripts.test_five_piece_gripper
"""
from pathlib import Path
import hashlib,json,unittest,subprocess,shutil
import trimesh
from Scripts.check_finger_plane_constraints import clipped,projection
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'Two Finger Gripper/versions/v328_generalist_five_piece'
OLD=HERE.with_name('v327_generalist_support_free')
def read(n):return json.loads((HERE/n).read_text())
class FivePieceGripper(unittest.TestCase):
 def test_real_print_count_not_mesh_groups(self):
  files=sorted((HERE/'exports/print').glob('*.stl'));self.assertEqual(len(files),5)
  for f in files:
   m=trimesh.load_mesh(f);self.assertTrue(m.is_watertight,f);self.assertEqual(len(m.split()),1,f);self.assertGreater(m.volume,100)
  old_count=sum(len(trimesh.load_mesh(f).split()) for f in (OLD/'exports/print').glob('*.stl'))
  self.assertEqual(old_count,12)
 def test_every_piece_shown_in_exploded_manifest(self):
  manifest=read('viewer_parts.json');count=0
  for p in manifest['parts']:
   m=trimesh.load_mesh(HERE/p['path']);self.assertTrue(m.is_watertight,p['path']);count+=len(m.split())
  self.assertEqual(count,23);self.assertEqual(len(trimesh.load_mesh(HERE/'exports/assembly.stl').split()),23)
  self.assertEqual(read('geometry_checks.json')['bom']['after_total'],23)
 def test_actual_paths_and_independent_layer_sections(self):
  for name in ['manufacturing_checks.json','slicer_checks.json']:
   r=read(name);self.assertTrue(r['passed'],name);self.assertEqual(len(r['parts']),5)
   for p in r['parts']:
    f=HERE/('exports/print/'+p['part']+'.stl' if name.startswith('manufacturing') else 'slicing/'+p['part']+'.gcode')
    self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),p['sha256'])
    if name.startswith('slicer'):
     self.assertTrue(p['supports_off']);self.assertEqual(p['support_paths'],0);self.assertEqual(p['bridge_segments'],0);self.assertFalse(p['overhang_layers_mm'])
 def test_original_working_blades_unchanged(self):
  # Compare actual distal band volume, allowing only changed roots below Z12.
  for k in ['left','right']:
   a=clipped(trimesh.load_mesh(HERE/f'exports/parts/{k}.stl'),-2.999,2.999)
   b=clipped(trimesh.load_mesh(OLD/f'exports/parts/{k}.stl'),-2.999,2.999)
   from shapely.geometry import box
   aa=projection(a).intersection(box(-100,12,100,100));bb=projection(b).intersection(box(-100,12,100,100))
   self.assertLess(aa.symmetric_difference(bb).area,1e-4)
 def test_full_stroke_and_real_axial_capture(self):
  r=read('geometry_checks.json');self.assertTrue(r['passed']);
  for name,sha in r['input_sha256'].items():self.assertEqual(hashlib.sha256((HERE/name).read_bytes()).hexdigest(),sha)
  self.assertEqual(r['full_stroke']['angles'],121);self.assertEqual(r['full_stroke']['pairs_per_angle'],105)
  self.assertTrue(r['axial_escape_controls']['passed']);self.assertEqual(len(r['axial_escape_controls']['controls']),4)
  self.assertTrue(r['rod_stack']['passed']);self.assertEqual(r['rod_stack']['nuts'],4)
  self.assertTrue(r['tool_access']['passed'])
 def test_closure_and_gear_engagement_have_red_controls(self):
  r=read('closure_checks.json');self.assertTrue(r['passed']);self.assertLess(r['nominal_tip_gap_mm'],.00005);self.assertTrue(r['overclose_control_detected'])
  r=read('gear_checks.json');self.assertTrue(r['passed']);self.assertEqual(len(r['samples']),121);self.assertEqual(len(r['wrong_phase_controls']),3)
 def test_source_hardware_interfaces(self):
  r=read('hardware_checks.json');self.assertTrue(r['passed']);self.assertEqual(r['plate']['hole_count'],8);self.assertEqual(r['case']['hole_count'],4)
  self.assertEqual(r['plate']['used_screws'],2);self.assertGreater(r['center_stack']['bore_floor_clearance_mm'],.19)
 def test_actual_jaws_are_independent_gallery_selection(self):
  if not shutil.which('node'):self.skipTest('Node unavailable')
  manifest=read('viewer_parts.json')
  catalog={'designs':[dict(id='two-finger-gripper-v328-generalist-five-piece',name='Base 27',project='Generalist Gripper',fingers='31',no_handles=True,models=manifest['parts'])]}
  script="""import {buildMix,initialPicks} from %s;
const catalog=JSON.parse(process.argv[1]);
const mix=buildMix(catalog,initialPicks(new URLSearchParams('base=27&gripper=31&arm=none&mount=none&handles=none')));
console.log(JSON.stringify({name:mix.name,pose:mix.pose,jaws:mix.models.filter(m=>m.part==='gripper').length,total:mix.models.length,notes:mix.rows.flatMap(r=>r.notes)}));""" % json.dumps(str(ROOT/'cad/mobile_gallery/model.js'))
  p=subprocess.run(['node','--input-type=module','-e',script,json.dumps(catalog)],capture_output=True,text=True,check=True)
  r=json.loads(p.stdout);self.assertEqual(r['name'],'Gripper 31 + Base 27');self.assertEqual(r['jaws'],2);self.assertEqual(r['total'],14);self.assertFalse(r['notes']);self.assertEqual(r['pose'],'two-finger-gripper-v328-generalist-five-piece')
 def test_registry_and_pose_publish_lineage(self):
  from Scripts.publish_designs import version_entry,own_part,finger_version
  self.assertEqual(own_part(HERE),('Base','27'));self.assertEqual(finger_version(HERE),'31');self.assertIn('Base 26',version_entry(HERE));self.assertIn('Gripper 30',version_entry(HERE))
  text=(ROOT/'cad/mobile_gallery/poses.js').read_text();line=next(l for l in text.splitlines() if 'v328-generalist-five-piece' in l)
  self.assertIn('Plate washers|Metal capture washer',line)
if __name__=='__main__':unittest.main()
