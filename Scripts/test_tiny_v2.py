"""Tiny V2 contracts: retained fingers, resized gearing and actual servo mounting."""
import importlib.util,json,math,re,subprocess,sys,tempfile,unittest
from pathlib import Path
import numpy as np
import trimesh
import publish_designs
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'Two Finger Gripper/versions/v318_generalist_tiny_v2'
# Run as its own process so these generic CAD module names cannot leak across version tests.
sys.path.insert(0,str(HERE))
import check_geometry as geometry
import params

class TinyV2Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.v=params.values();cls.meshes={k:trimesh.load_mesh(HERE/f'exports/parts/{k}.stl') for k in geometry.PARTS}
 def test_original_source_modules_and_trace_are_preserved(self):
  source=(geometry.SOURCE/'gripper.scad').read_text()
  tiny=(HERE/'large_source.scad').read_text()
  for start,end in [('module profile()', 'function hole_d'),('function hole_d','module ridges2d'),('module whole_finger()', 'module placed')]:
   self.assertEqual(source[source.index(start):source.index(end)],tiny[tiny.index(start):tiny.index(end)])
  self.assertEqual((geometry.SOURCE/'trace_px.scad').read_bytes(),(HERE/'trace_px.scad').read_bytes())
  self.assertTrue(all(r['passed'] for r in geometry.fidelity(self.meshes,self.v)))
 def test_retained_fingers_and_stroke_with_adjustable_gears(self):
  self.assertTrue(geometry.design_contract(self.v)['passed'])
  self.assertTrue(geometry.design_contract(dict(self.v,gear_teeth=28,pinion_teeth=24))['passed'])
  for key,value in [('beak_stretch',2),('pivot_spacing',60),('max_angle',31),('max_angle',9)]:
   self.assertFalse(geometry.design_contract(dict(self.v,**{key:value}))['passed'],key)
   with self.assertRaises(ValueError):params.values({key:value})
 def test_continuous_width_and_candidate_search(self):
  from compare_candidates import search,candidate
  self.assertAlmostEqual(geometry.continuous_width(self.meshes,self.v)['width_mm'],70.032302,places=5)
  fit=geometry.hardware_fit(self.v);self.assertTrue(fit['passed']);self.assertGreaterEqual(fit['rim_mm'],1)
  self.assertAlmostEqual(fit['ratio'],30/24)
  self.assertFalse(candidate(.5,34,16)['passed'])
  self.assertFalse(candidate(.49,28,24)['passed'])
  selected=search();self.assertEqual((selected['scale'],selected['side_teeth'],selected['pinion_teeth']),(.5,30,24))
  fake=trimesh.Trimesh(vertices=[[1,0,1]],faces=[],process=False)
  v=dict(self.v,pivot_spacing=0,max_angle=90)
  self.assertAlmostEqual(geometry.continuous_width({'right':fake},v)['per_part_x_mm']['right'][1],math.sqrt(2))
 def test_actual_hardware_and_complete_motion(self):
  report=json.loads((HERE/'geometry_checks.json').read_text())
  self.assertTrue(report['fasteners']['passed']);self.assertTrue(report['lattice']['passed']);self.assertTrue(all(report['mounting_controls'].values()));self.assertTrue(report['gear_phase_control']['passed']);self.assertTrue(report['motion_collisions']['passed']);self.assertEqual(report['motion_collisions']['angles'],121)
  self.assertEqual(report['motion_collisions']['pairs_per_angle'],66)
  self.assertEqual(report['hardware']['horn_screw_pcd_mm'],14)
  self.assertTrue(all(r['passed'] for r in json.loads((HERE/'mesh_checks.json').read_text())))
  motor=trimesh.load_mesh(HERE/'exports/parts/motor.stl')
  self.assertAlmostEqual(motor.extents[0],45.4,places=4);self.assertAlmostEqual(motor.extents[2],24.8,places=4)
  # params.scad compensates physical hardware before uniform scaling, exactly.
  text=(HERE/'params.scad').read_text()
  for key in ['sts_horn_pcd','sts_w','sts_len','screw_clear_d','sts_screw_d','base_clear','pillar_pilot_d']:
   value=float(re.search(r'^'+key+r'=([0-9.e+-]+);',text,re.M)[1]);self.assertAlmostEqual(value*.5,self.v[key])
 def test_tune_keeps_hardware_actual_size_and_returns_scaled_pivot(self):
  import live_render
  with tempfile.TemporaryDirectory() as tmp:
   r=live_render.render({'scale_factor':.6},tmp)
   self.assertTrue(r['ok'],r);self.assertAlmostEqual(r['pivot'],31.35*.6)
   tuned=trimesh.load_mesh(Path(tmp)/'right.stl')
   # Finger overall size changes while full-size servo remains 24.8 x 45.4.
   self.assertAlmostEqual(tuned.bounds[1][2]/self.meshes['right'].bounds[1][2],.6/.5,places=5)
   motor=trimesh.load_mesh(Path(tmp)/'motor.stl');self.assertAlmostEqual(motor.extents[0],45.4,places=4)
   self.assertFalse(live_render.render({'scale_factor':.49},tmp)['ok'])
 def test_catalog_and_compatible_picks(self):
  rows=publish_designs.discover(ROOT);row=next(r for r in rows if r['id']=='two-finger-gripper-v318-generalist-tiny-v2')
  self.assertEqual(row['name'],'Base 17');self.assertEqual(row['fingers'],'24');self.assertEqual(row['builds_on'],'Base 15')
  self.assertTrue(row['no_handles']);self.assertEqual(len(row['existing']),8)
  catalog={'designs':[dict(publish_designs.public_fields(r),models=r['existing']) for r in rows if r['existing']]}
  script='''import {MIX,buildMix,initialPicks,mixOptions,optionLabel} from %s;
const catalog=JSON.parse(process.argv[1]);
const option=mixOptions(catalog).gripper.find(o=>o.version==='24');
if(!optionLabel('Gripper',option).includes('from Gripper 22'))throw Error('missing carried finger lineage');
const picks=initialPicks(new URLSearchParams('gripper=24&base=17&handles=7&arm=none&mount=none'));
let mix=buildMix(JSON.parse(process.argv[1]),picks,MIX);
if(mix.rows.find(r=>r.key==='handles').chosen)throw Error('full-size handle drawn');
const b=mix.rows.find(r=>r.key==='base');if(b.notes.some(n=>n.text.includes('built on Gripper')))throw Error('matching pair flagged');
picks[MIX.id].gripper='22';mix=buildMix(JSON.parse(process.argv[1]),picks,MIX,'gripper');
if(!mix.rows.some(r=>r.notes.some(n=>n.text.includes('built on Gripper 24'))))throw Error('wrong fingers accepted');
''' % json.dumps((ROOT/'cad/mobile_gallery/model.js').as_uri())
  subprocess.run(['node','--input-type=module','-e',script,json.dumps(catalog,default=str)],check=True,capture_output=True,text=True)
  poses=(ROOT/'cad/mobile_gallery/poses.js').read_text();poses=json.loads(poses[poses.index('{'):poses.rindex('}')+1]);p=poses[row['id']]
  self.assertEqual(p['max'],30);self.assertAlmostEqual(p['hinges'][2]['sign'],-30/24)
  pivot,pin,ratio=geometry.axes(self.v);self.assertAlmostEqual(p['hinges'][0]['pivot'][0],pivot);np.testing.assert_allclose(p['hinges'][2]['pivot'],[pin[0],0,pin[1]])

if __name__=='__main__':unittest.main()
