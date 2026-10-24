"""Measure actual finite-sector gear engagement and wrong-phase controls over full stroke."""
import json,math
from pathlib import Path
import numpy as np,trimesh
from shapely.affinity import affine_transform
import params,check_geometry as c
HERE=Path(__file__).resolve().parent;v=params.values()
meshes={k:trimesh.load_mesh(HERE/f'exports/parts/{k}.stl') for k in ['left','right','pinion']}
lower_y=v['mesh_split']-.5
upper_y=v['mesh_split']+v['mesh_layer_gap']+v['fdm_upper_lift']+.5
shapes={k:c.projection(c.clipped(m,lower_y-.01,lower_y+.01)) for k,m in meshes.items() if k!='pinion'}
upper={k:c.projection(c.clipped(meshes[k],upper_y-.01,upper_y+.01)) for k in ['right','pinion']}
def posed(q,k,a):
 center,r=c.motion(k,v);t=math.radians((a-15)*r);co,si=math.cos(t),math.sin(t);x,z=center[0],center[2]
 return affine_transform(q,[co,si,-si,co,x*(1-co)-z*si,z*(1-co)+x*si])
rows=[];controls=[]
for a in np.linspace(0,30,121):
 lo=[posed(shapes[k],k,a) for k in ['left','right']];up=[posed(upper[k],k,a) for k in ['right','pinion']]
 rows.append(dict(angle_deg=float(a),lower_gap_mm=lo[0].distance(lo[1]),upper_gap_mm=up[0].distance(up[1])))
 if a in [0,15,30]:
  controls.append(dict(angle_deg=float(a),lower_wrong_phase_area_mm2=posed(shapes['left'],'left',a+4).intersection(lo[1]).area,upper_wrong_phase_area_mm2=posed(upper['pinion'],'pinion',a+8).intersection(up[0]).area))
report=dict(passed=all(0<q['lower_gap_mm']<=v['gear_backlash']+.01 and 0<q['upper_gap_mm']<=v['gear_backlash']+.01 for q in rows) and all(min(q['lower_wrong_phase_area_mm2'],q['upper_wrong_phase_area_mm2'])>1e-4 for q in controls),slice_y_mm=[lower_y,upper_y],samples=rows,wrong_phase_controls=controls,jaw_stroke_deg=[0,30],servo_stroke_deg=30*v['drive_teeth']/v['pinion_teeth'],ratio=v['drive_teeth']/v['pinion_teeth'],qualification='Actual finite-sector mesh slices, sampled engagement and red controls; no wear or strength rating. Base26 involute profiles and tooth counts unchanged.')
(HERE/'gear_checks.json').write_text(json.dumps(report,indent=2)+'\n');print('Gear checks',report['passed']);raise SystemExit(0 if report['passed'] else 1)
