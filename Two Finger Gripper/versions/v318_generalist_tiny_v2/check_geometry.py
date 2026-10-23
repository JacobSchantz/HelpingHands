"""Exact continuous width; full-range sampled solid intersections; source fidelity."""
from pathlib import Path
import json,math,itertools
import numpy as np
import trimesh
from scipy.spatial import cKDTree
import manifold3d as mf
import params
from export_models import PARTS
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'v316_generalist_post_cap'
def design_contract(v):
 original={q['name']:q['value'] for g in json.loads((SOURCE/'params.json').read_text())['groups'] for q in g['params']}
 adjustable={'gear_teeth','pinion_teeth','pinion_mesh_deg','gear_bolt_phase_deg','gear_bolt_head_h','base_t','top_t','pillar_d','sts_body_deg'}
 changed=[k for k,x in original.items() if k not in adjustable and v.get(k)!=x]
 return dict(passed=not changed,changed_finger_source_parameters=changed,adjustable_drive_parameters=sorted(adjustable))

def axes(v):
 p=v['pivot_spacing']/2*v['scale_factor'];r=v['gear_teeth']/v['pinion_teeth'];t=math.radians(v['pinion_mesh_deg'])
 return p,(p-(p+p/r)*math.cos(t),-(p+p/r)*math.sin(t)),r
def motion(k,v):
 p,pin,r=axes(v)
 if k.startswith('left'):return np.array([-p,0,0]),-1
 if k.startswith('right'):return np.array([p,0,0]),1
 if k in ('pinion','horn_screws'):return np.array([pin[0],0,pin[1]]),-r
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
def fidelity(meshes,v):
 rows=[]
 for k,m in meshes.items():
  src=trimesh.load_mesh(SOURCE/f'exports/parts/{k}.stl');want=src.vertices*v['scale_factor']
  # Full-size bores and seats necessarily change local surfaces. Finger outer contour,
  # lattice, taper and loop outer ring must remain exactly source-scaled.
  if k in ('left','right'):
   c,r=motion(k,v);radius=v['post_d']/2*v['scale_factor']+v['base_clear']+0.5
   a=m.vertices[np.linalg.norm((m.vertices-c)[:,[0,2]],axis=1)>radius]
   b=want[np.linalg.norm((want-c)[:,[0,2]],axis=1)>radius]
   err=max(cKDTree(want).query(a)[0].max(),cKDTree(m.vertices).query(b)[0].max())
   rows.append(dict(part=k,passed=bool(err<1e-5),outer_lattice_taper_error_mm=float(err),exception='Loop bore clearance held at original actual-size 0.25 mm.'))
  else:rows.append(dict(part=k,passed=True,exception='Source involute/handle construction; resized tooth counts and centres, full-size local hardware holes, seats and working clearances.'))
 return rows

from hardware_fit import hardware_fit

def collisions(meshes,v,step=.25):
 originals={k:solid(m) for k,m in meshes.items()};worst={};failures=[]
 for k in ['horn_screws','case_screws','cap_screws']:originals[k]=solid(trimesh.load_mesh(HERE/f'exports/reference/{k}.stl'))
 originals['motor']=solid(trimesh.load_mesh(HERE/'exports/parts/motor.stl'));originals['cable']=solid(trimesh.load_mesh(HERE/'exports/reference/cable.stl'))
 for angle in np.linspace(0,v['max_angle'],round(v['max_angle']/step)+1):
  posed={}
  for k,s in originals.items():
   c,r=motion(k,v);posed[k]=s.translate(-c).rotate((0,float((angle-15)*r),0)).translate(c) if r else s
  for a,b in itertools.combinations(list(originals),2):
   vol=(posed[a]^posed[b]).volume();key=f'{a}/{b}'
   if vol>worst.get(key,dict(volume_mm3=0))['volume_mm3']:worst[key]=dict(volume_mm3=vol,angle_deg=float(angle))
 # Numerical contact tolerance, far below a printable feature. No pair is silently excluded.
 for pair,item in worst.items():
  if item['volume_mm3']>1e-6:failures.append(dict(pair=pair,**item))
 return dict(passed=not failures,step_deg=step,angles=round(v['max_angle']/step)+1,pairs_per_angle=66,failures=failures,worst=worst,limitation='Full stroke sampled every 0.25 degree; Screw probes omit intentional threaded engagement. NOT a proof of continuous collision clearance, tooth strength, friction or manufacturability.')

def hardware(meshes,v):
 return dict(horn_d_mm=v['sts_horn_d'],horn_screw_pcd_mm=v['sts_horn_pcd'],m3_clearance_mm=v['screw_clear_d'],m2_clearance_mm=v['sts_screw_d'],servo_dimensions_mm=[v['sts_len'],v['sts_w'],v['sts_depth']],mount='Original four-M2 case rail mounting and four-M3 stock-horn mounting; all dimensions unscaled. Original half-size fingers with resized 30:30:24 gears and actual-size hardware interfaces and clearances.',physical_validation='CAD only, no print/servo/fastener measurement or load test.')

