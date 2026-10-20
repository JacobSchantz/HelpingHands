#!/usr/bin/env python3
"""Offline solid checks for Base 14 (Base 12's on the STS3215 plus Base 10's mount_checks on the new wrist bracket: its leg seats under the base's wrist tab, clear of the servo and its cable). Base 12 (Base 11's on the STS3215, with the closed gap read on the toed-in finger). Base 11 (Base 10's, on whichever motor params.json picks: motor_sts 0 runs Base 10's mount_checks on the RS00, 1 runs sts_checks on the Feetech STS3215 instead, which has no reBot wrist mount). Base 10 (Base 9's, plus the reBot Arm wrist mount: mount_checks()). Base 9 (Base 8's, plus the top plate: nothing that turns touches it at any swing, each top ring runs in its handle-gear's groove, and lifted 0.5 mm a handle-gear or finger hits the plate). Base 8 (Base 7's, with the strap keep-outs at both strap-loop slots). Base 7: Base 4's, plus printability: every exports/print/*.stl rests on the bed and has no face
that overhangs past 45 deg (printability_checks), and each handle-gear turns on its base post. Base 4: Base 3's, with each handle and its side gear one print (the finger drops into it from the dorsal side and rests on its web; no key, cradle or stop strip) and the pinion and base on 3 bolts each. 3.3: 2.6's checks on the 15 mm handle plus the in-plane drive (drive_checks: side gears, centred pinion, the cradles) and the strap tunnel mouths kept clear. 3.2: 2.6's checks plus the base and drive, and the strap slots kept clear. 2.6 (2.5's checks on 1.21's single-step fingers and the 67.4 mm handle). 2.5: (2.4's params on 1.20's double-hook fingers; one handle per finger spanning both
hooks); no hardware operations. 2.5 adds: the seated handle clears the finger, slides in across the finger's thickness from
the ventral side without touching it, and is held: pushed 0.5 mm outboard it hits both prongs, toward either hook that
notch's floor, and pushed on through 0.5 mm its stop strip hits the ventral face. 1.18: the ventral face is flat to the point
and the thickness follows the taper.
Gen 17 adds: each slide clears its own finger (the slide fit), and no finger or slide hits the other side over 0-30 deg.
Gen 14's spec is how the closed fingers contact: only the very points touch, the inner edges leave them at
a sharp angle (>= CONTACT_DEG included), and further back the gap follows the closed photo's curve plus
that wedge (trace_photo.py closed_gap)."""
from pathlib import Path
import json, math, struct, subprocess, tempfile
import export_models
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
import params as _params
STS=_params.values()['motor_sts']==1   # Base 11: which motor this export is for
ANGLES=list(range(0,31))
STEP=400
GAP_TOL=0.20   # mm: the closed gap may differ from the target curve (r3: the TRIANGLE) by this much, 1 to 20 mm behind the point. r3: 0.12 -> 0.20; the model runs a steady ~0.13 under it, the 0.065 mm per finger that tip_r moves the contact in (gripper.scad contact_back)
CONTACT_DEG=20  # r3: the triangle gives 20.7 at 1-2 mm and narrows to ~15 further back, never parallel. the jaws' included angle, from the gap's slope 1 to 2 mm behind the point, must be at least this (Gen 16 r2: designed 30, Jake "much wider"; r1: 6; Gen 13: ~0)
CONTACT_LEN=1.5   # pushed 0.02 mm together, the fingers may overlap only this far behind the contact (Gen 13: 6 mm)


def run(body,tmp,fast=False):
    src=Path(tmp)/'check.scad';out=Path(tmp)/'out.stl'
    src.write_text(f'include <{HERE/"gripper.scad"}>\n'+body+'\n')
    p=subprocess.run([SCAD,*(['--backend','manifold'] if fast else []),'--export-format','binstl','-D','part="none"','-o',str(out),str(src)],capture_output=True,text=True)
    return p.stdout+p.stderr,(out.read_bytes() if out.exists() else None)


def verts(raw):
    n=struct.unpack_from('<I',raw,80)[0]
    return [v for i in range(n) for v in (lambda q:(q[3:6],q[6:9],q[9:12]))(struct.unpack_from('<12f',raw,84+i*50))]


def volume(V):
    return sum((a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6 for a,b,c in zip(V[::3],V[1::3],V[2::3]))


def check(name,body,empty=True,touch=False,within_z=None,fast=False):
    with tempfile.TemporaryDirectory(prefix='generalist_g14_') as tmp:
        log,raw=run(body,tmp,fast)
        is_empty='Current top level object is empty.' in log and raw is None
        if touch and not is_empty:   # faces that only touch leave a sliver of float noise: no thicker than 1 µm, or no volume
            V=verts(raw);xs=[v[0] for v in V];is_empty=max(xs)-min(xs)<1e-3 or abs(volume(V))<1e-3
        ok=is_empty if empty else raw is not None and 'NoError' in log
        extra={}
        if ok and within_z is not None:   # the overlap must lie only in this z range: the point, not the jaw
            zs=[v[2] for v in verts(raw)];extra=dict(overlap_z=[round(min(zs),2),round(max(zs),2)])
            ok=within_z[0]<=min(zs) and max(zs)<=within_z[1]
        return dict(name=name,passed=ok,expected=('touch only' if touch else 'empty') if empty else 'contact',**extra,log=log.strip()[-300:])


def slice_x(V,z):
    """x of every point where the mesh's triangle edges cross the plane at z."""
    xs=[]
    for tri in zip(V[::3],V[1::3],V[2::3]):
        for a,b in ((tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])):
            if (a[2]-z)*(b[2]-z)<0:xs.append(a[0]+(z-a[2])/(b[2]-a[2])*(b[0]-a[0]))
    return xs


