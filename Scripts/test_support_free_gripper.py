"""Manufacturing and mechanism contracts for Base26/Gripper30's real exports."""
import hashlib,json,sys,unittest
from pathlib import Path
import trimesh,numpy as np
from shapely.geometry import LineString,box
ROOT=Path(__file__).resolve().parents[1]
NEW=ROOT/'Two Finger Gripper/versions/v327_generalist_support_free'
sys.path.insert(0,str(ROOT/'Scripts'))
from check_support_free_prints import section

class SupportFree(unittest.TestCase):
 def test_actual_critical_walls_not_only_nominal_dimensions(self):
  cases=[('left_blade',8,1.2),('right_upper',1,1.2),('left_gear',1,1.2),('right_gear',1,1.2),('base',12,1.05),('base',3.5,1.1),('ear_spacers',4,1.05)]
  for name,z,budget in cases:
   q=section(trimesh.load_mesh(NEW/f'exports/print/{name}.stl'),z)
   polygons=list(q.geoms) if hasattr(q,'geoms') else [q]
   for p in polygons:
    outer=LineString(p.exterior.coords);holes=[LineString(h.coords) for h in p.interiors]
    gaps=[outer.distance(h) for h in holes]+[a.distance(b) for i,a in enumerate(holes) for b in holes[i+1:]]
    self.assertTrue(gaps,name);self.assertGreaterEqual(min(gaps),budget-1e-4,(name,z,min(gaps)))
 def test_manufacturing_and_actual_slicer_paths(self):
  for f in ['manufacturing_checks.json','slicer_checks.json']:
   r=json.loads((NEW/f).read_text());self.assertTrue(r['passed'],f);self.assertEqual(len(r['parts']),9)
   for x in r['parts']:
    path=NEW/(f"exports/print/{x['part']}.stl" if f.startswith('manufacturing') else f"slicing/{x['part']}.gcode")
    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),x['sha256'])
  r=json.loads((NEW/'slicer_checks.json').read_text())
  self.assertTrue(all(x['supports_off'] and x['support_paths']==0 for x in r['parts']))
  self.assertEqual([x['part'] for x in r['parts'] if x['bridge_segments']],[])
 def test_mechanism_and_source_hardware_reports_current(self):
  for f in ['geometry_checks.json','closure_checks.json','hardware_checks.json','gear_checks.json']:
   r=json.loads((NEW/f).read_text());self.assertTrue(r['passed'],f)
   for p,h in r['input_sha256'].items():self.assertEqual(hashlib.sha256((NEW/p).read_bytes()).hexdigest(),h,p)
  g=json.loads((NEW/'geometry_checks.json').read_text());self.assertEqual(g['full_stroke']['angles'],121)
  self.assertEqual(g['full_stroke']['pairs_per_angle'],190);self.assertEqual(g['bom']['manifest_discrete_count'],33)
  self.assertGreaterEqual(g['retention']['sleeve_wall_mm'],1.0)
  self.assertLessEqual(g['support_band']['area_mm2'],29.1)
  c=json.loads((NEW/'closure_checks.json').read_text());self.assertLess(c['nominal_tip_gap_mm'],5e-5);self.assertTrue(c['overclose_control_detected'])
 def test_original_distal_outer_silhouette_no_connectors(self):
  # Interior lattice is intentionally filled. Compare only actual OUTER boundary beyond changed pivot roots.
  import importlib.util
  spec=importlib.util.spec_from_file_location('sfc',ROOT/'Scripts/check_finger_plane_constraints.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  for k in ['left','right']:
   polys=[]
   for f in [NEW,NEW.with_name('v326_generalist_small_drive')]:
    q=m.projection(m.clipped(trimesh.load_mesh(f/f'exports/parts/{k}.stl'),-2.999,2.999))
    from shapely.geometry import Polygon
    polys.append(Polygon(q.exterior).intersection(box(-100,15,100,100)))
   self.assertLess(polys[0].symmetric_difference(polys[1]).area,1e-4)
 def test_split_keys_and_spacer_screw_stack(self):
  v={x['name']:x['value'] for g in json.loads((NEW/'params.json').read_text())['groups'] for x in g['params']}
  self.assertGreaterEqual(v['gear_join_r']-v['fdm_key_r']-v['fdm_key_fit'],1.2)
  self.assertGreaterEqual(v['fdm_key_r']*np.cos(np.pi/6)-(v['post_d']*v['scale_factor']+2*v['base_clear'])/2,1.2)
  spacer=v['hls_plate_above_ear']-v['hls_plate_face'];top=v['fdm_spacer_screw_len']-(v['base_t']-v['fdm_spacer_head_h'])
  self.assertGreaterEqual(top,3);self.assertGreaterEqual(spacer-top-v['hls_case_pilot_depth'],.6)
  self.assertGreaterEqual(v['fdm_spacer_offset']+np.hypot(v['hls_mount_cad_u0'],v['hls_mount_span_w']/2)-v['tool_d']/2,12.2)
 def test_published_parts_and_lineage(self):
  from Scripts import publish_designs as pub
  import tempfile
  row=next(r for r in pub.discover() if r['id']=='two-finger-gripper-v327-generalist-support-free')
  self.assertEqual((row['name'],row['fingers'],row['builds_on']),('Base 26','30','Base 25'))
  self.assertEqual(row['finger_lineage']['builds_on'],'Gripper 29')
  with tempfile.TemporaryDirectory() as tmp:
   r=pub.publish_entry(row,Path(tmp),build=False);self.assertEqual(r['export_status'],'ready');self.assertEqual(len(r['models']),19)
if __name__=='__main__':unittest.main()
