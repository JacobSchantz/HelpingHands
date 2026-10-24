"""Base 25 / Gripper 29: actual meshes, all pairs, explicit prototype budgets.
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
 if k in ('pinion','plate_screws','plate_washers','capture_ring','stock_plate','center_screw','plate_tools','center_tools'):return np.array([pin[0],0,pin[1]]),-r
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
 bodies={k:solid(m) for k,m in meshes.items() if k in PARTS+['motor','stock_plate','pivot_screws','pivot_washers','pivot_nuts']}
 failures=[]
 for angle in np.linspace(0,v['max_angle'],121):
  for k,probe in probes.items():
   c,r=motion(k,v);tool=probe.translate(-c).rotate((0,float((angle-15)*r),0)).translate(c) if r else probe
   for name,body in bodies.items():
    c,r=motion(name,v);obj=body.translate(-c).rotate((0,float((angle-15)*r),0)).translate(c) if r else body
    vol=(tool^obj).volume()
    if vol>1e-4:failures.append(dict(tool=k,body=name,angle=float(angle),volume=float(vol)))
 straight=solid(trimesh.load_mesh(HERE/'exports/reference/case_straight_tools.stl'))
 straight_overlap=float((straight^bodies['motor']).volume())
 return dict(passed=not failures,straight_case_access_passed=straight_overlap<1e-4,straight_case_overlap_mm3=straight_overlap,near_ear_driver_tilt_deg=v['case_tool_tilt'],failures=failures,angles=121,shaft_d_mm=v['tool_d'],length_mm=v['tool_len'],limitation='Driver shaft envelopes: near ear screws require 10 degree tilt; straight access fails. Physical engagement of tilted Torx driver unverified. Install pinion and plate screws with spline center capture; integral fingers seat before local washer/bolt retainers. Physical tool handles, resin fits and real cable bend unverified.')

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
def retention(meshes,v):
 radial=(v['washer_d']-(v['post_d']*v['scale_factor']+2*v['base_clear']))/2
 gap=min(meshes[k].bounds[0,1] for k in ('left','right'))-meshes['pivot_washers'].bounds[1,1]
 nuts=meshes['pivot_nuts'];screws=meshes['pivot_screws']
 engage=min(screws.bounds[1,1],nuts.bounds[1,1])-nuts.bounds[0,1]
 escape={k:float((solid(meshes[k]).translate((0,-1,0))^solid(meshes['pivot_washers'])).volume()) for k in ('left','right')}
 endplay=float(gap+v['top_gap'])
 return dict(passed=bool(radial>=.7 and gap>=.19 and engage>=v['pivot_nut_h']-1e-4 and min(escape.values())>1),radial_capture_mm=radial,lower_gap_mm=float(gap),endplay_budget_mm=endplay,nut_engagement_mm=float(engage),escape_controls_mm3=escape,sleeve_wall_mm=(v['post_d']*v['scale_factor']-v['pivot_bore'])/2,load_path='Separate gear layers -> hex blade shaft -> smooth sleeve and M2 steel core -> overhead base. Washer/head stops downward escape; overhead base stops upward escape. Hex key fit and full-depth sockets provide torque transfer; axial endplay must be measured.',limitation='1.1 mm sleeve wall, keyed fits, nut locking, neck bending, clamp crush and strength remain physical tests.')
def outside_contacts(meshes,v):
 fail=[];p=v['pivot_spacing']*v['scale_factor']/2
 shapes={k:band_shape(meshes[k]) for k in ['left','right']}
 original={k:solid(m) for k,m in meshes.items()}
 for a in np.linspace(0,30,121):
  posed={}
  for k,m in original.items():
   c,r=motion(k,v);posed[k]=m.translate(-c).rotate((0,float((a-15)*r),0)).translate(c) if r else m
  for k,sgn in [('left',-1),('right',1)]:
   t=math.radians((a-15)*sgn);co,si=math.cos(t),math.sin(t);cx=sgn*p
   shape=affine_transform(shapes[k],[co,si,-si,co,cx*(1-co),cx*si])
   for z in (15,25,35):
    patch=shape.intersection(box(-100,z-1.5,100,z+1.5))
    if patch.is_empty:fail.append(dict(angle=float(a),jaw=k,reason='no contact surface',z=z));continue
    x=patch.bounds[2 if sgn>0 else 0];probe=mf.Manifold.cube((8,5,3)).translate((x+.1 if sgn>0 else x-8.1,-2.5,z-1.5))
    for name,m in posed.items():
     if name==k or name.startswith(k+'_'):continue
     vol=float((probe^m).volume())
     if vol>1e-4:fail.append(dict(angle=float(a),jaw=k,body=name,z=z,volume_mm3=vol))
 return dict(passed=not fail,probes=726,failures=fail,qualification='8 mm outside approach at Z 15/25/35, Y -2.5..2.5; not complete-hand acceptance.')
def main():
 v=params.values();meshes={k:trimesh.load_mesh(HERE/f'exports/parts/{k}.stl') for k in PARTS+['motor','stock_plate','left','right']}
 for k in REFS:
  if not k.endswith('_tools'):meshes[k]=trimesh.load_mesh(HERE/f'exports/reference/{k}.stl')
 checks=[]
 for folder in ['parts','print']:
  for k in (PARTS if folder=='parts' else PRINTS):
   m=trimesh.load_mesh(HERE/f'exports/{folder}/{k}.stl');checks.append(dict(part=k,folder=folder,passed=bool(m.is_watertight and len(m.split())==({'left':2,'right':3,'ear_spacers':4}.get(k,1)) and m.volume>0 and (folder!='print' or abs(m.bounds[0,2])<1e-5)),min_print_z_mm=float(m.bounds[0,2]) if folder=='print' else None,genus=(2-m.euler_number)//2))
 # Compare only the working band; the deliberately stepped overhead transmission is asymmetric.
 a=meshes['left'].copy();a.vertices[:,0]*=-1
 a=clipped(a,-2.999,2.999);b=clipped(meshes['right'],-2.999,2.999)
 symmetric=max(trimesh.proximity.closest_point(a,b.vertices)[1].max(),trimesh.proximity.closest_point(b,a.vertices)[1].max())
 stationary=['ear_spacers','spacer_screws','base','pivot_screws','pivot_washers','pivot_nuts'];areas=[]
 for k in stationary:
  m=meshes[k]
  if m.bounds[0,1]<3 and m.bounds[1,1]>-3:areas.append(projection(clipped(m,-3,3)))
 from shapely.ops import unary_union
 band=unary_union(areas);p,pin,ratio=axes(v)
 from shapely.geometry import Point
 budget=unary_union([Point(s*p,0).buffer(2.21,quad_segs=128) for s in [-1,1]])
 r=rear_clearance(meshes,v)
 brackets=HERE/'spacing_search.json'
 if brackets.exists():
  search=json.loads(brackets.read_text());r['spacing_search']=search;r['tighter_candidate_passed']=search['candidates'][-2]['passed']
 hw={k:len(meshes[k].split()) for k in ['plate_washers','spacer_screws','plate_screws','case_screws','pivot_screws','pivot_washers','pivot_nuts','center_screw']}
 bom=dict(before_printed=4,after_printed=12,before_total=19,after_total=33,purchased=dict(plate_washers=2,spacer_screws=4,motor=1,spline_plate=1,plate_screws=2,case_screws=4,center_screw=1,pivot_screws=2,pivot_washers=2,pivot_nuts=2),exported_hardware_components=hw,manifest_discrete_count=12+2+sum(hw.values()),change='12 prints plus 21 purchased pieces = 33 total. Four extra screws attach motor spacers. Flat keyed gear layers and solid blades retain original tips.')
 controls=[]
 for a in [0,15,30]:
  posed={}
  for k in ['pinion','left','right']:
   c,r0=motion(k,v);posed[k]=solid(meshes[k]).translate(-c).rotate((0,float((a-15)*r0),0)).translate(c)
  c,_=motion('pinion',v);badpin=posed['pinion'].translate(-c).rotate((0,4,0)).translate(c)
  c,_=motion('left',v);badleft=posed['left'].translate(-c).rotate((0,4,0)).translate(c)
  controls.append(dict(angle=a,pinion_phase_overlap_mm3=float((badpin^posed['right']).volume()),jaw_phase_overlap_mm3=float((badleft^posed['right']).volume())))
 control_pass=all(min(x['pinion_phase_overlap_mm3'],x['jaw_phase_overlap_mm3'])>1e-4 for x in controls)

 report=dict(meshes=checks,rear_clearance=r,bom=bom,full_stroke=collisions({k:m for k,m in meshes.items() if k not in ['left','right']},v),tool_access=tool_access({k:m for k,m in meshes.items() if k not in ['left','right']},v),retention=retention(meshes,v),finger_band_symmetry=dict(passed=bool(symmetric<1e-4),mirror_surface_error_mm=float(symmetric)),motor_center=dict(passed=abs(pin[0])<1e-5,output_axis_x_mm=pin[0],body_x_bounds_mm=meshes['motor'].bounds[:,0].tolist(),cable_x_bounds_mm=meshes['cable'].bounds[:,0].tolist(),asymmetries='Motor output is offset along its longitudinal Z, not X; body and ear placement centered on X=0. Actual case details, rotor plate 3-hole pattern and cable are not promised mirror-exact. Right jaw alone carries upper drive teeth; lower jaw surfaces mirror.'),support_band=dict(passed=band.difference(budget).area<.01,area_mm2=band.area,off_pivot_area_mm2=band.difference(budget).area),outside_contacts=outside_contacts(meshes,v),wrong_phase_control=dict(passed=control_pass,phase_error_deg=4,controls=controls),swept_bounds=swept_bounds({k:m for k,m in meshes.items() if k not in ['left','right']},v),qualification='CAD-only prototype. Whole-hand fit reported separately; no ergonomic/strength acceptance or motor actuation.')
 report['input_sha256']={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'params.json',HERE/'gripper.scad',HERE/'large_source.scad',HERE/'compact_source.scad',HERE/'params.scad',HERE/'check_geometry.py',HERE/'viewer_parts.json']+list((HERE/'exports').rglob('*.stl'))}
 report['passed']=all(x['passed'] for x in checks) and all(report[k]['passed'] for k in ['rear_clearance','full_stroke','tool_access','retention','finger_band_symmetry','motor_center','support_band','outside_contacts','wrong_phase_control'])
 (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['passed','rear_clearance','bom','motor_center','support_band']},indent=2))
 for k in ['full_stroke','tool_access','outside_contacts']:
  print(k,report[k]['passed'],report[k]['failures'][:10])
 raise SystemExit(0 if report['passed'] else 1)
if __name__=='__main__':main()