def gap_profile():
    """The closed gap of the whole right finger vs Gen 14's target and the photo's curve. A
    mirrored pair's gap at z is 2 * (the right finger's innermost x at z - its innermost x anywhere).
    Base 12: the finger as it sits closed, toed in by toe deg (pivot_spacing); the target opens by the same toe each side."""
    import trace_photo as tp,re
    with tempfile.TemporaryDirectory() as tmp:
        log,raw=run('echo(toe=[toe,reach]);rotate([0,-toe,0]) whole_finger();',tmp)
    toe,reach=map(float,re.search(r'toe = \[([-\d.e]+), ([-\d.e]+)\]',log).groups());t=math.tan(math.radians(toe))
    V=verts(raw);xc=min(v[0] for v in V)
    z0=float(tp.to_mm(tp.tip_px())[1])-tp.ROUND_BACK   # the designed contact, just behind the rounded point (finger frame)
    zc=-reach*math.sin(math.radians(toe))+z0*math.cos(math.radians(toe))   # Base 12: that point toed in (at x -reach)
    rows=[]
    for d in [0.5,1,1.5,2,3,4,6,8,10,12,14,16,18,20,22]:
        # Gen 15: the mesh cut at that z, not vertices near it. Gen 16: where there are grooves (>= 3 mm back) a cut can land
        # in a groove bottom, so take the ridge tops: the innermost reach over one 1 mm groove pitch around z
        ks=[0] if d<3 else [i/10 for i in range(-5,6)];xs=[x for k in ks for x in slice_x(V,zc-d+k)]
        # Gen 16 r2: the target read the same way (its least gap over that window), or the 30 deg wedge's slope reads as error
        if xs:rows.append(dict(d_mm=d,model_gap=round(2*(min(xs)-xc),3),target_gap=round(min(tp.closed_gap(d-k)+2*(d-k)*t for k in ks),3),photo_gap=round(tp.photo_gap(d),3)))
    worst=max(abs(r['model_gap']-r['target_gap']) for r in rows if 1<=r['d_mm']<=20)
    mono=all(a['model_gap']<=b['model_gap']+5e-3 for a,b in zip(rows,rows[1:]))
    g=lambda d:next(r['model_gap'] for r in rows if r['d_mm']==d);deg=2*math.degrees(math.atan((g(2)-g(1))/2))
    return [dict(name='closed_gap_follows_the_gen14_target',passed=bool(worst<=GAP_TOL and mono),
                 expected=f'within {GAP_TOL} mm of photo curve + wedge from 1 to 20 mm back, never closing again (5 µm faceting allowed)',
                 worst_mm=round(worst,3),contact_z=round(zc,2),toe_deg=round(toe,3),rows=rows),
            dict(name=f'contact_angle_at_least_{CONTACT_DEG}_deg_included',passed=bool(deg>=CONTACT_DEG),
                 expected='slope of the closed gap 1 to 2 mm behind the point, as an included angle',included_deg=round(deg,2))],zc


def thickness():
    """1.18: full plate behind the taper start, then the dorsal face drops as f^taper_power to tip_thick; the ventral face (min y)
    stays at -plate/2 everywhere, so the finger lies flat on the bed. Each station is a 0.5 mm slab across the finger."""
    import params
    v=params.values();plate,tip_t,pw=v['plate'],min(v['tip_thick'],v['plate']),v['taper_power']
    with tempfile.TemporaryDirectory() as tmp:
        log,_=run('echo(zz=[dot_z+taper_start,tip[1]]);cube(1);',tmp)
    import re
    z0,tip_z=map(float,re.search(r'zz = \[([-\d.]+), ([-\d.]+)\]',log).groups())
    want=lambda z:plate-(plate-tip_t)*min(1,max(0,(z-z0)/(tip_z-z0)))**pw
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        for z in (20,60,z0-2,z0+0.3*(tip_z-z0),z0+0.6*(tip_z-z0),z0+0.85*(tip_z-z0),tip_z-3):
            _,raw=run(f'intersection(){{whole_finger();translate([-80,-20,{z}])cube([160,40,0.5]);}}',tmp)
            ys=[v[1] for v in verts(raw)] if raw else [0]
            rows.append(dict(z_mm=round(z,2),bottom_y=round(min(ys),3),thick_mm=round(max(ys)-min(ys),3),want_mm=round(want(z+0.5),3)))
    ok=all(abs(r['bottom_y']+plate/2)<1e-3 and r['want_mm']-0.05<=r['thick_mm']<=want(r['z_mm'])+0.05 for r in rows)
    return dict(name='flat_bottom_and_one_sided_taper',passed=ok,
                expected=f'bottom face y=-{plate/2} at every station; thickness {plate} behind the taper start, then to {tip_t} at the point',
                taper_z=round(z0,2),tip_z=round(tip_z,2),rows=rows)


def handle_checks():
    """2.5: the handle between the hooks, in the right finger's frame (gripper.scad strap_slide(du, dw, dy))."""
    H=lambda du=0,dw=0,dy=0:f'intersection(){{whole_finger();strap_slide({du},{dw},{dy});}}'
    return [check('handle_seated_clears_the_finger',H()),
            check('handle_held_outboard_by_both_prongs_positive_control',H(dw=0.5),False),
            check('handle_held_toward_the_base_hook_positive_control',H(du=-0.5),False),
            check('handle_held_toward_the_top_hook_positive_control',H(du=0.5),False)]


