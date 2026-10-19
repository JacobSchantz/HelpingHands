#!/usr/bin/env python3
"""Bounded geometry checks, using OpenSCAD's exact solid intersections.
No electronics, motors, printers, or applications are controlled by this script.
"""
from pathlib import Path
import json
import math
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
OPENSCAD = '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'

def check(name, body):
    with tempfile.TemporaryDirectory(prefix='parallel_gripper_check_') as tmp:
        src = Path(tmp) / 'check.scad'
        output = Path(tmp) / 'intersection.stl'
        src.write_text(f'include <{HERE / "gripper.scad"}>\n{body}\n')
        p = subprocess.run([OPENSCAD, '-D', 'part="none"', '-o', str(output), str(src)], capture_output=True, text=True)
        log = p.stdout + p.stderr
        empty = 'Current top level object is empty.' in log and not output.exists()
        if not empty:
            failure = HERE / 'exports' / f'FAILED_{name}.stl'
            if output.exists():
                failure.write_bytes(output.read_bytes())
        return {'name': name, 'passed': empty, 'log': log.strip()}

def main():
    # This is a sampled sweep in 1 mm increments, not a continuous-motion proof.
    results = []
    results.append(check('frame_and_opposed_slides', 'for(g=[8:1:70]) translate([0,0,g*100]) collisions(g);'))
    results.append(check('rack_pinion_mesh', '''
for(g=[8:1:70]) let(pos=g/2+pad_offset) translate([0,0,g*100]) intersection() {
    translate([0,0,gear_z]) rotate([0,0,pos/pitch_r*180/PI+90+180/teeth]) spur_gear();
    union() {
        translate([-pos,0,0]) rack();
        translate([pos,0,0]) rotate([0,0,180]) rack();
    }
}'''))
    # Verify the center/outer collar surfaces actually prevent travel past limits.
    # The expected collision is tested separately; an empty intersection is failure.
    for name, gap in [('closing_stop', 7), ('opening_stop', 71)]:
        stops = check(name, f'collisions({gap});')
        stops['passed'] = not stops['passed'] and '3D object' in stops['log']
        expected_artifact = HERE / 'exports' / f'FAILED_{name}.stl'
        if stops['passed'] and expected_artifact.exists():
            expected_artifact.unlink()
        results.append(stops)
    # Encoder board clearance: body top is z14.8, carriage bottom is z16.
    results.append(check('encoder_board_clearance', '''
for(g=[8:1:70]) let(pos=g/2+pad_offset) translate([0,0,g*100]) intersection() {
    translate([0,0,14]) cube([18,18,1.6],center=true);
    union() {
        translate([-pos,0,0]) carriage();
        translate([pos,0,0]) rotate([0,0,180]) carriage();
    }
}'''))
    report = {
        'sampled_gaps_mm': list(range(8,71)),
        'parallelism': 'Jaw carriages translate only along X on two fixed guide rods; their contact-plane normals remain +/-X.',
        'kinematics': 'gap = 2 * (pitch_radius * pinion_angle_radians - pad_offset), with a fixed zero offset.',
        'independence': 'Each module has a distinct shaft, rack pair, guide pair, servo and sensors. Only the fixed support is shared.',
        'results': results,
        'limitations': ['No selected bearings, servo horn, load cell or encoder package.', 'No force, fit, friction, backdrive, fatigue or print validation.', 'Contact-pad sensor envelopes are conceptual; mounting and calibration remain open.']
    }
    (HERE / 'geometry_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    for result in results:
        print(('PASS' if result['passed'] else 'FAIL') + ': ' + result['name'])
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)

if __name__ == '__main__':
    main()
