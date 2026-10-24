"""Re-measure pinned HLS3606M/Aero STEP interfaces; run with cad/build123d/.venv Python.
Threads are NOT represented by the STEP cylinders. No physical fit declaration.
"""
from pathlib import Path
import json,math,hashlib
from build123d import import_step,Axis
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_SurfaceType
import params
HERE=Path(__file__).resolve().parent
v=params.values()
def shape(name):
 return import_step(HERE/f'reference/{name}.step').translate((-v['hls_ref_x'],-v['hls_ref_y'],-v['hls_ref_ear_z'])).rotate(Axis.X,-90).rotate(Axis.Y,90)
def cylinders(q):
 out=[]
 for f in q.faces():
  s=BRepAdaptor_Surface(f.wrapped)
  if s.GetType()!=GeomAbs_SurfaceType.GeomAbs_Cylinder:continue
  c=s.Cylinder();p=c.Axis().Location();d=c.Axis().Direction()
  if abs(abs(d.Y())-1)>1e-6:continue
  ends=[p.Y()+d.Y()*t for t in [s.FirstVParameter(),s.LastVParameter()]]
  out.append(dict(radius=c.Radius(),x=p.X(),z=p.Z(),y0=min(ends),y1=max(ends)))
 return out
plate=shape('stock_plate');servo=shape('servo');pc=cylinders(plate);sc=cylinders(servo)
holes=[c for c in pc if abs(c['radius']-1)<1e-5 and math.hypot(c['x'],c['z'])>5]
ears=[c for c in sc if abs(c['radius']-1.25)<1e-5]
bore=next(c for c in sc if abs(c['radius']-1.15)<1e-5 and math.hypot(c['x'],c['z'])<1e-5)
plate_d=min(c['y1']-c['y0'] for c in holes)
# OCP geometry is normalized in actual millimetres before the placement rotation.
p=v['pivot_spacing']*v['scale_factor']/2;ratio=v['drive_teeth']/v['pinion_teeth'];pin_z=-math.sqrt((v['drive_module']*(v['drive_teeth']+v['pinion_teeth'])/2)**2-p*p)
def rotate(x,z,a):
 a=math.radians(a);return [math.cos(a)*x+math.sin(a)*z, -math.sin(a)*x+math.cos(a)*z+pin_z]
actual=[rotate(c['x'],c['z'],v['hls_body_deg']-15*ratio) for c in holes]
used=[]
for t in v['hls_plate_angles']:
 a=-15*ratio+90+t+v['hls_body_deg'];q=rotate(v['hls_plate_pcd']/2,0,a)
 error=min(math.dist(q,b) for b in actual);used.append(dict(native_angle_deg=t,posed_x_z_mm=q,axis_error_mm=error))
clear=(v['hls_plate_clear_d']-v['hls_m2_shank_d'])/2
wrong=max(min(math.dist(rotate(7,0,-15*ratio+90+t+v['hls_body_deg']),b) for b in actual) for t in v['hls_plate_angles'])
# Actual exported seating planes, parsed without requiring a second CAD tessellation.
import struct

def bounds(path):
 raw=Path(path).read_bytes();n=struct.unpack('<I',raw[80:84])[0];mins=[float('inf')]*3;maxs=[-float('inf')]*3
 for i in range(n):
  row=struct.unpack('<12fH',raw[84+50*i:134+50*i]);xyz=row[3:12]
  for j in range(3):mins[j]=min(mins[j],*xyz[j::3]);maxs[j]=max(maxs[j],*xyz[j::3])
 return mins,maxs
