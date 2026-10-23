"""Preserve lattice and verify the new mount's holes remain open."""
from pathlib import Path
import trimesh
HERE=Path(__file__).resolve().parent
EXPECTED={'left':32,'right':32,'left_gear':3,'right_gear':3,'pinion':4,'base':1,'top_plate':3}
if __name__=='__main__':
 for k,want in EXPECTED.items():
  m=trimesh.load_mesh(HERE/f'exports/print/{k}.stl');got=(2-m.euler_number)//2
  assert got==want,(k,got,want)
  assert m.is_watertight and len(m.split())==1,k
  print('PASS',k,'genus',got)