def drive_checks():
    """Base 4: the side gears (in the finger plane, each one print with its handle), the centred pinion, the base and RS00
    motor, and the strap keep-outs (Manifold backend: the gears are too slow for CGAL over 31 angles)."""
    C=lambda *a,**k:check(*a,fast=True,**k)
    sweep=lambda body:'union(){'+';'.join(f'translate([0,0,{i}*{STEP}]){body.format(a=i)}' for i in ANGLES)+';}'
    other={'right':'left','left':'right'}
    rest=lambda q:f'union(){{{{piece("{q}",{{a}});core_piece("{q}",{{a}});side("{other[q]}",{{a}});pinion({{a}});base();motor({{a}});top_plate();}}}}'   # all but that side's handle (its gear without the handle is in)
    zone=lambda q:f'intersection(){{{{zone_piece("{q}",{{a}});{rest(q)}}}}}'
    return [C('side_gears_mesh_without_interference_0_to_30_deg',sweep('intersection(){{gear_piece("left",{a});gear_piece("right",{a});}}')),
            C('side_gears_interfere_when_one_turns_half_a_tooth_positive_control','intersection(){gear_piece("left",15,180/gear_teeth);gear_piece("right",15);}',False),
            C('pinion_meshes_the_right_gear_without_interference_0_to_30_deg',sweep('intersection(){{gear_piece("right",{a});pinion({a});}}')),
            C('pinion_interferes_when_turned_half_a_tooth_positive_control','intersection(){gear_piece("right",15);pinion(15,180/pinion_teeth);}',False),
            C('pinion_never_touches_the_left_side_0_to_30_deg',sweep('intersection(){{side("left",{a});pinion({a});}}')),
            C('pinion_never_touches_the_right_finger_or_handle_0_to_30_deg',sweep('intersection(){{union(){{piece("right",{a});slide_piece("right",{a});}}pinion({a});}}')),
            C('handle_gear_clears_its_seated_finger','intersection(){gear();whole_finger();}'),
            C('finger_rests_on_the_web_positive_control','intersection(){gear();translate([0,-0.3,0]) whole_finger();}',False),
            C('handle_gear_drives_the_finger_open_turned_1_deg_it_hits_positive_control','intersection(){rotate([0,1,0]) gear();whole_finger();}',False),
            C('handle_gear_drives_the_finger_closed_turned_1_deg_it_hits_positive_control','intersection(){rotate([0,-1,0]) gear();whole_finger();}',False),
            C('finger_drops_into_its_handle_gear_from_above_without_touching',   # assembly: handle-gear on its axle first, then the finger goes in along -y, 0.5 mm steps
              'intersection(){gear();union(){for(d=[0.5:0.5:20]) translate([0,d,0]) whole_finger();}}'),
            C('handle_gear_is_one_solid_handle_fused_to_the_hub_positive_control','intersection(){gear_core();handle_body();}',False),
            C('handle_gear_turns_on_its_post_without_touching_it_0_to_30_deg',sweep('intersection(){{union(){{gear_piece("left",{a});gear_piece("right",{a});}}base();}}'),touch=True),   # Base 7: the posts in their bores
            C('handle_gear_held_by_its_post_positive_control','intersection(){translate([0.5,0,0]) gear_piece("right",15);base();}',False),
            C('post_top_clears_the_finger_0_to_30_deg',sweep('intersection(){{union(){{piece("left",{a});piece("right",{a});}}base();}}')),
            C('strap_tunnel_mouths_clear_of_everything_but_their_handle_0_to_30_deg',sweep('union(){{'+zone('right')+zone('left')+'}}')),
            C('strap_keepout_sits_at_the_tunnel_mouths_positive_control','intersection(){strap_zone();strap_slide(dy=0.5);}',False),
            C('flange_bolts_reachable_from_above_the_pinion_0_to_30_deg',sweep('intersection(){{bolt_access({a});union(){{pinion({a});side("left",{a});side("right",{a});top_plate();}}}}'),touch=True),   # the access starts on the counterbore floors
            C('nothing_that_swings_hits_the_base_or_motor_0_to_30_deg',   # the pinion's spigot sits on the motor flange: face contact only
              sweep('intersection(){{union(){{side("left",{a});side("right",{a});pinion({a});}}union(){{base();motor({a});}}}}'),touch=True),
            C('left_and_right_sides_never_collide_1_to_30_deg',sweep('intersection(){{side("left",max(1,{a}));side("right",max(1,{a}));}}')),
            C('motor_output_screws_clear_the_pinion_holes','intersection(){pinion(15);motor_cores(15);}'),
            C('motor_front_screws_and_dowels_clear_the_base_holes','intersection(){base();motor_cores(15);}'),
            C('motor_sits_on_the_base_without_overlap',f'intersection(){{base();motor(15);}}',touch=True),
            # Base 9: the top plate
            C('nothing_that_turns_touches_the_top_plate_0_to_30_deg',   # the rings run in their grooves; fingers, handle-gears and pinion under the plate
              sweep('intersection(){{union(){{side("left",{a});side("right",{a});pinion({a});}}top_plate();}}')),
            C('handle_gear_lifted_0.5mm_hits_the_top_plate_positive_control','intersection(){translate([0,0.5,0]) gear_piece("right",15);top_plate();}',False),
            C('finger_lifted_0.5mm_hits_the_top_plate_positive_control','intersection(){translate([0,0.5,0]) piece("right",15);top_plate();}',False),
            C('top_ring_holds_the_handle_gear_shifted_0.5mm_positive_control','intersection(){translate([0.5,-0.1,0]) gear_piece("right",15);top_plate();}',False),   # 0.1 down, so only the ring (not the plate's underside) can touch
            C('top_ring_holds_the_left_handle_gear_shifted_0.5mm_positive_control','intersection(){translate([0,-0.1,0.5]) gear_piece("left",15);top_plate();}',False),
            C('top_plate_and_base_meet_only_at_the_pillar_feet','intersection(){top_plate();base();}',touch=True),
            C('top_plate_clears_the_motor','intersection(){top_plate();motor(15);}')]


