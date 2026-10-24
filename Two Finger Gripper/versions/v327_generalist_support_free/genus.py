"""Every real printed component is watertight; count separate motor spacers explicitly."""
from pathlib import Path
import trimesh
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
 for f in sorted((HERE/'exports/print').glob('*.stl')):
  m=trimesh.load_mesh(f);parts=m.split();want=4 if f.stem=='ear_spacers' else 1
  assert m.is_watertight and len(parts)==want,(f.stem,len(parts))
  assert all(c.volume>0 and c.euler_number<=2 for c in parts),f.stem
  print('PASS',f.stem,'components',len(parts),'genus',[(2-c.euler_number)//2 for c in parts])
