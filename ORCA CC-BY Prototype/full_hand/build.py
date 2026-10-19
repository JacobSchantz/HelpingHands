from pathlib import Path
import urllib.request,json,hashlib,xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import trimesh
R=Path(__file__).resolve().parent;S=R/'source';S.mkdir(exist_ok=True)
SHA='b9b349a21ee0238c62b6cf92ae7597027867adf8'
BASE=f'https://raw.githubusercontent.com/orcahand/orcahand_description/{SHA}/'
def get(p):
 d=urllib.request.urlopen(BASE+p,timeout=60).read();q=S/Path(p).name;q.write_bytes(d)
 return {'upstream_path':p,'sha256':hashlib.sha256(d).hexdigest(),'file':'source/'+q.name}
records=[get('LICENSE'),get('v2/models/urdf/orcahand_right.urdf')]
r=ET.parse(S/'orcahand_right.urdf').getroot()
paths=sorted({x.get('filename').replace('package://orcahand_description/','') for x in r.findall('.//visual/geometry/mesh')})
with ThreadPoolExecutor(max_workers=6) as ex:records.extend(ex.map(get,paths))
def origin(e):
 o=e.find('origin');m=np.eye(4)
 if o is not None:
  m=trimesh.transformations.euler_matrix(*[float(v) for v in o.get('rpy','0 0 0').split()],axes='sxyz')
  m[:3,3]=np.array([float(v) for v in o.get('xyz','0 0 0').split()])*1000
 return m
links={x.get('name'):x for x in r.findall('link')};children={};childnames=set()
for j in r.findall('joint'):
 parent=j.find('parent').get('link');child=j.find('child').get('link');children.setdefault(parent,[]).append(j);childnames.add(child)
meshes=[];lines=['// ORCA official v2 visualization at zero joint pose. Not a manufacturing STL.', '// Source MIT license: source/LICENSE. See README.txt for version limits.'];instances=[]
def walk(name,t):
 for v in links[name].findall('visual'):
  me=v.find('geometry/mesh')
  if me is None:continue
  path=Path(me.get('filename')).name;mat=t@origin(v);scale=np.diag([float(z)*1000 for z in me.get('scale','1 1 1').split()]+[1]);mat=mat@scale
  mesh=trimesh.load(S/path,force='mesh',process=False);mesh.apply_transform(mat);meshes.append(mesh)
  lines.append('multmatrix('+json.dumps(mat.tolist())+') import("source/'+path+'");')
  instances.append({'link':name,'mesh':path,'matrix_mm':mat.tolist()})
 for j in children.get(name,[]):walk(j.find('child').get('link'),t@origin(j))
for name in sorted(links.keys()-childnames):walk(name,np.eye(4))
combined=trimesh.util.concatenate(meshes);combined.export(R/'orca_v2_assembled_visual.stl')
(R/'assembled_hand.scad').write_text('\n'.join(lines)+'\n')
(R/'view_stl.scad').write_text('$vpt=[0,85,0];\n$vpr=[15,0,0];\n$vpd=900;\n// Assembled visualization only; see README.txt\nimport("orca_v2_assembled_visual.stl");\n')
(R/'manifest.json').write_text(json.dumps({'repository':'https://github.com/orcahand/orcahand_description','commit':SHA,'units':'mm','pose':'all joints zero','files':records,'instances':instances,'triangles':len(combined.faces),'bounds_mm':combined.bounds.tolist()},indent=2)+'\n')
(R/'README.txt').write_text('ORCA assembled hand visualization\n\nOriginal official orcahand_description v2 visual meshes and URDF transforms, all joints at zero, converted to mm. Source license is preserved in source/LICENSE (MIT). This does not change the CC BY4 license of the separate hardware CAD files.\n\nOpen view_stl.scad to see the assembled STL in OpenSCAD; assembled_hand.scad imports individually positioned source parts. build.py reproduces both using numpy and trimesh.\n\nThis is the official v2 simulation appearance reference, not a verified complete v2.1 manufacturing assembly. It omits hardware details absent from those visual meshes. The combined STL contains separate/possibly intersecting shells; use it for viewing, not as a one-piece print or mechanical fit validation. Original manufacturing parts remain under ../upstream/.\n')
print('Saved',len(meshes),'assembled visual instances;',len(combined.faces),'triangles; bounds mm',combined.bounds)