def screws_body():
    """Base 10: the mount's screw shanks (3 mm), each as long as it runs: tool screws from the head pocket floor up through the
    floor and the foot; radial screws from their seat to radial_pilot_len into the hub; leg screws through the leg."""
    return ('union(){translate([axis_c[0],axis_c[1],tool_z-tool_floor]) for(i=[0:3]) rotate(tool_screw_phase_deg+i*90) translate([tool_screw_pcd/2,0,0]) cylinder(d=3,h=tool_floor+foot_t,$fn=16);'
            'translate([axis_c[0],axis_c[1],tool_z]) for(i=[0:radial_n-1]) rotate(radial_phase_deg+i*360/radial_n) translate([hub_d/2-radial_pilot_len,0,-tool_floor-radial_h]) rotate([0,90,0]) cylinder(d=3,h=radial_seat_r-hub_d/2+radial_pilot_len,$fn=16);'
            'slab(leg_y1-leg_t,leg_t) for(p=leg_holes) translate(p) circle(d=3,$fn=16);}')


def sts_checks():
    """Base 11: the STS3215 seat. The base bears on the servo's rails and nothing of the servo is inside it (the generic drive
    checks already put the pinion's spigot on the horn and sweep everything that turns against the servo); pushed 0.5 mm the
    servo hits the base; the hump stands in its window and holds the servo across; the M2 heads sit below the base top, clear
    of everything that turns; the bus cable's plugs and bend behind the connectors are clear of every part."""
    C=lambda *a,**k:check(*a,fast=True,**k)
    sweep=lambda body:'union(){'+';'.join(f'translate([0,0,{i}*{STEP}]){body.format(a=i)}' for i in ANGLES)+';}'
    heads='slab(base_y1-sts_screw_head_h,1.6) sts_holes2d() circle(d=3.8,$fn=24)'   # M2 pan heads on their recess floors
    across=lambda d:f'translate([{d}*cos(sts_body_deg+90),0,{d}*sin(sts_body_deg+90)])'
    return [C('servo_rails_seat_on_the_base','intersection(){base();motor(15);}',touch=True),
            C('servo_pushed_0.5mm_into_the_base_positive_control','intersection(){base();translate([0,0.5,0]) motor(15);}',False),
            C('servo_hump_held_by_its_window_shifted_0.5mm_across_positive_control',f'intersection(){{base();{across(0.5)} translate([0,-0.01,0]) motor(15);}}',False),
            C('servo_hump_held_by_its_window_shifted_0.5mm_the_other_way_positive_control',f'intersection(){{base();{across(-0.5)} translate([0,-0.01,0]) motor(15);}}',False),
            C('m2_heads_below_everything_that_turns_0_to_30_deg',sweep('intersection(){{'+heads+';union(){{side("left",{a});side("right",{a});pinion({a});}}}}')),
            C('m2_heads_sit_in_their_recesses','intersection(){'+heads+';base();}',touch=True),
            C('m2_screws_bite_the_case_positive_control','intersection(){slab(base_y0-4,4) sts_holes2d() circle(d=2,$fn=12);motor(15);}',False),
            C('bus_cable_plugs_clear_of_every_part_0_to_30_deg',sweep('intersection(){{sts_cable();union(){{side("left",{a});side("right",{a});pinion({a});base();top_plate();}}}}')),
            C('bus_cable_keepout_sits_on_the_connectors_positive_control','intersection(){translate([0,sts_plug_len/2,0]) sts_cable();motor(15);}',False)]


