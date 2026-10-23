"""Preserve lattice and verify the new mount's holes remain open."""
from pathlib import Path
import trimesh
HERE=Path(__file__).resolve().parent
EXPECTED={'left':33,'right':33,'left_gear':1,'right_gear':1,'pinion':4,'base':1,'top_plate':2}
if __name__=='__main__':
 for k,want in EXPECTED.items():
  m=trimesh.load_mesh(HERE/f'exports/print/{k}.stl');got=(2-m.euler_number)//2
  assert got==want,(k,got,want)
  assert m.is_watertight and len(m.split())==1,k
  print('PASS',k,'genus',got)
