"""Same-scale side projection of actual exported STL triangles, measured finger band."""
from pathlib import Path
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
HERE=Path(__file__).resolve().parent
BASE=['left','right','left_gear','right_gear','pinion','base','top_plate','motor']
def draw(ax,folder,new):
 tris=[];colors=[];depth=[]
 for k in BASE+(['left_driver','right_driver','left_washer','right_washer'] if new else []):
  t=trimesh.load_mesh(folder/f'exports/parts/{k}.stl').triangles
  # Horizontal axis is along finger Z, vertical axis is dorsal height Y.
  tris.extend(t[:,:,[2,1]]);depth.extend(t[:,:,0].mean(1))
  colors.extend(['#efb83b' if k in ('left','right') else '#b5bec7' if k=='motor' else '#35596b']*len(t))
 order=np.argsort(depth);ax.add_collection(PolyCollection(np.array(tris)[order],facecolors=np.array(colors)[order],edgecolors='none'))
 ax.axhspan(-6,6,color='#e87e4f',alpha=.20,zorder=-1)
 ax.axhline(6,color='#cb6030',linestyle='--',linewidth=1);ax.axhline(-6,color='#cb6030',linestyle='--',linewidth=1)
 ax.set_xlim(-65,150);ax.set_ylim(-70,102);ax.set_aspect('equal');ax.set_xlabel('Along finger (mm)',fontsize=13);ax.set_ylabel('Dorsal height (mm)',fontsize=13)
 ax.spines[['top','right']].set_visible(False)
def main():
 fig,aa=plt.subplots(1,2,figsize=(16,12),facecolor='#f4f7fa');fig.subplots_adjust(top=.83,bottom=.20,wspace=.20)
 fig.suptitle('Clear the finger working plane',fontsize=32,weight='bold',y=.96)
 fig.text(.5,.90,'Base 19 · overhead STS3215 drive · Arm 2 / Mount 2',ha='center',fontsize=23)
 for ax,folder,title,new in [(aa[0],HERE.parent/'v316_generalist_post_cap','Base 15 · drive in finger band',False),(aa[1],HERE,'Base 19 · drive above finger band',True)]:
  draw(ax,folder,new);ax.set_title(title,fontsize=18)
 aa[0].text(35,12,'Measured finger band: 12 mm',fontsize=13,color='#a3441e')
 aa[1].annotate('Geared drive',xy=(-25,82),xytext=(15,96),arrowprops=dict(arrowstyle='->'),fontsize=15)
 aa[1].annotate('Stepped torque shafts',xy=(0,35),xytext=(20,52),arrowprops=dict(arrowstyle='->'),fontsize=15)
 aa[1].annotate('Existing fingers + cradles',xy=(40,0),xytext=(12,-30),arrowprops=dict(arrowstyle='->'),fontsize=15)
 fig.text(.5,.12,'8 mm gap above finger band, including reserved cable corridor\nGripper 22 unchanged · full 0–30° jaw stroke · shared Mount 2 interface',ha='center',fontsize=21)
 fig.text(.5,.045,'Actual CAD, matched scale · +Y must face up in use\nPhysical hand fit, shaft stiffness and bearing wear are unverified.',ha='center',fontsize=16,color='#914325')
 (HERE/'previews').mkdir(exist_ok=True);fig.savefig(HERE/'previews/side_comparison.png',dpi=100,facecolor=fig.get_facecolor());plt.close(fig)
if __name__=='__main__':main()