def mount_checks():
    """Base 10: the wrist mount. The bracket's leg seats on the RS00's back face and nothing else of the gripper touches it at any
    swing; the tool plate seats on the foot; the hub sits in the socket and is held there; every screw clears the part it passes
    through and bites into the one it threads into; the leg screws' heads are reachable; the arm (Seeed's URDF, as exported)
    stays below the hub's arm face; the Aero Hand's four wrist inserts (its CAD) sit on the tool plate's screw circle. Mount 2: the
    hub on the SO-101's horn (seated, centred, its 4 screws in the horn and stopping in it) and the SO-101 clear of everything
    that rolls, at any roll."""
    C=lambda *a,**k:check(*a,fast=True,**k)
    sweep=lambda body:'union(){'+';'.join(f'translate([0,0,{i}*{STEP}]){body.format(a=i)}' for i in ANGLES)+';}'
    if STS:   # Base 14: the leg lies flat under the base's wrist tab, beside the servo, and 2 M3 go up into the tab
        rows=[C('bracket_leg_seats_under_the_wrist_tab','intersection(){bracket();base();}',touch=True),
              C('bracket_pushed_0.5mm_into_the_base_positive_control','intersection(){translate([0,0.5,0]) bracket();base();}',False),
              C('bracket_clears_the_servo_and_its_bus_cable','intersection(){bracket();union(){motor(15);sts_cable();}}'),
              C('bracket_clears_everything_that_swings_and_the_top_plate_0_to_30_deg',sweep('intersection(){{bracket();union(){{side("left",{a});side("right",{a});pinion({a});top_plate();}}}}')),
              C('bracket_raised_by_the_gap_hits_the_wrist_tab_positive_control','intersection(){translate([0,-0.01,mount_gap+0.2]) bracket();base();}',False),
              C('wrist_tab_screws_bite_the_base_positive_control','intersection(){slab(base_y0,4) for(p=leg_holes) translate(p) circle(d=3,$fn=16);base();}',False),
              C('leg_screw_heads_clear_the_servo','intersection(){leg_heads();motor(15);}')]
    else: rows=[C('bracket_leg_seats_on_the_motor_back_face','intersection(){bracket();motor(15);}',touch=True),
          C('bracket_pushed_0.5mm_into_the_motor_positive_control','intersection(){translate([0,0.5,0]) bracket();motor(15);}',False),
          C('bracket_clears_the_motor_connectors','intersection(){bracket();translate([pin_c[0],0,pin_c[1]]) motor_connectors();}'),
          C('bracket_clears_everything_that_swings_and_the_plates_0_to_30_deg',sweep('intersection(){{bracket();union(){{side("left",{a});side("right",{a});pinion({a});base();top_plate();}}}}')),
          C('bracket_raised_by_the_gap_hits_the_gripper_positive_control',f'intersection(){{translate([0,0,mount_gap+0.2]) bracket();union(){{base();top_plate();}}}}',False)]
    rows+=[
          C('tool_plate_seats_on_the_foot','intersection(){bracket();mount_tool_plate();}',touch=True),
          C('hub_sits_in_the_socket_on_its_floor','intersection(){mount_hub();mount_tool_plate();}',touch=True),
          C('hub_held_by_the_socket_shifted_0.5mm_positive_control','intersection(){translate([0.5,0,0]) mount_hub();mount_tool_plate();}',False),
          C('hub_and_tool_plate_clear_the_gripper','intersection(){union(){mount_hub();mount_tool_plate();}union(){side("left",15);side("right",15);pinion(15);base();top_plate();motor(15);}}'),
          C('screws_clear_the_tool_plate_and_leg_holes',f'intersection(){{{screws_body()}union(){{mount_tool_plate();difference(){{bracket();translate([0,0,tool_z-1]) linear_extrude(foot_t+2) foot2d();}}}}}}'),
          C('tool_screws_bite_the_foot_positive_control',f'intersection(){{{screws_body()}translate([0,0,tool_z]) linear_extrude(foot_t) foot2d();bracket();}}',False),
          C('radial_screws_bite_the_hub_positive_control',f'intersection(){{{screws_body()}mount_hub();}}',False),
          C('leg_screw_heads_and_key_reach_clear','intersection(){leg_heads();bracket();}',touch=True),
          C('tool_screw_heads_clear_the_hub','intersection(){translate([axis_c[0],axis_c[1],tool_z-tool_floor-3]) for(i=[0:3]) rotate(tool_screw_phase_deg+i*90) translate([tool_screw_pcd/2,0,0]) cylinder(d=5.5,h=3,$fn=24);mount_hub();}')]
    # Mount 2: the hub on the SO-101's wrist-roll horn (a Ø sts_horn_d disc, 2.5 thick, its face at the socket floor)
    horn='translate([axis_c[0],axis_c[1],hub_z0+so_horn_z-2.5]) cylinder(d=sts_horn_d,h=2.5,$fn=96)'
    shanks=('translate([axis_c[0],axis_c[1],hub_z0]) for(i=[0:sts_horn_holes-1]) rotate(45+i*360/sts_horn_holes) translate([sts_horn_pcd/2,0,so_head_z-so_screw_len]) '
            'cylinder(d=3,h=so_screw_len-(so_head_d-screw_clear_d)/2,$fn=16)')   # M3 shank from the tip to the cone
    rows+=[C('so101_hub_seats_on_the_horn',f'intersection(){{mount_hub();{horn};}}',touch=True),
           C('so101_hub_pushed_0.5mm_onto_the_horn_positive_control',f'intersection(){{translate([0,0,-0.5]) mount_hub();{horn};}}',False),
           C('so101_horn_centred_by_the_socket_shifted_0.5mm_positive_control',f'intersection(){{translate([0.5,0,0.01]) mount_hub();{horn};}}',False),
           C('so101_horn_screws_bite_the_horn_positive_control',f'intersection(){{{shanks};{horn};}}',False),
           C('so101_horn_screws_stop_inside_the_horn',f'intersection(){{{shanks};translate([axis_c[0],axis_c[1],hub_z0+so_horn_z-2.5-20]) cylinder(d=40,h=20);}}'),
           C('so101_horn_screws_clear_the_hub',f'intersection(){{{shanks};mount_hub();}}')]
    # the arm, as export_models.py posed it (the meshes are not closed solids, so this is done on points). Everything from the
    # hub's neck up turns with the wrist roll, so its envelope is a solid of revolution about the axis: no arm point may come
    # within CLEAR of the neck (but the servo's spline inside the horn socket), of the tool plate's socket rim or anything
    # above it, at any roll; and none may lie inside the assembly as shown.
    n=solid_numbers();hz,hn,nd,sd,sh,mouth,ay=n
    import numpy as np, sys
    A=np.array(verts((HERE/'exports/assembly.stl').read_bytes())).reshape(-1,3,3)
    sys.path.insert(0,str(REPO/'cad/arm/so101'));import so101_pose,params
    with tempfile.TemporaryDirectory() as tmp:
        files=[f for f,*_ in so101_pose.export(tmp,horn=(0,ay,hn),roll_deg=params.values()['so_roll_deg'],lod='full')]
        P=np.array([v for f in files for v in verts(Path(f).read_bytes())])
    CLEAR=0.5
    def envelope(P):
        r=np.hypot(P[:,0],P[:,1]-ay);z=P[:,2]
        spline=(r<sd/2)&(z<=hn+0.05)   # the servo's output spline, under the horn, in the socket
        neck=(z>hn-sh-CLEAR)&(z<hz)&(r<nd/2+CLEAR)&~spline
        top=(z>mouth-CLEAR)
        return neck|top
    bad=P[envelope(P)]
    rows.append(dict(name='so101_arm_clears_everything_that_rolls_at_any_roll',passed=len(bad)==0,
                     expected=f'no arm vertex within {CLEAR} mm of the neck (r {nd/2}) or above the tool plate socket rim (z {round(mouth,2)}), but the spline inside the horn socket',
                     points=[[round(float(x),2) for x in p] for p in bad[:5]],horn_face_z=round(hn,3)))
    hits=int(envelope(P+[0,0,2]).sum())   # the arm 2 mm further in: the wrist's collar reaches the tool plate's rim
    rows.append(dict(name='so101_arm_raised_2mm_hits_the_roll_envelope_positive_control',passed=hits>0,expected='arm points in the envelope',points=hits))
    lo,hi=A.reshape(-1,3).min(0)-1,A.reshape(-1,3).max(0)+1;near=P[np.all((P>=lo)&(P<=hi),axis=1)]
    inside=[[round(float(x),2) for x in p] for p in near if inside_mesh(A,p)]
    rows.append(dict(name='so101_arm_clears_the_gripper_and_mount',passed=not inside,expected='no arm vertex inside the assembly',arm_points_near=len(near),inside=inside[:5]))
    r=np.hypot(P[:,0],P[:,1]-ay);top=float(P[r<3,2].max())   # the spline's end: the horn sits on it, 1.5 under the horn's face
    rows.append(dict(name='so101_spline_ends_under_the_horn_face',passed=bool(hn-2.5<top<hn),expected='the wrist-roll servo\'s spline (the arm mesh near the axis) tops out within the horn\'s 2.5 mm under its face',
                     spline_top_z=round(top,3),horn_face_z=round(hn,3)))
    pv=params.values();pcd,phase=pv['tool_screw_pcd'],pv['tool_screw_phase_deg']   # the tool plate's screw circle (Mount 1's, unchanged)
    # the Aero Hand's wrist pad: hole centres 1 mm into its palm mesh vs the tool screw circle
    mesh=REPO/'third_party/aero_hand/guide/anim41/left_base_link.STL'
    holes=pad_holes(verts(mesh.read_bytes()))
    want=[(pcd/2*math.cos(math.radians(phase+90*i)),pcd/2*math.sin(math.radians(phase+90*i))) for i in range(4)]
    err=max(min(math.hypot(h[0]-w[0],h[1]-w[1]) for h in holes) for w in want) if len(holes)>=4 else 99
    rows.append(dict(name='aero_hand_inserts_on_the_tool_screw_circle',passed=bool(err<0.3),expected='each of the 4 tool screws within 0.3 mm of an insert bore in the Aero Hand\'s CAD',
                     worst_mm=round(err,3),insert_bores_mm=[[round(x,2) for x in h] for h in holes]))
    return rows


