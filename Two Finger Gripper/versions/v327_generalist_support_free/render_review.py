from pathlib import Path
import json,sys
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
HERE=Path(__file__).resolve().parent

def draw(ax,mesh,axes,color):
 # Project actual STL triangles; no substituted proxy shapes.
 polys=mesh.vertices[mesh.faces][:,:,axes]
 ax.add_collection(PolyCollection(polys,facecolor=color,edgecolor='none',alpha=.95))
 ax.autoscale();ax.set_aspect('equal');ax.set_facecolor('#f5f4ef');ax.tick_params(labelsize=8)

def main():
 old=HERE.with_name('v326_generalist_small_drive');fig,aa=plt.subplots(2,2,figsize=(16,12));fig.patch.set_facecolor('#f5f4ef')
 for row,folder in enumerate([old,HERE]):
  data=json.loads((folder/'viewer_parts.json').read_text())
  for col,axes in enumerate([[0,2],[2,1]]):
   ax=aa[row,col]
   for p in reversed(data['parts']):
    if 'screws' in p['path'] or 'nuts' in p['path']:continue
    draw(ax,trimesh.load_mesh(folder/p['path']),axes,p['color'])
   if col==1:ax.axhspan(-3,3,facecolor='#ed7542',alpha=.18);ax.text(46,-2,'Finger band',fontsize=10,color='#a04420');ax.invert_xaxis()
   ax.set_title(('Base 25 + Gripper 29' if row==0 else 'Base 26 + Gripper 30')+(' • top' if col==0 else ' • side'),fontsize=17)
   ax.set_xlabel('X / Z (mm)' if col==0 else 'Along finger Z (mm)');ax.set_ylabel('Z / Y (mm)' if col==0 else 'Above finger Y (mm)')
 for col in range(2):
  xb=[aa[r,col].get_xlim() for r in range(2)];yb=[aa[r,col].get_ylim() for r in range(2)]
  xx=(min(min(x) for x in xb),max(max(x) for x in xb));yy=(min(min(y) for y in yb),max(max(y) for y in yb))
  for r in range(2):aa[r,col].set_xlim(xx[::-1] if col==1 else xx);aa[r,col].set_ylim(yy)
 fig.suptitle('Same gear sizes and original tips • solid blades + flat keyed gear layers',fontsize=23)
 fig.text(.5,.015,'Slicer verified with supports OFF • physical printing, fit, strength and hand comfort untested',ha='center',fontsize=15,color='#953e25');fig.tight_layout(rect=[0,.035,1,.95]);fig.savefig(HERE/'previews/comparison.png',dpi=100);plt.close(fig)
 plate=trimesh.load_mesh(HERE/'exports/print_plate.stl');fig,ax=plt.subplots(figsize=(16,12));fig.patch.set_facecolor('#f5f4ef')
 for i,m in enumerate(plate.split()):draw(ax,m,[0,1],['#d69a27','#28776e','#52677c'][i%3])
 ax.set_title('Twelve pieces • arranged print plate • supplied flat faces down',fontsize=23);ax.axis('off');fig.text(.5,.06,'2 solid blades  +  3 flat sectors  +  pinion  +  capture ring  +  base  +  4 motor spacers',ha='center',fontsize=18);fig.savefig(HERE/'previews/print_plate.png',dpi=100);plt.close(fig)
if __name__=='__main__':main()