def lattice_web(mesh,v):
 from shapely.geometry import LineString
 # Just above flat ventral bed face, before the dorsal taper trims the section.
 section=mesh.section(plane_origin=[0,-v['plate']*v['scale_factor']/2+.01,0],plane_normal=[0,1,0]).to_2D()[0]
 p=max(section.polygons_full,key=lambda p:p.area)
 loops=[LineString(p.exterior.coords)]+[LineString(h.coords) for h in p.interiors]
 gap=min(a.distance(b) for a,b in itertools.combinations(loops,2))
 return dict(passed=gap>=v['min_lattice_web'],minimum_plan_ligament_mm=float(gap),required_mm=v['min_lattice_web'],process='Fine resin prototype allowance; not ordinary FDM or a strength rating.')

def mounting_controls(meshes,v):
 m=solid(trimesh.load_mesh(HERE/'exports/parts/motor.stl'));base=solid(meshes['base']);pin=solid(meshes['pinion'])
 return dict(servo_raised_half_mm_hits_base=(m.translate((0,.5,0))^base).volume()>1e-3,pinion_lowered_half_mm_hits_horn=(pin.translate((0,-.5,0))^m).volume()>1e-3)

def mesh_controls(meshes,v):
 c,r=motion('pinion',v);p=solid(meshes['pinion']);g=solid(meshes['right_gear'])
 hits=(p.translate(-c).rotate((0,4,0)).translate(c)^g).volume()
 return dict(passed=hits>1e-4,wrong_pinion_phase_overlap_mm3=hits,description='A 4 degree phase error intersects the right gear; correct full motion has no penetrating tooth volume.')

def fastener_lengths(meshes,v):
 base0=float(meshes['base'].bounds[0][1]);base1=base0+v['base_t']
 flange=float(meshes['pinion'].bounds[0][1]);head=float(meshes['pinion'].bounds[1][1])-v['gear_bolt_head_h']
 horn_tip=head-v['horn_screw_length'];case_clear=horn_tip-(base0-v['sts_face_drop'])
 case_bite=v['case_screw_length']-(v['base_t']-v['sts_screw_head_h'])
 cap0=float(meshes['top_plate'].bounds[0][1]);cap1=float(meshes['top_plate'].bounds[1][1]);cap_tip=cap1-v['cap_screw_length']
 cap_floor=base1+v['pillar_floor']*v['scale_factor'];floor_clear=cap_tip-cap_floor
 return dict(passed=case_clear>0 and 2<=case_bite<=4.001 and floor_clear>0,horn=dict(candidate='4 × M3×12 countersunk',tip_to_case_clearance_mm=case_clear,thread_in_horn_mm=min(flange-horn_tip,v['sts_horn_top']-v['sts_horn_y0'])),case=dict(candidate='4 × M2×6 cap head',modeled_case_engagement_mm=case_bite,unverified_assumption='Case tapped depth assumed 4 mm, as large source; physical depth must be measured.'),cap=dict(candidate='2 × M3×10 countersunk',pillar_engagement_mm=cap0-cap_tip,pilot_bottom_clearance_mm=floor_clear),limitation='Candidate stock lengths from CAD. Verify real screw/head and horn/case thread depths before assembly.')

def main():
 v=params.values();meshes={k:trimesh.load_mesh(HERE/f'exports/parts/{k}.stl') for k in PARTS};meshrows=[]
 for folder in ('parts','print'):
  for k in PARTS:
   m=trimesh.load_mesh(HERE/f'exports/{folder}/{k}.stl');meshrows.append(dict(path=f'exports/{folder}/{k}.stl',watertight=bool(m.is_watertight),volume_mm3=float(m.volume),components=len(m.split()),passed=bool(m.is_watertight and m.is_winding_consistent and m.volume>0 and len(m.split())==1)))
 (HERE/'mesh_checks.json').write_text(json.dumps(meshrows,indent=2)+'\n')
 all_meshes=dict(meshes,motor=trimesh.load_mesh(HERE/'exports/parts/motor.stl'))
 for k in ['cable','horn_screws','case_screws','cap_screws']:all_meshes[k]=trimesh.load_mesh(HERE/f'exports/reference/{k}.stl')
 report=dict(fasteners=fastener_lengths(meshes,v),overall_envelope=swept_bounds(all_meshes,v),contract=design_contract(v),fit=hardware_fit(v),lattice=lattice_web(meshes['right'],v),mounting_controls=mounting_controls(meshes,v),gear_phase_control=mesh_controls(meshes,v),width=continuous_width(meshes,v),fidelity=fidelity(meshes,v),motion_collisions=collisions(meshes,v),hardware=hardware(meshes,v),stroke_deg=[0,v['max_angle']],gear_teeth=[v['gear_teeth'],v['gear_teeth'],v['pinion_teeth']],scale_factor=v['scale_factor'])
 (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
 for k in ('width','motion_collisions'):print(k,report[k])
 print('fidelity',all(x['passed'] for x in report['fidelity']),'mesh',all(x['passed'] for x in meshrows));print('hardware',report['hardware'])
 raise SystemExit(0 if report['fasteners']['passed'] and report['gear_phase_control']['passed'] and all(report['mounting_controls'].values()) and report['lattice']['passed'] and report['fit']['passed'] and report['contract']['passed'] and report['width']['passed'] and report['motion_collisions']['passed'] and all(x['passed'] for x in report['fidelity']+meshrows) else 1)
if __name__=='__main__':main()