REPO=HERE.parents[2]
def solid_numbers():
    """Mount 2: the hub's disc (arm face z), the horn face z, neck and socket, the tool plate's socket rim z, the roll axis' y."""
    import re
    with tempfile.TemporaryDirectory() as tmp:
        log,_=run('echo(hz=[hub_z0,hub_z0+so_horn_z,so_neck_d,so_socket_d,so_socket_h,tool_z-tool_t,mount_axis_y]);cube(1);',tmp)
    return map(float,re.search(r'hz = \[(.*?)\]',log).group(1).split(','))


def inside_mesh(T,p):
    """Base 10: is point p inside the closed triangle mesh T (n, 3, 3)? Parity of +z ray crossings (Moller-Trumbore)."""
    import numpy as np
    d=np.array([1e-4,2e-4,1.0]);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];h=np.cross(d,e2);a=(e1*h).sum(1);ok=np.abs(a)>1e-12
    f=np.where(ok,1/np.where(ok,a,1),0);s=p-T[:,0];u=f*(s*h).sum(1);q=np.cross(s,e1);v=f*(q*d).sum(1);t=f*(e2*q).sum(1)
    return int(np.count_nonzero(ok&(u>=0)&(v>=0)&(u+v<=1)&(t>1e-9)))%2==1
def pad_holes(V,z=1.0,link=1.5):
    """Base 10: centres (mm) of the 2-4 mm radius bores a z-plane cuts through the Aero Hand's palm mesh (metres): the plane's
    edge crossings, chained into loops (points within link mm), each loop's centre and radius."""
    pts=[]
    for tri in zip(V[::3],V[1::3],V[2::3]):
        P=[[c*1000 for c in t] for t in tri]
        for a,b in ((P[0],P[1]),(P[1],P[2]),(P[2],P[0])):
            if (a[2]-z)*(b[2]-z)<0:t=(z-a[2])/(b[2]-a[2]);pts.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
    parent=list(range(len(pts)))
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    order=sorted(range(len(pts)),key=lambda i:pts[i])
    for k,i in enumerate(order):   # sweep in x: only neighbours within link in x can link
        for j in order[k+1:]:
            if pts[j][0]-pts[i][0]>link:break
            if abs(pts[j][1]-pts[i][1])<link:parent[root(i)]=root(j)
    loops={}
    for i,p in enumerate(pts):loops.setdefault(root(i),[]).append(p)
    out=[]
    for g in loops.values():
        cx=sum(p[0] for p in g)/len(g);cy=sum(p[1] for p in g)/len(g);r=sum(math.hypot(p[0]-cx,p[1]-cy) for p in g)/len(g)
        if len(g)>=6 and 1.5<r<4:out.append((cx,cy))
    return out


