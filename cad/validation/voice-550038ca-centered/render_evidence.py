"""Same-scale STL assembly/side/exploded comparison; every physical BOM item drawn."""
from pathlib import Path
import json,sys,numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
V=ROOT/'Two Finger Gripper/versions';OLD=V/'v322_generalist_two_pivot_support';NEW=V/'v323_generalist_centered_drive'
def entries(folder):
 rows=json.loads((folder/'viewer_parts.json').read_text())['parts']
 if folder==OLD:
  for k,qty in [('plate_screws',3),('case_screws',4),('center_screw',1)]:
   rows.append(dict(path=f'exports/reference/{k}.stl',name=f'{k} ({qty})',color='#8595a5',explode=[0,15,-25]))
 return rows

def draw(ax,folder,mode):
 triangles=[];colors=[];depth=[]
 # Oblique explosion uses real solids translated apart, never merged or omitted.
 u=np.array([.85,0,-.53]);vv=np.array([.2,.92,.32]);normal=np.cross(u,vv)
 for part in entries(folder):
  t=trimesh.load_mesh(folder/part['path']).triangles
  if mode=='exploded':
   name=part['name'].lower();off=np.array(part.get('explode',[0,0,0]),float)
   # Identical exploded offsets by role for fair comparison.
   if 'gear' in name and 'finger' not in name:off=np.array([-25 if 'left' in name else 25,22,0])
   elif 'left' in name:off=np.array([-25,0,0])
   elif 'right' in name:off=np.array([25,0,0])
   elif 'motor' in name:off=np.array([0,75,0])
   elif name.startswith('base'):off=np.array([0,40,0])
   elif 'pivot' in name and 'washer' in name:off=np.array([0,-18,0])
   elif 'pivot' in name and 'screw' in name:off=np.array([0,-32,0])
   elif 'nut' in name:off=np.array([0,60,0])
   else:off=np.array([0,15,-25])
   t=t+off;xy=np.stack([t@u,t@vv],axis=2);d=t@normal
  elif mode=='side':xy=t[:,:,[2,1]];d=t[:,:,0]
  else:xy=t[:,:,[0,2]];d=t[:,:,1]
  triangles.extend(xy);depth.extend(d.mean(1));colors.extend([part['color']]*len(t))
 order=np.argsort(depth);ax.add_collection(PolyCollection(np.asarray(triangles)[order],facecolors=np.asarray(colors)[order],edgecolors='none',rasterized=True))
 ax.set_aspect('equal');ax.set_facecolor('#edf2f7');ax.tick_params(labelsize=9);ax.grid(alpha=.15)
 if mode=='side':
  ax.set_xlim(-65,65);ax.set_ylim(-9,54);ax.axhspan(-3,3,color='#efb83b',alpha=.3);ax.set_xlabel('Along fingers (mm)',fontsize=10);ax.set_ylabel('Above hand (mm)',fontsize=10)
 elif mode=='top':
  ax.set_xlim(-43,43);ax.set_ylim(-55,70);ax.axvline(0,color='#398397',lw=1,ls='--');ax.set_xlabel('Across jaws (mm)',fontsize=10)
 else:ax.set_xlim(-75,75);ax.set_ylim(-40,145);ax.set_xlabel('Every physical part shown; fasteners included',fontsize=10)

def main():
 fig,axes=plt.subplots(2,3,figsize=(16,12),facecolor='#f8fafc',gridspec_kw={'width_ratios':[1,1.35,1.05]})
 fig.subplots_adjust(top=.86,bottom=.12,hspace=.26,wspace=.28)
 fig.suptitle('Centered motor. Closer pivots. Two fewer prints.',fontsize=27,weight='bold',y=.97)
 fig.text(.5,.925,'Base 21 + Gripper 25  →  Base 22 + Gripper 26',ha='center',fontsize=19)
 fig.text(.5,.889,'Pivots 31.35 → 19.60 mm   |   Printed parts 6 → 4   |   All physical parts 22 → 20',ha='center',fontsize=16)
 for i,folder in enumerate([OLD,NEW]):
  for j,mode in enumerate(['top','side','exploded']):
   draw(axes[i,j],folder,mode);axes[i,j].set_title(('Before' if i==0 else 'After')+' · '+mode,fontsize=15)
 fig.text(.5,.065,'After: rear gap ≈ 0.827 mm; two pivot sleeves only in the finger band; same total height.',ha='center',fontsize=16)
 fig.text(.5,.03,'Right upper drive teeth remain asymmetric. Whole-hand acceptance and physical strength are NOT approved.',ha='center',fontsize=14,color='#a52d22')
 fig.savefig(HERE/'comparison.png',dpi=100);(NEW/'previews').mkdir(exist_ok=True);fig.savefig(NEW/'previews/comparison.png',dpi=100);plt.close(fig)
if __name__=='__main__':main()