motor_min,_=bounds(HERE/'exports/parts/motor.stl');ear_y=motor_min[1]+servo.bounding_box().max.Y
plate_front=ear_y-plate.bounding_box().max.Y
thread_start=ear_y-bore['y1'];thread_end=ear_y-bore['y0']
_,center_head_max=bounds(HERE/'exports/reference/center_screw.stl');seat=center_head_max[1]
length=5.0;tip=seat+length;engage=max(0,min(tip,thread_end)-thread_start);floor=thread_end-tip
old_tip=plate_front+length;old_margin=thread_end-old_tip
screw_min,_=bounds(HERE/'exports/reference/plate_screws.stl');underhead=screw_min[1]+v['hls_plate_head_h'];grip=plate_front-underhead;plate_engage=v['hls_plate_screw_length']-grip
cad_case=[[c['x'],c['z']] for c in ears]
expected=[[u,s*v['hls_mount_span_w']/2] for u in [v['hls_mount_cad_u0'],v['hls_mount_cad_u1']] for s in [-1,1]]
case_error=max(min(math.dist(q,b) for b in cad_case) for q in expected)
report=dict(plate=dict(hole_count=len(holes),used_screws=len(used),diameter_mm=18,pcd_mm=sum(2*math.hypot(c['x'],c['z']) for c in holes)/len(holes),modeled_hole_diameter_mm=2,modeled_disk_thickness_mm=plate_d,holes=holes,thread='BOM specifies M2x4; STEP has smooth diameter-2 cylinders, not threads. Actual production thread/minor diameter/pitch and four-hole recollection remain unverified.'),alignment=dict(passed=max(q['axis_error_mm'] for q in used)<clear,used=used,radial_clearance_mm=clear,sts_14mm_pcd_control_passed=wrong<clear,sts_control_error_mm=wrong),center_stack=dict(passed=.19<=floor<=.21 and 2.79<=engage<=2.81,manufacturer_screw='M2.3x5',spline='Manufacturer 25T / OD4.95; STEP smooth spline envelope diameter4.93, no tooth geometry',screw_underhead_length_assumed_mm=length,separate_capture_ring_mm=v['center_capture_t'],head_seat_y_mm=seat,thread_mouth_y_mm=thread_start,bore_floor_y_mm=thread_end,thread_engagement_mm=engage,bore_floor_clearance_mm=floor,old_unseated_stack_passed=old_margin>=0,old_margin_mm=old_margin,qualification='Nominal under-head length interpreted as5mm; supplier screw head/length tolerance and real bore depth must be measured. Cylinders are not real threads. Separate printed flat capture ring preserves original head seat and engagement; bought spline plate unchanged.'),plate_screws=dict(count=len(used),spec='Replacement M2x8 socket screws + DIN125 M2 washers, 0.3mm; original BOM M2x4 cannot span new unrecessed stack.',actual_seat_to_plate_grip_mm=grip,modeled_engagement_mm=plate_engage,nominal_disk_mm=plate_d,passes_nominal_stack=1<=plate_engage<=plate_d-.1),case=dict(hole_count=len(ears),modeled_diameter_mm=2.5,cad_centers=cad_case,cad_alignment_error_mm=case_error,manufacturer_u_mm=[-8.21,19.79],cad_u_mm=[v['hls_mount_cad_u0'],v['hls_mount_cad_u1']],pilot_slot_travel_mm=v['hls_mount_slot_travel'],source='Manufacturer p6 and pinned STEP; 0.25mm longitudinal discrepancy captured by existing 0.5mm pilot slots. Transverse7mm from STEP, not dimensioned in drawing.',screws='Four M2x6 self-tapping ear screws into printed posts; separate from rotating plate screws. Exact drive/head dimensions unverified; guide calls them flanged Torx, not assumed Phillips.'),sources=dict(manufacturer='https://www.feetechrc.com/Data/feetechrc/upload/file/20240807/6385862508379674057566108.pdf',edition='A/0 2024-04-22, pages4/6/7',bom='https://raw.githubusercontent.com/Chestnut-Robotics/aero-hand-open/7bb2f23485a7d440960c21046da642de132b7745/hardware/Assembly/BOM.csv',cad='Pinned Aero STEP extracted servo304 and aluminum plate248; reference/provenance.json'),qualification='CAD/source agreement and explicit discrepancies only; exact plate revision Jake owns, actual threads, supplied screw dimensions, angled driver engagement and physical fit remain unverified.')
report['passed']=all([report['alignment']['passed'],report['center_stack']['passed'],report['plate_screws']['passes_nominal_stack'],case_error<1e-5,len(holes)==8,len(ears)==4])
report['input_sha256']={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'params.json',HERE/'reference/servo.step',HERE/'reference/stock_plate.step',HERE/'reference/HLS3606M-C001.pdf',HERE/'compact_source.scad',HERE/'gripper.scad']}
(HERE/'hardware_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
