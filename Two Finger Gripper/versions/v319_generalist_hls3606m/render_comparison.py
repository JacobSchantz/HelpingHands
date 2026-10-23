"""Draw actual exported triangles at matched scale, front and side, for human review."""
from pathlib import Path
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
HERE=Path(__file__).resolve().parent
PARTS=['left','right','left_gear','right_gear','pinion','base','top_plate','motor']
def draw(ax,folder,side=False):
 tris=[];colors=[];depth=[]
 for k in PARTS+(['stock_plate'] if (folder/'stock_plate.stl').exists() else []):
  t=trimesh.load_mesh(folder/f'{k}.stl').triangles
  tris.extend(t[:,:,[1,2] if side else [0,2]]);depth.extend(t[:,:,0 if side else 1].mean(1))
  colors.extend(['#f0b73e' if k in ('left','right') else '#b1bac4' if k in ('motor','stock_plate') else '#334454']*len(t))
 order=np.argsort(depth);ax.add_collection(PolyCollection(np.array(tris)[order],facecolors=np.array(colors)[order],edgecolors='none'))
 ax.set_xlim((-52,27) if side else (-47,47));ax.set_ylim(-82,79);ax.set_aspect('equal');ax.axis('off')
def main():
 fig,aa=plt.subplots(2,2,figsize=(16,12),facecolor='#f3f6fa');fig.subplots_adjust(top=.86,bottom=.13,hspace=.12,wspace=.1)
 fig.suptitle('Base 18: Aero Hand servo, same lattice fingers',fontsize=28,weight='bold',y=.97)
 fig.text(.5,.915,'Base 17 / STS3215     →     Base 18 / HLS3606M-C001',ha='center',fontsize=21)
 for col,(folder,title) in enumerate([(HERE.parent/'v318_generalist_tiny_v2','Base 17'),(HERE,'Base 18')]):
  draw(aa[0,col],folder/'exports/parts');aa[0,col].set_title(title+' · front',fontsize=18)
  draw(aa[1,col],folder/'exports/parts',True);aa[1,col].set_title(title+' · side',fontsize=18)
 fig.text(.5,.075,'Gripper 24 unchanged · 30:30:24 gears · 0–30° jaw stroke\n62.90 → 46.40 mm depth, including stated cable clearance',ha='center',fontsize=20)
 fig.text(.5,.022,'Actual STL geometry · matching scales · fine-resin CAD prototype · physical fit and force untested',ha='center',fontsize=14,color='#873e25')
 (HERE/'previews').mkdir(exist_ok=True);fig.savefig(HERE/'previews/base17_vs_base18.png',dpi=100,facecolor=fig.get_facecolor());plt.close(fig)
if __name__=='__main__':main()
