"""Same-scale triangle projections; +Y vertical in side views, above the hand."""
from pathlib import Path
import json,numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
HERE=Path(__file__).resolve().parent
SOURCES=[('v319_generalist_hls3606m','Base 18 / Gripper 24'),('v320_generalist_overhead_drive','Base 19 / Gripper 22'),(HERE.name,'Base 20 / Gripper 25')]
def draw(ax,folder,side):
 manifest=json.loads((folder/'viewer_parts.json').read_text());tri=[];col=[];depth=[]
 for part in manifest['parts']:
  if any(x in part['name'] for x in ['Arm','Wrist hub','Tool plate']):continue
  t=trimesh.load_mesh(folder/part['path']).triangles
  tri.extend(t[:,:,[2,1] if side else [0,2]])
  depth.extend(t[:,:,0 if side else 1].mean(1));col.extend([part['color']]*len(t))
 order=np.argsort(depth);ax.add_collection(PolyCollection(np.asarray(tri)[order],facecolors=np.asarray(col)[order],edgecolors='none'))
 ax.set_aspect('equal');ax.set_facecolor('#eef2f6')
 if side:
  ax.set_xlim(-110,145);ax.set_ylim(-58,137);ax.set_xlabel('Along fingers (Z, mm)');ax.set_ylabel('Above hand (+Y, mm)')
 else:
  ax.set_xlim(-83,83);ax.set_ylim(-111,145);ax.set_xlabel('Across fingers (X, mm)');ax.set_ylabel('Along fingers (Z, mm)')
 ax.grid(alpha=.15)
def main():
 fig,aa=plt.subplots(2,3,figsize=(18,12),facecolor='#f5f7fa');fig.subplots_adjust(top=.86,bottom=.11,hspace=.3,wspace=.25)
 fig.suptitle('Direct tweezers. Drive just above the fingers.',fontsize=27,weight='bold',y=.98)
 fig.text(.5,.929,'Base 20: no handles • 7 mm roots / 3 mm pivots • 0.8 mm gear gap',ha='center',fontsize=20)
 for i,(name,title) in enumerate(SOURCES):
  folder=HERE.parent/name
  draw(aa[0,i],folder,False);aa[0,i].set_title(title+' · top',fontsize=16)
  draw(aa[1,i],folder,True);aa[1,i].set_title(title+' · side',fontsize=16)
  half=6 if i==1 else 3;aa[1,i].axhspan(-half,half,color='#f0b73e',alpha=.2,zorder=0)
 aa[1,2].annotate('0.8 mm gap',xy=(-28,3.8),xytext=(40,65),arrowprops=dict(arrowstyle='->'),fontsize=13)
 fig.text(.5,.05,'Gold = fingers / working band. Gray = purchased motor. Dark = printed drive and support.\nSame mm scale within each row; Base 19 uses larger fingers. CAD only: hand fit and strength unverified.',ha='center',fontsize=15)
 (HERE/'previews').mkdir(exist_ok=True);fig.savefig(HERE/'previews/comparison.png',dpi=100,facecolor=fig.get_facecolor());plt.close(fig)
 # Detail for human review; all geometry from new STLs, no invented hand pose.
 fig,aa=plt.subplots(1,2,figsize=(16,10),facecolor='#f5f7fa')
 draw(aa[0],HERE,False);aa[0].set_xlim(-43,43);aa[0].set_ylim(-77,76)
 draw(aa[1],HERE,True);aa[1].set_xlim(-77,76);aa[1].set_ylim(-12,52);aa[1].axhspan(-3,3,color='#f0b73e',alpha=.2)
 fig.suptitle('Base 20 + Gripper 25 · outside finger contact, clear grasp gap',fontsize=22)
 fig.tight_layout();fig.savefig(HERE/'previews/detail.png',dpi=100,facecolor=fig.get_facecolor());plt.close(fig)
if __name__=='__main__':main()
