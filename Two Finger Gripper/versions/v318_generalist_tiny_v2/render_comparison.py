"""Render the actual STL triangles, with normalized and true-scale comparisons."""
from pathlib import Path
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import params
from export_models import PARTS
HERE=Path(__file__).resolve().parent

def draw(ax,folder,scale=1,shift=0):
 tris=[];colors=[];depth=[]
 for k in PARTS+(['motor'] if (folder/'motor.stl').exists() else []):
  m=trimesh.load_mesh(folder/f'{k}.stl');t=m.triangles*scale;t[:,:,0]+=shift
  tris.extend(t[:,:,[0,2]]);depth.extend(t[:,:,1].mean(1));colors.extend(['#efb83b' if k in ('left','right') else '#9aa3b0' if k=='motor' else '#343a44']*len(t))
 order=np.argsort(depth);ax.add_collection(PolyCollection(np.array(tris)[order],facecolors=np.array(colors)[order],edgecolors='none'))
 ax.autoscale_view();ax.set_aspect('equal');ax.axis('off')

def main():
 s=params.values()['scale_factor'];fig=plt.figure(figsize=(16,12),facecolor='#f4f6f9');gs=fig.add_gridspec(2,2,height_ratios=[1.5,1],hspace=.3)
 fig.suptitle('Tiny V2 • the same gripper, smaller, with the original servo mounting',fontsize=26,weight='bold',y=.97)
 a=fig.add_subplot(gs[0,0]);draw(a,HERE.parent/'v316_generalist_post_cap/exports/parts');a.set_title('LARGE • Base 15 + Gripper 22',fontsize=18)
 a=fig.add_subplot(gs[0,1]);draw(a,HERE/'exports/parts',1/s);a.set_title('TINY V2 • Base 17 + Gripper 24\n50% fingers • real servo remains full size',fontsize=18)
 a=fig.add_subplot(gs[1,:]);draw(a,HERE.parent/'v316_generalist_post_cap/exports/parts',1,-80);draw(a,HERE/'exports/parts',1,65);a.set_title('Actual size ratio • full 0–30° stroke • new 30:30:24 gears',fontsize=18)
 fig.text(.5,.035,'50% fingers • 70.03 mm full moving width\nStock STS3215 + horn + M2/M3 mounting • fine resin prototype',ha='center',fontsize=18,color='#9a3b29')
 (HERE/'previews').mkdir(exist_ok=True);fig.savefig(HERE/'previews/large_vs_tiny.png',dpi=100,facecolor=fig.get_facecolor());plt.close(fig)
if __name__=='__main__':main()
