"""Bracket rear clearance using actual OpenSCAD re-exports and inherited jaw outline."""
import json,tempfile,shutil,subprocess
from pathlib import Path
import trimesh
import params
from check_geometry import rear_clearance
from export_models import SCAD
HERE=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as tmp:
 work=Path(tmp)
 for p in HERE.glob('*.scad'):shutil.copy2(p,work/p.name)
 shutil.copytree(HERE/'reference',work/'reference')
 rows=[]
 for pitch in [19,19.4,19.5,19.6]:
  v=params.values();v['pivot_spacing']=pitch/v['scale_factor'];params.write_scad(work/'params.scad',v)
  run=subprocess.run([SCAD,'--backend','manifold','--export-format','binstl','-D','part="viewer_right"','-o',str(work/'right.stl'),str(work/'gripper.scad')],capture_output=True,text=True,check=True)
  if 'WARNING' in run.stderr:raise RuntimeError(run.stderr)
  r=rear_clearance({'right':trimesh.load_mesh(work/'right.stl')},v)
  rows.append(dict(pivot_spacing_mm=pitch,minimum_gap_mm=r['minimum_gap_mm'],angle_deg=r['angle_deg'],passed=r['passed']))
 result=dict(candidates=rows,chosen_mm=19.6,resolution_mm=.1,qualification='Smallest passing 0.1 mm pitch in this re-exported bracket for inherited jaw outline, 0–30 degree stroke and 0.8 mm assumed tolerance/deflection budget. Further root reshaping was not searched; not a global minimum.')
 (HERE/'spacing_search.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
