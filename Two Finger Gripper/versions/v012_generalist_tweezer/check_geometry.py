#!/usr/bin/env python3
"""Offline solid checks for Generation 12, the tweezer (two fingers only); no hardware operations."""
from pathlib import Path
import json, struct, subprocess, tempfile
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
ANGLES=list(range(0,31))
STEP=400

def check(name,body,empty=True,touch=False):
    with tempfile.TemporaryDirectory(prefix='generalist_g12_') as tmp:
        src=Path(tmp)/'check.scad';out=Path(tmp)/'intersection.stl'
        src.write_text(f'include <{HERE/"gripper.scad"}>\n'+body+'\n')
        p=subprocess.run([SCAD,'--export-format','binstl','-D','part="none"','-o',str(out),str(src)],capture_output=True,text=True)
        log=p.stdout+p.stderr
        is_empty='Current top level object is empty.' in log and not out.exists()
        if touch and not is_empty:   # faces that only touch leave a sliver of float noise, no thicker than this
            raw=out.read_bytes();n=struct.unpack_from('<I',raw,80)[0]
            xs=[x for i in range(n) for x in struct.unpack_from('<12f',raw,84+i*50)[3::3]]
            is_empty=max(xs)-min(xs)<1e-3
        return dict(name=name,passed=is_empty if empty else out.exists() and 'NoError' in log,
                    expected=('touch only' if touch else 'empty') if empty else 'contact',log=log.strip()[-400:])

def main():
    results=[
       check('fingers_never_collide_1_to_30_deg',f'for(i=[1:30])translate([0,0,i*{STEP}])clash(i);'),
       check('closed_lands_touch_without_overlap_at_0_deg','clash(0);',touch=True),
       check('closed_lands_overlap_when_pushed_0.1mm_positive_control',
             'intersection(){translate([0.05,0,0])piece("left",0);translate([-0.05,0,0])piece("right",0);}',False),
       check('closed_lands_meet_along_the_tip_not_just_a_point',   # pushed 0.1 mm, the overlap runs most of the land, not one corner
             'intersection(){translate([0.05,0,0])piece("left",0);translate([-0.05,0,0])piece("right",0);translate([-5,-20,100])cube([10,40,5]);}',False)]
    report=dict(sampled_angles_degrees=ANGLES,results=results,limitations=[
       'Integer-degree samples only, not continuous motion.',
       'Outline traced by eye from one photo at an assumed 0.2 mm/px; no Generalist part was measured.',
       'Pivot bore is a placeholder: no body, axle, drive or stops exist in this generation.'])
    (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results:print(('PASS' if r['passed'] else 'FAIL')+': '+r['name'])
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
