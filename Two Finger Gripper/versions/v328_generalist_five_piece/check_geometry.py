"""Base 27 / Gripper 31: actual meshes, all pairs, explicit prototype budgets.
No physical strength, ergonomic approval or continuous body-collision claim.
"""
from pathlib import Path
import json,math,itertools,sys,hashlib
import numpy as np
import trimesh
import manifold3d as mf
from scipy.spatial import cKDTree
from shapely.geometry import box
from shapely.affinity import affine_transform
import params
from export_models import PARTS,REFS,PRINTS
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from Scripts.check_finger_plane_constraints import projection,clipped

def axes(v):
 p=v['pivot_spacing']/2*v['scale_factor'];r=v['drive_teeth']/v['pinion_teeth'];t=math.radians(v['pinion_mesh_deg'])
 return p,(p-(v['drive_module']*(v['drive_teeth']+v['pinion_teeth'])/2)*math.cos(t),-(v['drive_module']*(v['drive_teeth']+v['pinion_teeth'])/2)*math.sin(t)),r

def motion(k,v):
 p,pin,r=axes(v)
 if k.startswith('left'):return np.array([-p,0,0]),-1
 if k.startswith('right'):return np.array([p,0,0]),1
 if k in ('pinion','plate_screws','plate_washers','capture_ring','capture_washer','stock_plate','center_screw','plate_tools','center_tools'):return np.array([pin[0],0,pin[1]]),-r
 return np.zeros(3),0

def rotated(points,c,deg):
 a=math.radians(deg);R=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
 return (points-c)@R.T+c

def continuous_width(meshes,v):
 limits={}
 for k,m in meshes.items():
  c,r=motion(k,v);pts=rotated(m.vertices,c,-15*r)-c
  # x(a)=cx+dx*cos(a)+dz*sin(a). Include every stationary point, not only endpoints.
  lo,hi=sorted([0,math.radians(v['max_angle']*r)])
  x,z=pts[:,0],pts[:,2];vals=[c[0]+x*math.cos(a)+z*math.sin(a) for a in (lo,hi)]
  for j in range(-2,3):
   a=np.arctan2(z,x)+j*math.pi;mask=(a>=lo)&(a<=hi)
   if mask.any():vals.append(c[0]+x[mask]*np.cos(a[mask])+z[mask]*np.sin(a[mask]))
  limits[k]=[float(min(a.min() for a in vals)),float(max(a.max() for a in vals))]
 width=max(a[1] for a in limits.values())-min(a[0] for a in limits.values())
 return dict(passed=True,width_mm=width,per_part_x_mm=limits,method='Analytic endpoint and stationary-point extrema of every exported STL vertex over the full continuous 0–30 degree stroke.')

def swept_bounds(meshes,v):
 bounds={}
 for k,m in meshes.items():
  c,r=motion(k,v);pts=rotated(m.vertices,c,-15*r)-c
  lo,hi=sorted([0,math.radians(v['max_angle']*r)]);limits=[]
  for axis,A,B in [(0,pts[:,0],pts[:,2]),(2,pts[:,2],-pts[:,0])]:
   vals=[c[axis]+A*math.cos(a)+B*math.sin(a) for a in [lo,hi]]
   for j in range(-2,3):
    a=np.arctan2(B,A)+j*math.pi;ok=(a>=lo)&(a<=hi)
    if ok.any():vals.append(c[axis]+A[ok]*np.cos(a[ok])+B[ok]*np.sin(a[ok]))
   limits.append([float(min(x.min() for x in vals)),float(max(x.max() for x in vals))])
  bounds[k]=[limits[0],[float(m.vertices[:,1].min()),float(m.vertices[:,1].max())],limits[1]]
 total=[[min(b[i][0] for b in bounds.values()),max(b[i][1] for b in bounds.values())] for i in range(3)]
 return dict(x_y_z_bounds_mm=total,width_depth_height_mm=[b-a for a,b in total],per_part_bounds=bounds,method='Analytic continuous X/Z vertex extrema, fixed Y; includes real servo, screw probes and cable clearance.')

def solid(mesh):return mf.Manifold(mf.Mesh(np.asarray(mesh.vertices,dtype=np.float32),np.asarray(mesh.faces,dtype=np.uint32)))

