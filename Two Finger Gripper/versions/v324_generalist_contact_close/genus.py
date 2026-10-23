"""Four physical print solids; integral jaw/sector parts retain the original lattice holes."""
from pathlib import Path
import trimesh
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
 for name,want in {'left':33,'right':33,'pinion':3,'base':3}.items():
  m=trimesh.load_mesh(HERE/f'exports/print/{name}.stl');got=(2-m.euler_number)//2
  assert m.is_watertight and len(m.split())==1 and got==want,(name,got,want)
  print('PASS',name,'genus',got)
