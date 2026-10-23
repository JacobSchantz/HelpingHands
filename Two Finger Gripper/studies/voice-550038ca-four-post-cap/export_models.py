"""Export Base 21 and Gripper 25, plus actual-size hardware probes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess
import params
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
PARTS=['left','right','left_gear','right_gear','pinion','base','top_plate']
REFS=['plate_screws','case_screws','cap_screws','center_screw','cable','plate_tools','case_tools','cap_tools','center_tools','case_straight_tools']
def scad(out,part):
 out.parent.mkdir(parents=True,exist_ok=True)
 p=subprocess.run([SCAD,'--backend','manifold','--export-format','binstl','-D',f'part="{part}"','-o',str(out),str(HERE/'gripper.scad')],capture_output=True,text=True)
 if p.returncode or 'WARNING' in p.stderr:raise RuntimeError(p.stderr)
def main():
 params.write_scad()
 jobs=[(HERE/f'exports/{folder}/{k}.stl',f'{prefix}_{k}') for folder,prefix in [('parts','viewer'),('print','print')] for k in PARTS]
 jobs += [(HERE/f'exports/reference/{k}.stl',f'viewer_{k}') for k in REFS]
 jobs += [(HERE/'exports/assembly.stl','assembly')]+[(HERE/f'exports/parts/{k}.stl',f'viewer_{k}') for k in ['motor','stock_plate']]
 with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda j:scad(*j),jobs))
 original=json.loads((HERE.parent.parent/'versions/v319_generalist_hls3606m/viewer_parts.json').read_text())
 for p in original['parts']:
  p['name']=p['name'].split(' — ')[0].replace('handle-gear','drive gear')+' — Base 21 compact overhead HLS3606M drive, Gripper 25'

 original['finger_lineage']=dict(builds_on='Gripper 24',gist='Gripper 24 with smaller pivot, integral short hex boss and no handles')
 original['preview']='previews/comparison.png'
 (HERE/'viewer_parts.json').write_text(json.dumps(original,indent=2)+'\n')
 print('Exported seven printed parts; actual single-shaft servo and purchased spline plate.')
if __name__=='__main__':main()
