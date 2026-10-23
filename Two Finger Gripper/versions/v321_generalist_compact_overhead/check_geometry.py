"""Base 20 actual hardware, exact retained fingers and full-stroke sampled collision checks."""
from pathlib import Path
import json, math, itertools
import numpy as np
import trimesh
import manifold3d as mf
from scipy.spatial import cKDTree
import params
from export_models import PARTS, REFS
HERE=Path(__file__).resolve().parent

def axes(v):
 p=v['pivot_spacing']/2*v['scale_factor'];r=v['gear_teeth']/v['pinion_teeth'];t=math.radians(v['pinion_mesh_deg'])
 return p,(p-(p+p/r)*math.cos(t),-(p+p/r)*math.sin(t)),r

def motion(k,v):
 p,pin,r=axes(v)
 if k.startswith('left'):return np.array([-p,0,0]),-1
 if k.startswith('right'):return np.array([p,0,0]),1
 if k in ('pinion','plate_screws','stock_plate','center_screw','plate_tools','center_tools'):return np.array([pin[0],0,pin[1]]),-r
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

def lattice_web(mesh,v):
 from shapely.geometry import LineString
 # Just above flat ventral bed face, before the dorsal taper trims the section.
 section=mesh.section(plane_origin=[0,-v['plate']*v['scale_factor']/2+.01,0],plane_normal=[0,1,0]).to_2D()[0]
 p=max(section.polygons_full,key=lambda p:p.area)
 loops=[LineString(p.exterior.coords)]+[LineString(h.coords) for h in p.interiors]
 gap=min(a.distance(b) for a,b in itertools.combinations(loops,2))
 return dict(passed=gap>=v['min_lattice_web'],minimum_plan_ligament_mm=float(gap),required_mm=v['min_lattice_web'],process='Fine resin prototype allowance; not ordinary FDM or a strength rating.')

def mesh_controls(meshes,v):
 c,r=motion('pinion',v);p=solid(meshes['pinion']);g=solid(meshes['right_gear'])
 hits=(p.translate(-c).rotate((0,4,0)).translate(c)^g).volume()
 return dict(passed=hits>1e-4,wrong_pinion_phase_overlap_mm3=hits,description='A 4 degree phase error intersects the right gear; correct full motion has no penetrating tooth volume.')

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
def clearances(meshes,v):
 band=[float(min(meshes[k].bounds[0,1] for k in ['left','right'])),float(max(meshes[k].bounds[1,1] for k in ['left','right']))]
 # Pinion shares tooth faces with both overhead side sectors.
 gap=float(meshes['pinion'].bounds[0,1])-v['plate']*v['scale_factor']/2
 src=HERE.parent/'v319_generalist_hls3606m/exports/parts'
 hardware=[]
 for k in ['motor','stock_plate','pinion']:
  old=trimesh.load_mesh(src/f'{k}.stl');old.vertices[:,1]*=-1
  shift=meshes[k].bounds[0,1]-old.bounds[0,1]
  old.vertices[:,1]+=shift
  error=max(cKDTree(old.vertices).query(meshes[k].vertices)[0].max(),cKDTree(meshes[k].vertices).query(old.vertices)[0].max())
  hardware.append(dict(part=k,rigid_inversion_error_mm=float(error),passed=bool(error<1e-4)))
 return dict(passed=bool(abs(gap-v['drive_gap'])<1e-4 and all(h['passed'] for h in hardware)),finger_band_y_mm=[-v['plate']*v['scale_factor']/2,v['plate']*v['scale_factor']/2],gear_to_band_gap_mm=gap,hardware=hardware,description='Teeth entirely above band; only smaller finger roots and 3 mm pivot posts enter band; short hex bosses couple overhead gears. No long transmission shafts.')

def tool_access(meshes,v):
 probes={k:solid(trimesh.load_mesh(HERE/f'exports/reference/{k}.stl')) for k in REFS if k.endswith('_tools') and k!='case_straight_tools'}
 bodies={k:solid(m) for k,m in meshes.items() if k in PARTS+['motor','stock_plate']}
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
 return dict(passed=not failures,straight_case_access_passed=straight_overlap<1e-4,straight_case_overlap_mm3=straight_overlap,near_ear_driver_tilt_deg=v['case_tool_tilt'],failures=failures,angles=121,shaft_d_mm=v['tool_d'],length_mm=v['tool_len'],limitation='Driver shaft envelopes: near ear screws require 10 degree tilt; straight access fails. Physical engagement of tilted PH0 driver unverified. Install plate/spline retaining screw before pinion; finger bosses seat before cap. Physical tool handles, resin fits and real cable bend unverified.')

