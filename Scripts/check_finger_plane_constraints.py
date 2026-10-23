"""Geometry acceptance evidence for voice-550038ca; no human or strength certification.
Run with cad/blender/.venv/bin/python. --strict returns nonzero on failed CAD constraints.
The support-outline budget is explicit, not a claim of the physically smallest safe plate.
"""
from pathlib import Path
import argparse, importlib.util, json, math, sys
import numpy as np
import trimesh
import manifold3d as mf
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from shapely.affinity import affine_transform
ROOT=Path(__file__).resolve().parents[1]
VERSIONS=ROOT/'Two Finger Gripper/versions'
BASELINE=VERSIONS/'v321_generalist_compact_overhead'
CANDIDATE=ROOT/'Two Finger Gripper/studies/voice-550038ca-four-post-cap'

def solid(m):
 return mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def projection(m):
 return unary_union([Polygon(t[:,[0,2]]) for t in m.triangles if Polygon(t[:,[0,2]]).area>1e-9])
def clipped(m,y0,y1):
 b=m.bounds;clip=mf.Manifold.cube((float(b[1,0]-b[0,0]+2),y1-y0,float(b[1,2]-b[0,2]+2))).translate((float(b[0,0]-1),y0,float(b[0,2]-1)))
 s=solid(m)^clip;raw=s.to_mesh();return trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts,process=True)
def load(folder):
 return {p.stem:trimesh.load_mesh(p) for p in (folder/'exports/parts').glob('*.stl')}
def pose(m,k,angle):
 p=15.675;ratio=1.25
 if k.startswith('right'):c=np.array([p,0,0]);r=1
 elif k.startswith('left'):c=np.array([-p,0,0]);r=-1
 elif k in ('pinion','stock_plate'):c=np.array([p,0,-28.215]);r=-ratio
 else:return m
 a=math.radians((angle-15)*r);R=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
 out=m.copy();out.vertices=(out.vertices-c)@R.T+c;return out

def minimal_support(meshes):
 # Jaws and moving gears are excluded; inspect stationary support + axle hardware.
 names=[k for k in meshes if k not in ('left','right')]
 def occupied(lo,hi):
  shapes=[]
  for k in names:
   if meshes[k].bounds[0,1]<hi and meshes[k].bounds[1,1]>lo:
    shapes.append(projection(clipped(meshes[k],lo,hi)))
  return unary_union(shapes)
 band=occupied(-3,3);retention=occupied(-6.3,-3)
 pivots=[(-15.675,0),(15.675,0)]
 band_budget=unary_union([Point(*c).buffer(1.51,quad_segs=128) for c in pivots])
 retainer_budget=unary_union([Point(*c).buffer(2.51,quad_segs=128) for c in pivots])
 return dict(passed=band.difference(band_budget).area<.01 and retention.difference(retainer_budget).area<.01,
  band_support_area_mm2=band.area,retainer_projected_area_mm2=retention.area,
  off_pivot_band_area_mm2=band.difference(band_budget).area,
  off_pivot_retention_area_mm2=retention.difference(retainer_budget).area,
  description='Exclude jaws. Only 3 mm pivot sleeves through Y=-3..3; local retainers within diameter 5 mm below, including 0.01 mm tessellation allowance. No lower connecting plate/rear pillars. Strength and true structural minimum unverified.')

