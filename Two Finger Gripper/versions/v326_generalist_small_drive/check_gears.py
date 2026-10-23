"""Nominal involute + actual finite-sector engagement; no qualified material/load model."""
import json,math,hashlib
from pathlib import Path
import numpy as np,trimesh
from shapely.affinity import affine_transform
import params,check_geometry as c
HERE=Path(__file__).resolve().parent
OLD=HERE.with_name('v325_generalist_original_tip_closure')
v=params.values();s=v['scale_factor'];alpha=math.radians(v['gear_pressure_deg']);backlash=v['gear_backlash']

def gear(n,m):
 rp=n*m/2;rb=rp*math.cos(alpha);rf=rp-1.25*m;ra=rp+m
 def inv(a):return math.tan(a)-a
 def flank(r):return math.pi/(2*n)-backlash/(2*rp)+inv(alpha)-inv(math.acos(min(1,rb/r)))
 return dict(teeth=n,module_mm=m,pitch_diameter_mm=2*rp,addendum_diameter_mm=2*ra,root_diameter_mm=2*rf,base_diameter_mm=2*rb,root_chord_mm=2*rf*math.sin(flank(max(rb,rf))),tip_chord_mm=2*ra*math.sin(flank(ra)))

def contact(a,b):
 rp=[g['pitch_diameter_mm']/2 for g in (a,b)];ra=[g['addendum_diameter_mm']/2 for g in (a,b)];rb=[g['base_diameter_mm']/2 for g in (a,b)]
 return (sum(math.sqrt(a*a-b*b) for a,b in zip(ra,rb))-sum(rp)*math.sin(alpha))/(math.pi*a['module_mm']*math.cos(alpha))
lower=gear(v['gear_teeth'],v['pivot_spacing']*s/v['gear_teeth']);upper=gear(v['drive_teeth'],v['drive_module']);pin=gear(v['pinion_teeth'],v['drive_module'])
meshes={k:trimesh.load_mesh(HERE/f'exports/parts/{k}.stl') for k in ['left','right','pinion']}
def shape(k,y):return c.projection(c.clipped(meshes[k],y-.01,y+.01))
shapes={'lower_left':shape('left',5),'lower_right':shape('right',5),'upper_right':shape('right',9),'pinion':shape('pinion',9)}
def posed(q,k,a):
 center,r=c.motion(k,v);t=math.radians((a-15)*r);co,si=math.cos(t),math.sin(t);x,z=center[0],center[2]
 return affine_transform(q,[co,si,-si,co,x*(1-co)-z*si,z*(1-co)+x*si])
samples=[]
for a in np.linspace(0,30,121):
 lower_gap=posed(shapes['lower_left'],'left',a).distance(posed(shapes['lower_right'],'right',a));upper_gap=posed(shapes['upper_right'],'right',a).distance(posed(shapes['pinion'],'pinion',a))
 samples.append(dict(jaw_deg=float(a),lower_mesh_gap_mm=lower_gap,upper_mesh_gap_mm=upper_gap))
mech=json.loads((HERE/'geometry_checks.json').read_text());before=json.loads((OLD/'geometry_checks.json').read_text())
def envelopes(r):
 b=r['swept_bounds']['per_part_bounds'];names=['left','right','pinion'];ext=[[min(b[k][i][0] for k in names),max(b[k][i][1] for k in names)] for i in range(3)]
 return dict(whole_assembly_mm=r['swept_bounds']['width_depth_height_mm'],pinion_mm=[q[1]-q[0] for q in b['pinion']],housing_mm=[q[1]-q[0] for q in b['base']],jaw_and_gears_mm=[q[1]-q[0] for q in ext],housing_volume_mm3=trimesh.load_mesh((HERE if r is mech else OLD)/'exports/parts/base.stl').volume)
# Whole gear-train projection excludes blade solids below Y3.8; continuous Z/X extrema still in full report.
from shapely.ops import unary_union
gear_envelopes={}
for f in [OLD,HERE]:
 polygons=[];drive_meshes={}
 for k in ['left','right','pinion']:
  m=trimesh.load_mesh(f/f'exports/parts/{k}.stl');drive_meshes[k]=c.clipped(m,3.8,11.5);polygons.append(c.projection(drive_meshes[k]))
 u=unary_union(polygons);cv={p['name']:p['value'] for g in json.loads((f/'params.json').read_text())['groups'] for p in g['params']};cv.setdefault('drive_teeth',30);cv.setdefault('drive_module',1);continuous=c.swept_bounds(drive_meshes,cv);gear_envelopes[f.name]=dict(continuous_swept_bounds=continuous,exported_at_jaw_deg=15,x_z_bounds_mm=list(u.bounds),width_length_mm=[u.bounds[2]-u.bounds[0],u.bounds[3]-u.bounds[1]],projected_area_mm2=u.area)
