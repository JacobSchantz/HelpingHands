"""Export Base 19 from parameterized CAD; no application build."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,re,sys
import params
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
PARTS=['left','right','left_driver','right_driver','left_washer','right_washer','left_gear','right_gear','pinion','base','top_plate','bracket','tool_plate','hub']
def scad(out,part):
 out.parent.mkdir(parents=True,exist_ok=True)
 p=subprocess.run([SCAD,'--backend','manifold','--export-format','binstl','-D',f'part="{part}"','-o',str(out),str(HERE/'gripper.scad')],capture_output=True,text=True)
 if p.returncode or 'WARNING' in p.stderr or 'ERROR' in p.stderr:raise RuntimeError(p.stderr)
 return p.stderr
def main():
 params.write_scad()
 jobs=[(HERE/f'exports/parts/{k}.stl',f'viewer_{k}') for k in PARTS+['motor']]+[(HERE/'exports/reference/cable.stl','viewer_cable'),(HERE/'exports/assembly.stl','assembly')]
 jobs += [(HERE/f'exports/reference/{k}.stl',f'viewer_{k}') for k in ['retention_screws','horn_tools']]
 with ThreadPoolExecutor(max_workers=3) as pool: logs=list(pool.map(lambda j:scad(*j),jobs))
 import numpy as np
 import trimesh
 for k in PARTS:
  m=trimesh.load(HERE/f'exports/parts/{k}.stl',force='mesh');m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]));m.apply_translation([0,0,-m.bounds[0,2]])
  out=HERE/f'exports/print/{k}.stl';out.parent.mkdir(exist_ok=True);m.export(out)
 horn=json.loads(re.search(r'so101_horn = (\[.*?\])','\n'.join(logs)).group(1))
 sys.path.insert(0,str(HERE.parents[2]/'cad/arm/so101'))
 import so101_pose
 so101_pose.export(HERE/'exports/parts',horn=horn,roll_deg=params.values()['so_roll_deg'])
 old=json.loads((HERE.parent/'v316_generalist_post_cap/viewer_parts.json').read_text())
 names={Path(p['path']).stem:p for p in old['parts']}
 parts=[]
 for k in PARTS+['motor']:
  n=names.get(k,{'name':k.replace('_',' ').title(),'color':'#526977','explode':[0,-35,0]}).copy()
  n['path']=f'exports/parts/{k}.stl'
  if k in ['left_gear','right_gear']:n['name']=k.title()+' — overhead sector gear with integral stepped torque shaft'
  if k=='left_driver' or k=='right_driver':n['name']=k.title()+' — low strap-loop cradle with hex socket'
  if k=='base':n['name']='Base — overhead STS3215 rail seat, bored journals and cap pillars'
  if k=='hub':n['name']='Wrist hub — unchanged Mount 2 on SO-101 horn'
  if k=='top_plate':n['name']='Top plate — overhead cap with blind upper shaft sockets'
  parts.append(n)
 for f in sorted((HERE/'exports/parts').glob('arm_*.stl')):parts.append(dict(path=f'exports/parts/{f.name}',name='SO-101 Arm ('+f.stem[4:]+') — unchanged Arm 2 reference',color='#bcb8a3',explode=[0,0,-160]))
 (HERE/'viewer_parts.json').write_text(json.dumps(dict(no_handles=True,preview='previews/side_comparison.png',parts=parts),indent=2)+'\n')
 print('Exported Base 19, Gripper 22, Mount 2 and posed Arm 2; horn',horn)
if __name__=='__main__':main()
