"""Same-scale actual STL projections; side view marks the occupied finger slab."""
from pathlib import Path
import sys,math,json
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from Scripts.check_finger_plane_constraints import clipped,projection
HERE=Path(__file__).resolve().parent;F=ROOT/'Two Finger Gripper/versions/v326_generalist_small_drive';OLD=F.with_name('v325_generalist_original_tip_closure')
COLORS={'left':'#f5b83c','right':'#f5b83c','base':'#aac0d1','motor':'#667b8e','pinion':'#7461aa','stock_plate':'#adbdc7'}
def mesh(folder,k,angle=15):
 m=trimesh.load_mesh(folder/f'exports/parts/{k}.stl');r=0;c=np.zeros(3)
 if k in ['left','right']:r=1 if k=='right' else -1;c=np.array([r*15,0,0])
 elif k in ['pinion','stock_plate']:r=-18/28 if folder==F else -30/42;c=np.array([0,0,-10.6564534438 if folder==F else -32.7261363439])
 a=math.radians((angle-15)*r);R=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]]);m.vertices=(m.vertices-c)@R.T+c;return m

def view(ax,folder,side=False):
 keys=['base','motor','stock_plate','left','right','pinion'];tri=[];depth=[];colors=[]
 for k in keys:
  t=mesh(folder,k).triangles
  coords=[2,1] if side else [0,2];d=0 if side else 1
  tri.extend(t[:,:,coords]);depth.extend(t[:,:,d].mean(1));colors.extend([COLORS[k]]*len(t))
 order=np.argsort(depth);ax.add_collection(PolyCollection(np.array(tri)[order],facecolors=np.array(colors)[order],edgecolors='none',rasterized=True))
 if side:
  ax.axhspan(-3,3,color='#f3b640',alpha=.2);ax.set_xlim(-62,66);ax.set_ylim(-9,49);ax.text(-59,-1,'6 mm finger band',fontsize=11,color='#7b530a');ax.set_xlabel('Z along fingers (mm)');ax.set_ylabel('Y overhead (mm)')
 else:ax.set_xlim(-43,43);ax.set_ylim(-62,67);ax.set_xlabel('X across jaws (mm)');ax.set_ylabel('Z along fingers (mm)')
 ax.set_aspect('equal');ax.set_facecolor('#f2f6fa');ax.grid(alpha=.15)

def outline(ax,angle,zoom):
 for k in ['left','right']:
  q=projection(clipped(mesh(F,k,angle),-2.999,2.999))
  for poly in [q] if q.geom_type=='Polygon' else q.geoms:
   x,z=poly.exterior.xy;ax.fill(x,z,color='#f5b83c',ec='#735318',lw=.5)
   for h in poly.interiors:x,z=h.xy;ax.fill(x,z,color='#f2f6fa')
 ax.set_aspect('equal');ax.set_facecolor('#f2f6fa');ax.set_xlim(*((-8,8) if zoom else (-42,42)));ax.set_ylim(*((54,65) if zoom else (-12,65)));ax.set_xlabel('X (mm)');ax.set_ylabel('Z (mm)')

def main():
 fig,axes=plt.subplots(2,2,figsize=(16,12),facecolor='#fafcff',gridspec_kw={'height_ratios':[1.45,1]});fig.subplots_adjust(top=.87,bottom=.13,hspace=.30,wspace=.18)
 fig.suptitle('Smaller gears. Same original tips.',fontsize=28,weight='bold',y=.974)
 fig.text(.5,.925,'Base 25 + Gripper 29 · 30 mm pivots unchanged · 4 printed / 19 total parts',ha='center',fontsize=17)
 for i,f in enumerate([OLD,F]):
  view(axes[0,i],f);view(axes[1,i],f,True)
 axes[0,0].set_title('Before: Ø44 pinion / Ø32 upper sector',fontsize=18)
 axes[0,1].set_title('After: Ø24 pinion / Ø16 upper sector',fontsize=18)
 axes[1,0].set_title('Before: housing 47 × 59.7 mm',fontsize=17)
 axes[1,1].set_title('After: housing 37 × 32.2 mm',fontsize=17)
 fig.text(.5,.067,'Gear projection area −69% · housing material −70% · same 0–30° opening and 0.8 mm overhead tooth gap',ha='center',fontsize=16)
 fig.text(.5,.03,'CAD only: 121 sampled poses pass. Resin strength / physical servo fit unverified; whole-hand screening still fails.',ha='center',fontsize=13,color='#a8322b')
 fig.savefig(HERE/'comparison.png',dpi=100);(F/'previews').mkdir(exist_ok=True);fig.savefig(F/'previews/comparison.png',dpi=100);plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(16,12),facecolor='#fafcff');fig.subplots_adjust(top=.87,bottom=.12)
 fig.suptitle('Original blades preserved exactly',fontsize=28,weight='bold')
 outline(axes[0],0,True);axes[0].set_title('Closed: original rounded tips meet',fontsize=19)
 outline(axes[1],30,False);axes[1].set_title('Open: 30° jaw stroke',fontsize=19)
 fig.text(.5,.06,'No added tips. No distal trimming. 30 mm root spacing and 10.33 mm continuous rear clearance retained.',ha='center',fontsize=17)
 fig.savefig(HERE/'closure.png',dpi=100);plt.close(fig)
def gears():
 fig,axes=plt.subplots(1,2,figsize=(16,12),facecolor='#fafcff');fig.subplots_adjust(top=.83,bottom=.15)
 fig.suptitle('Actual overhead gear solids',fontsize=28,weight='bold')
 fig.text(.5,.91,'Housing and servo hidden · same scale · jaw 15° · original blades below Y=3.8 hidden',ha='center',fontsize=17)
 for ax,f in zip(axes,[OLD,F]):
  for k in ['left','right','pinion']:
   q=projection(clipped(mesh(f,k),3.8,11.5))
   for poly in [q] if q.geom_type=='Polygon' else q.geoms:
    x,z=poly.exterior.xy;ax.fill(x,z,color=('#7461aa' if k=='pinion' else '#f5b83c'),ec='#43364e',lw=.6)
    for h in poly.interiors:x,z=h.xy;ax.fill(x,z,color='#f2f6fa')
  ax.set_aspect('equal');ax.set_facecolor('#f2f6fa');ax.set_xlim(-25,25);ax.set_ylim(-58,12);ax.set_xlabel('X (mm)');ax.set_ylabel('Z (mm)');ax.grid(alpha=.15)
 axes[0].set_title('Before: 44.0 × 61.0 mm',fontsize=21);axes[1].set_title('After: 36.6 × 28.9 mm',fontsize=21)
 fig.text(.5,.082,'Upper: Ø32 → Ø16 mm · pinion: Ø44 → Ø24 mm · lower sectors: Ø32 mm retained',ha='center',fontsize=17)
 fig.text(.5,.045,'Projected gear area: 1604 → 492 mm² (−69%) · no additional gears or printed pieces',ha='center',fontsize=17)
 fig.savefig(HERE/'gears.png',dpi=100);plt.close(fig)
if __name__=='__main__':main();gears()