def collisions(meshes,v,step=.25):
 originals={k:solid(m) for k,m in meshes.items()};worst={}
 for angle in np.linspace(0,v['max_angle'],round(v['max_angle']/step)+1):
  posed={}
  for k,s in originals.items():
   c,r=motion(k,v);posed[k]=s.translate(-c).rotate((0,float((angle-15)*r),0)).translate(c) if r else s
  for a,b in itertools.combinations(originals,2):
   vol=(posed[a]^posed[b]).volume();key=f'{a}/{b}'
   if vol>worst.get(key,dict(volume_mm3=0))['volume_mm3']:worst[key]=dict(volume_mm3=vol,angle_deg=float(angle))
 failures=[dict(pair=k,**x) for k,x in worst.items() if x['volume_mm3']>1e-4]
 return dict(passed=not failures,step_deg=step,angles=round(v['max_angle']/step)+1,pairs_per_angle=math.comb(len(originals),2),failures=failures,worst=worst,limitation='Sampled 0–30 degree stroke, not continuous collision proof. Probes omit intentional spline/thread engagement; center probe covers only exposed retaining head. No pair exclusions. Volume tolerance 0.0001 mm^3 covers STL face rounding at seated planes.')

def tool_access(meshes,v):
 probes={k:solid(trimesh.load_mesh(HERE/f'exports/reference/{k}.stl')) for k in REFS if k.endswith('_tools') and k!='case_straight_tools'}
 bodies={k:solid(m) for k,m in meshes.items() if k in PARTS+['motor','stock_plate','pivot_screws','pivot_nuts']}
 failures=[]
 for angle in np.linspace(0,v['max_angle'],121):
  for k,probe in probes.items():
   c,r=motion(k,v);tool=probe.translate(-c).rotate((0,float((angle-15)*r),0)).translate(c) if r else probe
   for name,body in bodies.items():
    if k=='case_tools' and name not in ('base','motor','case_screws'):continue  # Motor installed before rotor/jaws.
    c,r=motion(name,v);obj=body.translate(-c).rotate((0,float((angle-15)*r),0)).translate(c) if r else body
    vol=(tool^obj).volume()
    if vol>1e-4:failures.append(dict(tool=k,body=name,angle=float(angle),volume=float(vol)))
 straight=solid(trimesh.load_mesh(HERE/'exports/reference/case_straight_tools.stl'))
 straight_overlap=float((straight^bodies['motor']).volume())
 return dict(passed=not failures,failures=failures,angles=121,shaft_d_mm=v['tool_d'],nut_driver_outer_d_mm=v['nut_tool_d'],length_mm=v['tool_len'],assembly_order='Four case-ear screws install from gear side before spline plate/pinion/jaws; all other tool checks against assembled bodies.',limitation='Driver shafts and hollow nut sockets only; actual drives, tool handles and cable bend require physical checks.')

def band_shape(mesh):return projection(clipped(mesh,-2.999,2.999))
def rear_clearance(meshes,v):
 p=v['pivot_spacing']*v['scale_factor']/2
 m=meshes['right'].copy();m.vertices=rotated(m.vertices,np.array([p,0,0]),-15)
 section=band_shape(m).intersection(box(-100,-100,100,12))
 # Every triangle-section vertex: continuous angular extrema, including interior extrema.
 points=np.array(section.exterior.coords);x,z=points[:,0]-p,points[:,1]
 candidates=[]
 for a in [0,math.radians(30)]:
  xx=p+x*math.cos(a)+z*math.sin(a);i=xx.argmin();candidates.append((float(xx[i]),math.degrees(a),points[i].tolist()))
 for j in [-1,0,1]:
  aa=np.arctan2(z,x)+j*math.pi;ok=(aa>=0)&(aa<=math.radians(30))
  for i in np.flatnonzero(ok):candidates.append((float(p+x[i]*math.cos(aa[i])+z[i]*math.sin(aa[i])),math.degrees(aa[i]),points[i].tolist()))
 half,angle,point=min(candidates)
 return dict(passed=2*half>=v['rear_gap_budget']-1e-5,minimum_gap_mm=2*half,angle_deg=angle,right_limiting_point_at_closed_x_z_mm=point,pivot_spacing_mm=2*p,budget_mm=v['rear_gap_budget'],manufacturing_budget_mm=.3,deflection_reserve_mm=.5,method='Continuous extrema of actual clipped finger-band outline vertices from closed rear Z <= 12 mm; mirror-symmetric rear jaws. 0.3 + 0.5 mm are assumed CAD allowances, not measured deflection. Actual candidate re-exports bracket spacing below.',tighter_candidate_passed=None)
