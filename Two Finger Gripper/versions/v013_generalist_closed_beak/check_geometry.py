#!/usr/bin/env python3
"""Offline solid checks for Generation 13, designed closed (two fingers only); no hardware operations.
Gen 13's spec is how the closed fingers contact: they touch at the point only, and behind it the gap
opens along the curve measured in the closed photo (trace_closed.py -> closed_trace.json)."""
from pathlib import Path
import json, struct, subprocess, tempfile
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
ANGLES=list(range(0,31))
STEP=400
GAP_TOL=0.12   # mm: the closed gap may differ from the photo's fitted curve by this much, 3 to 20 mm behind the point


def run(body,tmp):
    src=Path(tmp)/'check.scad';out=Path(tmp)/'out.stl'
    src.write_text(f'include <{HERE/"gripper.scad"}>\n'+body+'\n')
    p=subprocess.run([SCAD,'--export-format','binstl','-D','part="none"','-o',str(out),str(src)],capture_output=True,text=True)
    return p.stdout+p.stderr,(out.read_bytes() if out.exists() else None)


def verts(raw):
    n=struct.unpack_from('<I',raw,80)[0]
    return [v for i in range(n) for v in (lambda q:(q[3:6],q[6:9],q[9:12]))(struct.unpack_from('<12f',raw,84+i*50))]


def check(name,body,empty=True,touch=False,within_z=None):
    with tempfile.TemporaryDirectory(prefix='generalist_g13_') as tmp:
        log,raw=run(body,tmp)
        is_empty='Current top level object is empty.' in log and raw is None
        if touch and not is_empty:   # faces that only touch leave a sliver of float noise, no thicker than this
            xs=[v[0] for v in verts(raw)];is_empty=max(xs)-min(xs)<1e-3
        ok=is_empty if empty else raw is not None and 'NoError' in log
        extra={}
        if ok and within_z is not None:   # the overlap must lie only in this z range: the point, not the jaw
            zs=[v[2] for v in verts(raw)];extra=dict(overlap_z=[round(min(zs),2),round(max(zs),2)])
            ok=within_z[0]<=min(zs) and max(zs)<=within_z[1]
        return dict(name=name,passed=ok,expected=('touch only' if touch else 'empty') if empty else 'contact',**extra,log=log.strip()[-300:])


def gap_profile():
    """The closed gap of the exported right finger vs the photo's curve. A mirrored pair's gap at z is
    2 * (the right finger's innermost x at z - its innermost x anywhere)."""
    t=json.loads((HERE/'closed_trace.json').read_text())['gap_fit']
    with tempfile.TemporaryDirectory() as tmp:
        _,raw=run('finger();',tmp)
    V=verts(raw);xc=min(v[0] for v in V)
    import trace_photo as tp;zc=float(tp.to_mm(tp.tip_px())[1])-tp.ROUND_BACK   # the designed contact, where the photo's seam ends
    rows=[]
    for d in [1,2,3,4,6,8,10,12,14,16,18,20,22]:
        xs=[v[0] for v in V if abs(v[2]-(zc-d))<0.4]
        if xs:rows.append(dict(d_mm=d,model_gap=round(2*(min(xs)-xc),3),photo_gap=round(t['A']*d**t['P'],3)))
    worst=max(abs(r['model_gap']-r['photo_gap']) for r in rows if 3<=r['d_mm']<=20)
    mono=all(a['model_gap']<=b['model_gap']+5e-3 for a,b in zip(rows,rows[1:]))
    return dict(name='closed_gap_follows_the_photo_curve',passed=worst<=GAP_TOL and mono,
                expected=f'within {GAP_TOL} mm of the photo fit from 3 to 20 mm back, never closing again (5 µm faceting allowed)',
                worst_mm=round(worst,3),contact_z=round(zc,2),rows=rows),zc


def main():
    gp,zc=gap_profile()
    results=[
       check('fingers_never_collide_1_to_30_deg',f'for(i=[1:30])translate([0,0,i*{STEP}])clash(i);'),
       check('closed_fingers_touch_without_overlap_at_0_deg','clash(0);',touch=True),
       check('closed_fingers_overlap_when_pushed_0.02mm_positive_control',
             'intersection(){translate([0.01,0,0])piece("left",0);translate([-0.01,0,0])piece("right",0);}',False),
       check('pushed_0.02mm_together_they_meet_only_in_the_last_6mm',   # i.e. the contact is the point, not the jaw (Gen 11's mid-jaw reach)
             'intersection(){translate([0.01,0,0])piece("left",0);translate([-0.01,0,0])piece("right",0);}',False,within_z=(zc-6,zc+2)),
       gp]
    report=dict(sampled_angles_degrees=ANGLES,results=results,limitations=[
       'Integer-degree samples only, not continuous motion.',
       'Closed gap read from one blurred perspective photo (~0.5 mm/px); sub-pixel widths come from seam darkness.',
       'Plan shape traced from one photo at an assumed 0.2 mm/px; no Generalist part was measured.',
       'No body, axle, drive or stops exist in this generation.'])
    (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results:print(('PASS' if r['passed'] else 'FAIL')+': '+r['name']+(f" {r.get('overlap_z','')}" if 'overlap_z' in r else '')+(f" worst {r['worst_mm']} mm" if 'worst_mm' in r else ''))
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
