"""Read actual PrusaSlicer extrusion paths, hash evidence, and draw review figures."""
from pathlib import Path
import json,re,hashlib,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
HERE=Path(__file__).resolve().parent

def read(path):
 pos=dict(X=0.,Y=0.,Z=0.);role='';width=.45;segments=[]
 for line in path.read_text().splitlines():
  if line.startswith(';TYPE:'):role=line[6:]
  if line.startswith(';WIDTH:'):width=float(line[7:])
  if not line.startswith(('G0 ','G1 ')):continue
  v={k:float(x) for k,x in re.findall(r'([XYZE])(-?\d*\.?\d+)',line.split(';')[0])};q={k:v.get(k,pos[k]) for k in pos}
  dist=math.hypot(q['X']-pos['X'],q['Y']-pos['Y'])
  if v.get('E',0)>0 and dist>1e-5:segments.append(dict(a=[pos['X'],pos['Y']],b=[q['X'],q['Y']],z=q['Z'],role=role,width=width,length=dist))
  pos=q
 return segments

def main():
 rows=[];data={}
 for f in sorted((HERE/'slicing').glob('*.gcode')):
  s=read(f);data[f.stem]=s
  assert s,f
  bridges=[p for p in s if 'Bridge' in p['role']];over=[p for p in s if 'Overhang' in p['role']]
  firstz=min(p['z'] for p in s)
  r=dict(part=f.stem,extrusion_segments=len(s),layers=len(set(p['z'] for p in s)),first_layer_z_mm=min(p['z'] for p in s),first_layer_segments=sum(p['z']==firstz for p in s),bridge_segments=len(bridges),bridge_layers_mm=sorted(set(p['z'] for p in bridges)),overhang_layers_mm=sorted(set(p['z'] for p in over)),longest_bridge_extrusion_mm=max([p['length'] for p in bridges],default=0),minimum_line_width_mm=min(p['width'] for p in s),support_paths=sum('Support' in p['role'] for p in s),sha256=hashlib.sha256(f.read_bytes()).hexdigest())
  text=f.read_text();r['supports_off']='; support_material = 0' in text and '; raft_layers = 0' in text
  r['passed']=bool(r['supports_off'] and not r['support_paths'] and r['first_layer_segments']>0 and not bridges and not over)
  rows.append(r)
 fig,axes=plt.subplots(2,3,figsize=(16,10));fig.patch.set_facecolor('#f7f5ef')
 for ax,(k,s) in zip(axes.flat,data.items()):
  z=min(p['z'] for p in s);lines=[[p['a'],p['b']] for p in s if p['z']==z]
  ax.add_collection(LineCollection(lines,linewidths=.6,colors='#176b64'));ax.autoscale();ax.set_aspect('equal');ax.set_title(k.replace('_',' '),fontsize=15);ax.axis('off')
 for unused in axes.flat[len(data):]:unused.axis('off')
 fig.suptitle('Actual slicer first layers • supports OFF • 0.4 mm nozzle',fontsize=22);fig.tight_layout(rect=[0,0,1,.94]);(HERE/'previews').mkdir(exist_ok=True);fig.savefig(HERE/'previews/first_layers.png',dpi=120);plt.close(fig)
 s=data['pinion'];zs=sorted(set(p['z'] for p in s if 'Bridge' in p['role'] or 'Overhang' in p['role']))
 fig,axes=plt.subplots(1,max(1,len(zs)),figsize=(16,6));axes=np.atleast_1d(axes)
 if not zs:axes[0].text(.5,.5,'No bridge or overhang paths',ha='center',va='center',fontsize=26);axes[0].axis('off')
 for ax,z in zip(axes,zs):
  for color,select in [('#bcc8c5',lambda p:p['z']<z and p['z']>=z-.101),('#176b64',lambda p:p['z']==z and not ('Bridge' in p['role'] or 'Overhang' in p['role'])),('#db6328',lambda p:p['z']==z and ('Bridge' in p['role'] or 'Overhang' in p['role']))]:
   ax.add_collection(LineCollection([[p['a'],p['b']] for p in s if select(p)],colors=color,linewidths=.8))
  ax.autoscale();ax.set_aspect('equal');ax.axis('off');ax.set_title(f'Pinion roof • Z {z:.2f} mm')
 fig.suptitle('Orange: actual bridge / overhang paths • gray: previous layer',fontsize=19);fig.tight_layout();fig.savefig(HERE/'previews/bridge_paths.png',dpi=120);plt.close(fig)
 r=dict(passed=len(rows)==5 and all(p['passed'] for p in rows),slicer='Installed PrusaSlicer 2.9.4',profile='fdm_screen.ini; generic PLA 210/60 C, 0.4 nozzle, 0.1 layer/0.2 first, Arachne, 100% infill, 4 perimeters, no brim/raft/support',parts=rows,qualification='Actual exported-part paths inspected. No bridge or overhang paths; unprinted, no strength, adhesion, dimensional-fit or X1 machine-Gcode qualification. Open portable 3MF in Bambu Studio and select real machine profile.')
 (HERE/'slicer_checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));raise SystemExit(0 if r['passed'] else 1)
if __name__=='__main__':main()
