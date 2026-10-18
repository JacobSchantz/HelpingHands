#!/usr/bin/env python3
"""Offline bounded solid checks for Generation 6; no motor/device operations."""
from pathlib import Path
import json, struct, subprocess, tempfile
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
ANGLES=[i/2 for i in range(45)]
STEP=400

def check(name,body,empty=True,all_sample_contacts=False):
    with tempfile.TemporaryDirectory(prefix='generalist_g6_') as tmp:
        src=Path(tmp)/'check.scad';out=Path(tmp)/'intersection.stl'
        src.write_text(f'include <{HERE/"gripper.scad"}>\n'+body+'\n')
        p=subprocess.run([SCAD,'--export-format','binstl','-D','part="none"','-o',str(out),str(src)],capture_output=True,text=True)
        log=p.stdout+p.stderr
        is_empty='Current top level object is empty.' in log and not out.exists()
        passed=is_empty if empty else out.exists() and 'NoError' in log
        occupied=[]
        if all_sample_contacts and out.exists():
            raw=out.read_bytes();n=struct.unpack_from('<I',raw,80)[0]
            occupied=sorted({round(sum(struct.unpack_from('<12fH',raw,84+i*50)[5:12:3])/3/STEP) for i in range(n)})
            passed=passed and occupied==list(range(len(ANGLES)))
        artifact=HERE/'exports'/('FAILED_'+name+'.stl')
        if not passed and out.exists():artifact.write_bytes(out.read_bytes())
        elif passed:artifact.unlink(missing_ok=True)
        return dict(name=name,passed=passed,expected='empty' if empty else 'contact at every sample' if all_sample_contacts else 'contact',
                    occupied_sample_indices=occupied,log=log.strip()[-400:])

def sweep(body):return f'for(i=[0:44])translate([0,0,i*{STEP}]){body};'

def main():
    results=[
       check('free_motion_half_degree_samples',sweep('clash(i/2)')),
       check('thumb_index_web_empty_all_samples',sweep('intersection(){web_keepout();everything(i/2);}')),
       check('web_keepout_positive_control','intersection(){web_keepout();translate([0,0,-30])cube(4,center=true);}',False),
       check('gear_mesh_no_material_overlap',sweep('gear_pair(i/2)')),
       check('gear_flank_engages_plus_1deg',sweep('gear_pair(i/2,1)'),False,True),
       check('gear_flank_engages_minus_1deg',sweep('gear_pair(i/2,-1)'),False,True),
       check('tips_do_not_touch_when_closed','intersection(){piece("left_tip",0);piece("right_tip",0);}')]
    report=dict(sampled_jaw_angles_degrees=ANGLES,
      dof='ONE servo -> right gear -> equal counter-rotation of left gear, ratio 1:1.',
      web_keepout='hand-plane band |Y|<=12 mm, everything behind Z=-9.5 (behind the pivots), 120 mm wide',
      results=results,limitations=[
       '45 sampled poses, not continuous motion or strength proof.',
       '+/-1 degree follower misphase overlaps at all poses: bounds nominal freeplay, not measured backlash.',
       'Finger outline and perforations are estimated by eye from photos; no dimensions were measured from a real Generalist part.',
       'No hard travel stops in this generation; the servo limits travel.',
       'Unselected servo, horn, axle pins and fasteners; no print, fit, strength or backdrive validation.'])
    (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results:print(('PASS' if r['passed'] else 'FAIL')+': '+r['name'])
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