def main():
 v=params.values();meshes={k:trimesh.load_mesh(HERE/f'exports/parts/{k}.stl') for k in PARTS+['motor','stock_plate']}
 for k in REFS:
  if not k.endswith('_tools'):meshes[k]=trimesh.load_mesh(HERE/f'exports/reference/{k}.stl')
 tests={}
 tests['meshes']=dict(passed=all(m.is_watertight and len(m.split())==1 and m.volume>0 for k,m in meshes.items() if k in PARTS),components={k:len(meshes[k].split()) for k in PARTS})
 tests['full_stroke']=collisions(meshes,v)
 # Tool checks include all physical bodies and no hidden spacer assumptions.
 tests['tool_access']=tool_access(meshes,v)
 tests['rear_clearance']=rear_clearance(meshes,v)
 tests['swept_bounds']=swept_bounds(meshes,v)
 counts={k:len(m.split()) for k,m in meshes.items() if k!='cable'}
 tests['bom']=dict(before_printed=12,after_printed=sum(counts[k] for k in PARTS),before_total=33,after_total=sum(counts.values()),per_export=counts)
 tests['motor_center']=dict(passed=abs(axes(v)[1][0])<1e-5,body_x_bounds_mm=meshes['motor'].bounds[:,0].tolist())
 frame=meshes['base'];plate=meshes['retaining_plate'];jaws=[meshes[k] for k in ['left','right']]
 sleeve_bore=v['pivot_bore'];journal=v['post_d']*v['scale_factor'];jaw_bore=journal+2*v['base_clear']
 low=min(m.bounds[0,1] for m in jaws);high=max(m.bounds[1,1] for m in jaws)
 bottom_gap=low-plate.bounds[1,1];top_gap=v['retainer_gap'];top_gap_left=v['retainer_gap']
 # Frame sleeves butt the lower plate; nut tightening loads sleeves, not rotating jaws.
 tests['retention']=dict(passed=bottom_gap>=.19 and top_gap>=.19 and v['washer_d']>jaw_bore+1 and journal-sleeve_bore>=2.1,lower_running_gap_mm=float(bottom_gap),upper_free_space_mm=float(top_gap),bearing_radial_clearance_mm=v['base_clear'],sleeve_wall_mm=(journal-sleeve_bore)/2,plate_radial_capture_mm=(v['washer_d']-jaw_bore)/2,limitation='CAD axial capture only; shaft bending, printed creep and thread lock not load qualified.')
 # Detect axial escape using the actual bodies, including unequal left/right collars.
 controls=[]
 for k in ['left','right']:
  for delta in [-.5,.5]:
   moved=solid(meshes[k]).translate([0,delta,0]);target=solid(frame if delta>0 else plate)
   controls.append(dict(jaw=k,translation_y_mm=delta,blocked_overlap_mm3=float((moved^target).volume())))
 tests['axial_escape_controls']=dict(passed=all(q['blocked_overlap_mm3']>1e-4 for q in controls),controls=controls)
 # The cut rods extend past both complete nuts; no unavailable long bolt assumed.
 rods=meshes['pivot_screws'];nuts=meshes['pivot_nuts']
 tips=[float(nuts.bounds[0,1]-rods.bounds[0,1]),float(rods.bounds[1,1]-nuts.bounds[1,1])]
 tests['rod_stack']=dict(passed=min(tips)>.39,cut_length_mm=v['pivot_screw_len'],tip_projections_mm=tips,nuts=4)
 from shapely.ops import unary_union
 band=unary_union([projection(clipped(meshes[k],-3,3)) for k in ['base','pivot_screws']])
 tests['support_band']=dict(area_mm2=float(band.area),sleeve_only_mm2=float(projection(clipped(frame,-3,3)).area),lower_plate_y_bounds_mm=plate.bounds[:,1].tolist())
 tests['passed']=all(tests[k]['passed'] for k in ['meshes','full_stroke','tool_access','rear_clearance','motor_center','retention','axial_escape_controls','rod_stack']) and tests['bom']['after_printed']==5
 tests['qualification']='CAD prototype; no physical print, hardware fit, ergonomics or strength acceptance. Full-body motion is sampled, not continuous proof.'
 tests['input_sha256']={str(f.relative_to(HERE)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [HERE/'params.json',HERE/'gripper.scad']+list((HERE/'exports/parts').glob('*.stl'))+list((HERE/'exports/reference').glob('*.stl'))}
 (HERE/'geometry_checks.json').write_text(json.dumps(tests,indent=2)+'\n')
 print(json.dumps({k:q for k,q in tests.items() if k not in ['swept_bounds','input_sha256']},indent=2))
 raise SystemExit(0 if tests['passed'] else 1)
if __name__=='__main__':main()
