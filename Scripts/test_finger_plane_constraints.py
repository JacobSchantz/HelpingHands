"""Acceptance tests plus known-failure reproducers for voice-550038ca.
A green suite means the evidence is reproducible, NOT that either design is approved.
Run: cad/blender/.venv/bin/python -m unittest Scripts.test_finger_plane_constraints -v
"""
import json, unittest
from pathlib import Path
import numpy as np
from Scripts import check_finger_plane_constraints as checks
OUT=checks.ROOT/'cad/validation/voice-550038ca'
class FingerPlaneConstraints(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=checks.evaluate(checks.BASELINE);cls.candidate=checks.evaluate(checks.CANDIDATE)
  cls.new=checks.evaluate(checks.VERSIONS/'v322_generalist_two_pivot_support')
  OUT.mkdir(parents=True,exist_ok=True)
  for name,report in [('base20',cls.old),('unpublished-candidate',cls.candidate),('base21',cls.new)]:
   (OUT/f'{name}.json').write_text(json.dumps(report,indent=2)+'\n')
 def test_only_local_pivots_and_retainers_reproduces_current_failure(self):
  self.assertFalse(self.old['minimal_in_plane_support']['passed'])
  self.assertFalse(self.candidate['minimal_in_plane_support']['passed'])
 def test_new_only_local_pivot_support_passes_without_shrinking_jaws(self):
  self.assertTrue(self.new['minimal_in_plane_support']['passed'])
  self.assertLess(self.new['minimal_in_plane_support']['band_support_area_mm2'],14.2)
  self.assertEqual(self.new['cap_footprint']['plate_area_mm2'],0)
  self.assertTrue(self.new['full_stroke']['passed'])
  self.assertTrue(self.new['tool_access']['passed'])
  self.assertTrue(self.new['outside_contacts']['passed'])
  old=checks.load(checks.BASELINE);new=checks.load(checks.VERSIONS/'v322_generalist_two_pivot_support')
  for k in ('left','right'):
   np.testing.assert_array_equal(old[k].vertices,new[k].vertices)
   np.testing.assert_array_equal(old[k].faces,new[k].faces)
 def test_existing_cap_reproduces_unnecessary_footprint(self):
  self.assertFalse(self.old['cap_footprint']['passed'])
  self.assertGreater(self.old['cap_footprint']['avoidable_overhang_mm2'],250)
 def test_candidate_meets_outline_budget_but_is_not_accepted(self):
  self.assertTrue(self.candidate['cap_footprint']['passed'])
  self.assertFalse(self.candidate['full_stroke']['passed'])
  self.assertTrue(any(set(x['pair'].split('/'))=={'pinion','base'} for x in self.candidate['full_stroke']['failures']))
  self.assertFalse(self.candidate['tool_access']['passed'])
 def test_fingers_stay_exactly_in_original_plane(self):
  a=checks.load(checks.BASELINE);b=checks.load(checks.CANDIDATE)
  for k in ('left','right'):
   np.testing.assert_array_equal(a[k].vertices,b[k].vertices)
   np.testing.assert_array_equal(a[k].faces,b[k].faces)
 def test_direct_outside_contacts_have_full_stroke_cad_approach(self):
  for report in (self.old,self.candidate):
   self.assertTrue(report['outside_contacts']['passed'])
   self.assertEqual(report['outside_contacts']['probes'],121*2*3)
   self.assertEqual(report['human_contact']['status'],'unverified')
 def test_peg_minimality_is_not_inferred_from_collision_clearance(self):
  for report in (self.old,self.candidate):
   self.assertEqual(report['peg_placement']['status'],'unverified')
   self.assertTrue(report['peg_placement']['outside_corridor_clear'])
   self.assertEqual(report['retention']['status'],'unverified')
  self.assertLess(self.candidate['peg_placement']['band_support_area_mm2'],self.old['peg_placement']['band_support_area_mm2'])
 def test_drive_stays_overhead_and_baseline_motion_is_clear(self):
  for report in (self.old,self.candidate):
   self.assertTrue(report['overhead_drive']['passed'])
   self.assertAlmostEqual(report['overhead_drive']['minimum_gap_mm'],.8,places=5)
   self.assertEqual(report['full_stroke']['angles'],121)
  self.assertTrue(self.old['full_stroke']['passed'])
  self.assertTrue(self.old['tool_access']['passed'])
  self.assertFalse(self.old['tool_access']['straight_case_access_passed'])

class PublishedTwoPivotTests(unittest.TestCase):
 def test_version_catalog_and_pose_contract(self):
  from Scripts import publish_designs as pub
  import tempfile,subprocess
  row=next(r for r in pub.discover() if r['id']=='two-finger-gripper-v322-generalist-two-pivot-support')
  self.assertEqual((row['name'],row['builds_on'],row['fingers']),('Base 21','Base 20','25'))
  self.assertTrue(row['no_handles']);self.assertFalse(row.get('carries'))
  with tempfile.TemporaryDirectory() as tmp:
   result=pub.publish_entry(row,Path(tmp),build=False)
   self.assertEqual(result['export_status'],'ready');self.assertEqual(len(result['models']),11)
   self.assertFalse(any('top plate' in m['name'].lower() for m in result['models']))
  script="import P from './cad/mobile_gallery/poses.js';console.log(JSON.stringify(P['two-finger-gripper-v322-generalist-two-pivot-support']));"
  p=json.loads(subprocess.check_output(['node','--input-type=module','-e',script],cwd=checks.ROOT,text=True))
  self.assertEqual(p['min'],0);self.assertEqual(p['max'],30);self.assertEqual(p['hinges'][0]['pivot'],[15.675,0,0])
 def test_saved_whole_skin_evidence_matches_geometry_and_reports_failed_fit(self):
  import hashlib
  d=json.loads((OUT/'whole-hand.json').read_text())
  self.assertFalse(d['passed'])
  for path,want in d['input_sha256'].items():self.assertEqual(hashlib.sha256((checks.ROOT/path).read_bytes()).hexdigest(),want,path)
  for c in d['cases']:
   self.assertEqual(len(c['samples']),13)
   self.assertIn('wrist',c['joint_names'])
   for finger in ('thumb','index','middle','ring','pinky'):self.assertTrue(any(finger in name for name in c['joint_names']))
   self.assertFalse(c['passed']);self.assertGreater(max(s['contact_miss_mm'] for s in c['samples']),10)
   self.assertTrue(any(s['skin_vertices_inside_cad'] for s in c['samples']))
 def test_local_retention_has_escape_stop_and_thread_capture(self):
  d=json.loads((checks.VERSIONS/'v322_generalist_two_pivot_support/geometry_checks.json').read_text())['retention']
  self.assertTrue(d['passed']);self.assertGreaterEqual(d['minimum_key_engagement_mm'],1.9)
  self.assertAlmostEqual(d['radial_capture_mm'],.75,places=5)
  self.assertGreater(min(d['downward_escape_positive_controls_mm3'].values()),1)

if __name__=='__main__':unittest.main()