# Static load SCREEN, not a safe operating rating. 1N on EACH original distal tip.
lever=json.loads((HERE/'closure_checks.json').read_text())['actual_contact_x_z_mm'][0][1]
F=1.;jaw_torque=F*lever/1000;ratio=v['drive_teeth']/v['pinion_teeth'];servo_torque=2*jaw_torque/ratio
upper_ft=2*jaw_torque/(upper['pitch_diameter_mm']/2000);lower_ft=jaw_torque/(lower['pitch_diameter_mm']/2000)
# Lewis Y=0.484-2.87/z, simple 20deg full-depth approximation; all dynamic factors omitted.
Y=.484-2.87/v['drive_teeth'];face=11.5-(v['mesh_split']+v['mesh_layer_gap'])
rootwall=(pin['root_diameter_mm']-v['hls_plate_d'])/2
r=dict(lower=lower,upper=upper,pinion=pin,upper_contact_ratio=contact(upper,pin),lower_contact_ratio=contact(lower,lower),minimum_unshifted_teeth=math.ceil(2/math.sin(alpha)**2),pinion_root_radial_material_outside_plate_mm=rootwall,minimum_root_chord_assumption_mm=1,minimum_plate_rim_assumption_mm=1.2,assumed_process='Fine resin prototype; 1.0mm tooth-root chord and1.2mm radial root material are design screens, not measured printer/material minima; FDM unqualified.',servo=dict(before_ratio=30/42,after_ratio=ratio,before_travel_deg=30*30/42,after_travel_deg=30*ratio,motor_axis_x_z_mm=list(c.axes(v)[1]),rated_6V_Nm=1.5*.0980665,source='Pinned Feetech A/0 p4: rated1.5kg.cm at6V; stall6kg.cm is NOT continuous rating'),load_screen=dict(finger_force_each_assumed_N=F,tip_axial_lever_mm=lever,each_jaw_torque_Nm=jaw_torque,servo_torque_ideal_Nm=servo_torque,required_efficiency_for_6V_rating=servo_torque/(1.5*.0980665),upper_tangential_force_N=upper_ft,lower_tangential_force_N=lower_ft,upper_face_mm=face,lewis_form_factor=Y,lewis_nominal_bending_MPa=upper_ft/(face*v['drive_module']*Y),qualification='Ideal static only: no friction/backlash/dynamics/fillet/stress concentrations, actual resin fatigue or measured strength. The 1N-per-tip example exceeds continuous6V rating even at100% efficiency; do not imply that grip rating. No physical servo actuation.'),before=envelopes(before),after=envelopes(mech),gear_projection=gear_envelopes,finite_sector_contact=dict(samples=samples,max_lower_gap_mm=max(q['lower_mesh_gap_mm'] for q in samples),max_upper_gap_mm=max(q['upper_mesh_gap_mm'] for q in samples),maximum_gap_budget_mm=backlash+.01,method='Actual STL slices through each gear level; gap sampled every0.25deg to reject missing sector teeth. Gap is consistent with backlash, not measured contact under load.'),references=['https://khkgears.net/gear-knowledge/gear-technical-reference/calculation-gear-dimensions/','https://khkgears.us/media/e5hdctid/gear-solutions_khk_addendum-modification-and-undercut.pdf'])
r['passed']=bool(min(g['teeth'] for g in [lower,upper,pin])>=r['minimum_unshifted_teeth'] and min(g['root_chord_mm'] for g in [lower,upper,pin])>=1 and rootwall>=1.2-1e-6 and min(r['upper_contact_ratio'],r['lower_contact_ratio'])>1.4 and max(max(q['lower_mesh_gap_mm'],q['upper_mesh_gap_mm']) for q in samples)<=backlash+.01)
r['input_sha256']={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'params.json',HERE/'check_gears.py',HERE/'geometry_checks.json',HERE/'closure_checks.json']}
(HERE/'gear_checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:q for k,q in r.items() if k not in ['finite_sector_contact','input_sha256']},indent=2));raise SystemExit(0 if r['passed'] else 1)
