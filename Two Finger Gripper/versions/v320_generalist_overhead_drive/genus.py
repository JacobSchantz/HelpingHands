"""Report closed mesh topology; assert unchanged Gripper 22 topology."""
from pathlib import Path
import json,trimesh
HERE=Path(__file__).resolve().parent
rows=[]
for f in sorted((HERE/'exports/print').glob('*.stl')):
 m=trimesh.load_mesh(f)
 assert m.is_watertight and m.volume>0 and len(m.split())==1,f
 row=dict(part=f.stem,genus=(2-m.euler_number)//2)
 if f.stem in ('left','right'):
  original=trimesh.load_mesh(HERE.parent/f'v316_generalist_post_cap/exports/print/{f.name}')
  assert m.euler_number==original.euler_number
 rows.append(row)
(HERE/'mesh_topology.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS',len(rows),'single closed print meshes; Gripper 22 topology unchanged.')
