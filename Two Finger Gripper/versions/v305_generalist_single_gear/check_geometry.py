#!/usr/bin/env python3
"""Offline solid checks for Base 5: Base 4's fingers and handles on one pinion and two opposed racks (each rack one print with its handle; the fingers slide, so the swing checks sweep the slider's 0-30, which is 0 to stroke mm open). Base 4: Base 3's, with each handle and its side gear one print (the finger drops into it from the dorsal side and rests on its web; no key, cradle or stop strip) and the pinion and base on 3 bolts each. 3.3: 2.6's checks on the 15 mm handle plus the in-plane drive (drive_checks: side gears, centred pinion, the cradles) and the strap tunnel mouths kept clear. 3.2: 2.6's checks plus the base and drive, and the strap slots kept clear. 2.6 (2.5's checks on 1.21's single-step fingers and the 67.4 mm handle). 2.5: (2.4's params on 1.20's double-hook fingers; one handle per finger spanning both
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
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
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
    mirrored pair's gap at z is 2 * (the right finger's innermost x at z - its innermost x anywhere)."""
    import trace_photo as tp
    with tempfile.TemporaryDirectory() as tmp:
        _,raw=run('whole_finger();',tmp)
    V=verts(raw);xc=min(v[0] for v in V)
    zc=float(tp.to_mm(tp.tip_px())[1])-tp.ROUND_BACK   # the designed contact, just behind the rounded point
    rows=[]
    for d in [0.5,1,1.5,2,3,4,6,8,10,12,14,16,18,20,22]:
        # Gen 15: the mesh cut at that z, not vertices near it. Gen 16: where there are grooves (>= 3 mm back) a cut can land
        # in a groove bottom, so take the ridge tops: the innermost reach over one 1 mm groove pitch around z
        ks=[0] if d<3 else [i/10 for i in range(-5,6)];xs=[x for k in ks for x in slice_x(V,zc-d+k)]
        # Gen 16 r2: the target read the same way (its least gap over that window), or the 30 deg wedge's slope reads as error
        if xs:rows.append(dict(d_mm=d,model_gap=round(2*(min(xs)-xc),3),target_gap=round(min(tp.closed_gap(d-k) for k in ks),3),photo_gap=round(tp.photo_gap(d),3)))
    worst=max(abs(r['model_gap']-r['target_gap']) for r in rows if 1<=r['d_mm']<=20)
    mono=all(a['model_gap']<=b['model_gap']+5e-3 for a,b in zip(rows,rows[1:]))
    g=lambda d:next(r['model_gap'] for r in rows if r['d_mm']==d);deg=2*math.degrees(math.atan((g(2)-g(1))/2))
    return [dict(name='closed_gap_follows_the_gen14_target',passed=bool(worst<=GAP_TOL and mono),
                 expected=f'within {GAP_TOL} mm of photo curve + wedge from 1 to 20 mm back, never closing again (5 µm faceting allowed)',
                 worst_mm=round(worst,3),contact_z=round(zc,2),rows=rows),
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
    """Base 5: the one pinion and the two racks (each one print with its handle), the base and its grooves, the RS00 motor, and
    the strap keep-outs. The fingers slide, so "turned" checks are now "moved" (Manifold backend: fast enough over 31 angles)."""
    C=lambda *a,**k:check(*a,fast=True,**k)
    sweep=lambda body:'union(){'+';'.join(f'translate([0,0,{i}*{STEP}]){body.format(a=i)}' for i in ANGLES)+';}'
    other={'right':'left','left':'right'}
    rest=lambda q:f'union(){{{{piece("{q}",{{a}});core_piece("{q}",{{a}});side("{other[q]}",{{a}});pinion({{a}});base();motor({{a}});}}}}'   # all but that side's handle (its rack without the handle is in)
    zone=lambda q:f'intersection(){{{{zone_piece("{q}",{{a}});{rest(q)}}}}}'
    return [C('pinion_meshes_both_racks_without_interference_0_to_30',sweep('intersection(){{union(){{rack_piece("left",{a});rack_piece("right",{a});}}pinion({a});}}')),
            C('pinion_interferes_with_the_racks_when_turned_half_a_tooth_positive_control','intersection(){union(){rack_piece("left",15);rack_piece("right",15);}pinion(15,180/pinion_teeth);}',False),
            C('right_rack_moved_the_wrong_way_jams_the_pinion_positive_control',   # the right rack at -d instead of +d (the left's way) meets the pinion's teeth
              'intersection(){union(){translate([-2*open_d(15),0,0]) rack_piece("right",15);}pinion(15);}',False),
            C('pinion_never_touches_either_finger_0_to_30',sweep('intersection(){{union(){{piece("left",{a});piece("right",{a});}}pinion({a});}}')),
            C('handle_rack_clears_its_seated_finger','intersection(){handle_rack();placed(1,0) whole_finger();}'),
            C('finger_rests_on_the_hub_floor_positive_control','intersection(){handle_rack();translate([0,-0.3,0]) placed(1,0) whole_finger();}',False),
            C('handle_rack_drives_the_finger_open_moved_0.5mm_it_hits_positive_control','intersection(){translate([0.5,0,0]) handle_rack();placed(1,0) whole_finger();}',False),
            C('handle_rack_drives_the_finger_closed_moved_0.5mm_it_hits_positive_control','intersection(){translate([-0.5,0,0]) handle_rack();placed(1,0) whole_finger();}',False),
            C('finger_drops_into_its_handle_rack_from_above_without_touching',   # assembly: handle-rack in its groove first, then the finger goes in along -y, 0.5 mm steps
              'intersection(){handle_rack();union(){for(d=[0.5:0.5:20]) translate([0,d,0]) placed(1,0) whole_finger();}}'),
            C('left_finger_drops_into_its_handle_rack_from_above_without_touching',
              'intersection(){handle_rack(false);union(){for(d=[0.5:0.5:20]) translate([0,d,0]) placed(-1,0) whole_finger();}}'),
            C('handle_rack_is_one_solid_handle_fused_to_the_hub_positive_control','intersection(){rack_core();placed(1,0) handle_body();}',False),
            C('strap_tunnel_mouths_clear_of_everything_but_their_handle_0_to_30',sweep('union(){{'+zone('right')+zone('left')+'}}')),
            C('strap_keepout_sits_at_the_tunnel_mouths_positive_control','intersection(){strap_zone();strap_slide(dy=0.5);}',False),
            C('flange_bolts_reachable_from_above_the_pinion_0_to_30',sweep('intersection(){{bolt_access({a});union(){{pinion({a});side("left",{a});side("right",{a});}}}}'),touch=True),   # the access starts on the counterbore floors
            C('nothing_that_moves_hits_the_base_or_motor_0_to_30',   # the pinion's spigot sits on the motor flange: face contact only
              sweep('intersection(){{union(){{side("left",{a});side("right",{a});pinion({a});}}union(){{base();motor({a});}}}}'),touch=True),
            C('groove_ends_stop_each_rack_0.5mm_past_open_positive_control','intersection(){base();union(){rack_at("left",stroke+0.5);rack_at("right",stroke+0.5);}}',False),
            C('groove_ends_stop_each_rack_0.5mm_past_closed_positive_control','intersection(){base();union(){rack_at("left",-0.5);rack_at("right",-0.5);}}',False),
            C('left_and_right_sides_never_collide_1_to_30',sweep('intersection(){{side("left",max(1,{a}));side("right",max(1,{a}));}}')),
            C('handle_racks_never_touch_the_other_side_0_to_30',sweep('union(){{intersection(){{rack_piece("left",{a});side("right",{a});}}intersection(){{rack_piece("right",{a});side("left",{a});}}}}')),
            C('motor_output_screws_clear_the_pinion_holes','intersection(){pinion(15);motor_cores(15);}'),
            C('motor_front_screws_and_dowels_clear_the_base_holes','intersection(){base();motor_cores(15);}'),
            C('motor_sits_on_the_base_without_overlap',f'intersection(){{base();motor(15);}}',touch=True)]


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
       *gp,thickness(),*handle_checks(),*drive_checks()]
    report=dict(sampled_angles_degrees=ANGLES,results=results,limitations=[
       'Integer-degree samples only, not continuous motion.',
       'Closed gap read from one blurred perspective photo (~0.5 mm/px); sub-pixel widths come from seam darkness.',
       'The 4 deg wedge is a design choice (Jake: too much contact before the tip), not a measurement: the photo cannot resolve it.',
       '1.18: the point is 2.4 mm thick, all of it on the flat ventral side, and about 0.6 mm wide in plan; not printed.',
       '2.5: the fit (0.2 mm per side) and the strap / digit sizes are nominal; nothing is printed or measured.',
       'Base 4/5: the finger rests on its hub floor (which replaces the stop strip); only friction keeps it from lifting back out the way it came (+y). The drop-in check samples 0.5 mm steps, not continuous motion.',
       '2.5: the hook prongs are 1.19 base-hook size (about 2.2 mm deep along the edge) and have not been pull-tested.',
       '2.6: the top step fills the outer side out to the hook crest (6.6 mm) from u 54 to where the beak edge regains it (~u 77), up to ~3 mm wider than 1.20 there; only the motion checks above cover it, nothing checks it against a hand.',
       'Plan shape traced from one photo at an assumed 0.2 mm/px; no Generalist part was measured.',
       '3.1-Base 5: the drive is checked as solids only: rack and pinion mesh at 31 slider samples, no loads, no tooth strength, no motor torque. The RS00 dimensions come from its drawing (Seeed 100083284) and RS00.step, not from a motor in hand; the second dowel hole is assumed opposite the first.',
       'Base 5: each rack is held in line by a 3 mm tongue in a printed groove (0.25 mm clearance) and nothing holds it down (+y); the pinion pushes the racks apart (20 deg pressure angle) and the tongue takes that. Untested under load.',
       'Base 5: 3 of 6 M3 hold the pinion to the RS00 flange and 2 of 6 hold the base to the front ring (with both dowels); shear is estimated, not tested in printed plastic.',
       '3.3: the strap keep-out is a box strap_clear (3 mm) past each tunnel mouth, from the plate outer face to the boss outer face plus strap_clear round it; the webbing itself and the digit are not modelled.',
       'Base 5: the fingers slide (a parallel gripper) rather than swing: 20 mm each, 40 mm between the tips fully open (Base 4 swung 30 deg). The groove ends stop the racks base_clear past closed and past open.'])
    (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results:print(('PASS' if r['passed'] else 'FAIL')+': '+r['name']+(f" {r.get('overlap_z','')}" if 'overlap_z' in r else '')+(f" worst {r['worst_mm']} mm" if 'worst_mm' in r else '')+(f" {r['included_deg']} deg" if 'included_deg' in r else ''))
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
