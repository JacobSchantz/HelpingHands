#!/usr/bin/env python3
"""Offline checks for the Generation 16 device around the fingers (check_geometry.py covers the fingers' contact).
Over the whole 0-30 deg swing: neither finger + side pad hits the pivot plate, the camera or the other side, and the
thumb-index web under the plate stays empty. At rest: the camera sits in its cradle, a nominal digit fits under each
pad without touching the finger, and the printed finger has no wall under two 0.4 mm perimeters.
No hardware operations."""
from pathlib import Path
import json, re, subprocess, tempfile
import numpy as np
from check_geometry import check, run
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
STEP=600
MIN_WALL=0.8
SWING=f'for(i=[0:30])translate([0,0,i*{STEP}])'   # one solid per sampled angle, spaced apart so they never merge


def min_wall():
    """Least distance between any two edges of the printed finger seen in plan (holes, slots, grooves, outline)."""
    with tempfile.TemporaryDirectory() as tmp:
        src=Path(tmp)/'p.scad';out=Path(tmp)/'p.svg'
        src.write_text(f'include <{HERE/"gripper.scad"}>\nprojection() rotate([90,0,0]) whole_finger();\n')
        subprocess.run([SCAD,'-D','part="none"','-o',str(out),str(src)],capture_output=True)
        d=re.findall(r'd="([^"]+)"',out.read_text())[0]
    loops=[]
    for l in [l for l in re.split(r'[zZ]',d) if l.strip()]:
        n=list(map(float,re.findall(r'-?[\d.]+',l)));loops.append(np.array(list(zip(n[::2],n[1::2]))))
    loops.sort(key=len,reverse=True)
    def dense(p,step=0.05):
        return np.concatenate([a+(b-a)*np.linspace(0,1,max(1,int(np.linalg.norm(b-a)/step)),endpoint=False)[:,None] for a,b in zip(p,np.roll(p,-1,0))])
    D=[dense(p) for p in loops];worst=(9e9,None)
    for i in range(1,len(D)):
        for j in range(i):
            dd=np.sqrt(((D[i][:,None,:]-D[j][None,:,:])**2).sum(-1)).min()
            if dd<worst[0]:worst=(dd,loops[i].mean(0).round(1).tolist())
    return dict(name=f'printed_finger_walls_at_least_{MIN_WALL}mm',passed=bool(worst[0]>=MIN_WALL-0.02),
                expected='every wall between holes, slots, grooves and the outline >= two 0.4 mm perimeters (Gen 14: 0.6)',
                min_wall_mm=round(float(worst[0]),3),at_xz=worst[1])


def main():
    pads=lambda s:f'placed({s},i)side_pad_only()'
    results=[
      check('right_swing_never_hits_the_plate_or_camera_0_to_30',SWING+'intersection(){moving(1,i);fixed();}'),
      check('left_swing_never_hits_the_plate_or_camera_0_to_30',SWING+'intersection(){moving(-1,i);fixed();}'),
      check('right_side_pad_never_hits_the_left_side_0_to_30',SWING+f'intersection(){{{pads(1)};moving(-1,i);}}'),
      check('left_side_pad_never_hits_the_right_side_0_to_30',SWING+f'intersection(){{{pads(-1)};moving(1,i);}}'),
      check('thumb_index_web_stays_empty_0_to_30',SWING+'intersection(){web_zone();union(){moving(1,i);moving(-1,i);fixed();}}'),
      check('pivot_plate_sits_on_nothing_but_washers','intersection(){pivot_plate();union(){moving(1,0);moving(-1,0);}}'),
      check('camera_sits_in_its_cradle_without_overlap','intersection(){camera();pivot_plate();}',touch=True),
      check('nominal_digit_rests_under_the_pad_clear_of_the_finger','intersection(){digit_zone();finger_pad();}',touch=True),
      check('strap_slot_is_clear_of_the_finger_below_it','intersection(){fy(-7,pad_y[0]+0.5)translate([strap_slot[0][0],strap_slot[1][0]])square([strap_slot[0][1]-strap_slot[0][0],strap_slot[1][1]-strap_slot[1][0]]);whole_finger();}'),
      check('positive_control_a_web_zone_reaching_the_pads_catches_them','intersection(){scale([4.4,1,1])web_zone();union(){moving(1,0);moving(-1,0);}}',False),
      min_wall()]
    report=dict(sampled_angles_degrees=list(range(31)),results=results,limitations=[
      'Each finger is swept 0-30 deg on its own and both together at the same angle; unequal angles are not sampled, but no side pad reaches past the centreline.',
      'Washers, bolts and nuts are not modelled; their clearances are from catalogue sizes (README).',
      'Straps are not modelled (Jake). The hand is not modelled: the digit under each pad is a nominal 22.5 mm cylinder.'])
    (HERE/'device_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results:print(('PASS' if r['passed'] else 'FAIL')+': '+r['name']+(f" {r['min_wall_mm']} mm at {r['at_xz']}" if 'min_wall_mm' in r else ''))
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
