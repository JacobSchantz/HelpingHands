"""Reject lost lattice holes, loop bores or merged pieces after scaling."""
from pathlib import Path
import trimesh
from export_models import PARTS
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
 for k in PARTS:
  a=trimesh.load_mesh(HERE/f'exports/print/{k}.stl');b=trimesh.load_mesh(HERE.parent/f'v316_generalist_post_cap/exports/print/{k}.stl')
  want=5 if k=='base' else (2-b.euler_number)//2
  assert (2-a.euler_number)//2==want,(k,a.euler_number,b.euler_number)
  print(f'PASS: {k}: genus {(2-a.euler_number)//2}, matches retained holes (base omits two unused wrist-tab pilots)')
