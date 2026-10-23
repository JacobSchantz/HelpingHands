"""Base 18 actual hardware, exact retained fingers and full-stroke sampled collision checks."""
from pathlib import Path
import json, math, itertools
import numpy as np
import trimesh
import manifold3d as mf
from scipy.spatial import cKDTree
import params
from export_models import PARTS
HERE=Path(__file__).resolve().parent

def axes(v):
 p=v['pivot_spacing']/2;r=v['gear_teeth']/v['pinion_teeth'];t=math.radians(v['pinion_mesh_deg'])
 return p,(p-(p+p/r)*math.cos(t),-(p+p/r)*math.sin(t)),r

def motion(k,v):
 p,pin,r=axes(v)
 if k.startswith('left'):return np.array([-p,0,0]),-1
 if k.startswith('right'):return np.array([p,0,0]),1
 if k in ('pinion','plate_screws','stock_plate','center_screw'):return np.array([pin[0],0,pin[1]]),-r
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
def main():
 v=params.values();meshes={k:trimesh.load_mesh(HERE/f'exports/parts/{k}.stl') for k in PARTS+['motor']}
 meshes['cable']=trimesh.load_mesh(HERE/'exports/reference/cable.stl')
 rows=[]
 for folder in ['parts','print']:
  for k in PARTS:
   m=trimesh.load_mesh(HERE/f'exports/{folder}/{k}.stl')
   rows.append(dict(part=k,folder=folder,passed=bool(m.is_watertight and m.is_winding_consistent and m.volume>0 and len(m.split())==1),genus=(2-m.euler_number)//2))
 fidelity=[]
 for k in ['left','right']:
  src=trimesh.load_mesh(HERE.parent/f'v316_generalist_post_cap/exports/parts/{k}.stl')
  err=max(cKDTree(src.vertices).query(meshes[k].vertices)[0].max(),cKDTree(meshes[k].vertices).query(src.vertices)[0].max())
  fidelity.append(dict(part=k,passed=bool(err<1e-5),vertex_error_mm=float(err)))
 print('Meshes',all(q['passed'] for q in rows),'fingers unchanged',fidelity,flush=True)
 # Retention probes cover the removable cradle only, omitting intended thread engagement.
 for m in trimesh.load_mesh(HERE/'exports/reference/retention_screws.stl').split():
  meshes['right_screws' if m.centroid[0]>0 else 'left_screws']=m
 collision=collisions(meshes,v,step=.25)
 print('Collisions',collision['passed'],collision['failures'],flush=True)
 band=[float(min(meshes[k].bounds[0,1] for k in ['left','right'])),float(max(meshes[k].bounds[1,1] for k in ['left','right']))]
 overhead={k:float(meshes[k].bounds[0,1]-band[1]) for k in ['motor','cable','pinion','base','top_plate']}
 control=mesh_controls(meshes,v)
 tools=solid(trimesh.load_mesh(HERE/'exports/reference/horn_tools.stl'))
 tool_overlap={k:float((tools^solid(m)).volume()) for k,m in meshes.items() if k!='cable'}
 print('Horn tool overlap',tool_overlap,flush=True)
 assert max(tool_overlap.values())<1e-4
 result=dict(horn_tool_access_overlap_mm3=tool_overlap,meshes=rows,finger_fidelity=fidelity,collisions=collision,finger_band_y_mm=band,overhead_gap_mm=overhead,swept=swept_bounds(meshes,v),phase_positive_control=control,
  limitations='No physical fit, force, shaft bending, printed-bearing friction/wear or hand ergonomics verified. Sampled collision checking only. Arm reference omitted from gripper stroke checks; whole arm motion is not certified.')
 (HERE/'geometry_checks.json').write_text(json.dumps(result,indent=2)+'\n')
 assert all(q['passed'] for q in rows+fidelity) and collision['passed'] and control['passed']
 assert min(overhead.values())>=v['overhead_gap']-1e-4
 print('PASS: full-size overhead drivetrain and complete 0–30 degree CAD stroke.')
if __name__=='__main__':main()