MAX_OVERHANG_DEG=45
def overhang(raw,bed_tol=1e-3):
    """Base 7: the area (mm^2) of faces that overhang past MAX_OVERHANG_DEG (+0.5 deg for faceting) anywhere above the bed, and the
    lowest z of the part (the bed is z 0). A face overhangs by asin(-n_z) from the vertical: a wall 0, a ceiling 90."""
    n=struct.unpack_from('<I',raw,80)[0];tris=[struct.unpack_from('<12f',raw,84+i*50)[3:] for i in range(n)]
    zmin=min(min(t[2],t[5],t[8]) for t in tris);area=0;zs=set();lim=-math.sin(math.radians(MAX_OVERHANG_DEG+0.5))
    for t in tris:
        a,b,c=t[0:3],t[3:6],t[6:9];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        nx,ny,nz=u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0];L=math.sqrt(nx*nx+ny*ny+nz*nz)
        if L>1e-12 and nz/L<lim and max(a[2],b[2],c[2])>zmin+bed_tol:area+=L/2;zs.add(round(min(a[2],b[2],c[2]),2))
    return zmin,area,sorted(zs)[:8]


def printability_checks():
    """Base 7: Jake's rule, every piece prints on an FDM printer without supports. Each print STL (exports/print, written by
    export_models.py lying on the bed in its print orientation) must sit on z 0, be one solid (mesh_checks.json: no floating
    features) and have no overhang past 45 deg. The pinion turned spigot-down (Base 4's way up for its counterbores) must fail."""
    rows=[];comps={m['path']:m['components'] for m in json.loads((HERE/'mesh_checks.json').read_text())}
    for k,*_ in export_models.PARTS:
        if k=='motor':continue
        rel=f'exports/print/{k}.stl';zmin,area,zs=overhang((HERE/rel).read_bytes())
        rows.append(dict(name=f'{k}_prints_flat_without_supports',passed=abs(zmin)<1e-3 and area<0.01 and comps.get(rel)==1,
                         expected=f'on the bed (z 0), one solid, no face past {MAX_OVERHANG_DEG} deg',z_min=round(zmin,3),overhang_mm2=round(area,3),overhang_at_z=zs,components=comps.get(rel)))
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp)/'flipped.stl'
        subprocess.run([SCAD,'--backend','manifold','--export-format','binstl','-D','part="print_pinion_flipped"','-o',str(out),str(HERE/'gripper.scad')],capture_output=True)
        zmin,area,zs=overhang(out.read_bytes())
    rows.append(dict(name='pinion_upside_down_overhangs_positive_control',passed=area>100,expected='the spigot-down pinion overhangs (its teeth hang out past the spigot)',overhang_mm2=round(area,1),overhang_at_z=zs))
    return rows


