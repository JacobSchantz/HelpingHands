"""Normalize pinned extracted Aero STEP solids; run with cad/build123d/.venv Python."""
from pathlib import Path
import json
from build123d import import_step, export_stl, Axis
HERE=Path(__file__).resolve().parent
v={p['name']:p['value'] for g in json.loads((HERE/'params.json').read_text())['groups'] for p in g['params']}
for name in ['servo','stock_plate','aero_spool']:
 q=import_step(HERE/f'reference/{name}.step')
 q=q.translate((-v['hls_ref_x'],-v['hls_ref_y'],-v['hls_ref_ear_z'])).rotate(Axis.X,-90).rotate(Axis.Y,90)
 export_stl(q,HERE/f'reference/{name}.stl',tolerance=.01,angular_tolerance=.05)
 print(name,q.bounding_box().min,q.bounding_box().max)
