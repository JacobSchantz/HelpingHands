#!/usr/bin/env python3
"""Bounded, offline mechanism checks, not a continuous or hardware validation."""
from pathlib import Path
import json, math, re, subprocess, tempfile
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'

def check(name,body,empty=True,volume_tolerance=None):
    with tempfile.TemporaryDirectory(prefix='generalist_g4_') as tmp:
        src=Path(tmp)/'check.scad'; out=Path(tmp)/'intersection.stl'
        src.write_text(f'include <{HERE/"gripper.scad"}>\n'+body+'\n')
        p=subprocess.run([SCAD,'-D','part="none"','-o',str(out),str(src)],capture_output=True,text=True)
        log=p.stdout+p.stderr
        is_empty='Current top level object is empty.' in log and not out.exists()
        volume=None
        if volume_tolerance is not None and out.exists():
            vs=[tuple(map(float,q.split())) for q in re.findall(r'vertex\s+([^\n]+)',out.read_text())]
            volume=abs(sum(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]) for a,b,c in zip(vs[::3],vs[1::3],vs[2::3]))/6)
        passed=(is_empty or (volume is not None and volume<=volume_tolerance)) if empty else out.exists() and 'NoError' in log
        artifact=HERE/'exports'/('FAILED_'+name+'.stl')
        if not passed and out.exists():artifact.write_bytes(out.read_bytes())
        elif passed:artifact.unlink(missing_ok=True)
        return dict(name=name,passed=passed,expected='empty' if empty else 'positive contact',subtraction_volume_mm3=volume,volume_tolerance_mm3=volume_tolerance,log=log.strip())

def main():
    samples=[i/2 for i in range(45)]
    mid=2+10*math.sin(math.radians(22)); rows=[]
    for a in samples:
        r=math.radians(a); x=16-10*math.cos(r)-10*math.sin(r); z=10*math.sin(r)-10*math.cos(r)
        t=2+20*math.sin(r); phi=math.asin((t-mid)/6)
        rows.append(dict(jaw_angle_deg=a,slider_z_mm=t,servo_angle_deg=math.degrees(phi),
          follower_slot_error_mm=z-t-(x-18),crank_slot_error_mm=-30+6*math.sin(phi)-(t-30-mid),
          follower_slot_end_clearance_mm=min(x-1.5,7.5-x),
          crank_slot_end_clearance_mm=7-6*math.cos(phi),crank_vertical_gain_mm_per_radian=6*math.cos(phi)))
    algebra=dict(name='follower_constraints_and_no_crank_dead_center',passed=all(
       abs(q['follower_slot_error_mm'])<1e-10 and abs(q['crank_slot_error_mm'])<1e-10
       and q['follower_slot_end_clearance_mm']>0.25 and q['crank_slot_end_clearance_mm']>0.25
       and q['crank_vertical_gain_mm_per_radian']>4 for q in rows),samples=rows)
    results=[algebra,
      check('free_motion_half_degree_samples','for(a=[0:0.5:22]) translate([0,0,a*180]) clash(a);'),
      check('closing_stop_overrun','intersection(){hub();piece("yoke",-1.5);}',False),
      check('opening_stop_overrun','intersection(){hub();piece("yoke",23.5);}',False),
      check('mirror_jaw_geometry','difference(){placed(-1)jaw();mirror([1,0,0])placed(1)jaw();}'),
      check('centered_fixed_geometry','difference(){hub();mirror([1,0,0])hub();}',volume_tolerance=1e-8)]
    report=dict(dof='One servo rotation -> guided yoke translation -> equal and opposite jaw rotation.',
      intended_jaw_angles_degrees=[0,22],results=results,
      limitations=['45 sampled solid poses; not a continuous-motion, strength or tolerance proof.',
       'Servo, horn, follower/pivot retention, bearings, materials and fit remain unselected.',
       'No force sensor in Generation 4. Pinch force and operator effort are unmeasured.',
       'Sliding cams and an unknown servo gearbox may resist backdrive. No hardware was operated.'])
    (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results:print(('PASS' if r['passed'] else 'FAIL')+': '+r['name'])
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