def evaluate(folder):
 meshes=load(folder)
 for k in ('pivot_screws','pivot_washers','pivot_nuts'):
  f=folder/f'exports/reference/{k}.stl'
  if f.exists():meshes[k]=trimesh.load_mesh(f)
 cap=meshes.get('top_plate');support=clipped(meshes['base'],-3,3)
 sections=support.split();centers=[]
 for m in sections:
  b=m.bounds;centers.append(dict(x=float((b[0,0]+b[1,0])/2),z=float((b[0,2]+b[1,2])/2),radius=float(m.extents[0]/2)))
 # Preserve current axle socket wall (1.6 mm) and M3 head rim (0.5 mm).
 # These are declared prototype design budgets, not measured strength minima.
 circles=[Point(c['x'],c['z']).buffer(1.65+1.6 if abs(c['z'])<.01 else max(c['radius'],3)+.5,quad_segs=128) for c in centers]
 target=unary_union(circles).convex_hull;footprint=projection(cap) if cap is not None else Polygon()
 excess=footprint.difference(target.buffer(.01)).area
 footprint_result=dict(passed=excess<.1,plate_area_mm2=footprint.area,plate_x_z_mm=[float(cap.extents[0]),float(cap.extents[2])] if cap is not None else [0,0],support_hull_budget_mm2=target.area,avoidable_overhang_mm2=excess,axle_socket_wall_budget_mm=1.6,m3_head_rim_budget_mm=.5,tessellation_allowance_mm=.01,description='Cap projection must fit the hull of its actual supports plus declared socket/head material. Does not require four pegs or prove structural minimality.')
 # Outside contact test: choose distal-side contact stations in the finger band,
 # then offer an 8 mm approach from the outside, across a 3 mm contact patch.
 obstacles={k:solid(m) for k,m in meshes.items() if k not in ('left','right')};fail=[];count=0
 outlines={k:projection(clipped(meshes[k],-2.5,2.5)) for k in ('left','right')}
 for a in np.linspace(0,30,121):
  bodies={k:solid(pose(meshes[k],k,a)) for k in obstacles}
  for side in ('left','right'):
   sign=1 if side=='right' else -1
   theta=math.radians((a-15)*sign);co=math.cos(theta);si=math.sin(theta);cx=sign*15.675
   outline=affine_transform(outlines[side],[co,si,-si,co,cx*(1-co),cx*si])
   for z in (15,25,35):
    patch=outline.intersection(box(-100,z-1.5,100,z+1.5))
    if patch.is_empty:fail.append(dict(angle=float(a),side=side,z=z,reason='no finger at station'));continue
    x=patch.bounds[2 if sign>0 else 0];x0=x+.1 if sign>0 else x-8.1
    probe=mf.Manifold.cube((8,5,3)).translate((x0,-2.5,z-1.5));count+=1
    for k,b in bodies.items():
     vol=(probe^b).volume()
     if vol>1e-4:fail.append(dict(angle=float(a),side=side,z=z,body=k,overlap_mm3=float(vol)))
 outside=dict(passed=not fail,probes=count,failures=fail,description='8 mm outward X approach, 3 mm patch at Z=15/25/35, Y=-2.5..2.5, over 121 poses. CAD access only; no hand model, skin pressure or ergonomics claim.')
 drive_names=('motor','stock_plate','pinion','left_gear','right_gear')
 low={k:float(meshes[k].bounds[0,1]) for k in drive_names}
 overhead=dict(passed=all(y>=3+.8-1e-4 for y in low.values()),finger_band_mm=[-3,3],minimum_drive_y_mm=low,minimum_gap_mm=min(low.values())-3)
 support_projection=projection(support)
 peg=dict(status='unverified',outside_corridor_clear=not fail,band_support_area_mm2=support_projection.area,band_supports=centers,description='Support orientation/removal has no prescribed direction or peg count. Measured occupied band and outside contact collisions are the evidence; redundant load paths require stiffness/strength evidence.')
 # Re-run actual collisions and tool probes; do not trust an archived passed flag.
 sys.path.insert(0,str(folder))
 for name in ('params','export_models'):sys.modules.pop(name,None)
 spec=importlib.util.spec_from_file_location('constraint_geometry',folder/'check_geometry.py')
 geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
 v=geo.params.values();all_bodies=dict(meshes)
 for k in [x for x in geo.REFS if not x.endswith('_tools')]:all_bodies[k]=trimesh.load_mesh(folder/f'exports/reference/{k}.stl')
 evidence=dict(motion_collisions=geo.collisions(all_bodies,v),tool_access=geo.tool_access(all_bodies,v))
 sys.path.pop(0)
 return dict(folder=folder.name,cap_footprint=footprint_result,minimal_in_plane_support=minimal_support(meshes),outside_contacts=outside,peg_placement=peg,overhead_drive=overhead,full_stroke=evidence['motion_collisions'],tool_access=evidence['tool_access'],retention=dict(status='unverified',description='Blind pivot sockets and two M3 pillars retained. Stiffness, post bending, screw pullout and axial endplay need physical/load tests.'),human_contact=dict(status='unverified',description='Finger band unchanged; no measured human hand or pressure model. CAD corridor success is not human fit.'))

def main():
 p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,default=BASELINE);p.add_argument('--out',type=Path);p.add_argument('--strict',action='store_true');a=p.parse_args()
 report=evaluate(a.folder)
 if a.out:a.out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:({z:x[z] for z in ('passed','status','plate_area_mm2','avoidable_overhang_mm2','band_support_area_mm2','minimum_gap_mm') if z in x} if isinstance(x,dict) else x) for k,x in report.items()},indent=2))
 return int(a.strict and any(isinstance(x,dict) and x.get('passed') is False for x in report.values()))
if __name__=='__main__':sys.exit(main())
