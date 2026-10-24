"""Render actual STL bodies, with all purchased hardware present in the exploded view."""
from pathlib import Path
import json
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import check_geometry as c,params
HERE=Path(__file__).resolve().parent
PRE=HERE/'previews';PRE.mkdir(exist_ok=True)
def draw(ax,m,axes,color):
 ax.add_collection(PolyCollection(m.vertices[m.faces][:,:,axes],facecolor=color,edgecolor='none'));ax.autoscale();ax.set_aspect('equal');ax.set_facecolor('#f5f4ef')
def main():
 old=HERE.with_name('v327_generalist_support_free');fig,aa=plt.subplots(2,2,figsize=(16,12));fig.patch.set_facecolor('#f5f4ef')
 for row,folder in enumerate([old,HERE]):
  data=json.loads((folder/'viewer_parts.json').read_text())
  for col,axes in enumerate([[0,2],[2,1]]):
   ax=aa[row,col]
   for p in reversed(data['parts']):draw(ax,trimesh.load_mesh(folder/p['path']),axes,p['color'])
   if col==1:ax.axhspan(-3,3,color='#ed7542',alpha=.2);ax.invert_xaxis();ax.set_ylabel('Above finger Y (mm)')
   ax.set_title(('Base 26 + Gripper 30: 12 prints / 33 total' if row==0 else 'Base 27 + Gripper 31: 5 prints / 23 total')+(' | top' if col==0 else ' | side'),fontsize=16)
 for col in range(2):
  xs=[a.get_xlim() for a in aa[:,col]];ys=[a.get_ylim() for a in aa[:,col]];xb=[min(min(x) for x in xs),max(max(x) for x in xs)];yb=[min(min(y) for y in ys),max(max(y) for y in ys)]
  for ax in aa[:,col]:ax.set_xlim(xb[::-1] if col==1 else xb);ax.set_ylim(yb)
 fig.suptitle('Five actual prints; larger overhead stack buys integral support-free parts',fontsize=23)
 fig.text(.5,.015,'Orange band: unchanged 6 mm finger slab | 13 mm to lower gears (was 0.8) | Physical fit / strength untested',ha='center',fontsize=15)
 fig.tight_layout(rect=[0,.04,1,.95]);fig.savefig(PRE/'comparison.png',dpi=100);plt.close(fig)
 data=json.loads((HERE/'viewer_parts.json').read_text());fig=plt.figure(figsize=(16,12));ax=fig.add_subplot(111,projection='3d');bounds=[]
 for p in data['parts']:
  m=trimesh.load_mesh(HERE/p['path']);m.apply_translation(p['explode']);q=m.vertices[:,[0,2,1]];bounds.append(q)
  ax.add_collection3d(Poly3DCollection(q[m.faces],facecolor=p['color'],edgecolor='none',alpha=1,zsort='average'))
 q=np.vstack(bounds);ax.set_xlim(q[:,0].min()-5,q[:,0].max()+5);ax.set_ylim(q[:,1].min()-5,q[:,1].max()+5);ax.set_zlim(q[:,2].min()-5,q[:,2].max()+5);ax.set_box_aspect(np.ptp(q,axis=0));ax.view_init(22,-65);ax.set_axis_off()
 fig.suptitle('All 23 physical pieces | no hidden printed spacers or retainers',fontsize=24)
 fig.text(.04,.12,'5 PRINTED\n2 integral jaws + drive pinion\nTop motor frame + lower plate',fontsize=18,color='#28776e')
 fig.text(.57,.10,'17 BOUGHT + 1 FABRICATED\nServo + metal spline plate\n4 ear screws + 2 plate screws + center screw\n3 metal washers* + 2 cut tie rods + 4 nuts\n*Center capture washer requires fabrication',fontsize=17,color='#52677c')
 fig.savefig(PRE/'exploded.png',dpi=100);plt.close(fig)
 # Show every bought/fabricated solid separately; never overlay washers or screws.
 groups=[p for p in data['parts'] if p['name'].split(' — ')[0] not in ['Left finger integral jaw','Right finger integral jaw','Pinion','Top motor frame','Bottom retaining plate']]
 fig,aa=plt.subplots(3,3,figsize=(16,12))
 for ax,p in zip(aa.flat,groups):
  m=trimesh.load_mesh(HERE/p['path']);pieces=m.split();offset=0
  for body in pieces:
   body=body.copy();axes=[2,1] if 'tie rods' in p['name'] else [0,2]
   body.apply_translation([offset if axes[0]==0 else 0,0,offset if axes[0]==2 else 0]);draw(ax,body,axes,p['color']);offset+=max(body.extents[axes[0]],4)+4
  ax.set_title(p['name'].split(' — ')[0],fontsize=14);ax.axis('off')
 for ax in aa.flat[len(groups):]:ax.axis('off')
 fig.suptitle('All 18 nonprinted pieces, individually separated | panels use separate scales',fontsize=22)
 fig.text(.5,.03,'7 screws + 2 cut rods + 4 nuts + 3 washers + servo + metal spline plate | Center washer: fabricated steel',ha='center',fontsize=16)
 fig.tight_layout(rect=[0,.06,1,.94]);fig.savefig(PRE/'hardware_inventory.png',dpi=100);plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(16,9));v=params.values()
 for ax,a in zip(axes,[0,30]):
  for k in ['left','right']:
   m=trimesh.load_mesh(HERE/f'exports/parts/{k}.stl');pivot,r=c.motion(k,v);m.vertices=c.rotated(m.vertices,pivot,(a-15)*r);draw(ax,m,[0,2],'#d69a27')
  ax.set_title(f'Jaw {a} degrees',fontsize=22);ax.axis('off')
 fig.suptitle('Original rounded tips meet; unchanged 0–30 degree opening',fontsize=24);fig.tight_layout();fig.savefig(PRE/'closure.png',dpi=100);plt.close(fig)
 plate=trimesh.load_mesh(HERE/'exports/print_plate.stl');fig,ax=plt.subplots(figsize=(16,12))
 for i,m in enumerate(plate.split()):draw(ax,m,[0,1],['#d69a27','#28776e','#52677c'][i%3])
 ax.axis('off');ax.set_title('Exactly five bodies on the print plate | supplied orientations',fontsize=24)
 fig.text(.5,.04,'Supports OFF | 0.4 mm nozzle | 0.1 mm layers | Select actual machine/material and reslice',ha='center',fontsize=18)
 fig.savefig(PRE/'print_plate.png',dpi=100);plt.close(fig)
if __name__=='__main__':main()
