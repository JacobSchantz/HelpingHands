"""Review views from actual exported solids, with no schematic replacement of tips."""
from pathlib import Path
import sys,json,math,numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from Scripts.check_finger_plane_constraints import clipped,projection
HERE=Path(__file__).resolve().parent;F=ROOT/'Two Finger Gripper/versions/v325_generalist_original_tip_closure';OLD=F.with_name('v324_generalist_contact_close')
def mesh(folder,k,angle):
 sub='reference' if k.endswith('screws') or k in ['pivot_washers','pivot_nuts','center_screw'] else 'parts'
 m=trimesh.load_mesh(folder/f'exports/{sub}/{k}.stl');p=15 if folder==F else 10
 if k in ['left','right']:
  s=1 if k=='right' else -1;c=np.array([s*p,0,0]);a=math.radians((angle-15)*s);r=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]]);m.vertices=(m.vertices-c)@r.T+c
 return m

def plan(ax,folder,angle,zoom=False):
 for k in ['left','right']:
  q=projection(clipped(mesh(folder,k,angle),-2.999,2.999))
  for poly in ([q] if q.geom_type=='Polygon' else q.geoms):
   x,z=poly.exterior.xy;ax.fill(x,z,color='#eeb83b',ec='#79551b',lw=.6)
   for h in poly.interiors:x,z=h.xy;ax.fill(x,z,color='#f0f4f8')
 ax.set_aspect('equal');ax.set_facecolor('#f0f4f8');ax.axvline(0,color='#388d99',ls='--',lw=.7)
 ax.set_xlabel('X across fingers (mm)');ax.set_ylabel('Z along fingers (mm)')
 if zoom:ax.set_xlim(-9,9);ax.set_ylim(52,65)
 else:ax.set_xlim(-50,50);ax.set_ylim(-18,67)

def side(ax):
 roles=['base','motor','pinion','stock_plate','pivot_screws','pivot_washers','pivot_nuts','left','right'];tri=[];depth=[];colors=[]
 u=np.array([.87,.25,-.43]);v=np.array([-.04,.9,.44]);n=np.cross(u,v)
 for k in roles:
  m=mesh(F,k,0);t=m.triangles;tri.extend(np.stack([t@u,t@v],axis=2));depth.extend((t@n).mean(1));colors.extend([('#eeb83b' if k in ['left','right'] else '#8592a4' if k=='motor' else '#3b485a')]*len(t))
 order=np.argsort(depth);ax.add_collection(PolyCollection(np.array(tri)[order],facecolors=np.array(colors)[order],edgecolors='none'));ax.autoscale();ax.set_aspect('equal');ax.set_facecolor('#f0f4f8');ax.set_xticks([]);ax.set_yticks([])

def main():
 fig,axes=plt.subplots(2,2,figsize=(16,12),facecolor='#fafcff');fig.subplots_adjust(top=.88,bottom=.12,wspace=.2,hspace=.32)
 fig.suptitle('Original tips. Wider bases. No added connectors.',fontsize=27,weight='bold',y=.974)
 fig.text(.5,.925,'Base 24 + Gripper 28 · 30 mm pivots · centered motor · 4 printed / 19 total parts',ha='center',fontsize=17)
 plan(axes[0,0],OLD,0,True);axes[0,0].set_title('Before: added noses and trimmed original tips',fontsize=16)
 plan(axes[0,1],F,0,True);axes[0,1].set_title('Closed: original rounded tips touch',fontsize=16)
 plan(axes[1,0],F,30);axes[1,0].set_title('Open: original blade shape, 0–30° stroke',fontsize=16)
 side(axes[1,1]);axes[1,1].set_title('Overhead integral drive; local pivot support only',fontsize=16)
 fig.text(.5,.065,'121 poses × 78 body pairs pass · 10.33 mm continuous rear gap · original-blade solid comparison passes',ha='center',fontsize=16)
 fig.text(.5,.028,'CAD only. Whole-hand screening fails; physical plate threads, driver engagement and strength unverified.',ha='center',fontsize=14,color='#a8322b')
 fig.savefig(HERE/'comparison.png',dpi=100);(F/'previews').mkdir(exist_ok=True);fig.savefig(F/'previews/comparison.png',dpi=100);plt.close(fig)
if __name__=='__main__':main()
