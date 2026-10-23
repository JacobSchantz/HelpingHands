"""Actual tip contact and non-overtravel contract; CAD only, no servo commands sent."""
from pathlib import Path
import json,math,hashlib,itertools
import numpy as np
import trimesh
from shapely.geometry import box,LineString
import params
import check_geometry as c
HERE=Path(__file__).resolve().parent
v=params.values();p,_,ratio=c.axes(v)
meshes={k:trimesh.load_mesh(HERE/f'exports/parts/{k}.stl') for k in ['left','right']}
def posed(k,a):
 m=meshes[k].copy();pivot,r=c.motion(k,v);m.vertices=c.rotated(m.vertices,pivot,(a-15)*r);return m
def tips(a):return [c.band_shape(posed(k,a)).intersection(box(-100,v['closure_pad_z0']-.01,100,100)) for k in ['left','right']]
a,b=tips(0);aa,bb=tips(.1)
closed_volume=float((c.solid(posed('left',0))^c.solid(posed('right',0))).volume())
negative_volume=float((c.solid(posed('left',-.1))^c.solid(posed('right',-.1))).volume())
whole=[c.band_shape(posed(k,0)).intersection(box(-100,12,100,v['closure_pad_z0']-2)) for k in ['left','right']]
mech=json.loads((HERE/'geometry_checks.json').read_text())
closed_tick=2048;open_tick=math.ceil(closed_tick-30*ratio*4096/360)
limits=dict(mode='Design/calibration contract only, not executable motor control',jaw_deg=[0,30],closed_tick_nominal=closed_tick,open_tick_not_past_limit=open_tick,closed_deg_nominal=closed_tick*360/4096,open_deg=open_tick*360/4096,jaw_open_with_integer_ticks_deg=(closed_tick-open_tick)*360/4096/ratio,manufacturer_mechanical_stop='No limit: no physical servo end stop to rely on',qualification='Require real plate/gear phase calibration and gentle contact teaching with limited force/current; do not blindly drive to these absolute ticks or command negative jaw angles. Encoder quantization, gearbox backlash and resin compliance mean nominal CAD contact is not physical fit approval.')
(HERE/'motion_limits.json').write_text(json.dumps(limits,indent=2)+'\n')
section=meshes['right'].section(plane_origin=[0,-2.99,0],plane_normal=[0,1,0]).to_2D()[0]
outline=max(section.polygons_full,key=lambda p:p.area);loops=[LineString(outline.exterior.coords)]+[LineString(h.coords) for h in outline.interiors]
web=min(a.distance(b) for a,b in itertools.combinations(loops,2))
report=dict(nominal_tip_gap_mm=a.distance(b),tip_contact_z_mm=[v['closure_pad_z0'],v['closure_pad_z1']],closed_intersection_area_mm2=a.intersection(b).area,closed_jaw_intersection_volume_mm3=closed_volume,opening_at_point_one_degree_mm=aa.distance(bb),overclose_control_detected=negative_volume>1e-4,overclose_control_volume_mm3=negative_volume,uncommanded_control_angle_deg=-.1,body_gap_mm=whole[0].distance(whole[1]),rear_minimum_mm=mech['rear_clearance']['minimum_gap_mm'],servo_index_margin_to_wrap_deg=min(limits['open_deg'],360-limits['closed_deg_nominal']),jaw_command_limits_deg=[0,30],motion_limits=limits,tolerances=dict(assumed_print_error_per_side_mm=.3,designed_middle_blade_gap_mm=v['body_closure_gap'],servo_encoder_step_deg=360/4096,jaw_step_deg=360/4096/ratio,half_lsb_tip_separation_mm=2*v['closure_pad_z1']*math.sin(math.radians(.5*360/4096/ratio)),manufacturer_servo_backlash_bound_deg=.5,compliance='No stiffness/contact-force model or qualified flexure. Nominal rigid contact faces need physical tolerance/force-limited calibration; never close farther to hide error.'),qualification='Actual CAD tips contact at jaw0 on integral1.5mm distal faces; 20mm pivots keep rear clearance. Whole-hand and physical hardware-fit/strength acceptance are separate and unverified.')
report['minimum_plan_ligament_mm']=web
report['passed']=bool(web>=.4 and report['nominal_tip_gap_mm']<=5e-5 and report['closed_intersection_area_mm2']<=1e-5 and closed_volume<=1e-4 and report['opening_at_point_one_degree_mm']>0 and report['overclose_control_detected'] and report['rear_minimum_mm']>=.8 and mech['full_stroke']['passed'])
report['input_sha256']={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'params.json',HERE/'gripper.scad',HERE/'geometry_checks.json',HERE/'hardware_checks.json',HERE/'exports/parts/left.stl',HERE/'exports/parts/right.stl']}
(HERE/'closure_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
