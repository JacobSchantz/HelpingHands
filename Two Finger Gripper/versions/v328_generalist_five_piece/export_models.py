"""Export Base 27 and Gripper 31, plus actual-size hardware probes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess
import params
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
PARTS=PRINTS=['left','right','pinion','base','retaining_plate']
REFS=['plate_screws','plate_washers','case_screws','center_screw','capture_washer','pivot_screws','pivot_nuts','cable','plate_tools','case_tools','center_tools','pivot_tools','nut_tools','case_straight_tools']
def scad(out,part):
 out.parent.mkdir(parents=True,exist_ok=True)
 p=subprocess.run([SCAD,'--backend',('CGAL' if part.endswith(('left','right','base')) else 'manifold'),'--export-format','binstl','-D',f'part="{part}"','-o',str(out),str(HERE/'gripper.scad')],capture_output=True,text=True)
 if p.returncode or 'WARNING' in p.stderr:raise RuntimeError(p.stderr)
def normalize_jaw(path):
 import trimesh,numpy as np
 from scipy.spatial import cKDTree
 m=trimesh.load_mesh(path);before=m.volume
 if not m.is_watertight:
  # Binary STL rounds independent CGAL vertices to float32. Weld only points
  # within0.00002mm; keep every triangle except duplicate-index zero-area faces.
  idx=np.arange(len(m.vertices))
  def root(i):
   while idx[i]!=i:i=idx[i]
   return i
  for a,b in cKDTree(m.vertices).query_pairs(.00002):idx[root(b)]=root(a)
  remap=np.array([root(i) for i in idx]);faces=remap[m.faces]
  keep=(faces[:,0]!=faces[:,1])&(faces[:,1]!=faces[:,2])&(faces[:,0]!=faces[:,2])
  q=trimesh.Trimesh(m.vertices,faces[keep],process=False);q.remove_unreferenced_vertices();q.update_faces(q.unique_faces())
  if not q.is_watertight or len(q.split())!=1 or abs(q.volume-before)>max(.0001,abs(before)*1e-5):raise RuntimeError(f'Unrepairable STL quantization: {path}')
  q.export(path)

def main():
 params.write_scad()
 jobs=[(HERE/f'exports/parts/{k}.stl',f'viewer_{k}') for k in PARTS+['motor','stock_plate']]+[(HERE/f'exports/print/{k}.stl',f'print_{k}') for k in PRINTS]+[(HERE/f'exports/reference/{k}.stl',f'viewer_{k}') for k in REFS]
 import sys
 if '--reuse' not in sys.argv:
  with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda j:scad(*j),jobs))
 for folder in ['parts','print']:
  for k in ['left','right']:normalize_jaw(HERE/f'exports/{folder}/{k}.stl')
 entries=[]
 names={'left':'Left finger integral jaw','right':'Right finger integral jaw','pinion':'Pinion','base':'Top motor frame','retaining_plate':'Bottom retaining plate','motor':'Motor HLS3606M','stock_plate':'Stock aluminum spline plate','plate_screws':'Plate screws (2)','plate_washers':'Plate washers (2)','case_screws':'Case screws (4)','center_screw':'Center screw','capture_washer':'Metal capture washer','pivot_screws':'M2 tie rods (2)','pivot_nuts':'Pivot nuts (4)'}
 for k in PARTS+['motor','stock_plate']+[r for r in REFS if not r.endswith('_tools') and r!='cable']:
  entries.append(dict(path=f'exports/{"reference" if k in REFS else "parts"}/{k}.stl',name=names[k]+' — Base 27, Gripper 31',color='#efb83b' if k in ['left','right'] else '#718096' if k in REFS or k in ['motor','stock_plate'] else '#28776e',explode=[-30 if k=='left' else 30 if k=='right' else 0,60 if k=='base' else -40 if k=='retaining_plate' else -70 if k=='pivot_screws' else 80 if k=='pivot_nuts' else 15,35 if k=='motor' else 0]))
 import trimesh
 trimesh.util.concatenate([trimesh.load_mesh(HERE/e['path']) for e in entries]).export(HERE/'exports/assembly.stl')
 (HERE/'viewer_parts.json').write_text(json.dumps(dict(no_handles=True,parts=entries,finger_lineage=dict(builds_on='Gripper 30',gist='Integral tapered gear supports; five support-free printed pieces'),preview='previews/comparison.png'),indent=2)+'\n')
 print('Five printed pieces exported.')
if __name__=='__main__':main()
