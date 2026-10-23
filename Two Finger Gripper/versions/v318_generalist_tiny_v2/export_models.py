"""Export faithful Tiny V2 CAD; no application build or hardware operation."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess
import params
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
PARTS=['left','right','left_gear','right_gear','pinion','base','top_plate']
def scad(out,part):
 out.parent.mkdir(parents=True,exist_ok=True)
 p=subprocess.run([SCAD,'--backend','manifold','--export-format','binstl','-D',f'part="{part}"','-o',str(out),str(HERE/'gripper.scad')],capture_output=True,text=True)
 if p.returncode or 'WARNING' in p.stderr:raise RuntimeError(p.stderr)
def main():
 params.write_scad()
 jobs=[(HERE/f'exports/{folder}/{k}.stl',f'{prefix}_{k}') for folder,prefix in [('parts','viewer'),('print','print')] for k in PARTS]
 jobs += [(HERE/f'exports/reference/{k}.stl',f'viewer_{k}') for k in ['horn_screws','case_screws','cap_screws']]
 jobs += [(HERE/'exports/assembly.stl','assembly'),(HERE/'exports/parts/motor.stl','viewer_motor'),(HERE/'exports/reference/cable.stl','viewer_cable'),(HERE/'exports/reference/actual_sts3215.stl','hardware_reference')]
 with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda j:scad(*j),jobs))
 original=json.loads((HERE.parent/'v316_generalist_post_cap/viewer_parts.json').read_text())
 pieces=[]
 for p in original['parts']:
  k=Path(p['path']).stem
  if k not in PARTS+['motor']:continue
  p=dict(p);p['name']=p['name'].split(' — ')[0]+' — Tiny V2, original mechanism with full-size hardware interfaces';p['explode']=[v*params.values()['scale_factor'] for v in p['explode']];pieces.append(p)
 (HERE/'viewer_parts.json').write_text(json.dumps(dict(no_handles=True,finger_lineage=dict(builds_on='Gripper 22',gist='Tiny V2, half-size original lattice fingers'),parts=pieces),indent=2)+'\n')
 print('Exported seven mechanism parts in assembly and print orientations; actual servo mounted, cable reference separate.')
if __name__=='__main__':main()