def main():
 v=params.values();meshes={k:trimesh.load_mesh(HERE/f'exports/parts/{k}.stl') for k in PARTS+['motor','stock_plate']}
 for k in [x for x in REFS if not x.endswith('_tools')]:meshes[k]=trimesh.load_mesh(HERE/f'exports/reference/{k}.stl')
 rows=[]
 for folder in ('parts','print'):
  for k in PARTS:
   m=trimesh.load_mesh(HERE/f'exports/{folder}/{k}.stl');rows.append(dict(path=f'exports/{folder}/{k}.stl',passed=bool(m.is_watertight and m.is_winding_consistent and m.volume>0 and len(m.split())==1),genus=(2-m.euler_number)//2,volume_mm3=float(m.volume),min_print_z_mm=float(m.bounds[0,2]) if folder=='print' else None))
 fidelity=[]
 for k in ['left','right']:
  src=trimesh.load_mesh(HERE.parent/f'v318_generalist_tiny_v2/exports/parts/{k}.stl')
  a=src.vertices[src.vertices[:,2]>40];b=meshes[k].vertices[meshes[k].vertices[:,2]>40]
  err=max(trimesh.proximity.closest_point(src,b)[1].max(),trimesh.proximity.closest_point(meshes[k],a)[1].max())
  fidelity.append(dict(part=k,passed=bool(err<1e-5),distal_surface_error_mm=float(err),region='Exported Z > 40 mm, beyond the retired handle hooks'))
 # Use actual exported seating faces to calculate M2x4 engagement, not nominal servo dimensions.
 face=float(meshes['stock_plate'].bounds[0,1]);g1=float(meshes['pinion'].bounds[0,1]);head0=g1+v['hls_plate_head_recess']+v['hls_plate_head_h']
 grip=face-head0;engagement=v['hls_plate_screw_length']-grip
 fasteners=dict(passed=bool(1<=engagement<=2),plate_grip_mm=grip,plate_engagement_mm=engagement,plate='3 × M2×4, reuses 2 mm disk threaded thickness; actual thread depth unmeasured')
 motor=trimesh.load_mesh(HERE/'reference/servo.stl');plate=trimesh.load_mesh(HERE/'reference/stock_plate.stl')
 body_ok=np.allclose(motor.extents,[32,31.9,12],atol=.001) and np.allclose(plate.extents,[18,4.5,18],atol=.001)
 base=solid(meshes['base']);motor_s=solid(meshes['motor']);pin=solid(meshes['pinion']);plate_s=solid(meshes['stock_plate'])
 controls=dict(passed=bool(body_ok and (motor_s.translate((0,-.5,0))^base).volume()>1e-3 and (pin.translate((0,.5,0))^plate_s).volume()>1e-3),unscaled_hardware=bool(body_ok),case_ear_screw_engagement_mm=v['hls_case_screw_length']-v['hls_ear_thickness'],case_pilot_tip_clearance_mm=v['hls_case_pilot_depth']-(v['hls_case_screw_length']-v['hls_ear_thickness']))
 rep=dict(tool_access=tool_access(meshes,v),clearances=clearances(meshes,v),hardware_controls=controls,meshes=rows,fidelity=fidelity,lattice=lattice_web(meshes['right'],v),overall_envelope=swept_bounds(meshes,v),gear_phase_control=mesh_controls(meshes,v),fasteners=fasteners,motion_collisions=collisions(meshes,v))
 (HERE/'geometry_checks.json').write_text(json.dumps(rep,indent=2)+'\n')
 for k,x in rep.items():print(k,x if k not in ('motion_collisions','overall_envelope') else ({z:x[z] for z in ('passed','failures') } if k=='motion_collisions' else x['width_depth_height_mm']),flush=True)
 raise SystemExit(0 if all(x['passed'] for x in rows+fidelity) and rep['tool_access']['passed'] and rep['clearances']['passed'] and rep['hardware_controls']['passed'] and rep['lattice']['passed'] and rep['fasteners']['passed'] and rep['gear_phase_control']['passed'] and rep['motion_collisions']['passed'] else 1)
if __name__=='__main__':main()