def main():
    gp,zc=gap_profile()
    results=[
       check('fingers_never_collide_1_to_30_deg',f'for(i=[1:30])translate([0,0,i*{STEP}])clash(i);'),
       check('closed_fingers_touch_without_overlap_at_0_deg','clash(0);',touch=True),
       check('closed_fingers_overlap_when_pushed_0.02mm_positive_control',
             'intersection(){translate([0.01,0,0])piece("left",0);translate([-0.01,0,0])piece("right",0);}',False),
       check(f'pushed_0.02mm_together_they_meet_only_in_the_last_{CONTACT_LEN}mm',   # the point, not the jaw (Gen 13 met along 6 mm)
             'intersection(){translate([0.01,0,0])piece("left",0);translate([-0.01,0,0])piece("right",0);}',False,within_z=(zc-CONTACT_LEN,zc+2)),
       check('slides_never_hit_the_other_side_1_to_30_deg',
             f'for(i=[0:30])translate([0,0,i*{STEP}]){{intersection(){{slide_piece("left",i);union(){{piece("right",i);slide_piece("right",i);}}}}intersection(){{slide_piece("right",i);piece("left",i);}}}}'),
       *gp,thickness(),*handle_checks(),*drive_checks(),*(sts_checks() if STS else []),*mount_checks(),*printability_checks()]
    report=dict(sampled_angles_degrees=ANGLES,results=results,limitations=[
       'Integer-degree samples only, not continuous motion.',
       'Closed gap read from one blurred perspective photo (~0.5 mm/px); sub-pixel widths come from seam darkness.',
       'The 4 deg wedge is a design choice (Jake: too much contact before the tip), not a measurement: the photo cannot resolve it.',
       '1.18: the point is 2.4 mm thick, all of it on the flat ventral side, and about 0.6 mm wide in plan; not printed.',
       '2.5: the fit (0.2 mm per side) and the strap / digit sizes are nominal; nothing is printed or measured.',
       'Base 4: the finger rests on its gear web (which replaces the stop strip); only friction keeps it from lifting back out the way it came (+y). The drop-in check samples 0.5 mm steps, not continuous motion.',
       '2.5: the hook prongs are 1.19 base-hook size (about 2.2 mm deep along the edge) and have not been pull-tested.',
       '2.6: the top step fills the outer side out to the hook crest (6.6 mm) from u 54 to where the beak edge regains it (~u 77), up to ~3 mm wider than 1.20 there; only the swing checks above cover it, nothing checks it against a hand.',
       'Plan shape traced from one photo at an assumed 0.2 mm/px; no Generalist part was measured.',
       '3.1-3.3: the drive is checked as solids only: gear mesh at 31 integer angles, no loads, no tooth strength, no motor torque. The RS00 dimensions come from its drawing (Seeed 100083284) and RS00.step, not from a motor in hand; the second dowel hole is assumed opposite the first.',
       'Base 7: overhangs are measured on the exported meshes (faces past 45.5 deg anywhere above the bed); bridging, first-layer adhesion, warping, elephant foot and tolerances of a real printer are not modelled. Nothing was sliced or printed.',
       'Base 7: each handle-gear turns on a printed post only web_t (3 mm) long, with its flat underside riding stack_gap over the base; no wear or wobble test.',
       '3.3/Base 4: both side gears turn in plain printed bushings in the base (Base 7: on printed posts) and nothing holds them down axially; the finger sits in its handle-gear with a 0.2 mm fit (0.4 round the hub) and only gravity/friction keeps it from lifting out (+y); untested under load.',
       'Base 4/7: 3 of 6 M3 (Base 7: countersunk) hold the pinion to the RS00 flange and 3 of 6 hold the base to the front ring; shear is estimated (~350 N per bolt at 14 N m peak), not tested in printed plastic.',
       '3.3: the strap keep-out is a box strap_clear (3 mm) past each tunnel mouth, from the plate outer face to the boss outer face plus strap_clear round it; the webbing itself and the digit are not modelled.',
       '3.3: the left gear carries only the teeth the right gear meets over 0-30 deg (plus gear_extra), so it cannot reach the pinion; driving past 30 deg runs the gears off their teeth. No stops limit the swing; the motor must.',
       '3.1-Base 4: the fingers have no pivot pin: each finger is held by its handle-gear only (both hooks, the tail and the hub pocket).',
       'Base 9: each handle-gear is held radially at the top by a C-shaped printed rib (ring_clear 0.25 mm) in a groove round its pivot, not a full axle: the finger\'s base hook covers the pivot. The C is open for about 110 deg where the finger is; the rib and the post are coaxial only as far as the pillar sockets locate the plate (0.15 mm fit). No load, wear or wobble test.',
       'Base 9: the top plate is held by M3 self-tapped into printed pillars from below (Base 12: 2 pillars, plus the C rings in the handle-gears); pull-out strength in printed plastic is not tested.',
       'Base 10: the wrist interface copies Seeed\'s Connector A and B (STEP files at reBot-DevArm 9e8634c, measured with OCCT); no reBot Arm or stock connector was in hand. The arm is checked only as exported (one pose, decimated meshes, 1-3 mm off Seeed\'s): it must stay below the hub\'s arm face; other poses, cable runs and J6 roll limits are not checked.',
       'Base 10: the gripper hangs on the RS00\'s back face (4 M3, 3 mm of thread each) and the bracket\'s foot carries it ~70 mm across to the J6 axis (mount_axis_y 0); no load, stiffness or fatigue test. The radial and tool screws self-tap into printed plastic.',
       'Base 10: the RS00 connectors are a box per side measured from Seeed\'s motor_7 mesh, and their real direction on our motor (motor_conn_deg) is assumed, not seen.',
       'Base 11: the STS3215 is The Robot Studio\'s STEP (SO-ARM100, STS3215_03a), not a servo in hand. The base bears on its rails with 4 M2 (M2x8, self-tapped into the case as the SO-101 does with M2x6) and the pinion on its horn with 4 M3 (as the SO-101 fixes its links); no torque, backlash or stall test. Its far case screws sit 2 mm from the base\'s edge.',
       'Base 14: the gripper hangs on the base\'s wrist tab (2 M3 self-tapped into 6 mm of printed plate) and the bracket\'s foot carries it to the J6 axis; no load, stiffness or fatigue test, and the bus cable\'s run past the tie point to J6 is not modelled.',
       'Mount 2: the SO-101 and its wrist-roll horn are The Robot Studio\'s meshes (SO-ARM100 a758567, Simulation/SO101, decimated to 20%), not an arm in hand. The horn face is the stock fixed jaw\'s seat on its mesh (gripper_link z -3.0) and its screw circle the jaw\'s 4 holes (14, 0.7 mm off the URDF\'s roll axis; the hub follows the jaw). The roll envelope is checked for every roll angle but in one arm pose; the cable run and the wrist-flex sweep are not checked.',
       'Mount 2: the gripper (about 300 g with its STS3215) hangs on the SO-101\'s wrist-roll horn by 4 countersunk M3 with 2.3 mm of thread in a plastic horn; the SO-101\'s own jaw uses the same 4 holes. No load, stiffness or stall test of the STS3215 wrist under this heavier tool.',
       'Base 10: the Aero Hand\'s insert positions come from the guide\'s left palm mesh (third_party/aero_hand/guide/anim41), not from the hand itself or its Onshape CAD.'])
    (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results:print(('PASS' if r['passed'] else 'FAIL')+': '+r['name']+(f" {r.get('overlap_z','')}" if 'overlap_z' in r else '')+(f" worst {r['worst_mm']} mm" if 'worst_mm' in r else '')+(f" {r['included_deg']} deg" if 'included_deg' in r else ''))
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
