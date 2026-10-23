"""Render actual STL top/side comparison; no invented human hand."""
from pathlib import Path
import sys,json,numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from Scripts.check_finger_plane_constraints import BASELINE,VERSIONS,projection
HERE=Path(__file__).resolve().parent

def draw(ax,folder,side):
 manifest=json.loads((folder/'viewer_parts.json').read_text());tri=[];col=[];depth=[]
 for part in manifest['parts']:
  t=trimesh.load_mesh(folder/part['path']).triangles
  tri.extend(t[:,:,[2,1] if side else [0,2]])
  depth.extend(t[:,:,0 if side else 1].mean(1));col.extend([part['color']]*len(t))
 order=np.argsort(depth);ax.add_collection(PolyCollection(np.asarray(tri)[order],facecolors=np.asarray(col)[order],edgecolors='none'))
 if not side:
  f=folder/'exports/parts/top_plate.stl'
  if not f.exists():f=folder/'exports/reference/pivot_washers.stl'
  outline=projection(trimesh.load_mesh(f))
  for p in ([outline] if outline.geom_type=='Polygon' else outline.geoms):
   x,z=p.exterior.xy;ax.plot(x,z,color='#168aad',lw=2.5)
 ax.set_aspect('equal');ax.set_facecolor('#eef2f6');ax.grid(alpha=.15)
 if side:
  ax.set_xlim(-70,75);ax.set_ylim(-10,50);ax.axhspan(-3,3,color='#efb83b',alpha=.25);ax.set_xlabel('Along fingers Z (mm)');ax.set_ylabel('Above fingers Y (mm)')
 else:
  ax.set_xlim(-43,43);ax.set_ylim(-66,70);ax.set_xlabel('Across fingers X (mm)');ax.set_ylabel('Along fingers Z (mm)')

def main():
 reports=[json.loads((HERE/f'{n}.json').read_text()) for n in ('base20','base21')]
 fig,axes=plt.subplots(2,2,figsize=(16,12),facecolor='#f7f9fb',gridspec_kw={'height_ratios':[1.5,1]});fig.subplots_adjust(top=.84,bottom=.13,hspace=.3,wspace=.2)
 fig.suptitle('Only the two pivots cross the finger band.',fontsize=26,weight='bold',y=.98)
 fig.text(.5,.935,'Gold = unchanged fingers   |   Blue outline = lower plate / local washers   |   Side band = Y -3 to +3 mm',ha='center',fontsize=15)
 for i,(folder,title,report) in enumerate(zip((BASELINE,VERSIONS/'v322_generalist_two_pivot_support'),('Base 20 + Gripper 25','Base 21 + same Gripper 25'),reports)):
  draw(axes[0,i],folder,False);draw(axes[1,i],folder,True)
  axes[0,i].set_title(f"{title}\nIn-plane support {report['minimal_in_plane_support']['band_support_area_mm2']:.1f} mm²",fontsize=17)
  axes[1,i].set_title('Same finger plane; 0.8 mm gear gap',fontsize=15)
 fig.text(.25,.065,'BEFORE: broad lower plate + rear pillars\nJaw solids excluded from support area',ha='center',fontsize=16,color='#985b00')
 fig.text(.75,.065,'AFTER: local retainers; CAD stroke passes\nWhole-hand screening FAILS; physical fit unverified',ha='center',fontsize=16,color='#b3261e')
 fig.savefig(HERE/'comparison.png',dpi=100);
 (VERSIONS/'v322_generalist_two_pivot_support/previews').mkdir(exist_ok=True)
 fig.savefig(VERSIONS/'v322_generalist_two_pivot_support/previews/comparison.png',dpi=100);plt.close(fig)
if __name__=='__main__':main()
