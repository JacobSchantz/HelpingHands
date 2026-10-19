#!/usr/bin/env python3
"""Offline bounded solid/mesh timing checks; no motor/device operations."""
from pathlib import Path
import json, re, struct, subprocess, tempfile
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
ANGLES=[i/2 for i in range(45)]

def check(name,body,empty=True,all_sample_contacts=False):
    with tempfile.TemporaryDirectory(prefix='generalist_g5_') as tmp:
        src=Path(tmp)/'check.scad';out=Path(tmp)/'intersection.stl'
        src.write_text(f'include <{HERE/"gripper.scad"}>\n'+body+'\n')
        cmd=[SCAD,'--export-format','binstl','-D','part="none"','-o',str(out),str(src)]
        p=subprocess.run(cmd,capture_output=True,text=True);log=p.stdout+p.stderr
        is_empty='Current top level object is empty.' in log and not out.exists()
        passed=is_empty if empty else out.exists() and 'NoError' in log
        occupied=[]
        if all_sample_contacts and out.exists():
            raw=out.read_bytes();n=struct.unpack_from('<I',raw,80)[0];seen=set()
            for i in range(n):
                q=struct.unpack_from('<12fH',raw,84+i*50)
                center_z=(q[5]+q[8]+q[11])/3
                seen.add(round(center_z/200))
            occupied=sorted(seen);passed=passed and occupied==list(range(len(ANGLES)))
        artifact=HERE/'exports'/('FAILED_'+name+'.stl')
        if not passed and out.exists():artifact.write_bytes(out.read_bytes())
        elif passed:artifact.unlink(missing_ok=True)
        return dict(name=name,passed=passed,expected='empty' if empty else 'positive contact at every sample' if all_sample_contacts else 'positive contact',occupied_sample_indices=occupied,log=log.strip())

def main():
    results=[
       check('free_motion_half_degree_samples','for(i=[0:44])translate([0,0,i*200])clash(i/2);'),
       check('gear_mesh_no_material_overlap','for(i=[0:44])translate([0,0,i*200])gear_pair(i/2);'),
       check('gear_flank_engages_plus_1deg','for(i=[0:44])translate([0,0,i*200])gear_pair(i/2,1);',False,True),
       check('gear_flank_engages_minus_1deg','for(i=[0:44])translate([0,0,i*200])gear_pair(i/2,-1);',False,True),
       check('minimum_3mm_channel_to_inner_face_wall','intersection(){finger_groove();wall_guard();finger_blank();}'),
       check('minimum_1mm_channel_side_lips','intersection(){finger_groove();side_wall_guard();}'),
       check('mirror_finger_body_and_common_bores','difference(){placed(-1)finger_body();mirror([1,0,0])placed(1)finger_body();}'),
       check('adapter_fits_common_jaw_socket','intersection(){piece("adapter");piece("right");}'),
       check('closing_stop_positive_control','intersection(){hub();moving(-0.5,false);}',False),
       check('opening_stop_positive_control','intersection(){hub();moving(22.5,false);}',False)]
    report=dict(sampled_jaw_angles_degrees=ANGLES,
      dof='ONE input -> right jaw gear -> equal counter-rotation of left jaw gear, ratio1:1.',
      tooth_phase_deg=dict(right=0,left=7.5),minimum_protected_groove_wall_mm=3,minimum_side_lip_mm=1,
      results=results,limitations=[
       '45 sampled poses, not continuous motion or strength proof.',
       'Plus/minus1degree intentional follower misphase produces gear overlap at ALL45poses; this bounds nominal freeplay but is not a manufactured backlash measurement.',
       'Wall guard covers distance to inner profile; intentional tie apertures and final rounded tip are not minimum-wall test regions.',
       'Unselected motor, mount/horn and pivot/adapter retention; no print/fit/wear/backdrive validation.',
       'No force transducer: both object pinch force and human input effort remain unmeasured.'])
    (HERE/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for r in results:print(('PASS' if r['passed'] else 'FAIL')+': '+r['name'])
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
