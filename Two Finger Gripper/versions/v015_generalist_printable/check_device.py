#!/usr/bin/env python3
"""Offline checks for the Generation 15 device around the fingers (check_geometry.py covers the fingers' contact).
Over the whole 0-30 deg swing: nothing that moves with a finger hits the fixed parts or the other side, and the
thumb-index web under the pivot plate stays empty. At rest: the parts that bolt together touch without overlapping,
the straps clear what they pass through, and the printed finger has no wall under two 0.4 mm perimeters.
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
    near=lambda s:f'placed({s},i){{carrier();digit_strap();}}'
    results=[
      check('right_swing_never_hits_the_fixed_parts_0_to_30',SWING+'intersection(){moving(1,i);fixed();}'),
      check('left_swing_never_hits_the_fixed_parts_0_to_30',SWING+'intersection(){moving(-1,i);fixed();}'),
      check('right_carrier_and_strap_never_hit_the_left_side_0_to_30',SWING+f'intersection(){{{near(1)};moving(-1,i);}}'),
      check('left_carrier_and_strap_never_hit_the_right_side_0_to_30',SWING+f'intersection(){{{near(-1)};moving(1,i);}}'),
      check('thumb_index_web_stays_empty_0_to_30',SWING+'intersection(){web_zone();union(){moving(1,i);moving(-1,i);fixed();}}'),
      check('carrier_sits_on_its_finger_without_overlap','intersection(){carrier();whole_finger();}',touch=True),
      check('digit_strap_clears_the_carrier','intersection(){digit_strap();carrier();}'),
      check('digit_strap_clears_the_finger','intersection(){digit_strap();whole_finger();}'),
      check('pivot_plate_sits_on_nothing_but_washers','intersection(){pivot_plate();union(){moving(1,0);moving(-1,0);}}'),
      check('hand_frame_sits_on_the_pivot_plate_without_overlap','intersection(){hand_frame();pivot_plate();}',touch=True),
      check('camera_mount_sits_on_the_frame_without_overlap','intersection(){camera_mount();hand_frame();}',touch=True),
      check('camera_sits_in_its_mount_without_overlap','intersection(){camera();camera_mount();}',touch=True),
      check('wrist_strap_only_touches_the_frame','intersection(){wrist_strap();hand_frame();}',touch=True),
      check('positive_control_a_web_zone_40mm_wider_catches_the_carriers','intersection(){scale([4.4,1,1])web_zone();union(){moving(1,0);moving(-1,0);}}',False),
      min_wall()]
    report=dict(sampled_angles_degrees=list(range(31)),results=results,limitations=[
      'Each finger is swept 0-30 deg on its own and both together at the same angle; unequal angles are not sampled, but no carrier reaches past the centreline.',
      'Washers, bolts and nuts are not modelled; their clearances are from catalogue sizes (README).',
      'The hand is not modelled: the thumb/index digit (22.5 mm), wrist (60 x 44 mm) and back-of-hand height are nominal, not measured.'])
    (HERE/'device_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results:print(('PASS' if r['passed'] else 'FAIL')+': '+r['name']+(f" {r['min_wall_mm']} mm at {r['at_xz']}" if 'min_wall_mm' in r else ''))
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
