"""Export Base 18 and unchanged Gripper 24, plus actual-size hardware probes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess
import params
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
PARTS=['left','right','left_gear','right_gear','pinion','base','top_plate']
REFS=['plate_screws','case_screws','cap_screws','center_screw','cable']
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
 original=json.loads((HERE.parent/'v318_generalist_tiny_v2/viewer_parts.json').read_text())
 for p in original['parts']:
  p['name']=p['name'].split(' — ')[0]+' — Base 18 HLS3606M drive, Gripper 24'
 original['parts'].append(dict(path='exports/parts/stock_plate.stl',name='Stock aluminum spline plate — purchased HLS3606M part',color='#a3a8ad',explode=[0,-30,0]))
 original['finger_lineage']=dict(builds_on='Gripper 24',gist='Unchanged Tiny V2 fingers')
 (HERE/'viewer_parts.json').write_text(json.dumps(original,indent=2)+'\n')
 print('Exported seven printed parts; actual single-shaft servo and purchased spline plate.')
if __name__=='__main__':main()
