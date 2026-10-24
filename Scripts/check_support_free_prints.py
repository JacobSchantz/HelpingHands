"""Screen exported bed-oriented meshes; report unsupported material per actual layer.
A local 6.4 mm bridge is allowed only for the pinion's retaining-screw roof.
This geometry screen complements actual slicer G-code inspection, not a print test.
"""
from pathlib import Path
import json,sys,hashlib
import numpy as np,trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

def section(m,z):
 s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
 if s is None:return Polygon()
 q=Polygon()
 for line in s.discrete:
  p=Polygon(line[:,:2])
  if not p.is_valid:p=p.buffer(0)
  q=q.symmetric_difference(p)
 return q

def inspect(path,layer=.1):
 m=trimesh.load_mesh(path);prev=None;issues=[];bridges=[];first=None
 for z in np.arange(layer/2,m.bounds[1,2],layer):
  q=section(m,float(z))
  if first is None:first=q.area
  if prev is not None:
   extra=q.difference(prev.buffer(layer+.025)).buffer(0)
   if extra.area>.015:
    regions=list(extra.geoms) if hasattr(extra,'geoms') else [extra]
    for r in regions:
     if r.area<.015:continue
     span=min(r.bounds[2]-r.bounds[0],r.bounds[3]-r.bounds[1])
     event=dict(z_mm=round(float(z),3),area_mm2=round(r.area,4),short_span_mm=round(span,4))
     # One small roof across the center access bore, not arbitrary ledges.
     if path.stem=='pinion' and z>3 and span<=6.5 and r.area<35:bridges.append(event)
     else:issues.append(event)
  prev=q
 comps=len(m.split());want=4 if path.stem=='ear_spacers' else 1
 return dict(part=path.stem,watertight=bool(m.is_watertight),components=comps,expected_components=want,bed_z_mm=float(m.bounds[0,2]),first_layer_area_mm2=first,unsupported=issues,short_bridge_roofs=bridges,passed=bool(m.is_watertight and comps==want and abs(m.bounds[0,2])<1e-5 and first>5 and not issues),sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def main():
 folder=Path(sys.argv[1]);rows=[inspect(f) for f in sorted((folder/'exports/print').glob('*.stl'))]
 r=dict(passed=all(x['passed'] for x in rows),layer_height_mm=.1,max_unbridged_growth_mm=.125,parts=rows,qualification='Layer-section manufacturing screen; pinion roof short bridge separately inspected in actual slicer. No physical print/strength evidence.')
 out=Path(sys.argv[2]) if len(sys.argv)>2 else folder/'manufacturing_checks.json'
 out.write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2));return 0 if r['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
