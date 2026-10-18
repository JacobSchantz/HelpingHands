#!/usr/bin/env python3
"""Offline solid checks for Generation 10 (two fingers only); no hardware operations."""
from pathlib import Path
import json, subprocess, tempfile
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
ANGLES=list(range(0,31))
STEP=400

def check(name,body,empty=True):
    with tempfile.TemporaryDirectory(prefix='generalist_g10_') as tmp:
        src=Path(tmp)/'check.scad';out=Path(tmp)/'intersection.stl'
        src.write_text(f'include <{HERE/"gripper.scad"}>\n'+body+'\n')
        p=subprocess.run([SCAD,'--export-format','binstl','-D','part="none"','-o',str(out),str(src)],capture_output=True,text=True)
        log=p.stdout+p.stderr
        is_empty='Current top level object is empty.' in log and not out.exists()
        return dict(name=name,passed=is_empty if empty else out.exists() and 'NoError' in log,
                    expected='empty' if empty else 'contact',log=log.strip()[-400:])

def main():
    results=[
       check('fingers_never_collide_0_to_30_deg',f'for(i=[0:30])translate([0,0,i*{STEP}])clash(i);'),
       check('closed_tips_do_not_touch','clash(0);'),
       check('closed_tips_touch_with_gap_removed_positive_control',
             'intersection(){translate([0.6,0,0])piece("left",0);translate([-0.6,0,0])piece("right",0);}',False)]
    report=dict(sampled_angles_degrees=ANGLES,results=results,limitations=[
       'Integer-degree samples only, not continuous motion.',
       'Outline traced by eye from one photo at an assumed 0.2 mm/px; no Generalist part was measured.',
       'Pivot bore is a placeholder: no body, axle, drive or stops exist in this generation.'])
    (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results:print(('PASS' if r['passed'] else 'FAIL')+': '+r['name'])
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
