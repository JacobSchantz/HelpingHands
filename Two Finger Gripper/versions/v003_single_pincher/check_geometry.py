#!/usr/bin/env python3
"""Sampled OpenSCAD solid intersections only; no device or hardware operations."""
from pathlib import Path
import json, subprocess, tempfile
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'

def check(name,body,expect_empty=True):
    with tempfile.TemporaryDirectory(prefix='generalist_g3_') as tmp:
        src=Path(tmp)/'check.scad'; out=Path(tmp)/'intersection.stl'
        src.write_text(f'include <{HERE / "gripper.scad"}>\n'+body+'\n')
        p=subprocess.run([SCAD,'-D','part="none"','-D','show_straps=false','-D','show_sensor=false','-o',str(out),str(src)],capture_output=True,text=True)
        log=p.stdout+p.stderr
        empty='Current top level object is empty.' in log and not out.exists()
        passed=empty if expect_empty else out.exists() and 'NoError' in log
        failed_artifact=HERE/'exports'/('FAILED_'+name+'.stl')
        if not passed and out.exists(): failed_artifact.write_bytes(out.read_bytes())
        elif passed: failed_artifact.unlink(missing_ok=True)
        return dict(name=name,passed=passed,expected='empty' if expect_empty else 'positive contact',log=log.strip())

def main():
    results=[
      check('free_motion_half_degree_samples','for(a=[0:0.5:22]) translate([0,0,a*150]) clash(a);'),
      check('gear_mesh_half_degree_samples','for(a=[0:0.5:22]) translate([0,0,a*150]) intersection(){placed(-1,a) xz(5) gear2d(180/teeth); placed(1,a) xz(5) gear2d();}'),
      check('closing_stop_overrun','clash(-0.5);',False),
      check('opening_stop_overrun','clash(22.5);',False),
      check('floating_force_pad_no_rigid_bypass','intersection(){sensor_pad();union(){jaw(-1);guide_lands();}}'),
      check('sensor_seat_material_clearance','intersection(){translate([-5,0,pad_z])x_cyl(8,4);union(){jaw(-1);guide_lands();}}')]
    report=dict(sampled_jaw_angles_degrees=[i/2 for i in range(45)],
      dof='One input angle; the equal gears counter-rotate the two jaws. These are angular jaws, not parallel slides.',
      contact_patch_gap_mm={str(a):2*(12-10*__import__('math').cos(__import__('math').radians(a))+50*__import__('math').sin(__import__('math').radians(a))) for a in (0,18,22)},
      results=results,limitations=['Sampled intersections only, not a continuous motion/strength proof.','Motor body/horn, bearing fits and sensor remain unselected.','No human fit, print, backdrive, force calibration, friction, fatigue or payload validation.','Sensor reads the local normal force at its patch; other contacts and operator backdrive effort are not measured.'])
    (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results: print(('PASS' if r['passed'] else 'FAIL')+': '+r['name'])
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
