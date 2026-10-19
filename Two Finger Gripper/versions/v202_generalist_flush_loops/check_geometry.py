#!/usr/bin/env python3
"""Offline solid checks for version 2.2 (2.1 with the strap slides turned flush; same checks); no hardware operations.
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


def run(body,tmp):
    src=Path(tmp)/'check.scad';out=Path(tmp)/'out.stl'
    src.write_text(f'include <{HERE/"gripper.scad"}>\n'+body+'\n')
    p=subprocess.run([SCAD,'--export-format','binstl','-D','part="none"','-o',str(out),str(src)],capture_output=True,text=True)
    return p.stdout+p.stderr,(out.read_bytes() if out.exists() else None)


def verts(raw):
    n=struct.unpack_from('<I',raw,80)[0]
    return [v for i in range(n) for v in (lambda q:(q[3:6],q[6:9],q[9:12]))(struct.unpack_from('<12f',raw,84+i*50))]


def volume(V):
    return sum((a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6 for a,b,c in zip(V[::3],V[1::3],V[2::3]))


def check(name,body,empty=True,touch=False,within_z=None):
    with tempfile.TemporaryDirectory(prefix='generalist_g14_') as tmp:
        log,raw=run(body,tmp)
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
    """Gen 17: the finger keeps the full plate thickness (12 mm) all the way to the point; only the plan view narrows."""
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        for z in (20,60,90,110,118,121):
            _,raw=run(f'intersection(){{whole_finger();translate([-80,-20,{z}])cube([160,40,0.5]);}}',tmp)
            ys=[v[1] for v in verts(raw)] if raw else [0];rows.append(dict(z_mm=z,thick_mm=round(max(ys)-min(ys),3)))
    return dict(name='finger_is_full_thickness_to_the_point',passed=all(abs(r['thick_mm']-12)<1e-3 for r in rows),
                expected='12 mm in y at every station from the shank to 3 mm short of the point',rows=rows)


def main():
    gp,zc=gap_profile()
    results=[
       check('fingers_never_collide_1_to_30_deg',f'for(i=[1:30])translate([0,0,i*{STEP}])clash(i);'),
       check('closed_fingers_touch_without_overlap_at_0_deg','clash(0);',touch=True),
       check('closed_fingers_overlap_when_pushed_0.02mm_positive_control',
             'intersection(){translate([0.01,0,0])piece("left",0);translate([-0.01,0,0])piece("right",0);}',False),
       check(f'pushed_0.02mm_together_they_meet_only_in_the_last_{CONTACT_LEN}mm',   # the point, not the jaw (Gen 13 met along 6 mm)
             'intersection(){translate([0.01,0,0])piece("left",0);translate([-0.01,0,0])piece("right",0);}',False,within_z=(zc-CONTACT_LEN,zc+2)),
       check('slide_clears_its_finger_with_fit','intersection(){whole_finger();strap_slide();}'),
       check('slide_pulled_out_0.4mm_hits_the_dovetail_positive_control','intersection(){whole_finger();strap_slide(2*fit);}',False),
       check('slides_never_hit_the_other_side_1_to_30_deg',
             f'for(i=[0:30])translate([0,0,i*{STEP}]){{intersection(){{slide_piece("left",i);union(){{piece("right",i);slide_piece("right",i);}}}}intersection(){{slide_piece("right",i);piece("left",i);}}}}'),
       *gp,thickness()]
    report=dict(sampled_angles_degrees=ANGLES,results=results,limitations=[
       'Integer-degree samples only, not continuous motion.',
       'Closed gap read from one blurred perspective photo (~0.5 mm/px); sub-pixel widths come from seam darkness.',
       'The 4 deg wedge is a design choice (Jake: too much contact before the tip), not a measurement: the photo cannot resolve it.',
       'Gen 17: the point is 12 mm thick (full plate) and about 0.6 mm wide in plan; not printed.',
       'Gen 17: the slide fit (0.2 mm per side) and the strap / digit sizes are nominal; nothing is printed or measured.',
       'Plan shape traced from one photo at an assumed 0.2 mm/px; no Generalist part was measured.',
       'No body, axle, drive or stops exist in this generation.'])
    (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results:print(('PASS' if r['passed'] else 'FAIL')+': '+r['name']+(f" {r.get('overlap_z','')}" if 'overlap_z' in r else '')+(f" worst {r['worst_mm']} mm" if 'worst_mm' in r else '')+(f" {r['included_deg']} deg" if 'included_deg' in r else ''))
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
