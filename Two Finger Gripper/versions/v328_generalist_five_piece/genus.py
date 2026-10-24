"""Topology report of every actual printed/exported body, not a proxy assembly."""
from pathlib import Path
import json,trimesh
HERE=Path(__file__).resolve().parent
rows=[]
for f in sorted((HERE/'exports/print').glob('*.stl')):
 m=trimesh.load_mesh(f)
 rows.append(dict(part=f.stem,components=len(m.split()),watertight=bool(m.is_watertight),genus=(2-m.euler_number)//2,volume_mm3=float(m.volume),passed=bool(m.is_watertight and len(m.split())==1 and m.volume>0)))
r=dict(passed=len(rows)==5 and all(x['passed'] for x in rows),printed_parts=rows,physical_assembly_components=len(trimesh.load_mesh(HERE/'exports/assembly.stl').split()))
(HERE/'topology_checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));raise SystemExit(0 if r['passed'] and r['physical_assembly_components']==23 else 1)
