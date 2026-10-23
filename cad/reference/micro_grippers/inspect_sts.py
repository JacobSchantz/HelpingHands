"""Inspect the pinned STS3215 STEP; no threads or physical fit inferred from cylinders.
Run with cad/build123d/.venv/bin/python; arguments: input.step output.json output.stl.
"""
import hashlib,json,sys,math
from pathlib import Path
from build123d import import_step,export_stl
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_SurfaceType
source,report,mesh=map(Path,sys.argv[1:4])
s=import_step(source);rows=[]
for f in s.faces():
 a=BRepAdaptor_Surface(f.wrapped)
 if a.GetType()!=GeomAbs_SurfaceType.GeomAbs_Cylinder:continue
 c=a.Cylinder();p=c.Axis().Location();d=c.Axis().Direction()
 rows.append(dict(radius_mm=c.Radius(),position_mm=[p.X(),p.Y(),p.Z()],axis=[d.X(),d.Y(),d.Z()],v_mm=[a.FirstVParameter(),a.LastVParameter()]))
horn=[c for c in rows if abs(c['radius_mm']-1.25)<1e-5 and abs(c['position_mm'][2]-18.7)<1e-5]
case=[c for c in rows if abs(c['radius_mm']-.75)<1e-5 and abs(c['position_mm'][2]-14.4)<1e-5]
pcds=[2*math.hypot(c['position_mm'][0]-12.5,c['position_mm'][1]) for c in horn]
assert len(horn)==4 and max(abs(p-14) for p in pcds)<1e-4
assert len(case)==4 and all(abs(c['v_mm'][1]-c['v_mm'][0]-1.5)<1e-5 for c in case)
out=dict(source='https://github.com/TheRobotStudio/SO-ARM100/blob/a758567c3978dfeefe282ede0500085a48fe8f78/STEP/SO100/STS3215_03a.step',sha256=hashlib.sha256(source.read_bytes()).hexdigest(),passed=True,front_horn=dict(holes=horn,pcd_mm=sum(pcds)/4,disk_thickness_mm=2.5,modeled_hole_diameter_mm=2.5),front_case=dict(holes=case,modeled_hole_diameter_mm=1.5,modeled_axial_depth_mm=1.5,rectangle_mm=[20.7,20.5]),qualification='Smooth cylinders only. M3 horn and M2 case fasteners / M3x6 center retention come from the LeRobot SO101 assembly guide. True thread depth, supplied horn revision, spline tooth form and physical fit not verified. SO100 STEP is the servo reference used by this repo; SO101 stock jaw uses the same14mm four-hole pattern, checked separately in its STEP. Not every hole on the motor is an assembly fastener.')
jaw_source=Path(__file__).resolve().parents[2]/'arm/so101/interface/Wrist_Roll_Follower_SO101.step'
jaw=import_step(jaw_source);jaw_holes=[]
for face in jaw.faces():
 surf=BRepAdaptor_Surface(face.wrapped)
 if surf.GetType()!=GeomAbs_SurfaceType.GeomAbs_Cylinder:continue
 cyl=surf.Cylinder();loc=cyl.Axis().Location();direction=cyl.Axis().Direction()
 if abs(cyl.Radius()-1.6)<1e-5 and abs(abs(direction.Z())-1)<1e-5:
  jaw_holes.append([loc.X(),loc.Y(),loc.Z()])
# Source jaw coordinates carry an offset; recover the bolt-circle center from its four bores.
assert len(jaw_holes)==4
cx=sum(p[0] for p in jaw_holes)/4;cy=sum(p[1] for p in jaw_holes)/4
jaw_pcd=[2*math.hypot(p[0]-cx,p[1]-cy) for p in jaw_holes]
assert max(abs(v-14) for v in jaw_pcd)<1e-4
out['so101_jaw']=dict(source_path=str(jaw_source.relative_to(Path(__file__).resolve().parents[3])),sha256=hashlib.sha256(jaw_source.read_bytes()).hexdigest(),clearance_hole_count=4,clearance_hole_diameter_mm=3.2,pcd_mm=sum(jaw_pcd)/4,center_xy_mm=[cx,cy])
report.write_text(json.dumps(out,indent=2)+'\n');export_stl(s,mesh)
print(json.dumps({k:v for k,v in out.items() if k not in ['front_horn','front_case']}))
