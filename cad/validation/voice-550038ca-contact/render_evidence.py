"""Actual STL tip closeups and exploded servo connection; sourced center-screw stack."""
from pathlib import Path
import json,sys,numpy as np,trimesh,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));HERE=Path(__file__).resolve().parent
from Scripts.check_finger_plane_constraints import projection,clipped
VERSIONS=ROOT/'Two Finger Gripper/versions';BEFORE=VERSIONS/'v323_generalist_centered_drive';NEW=VERSIONS/'v324_generalist_contact_close'
def tips(ax,folder,pivot):
 for k,sign in [('left',-1),('right',1)]:
  m=trimesh.load_mesh(folder/f'exports/parts/{k}.stl');a=math.radians(-15*sign);R=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]]);c=np.array([sign*pivot,0,0]);m.vertices=(m.vertices-c)@R.T+c
  shape=projection(clipped(m,-2.999,2.999))
  for g in ([shape] if shape.geom_type=='Polygon' else shape.geoms):
   x,z=g.exterior.xy;ax.fill(x,z,color='#edb737',ec='#916012',lw=.6)
   for ring in g.interiors:x,z=ring.xy;ax.fill(x,z,color='#edf2f7')
 ax.set_xlim(-8,8);ax.set_ylim(58,64.5);ax.axvline(0,c='#0d8794',ls='--',lw=1);ax.set_aspect('equal');ax.set_facecolor('#edf2f7');ax.set_xlabel('Across tips X (mm)');ax.set_ylabel('Along fingers Z (mm)')
def exploded(ax):
 u=np.array([.85,0,-.53]);v=np.array([.2,.92,.32]);n=np.cross(u,v);tri=[];dep=[];col=[]
 roles={'motor':([0,65,0],'#7c8fa5'),'pinion':([0,-10,0],'#333a44'),'stock_plate':([0,25,0],'#aab8c8'),'plate_screws':([0,-22,0],'#498ca5'),'center_screw':([0,-40,0],'#157e63')}
 for k,(offset,color) in roles.items():
  path=NEW/f'exports/{"reference" if k.endswith("screws") or k=="center_screw" else "parts"}/{k}.stl';t=trimesh.load_mesh(path).triangles+offset
  tri.extend(np.stack([t@u,t@v],axis=2));dep.extend((t@n).mean(1));col.extend([color]*len(t))
 order=np.argsort(dep);ax.add_collection(PolyCollection(np.array(tri)[order],facecolors=np.array(col)[order],edgecolors='none'))
 ax.set_xlim(-30,40);ax.set_ylim(-45,125);ax.set_aspect('equal');ax.set_facecolor('#edf2f7');ax.set_xticks([]);ax.set_yticks([])
 ax.text(-27,114,'Same actual HLS3606M',fontsize=11);ax.text(-27,52,'Metal plate: 8 holes',fontsize=11);ax.text(-27,27,'Pinion: 1 mm capture web',fontsize=11);ax.text(-27,0,'2 opposed M2×4 screws',fontsize=11);ax.text(-27,-37,'Original M2.3×5 center screw',fontsize=10)
def stack(ax):
 # Axial positions taken from actual exported head seating faces + source STEP bore.
 h=json.loads((NEW/'hardware_checks.json').read_text());c=h['center_stack'];seat=c['head_seat_y_mm'];mouth=c['thread_mouth_y_mm'];floor=c['bore_floor_y_mm']
 ax.axhspan(mouth,floor,color='#a5b5c7',alpha=.4);ax.axhline(floor,c='#394c61',lw=2);ax.axhspan(seat,seat+1,color='#333a44',alpha=.6)
 for x,y,color,label in [(-1.2,seat+1,'#bb3e38','Old: 0.8 mm too deep'),(1.2,seat,'#16805c','New: 0.2 mm clear')]:
  ax.plot([x,x],[y,y+5],c=color,lw=7);ax.plot([x-.35,x+.35],[y,y],c=color,lw=10);ax.text(x,9.7,label,ha='center',c=color,fontsize=11)
 ax.text(2.6,16.4,'3 mm modeled bore',fontsize=11,ha='right');ax.text(2.6,13.2,'1 mm integral web',fontsize=11,ha='right')
 ax.set_ylim(19.3,9.2);ax.set_xlim(-2.7,2.7);ax.set_xticks([]);ax.set_ylabel('Above finger plane Y (mm)');ax.set_facecolor('#edf2f7')
 ax.text(0,18.9,'2.8 mm nominal engagement; threads unmodeled',ha='center',fontsize=10)
def main():
 fig,ax=plt.subplots(2,2,figsize=(16,12),facecolor='#f8fafc',gridspec_kw={'height_ratios':[.85,1.4]});fig.subplots_adjust(top=.86,bottom=.13,hspace=.3,wspace=.25)
 fig.suptitle('Tips meet. The pinion captures the center screw.',fontsize=26,weight='bold',y=.97)
 fig.text(.5,.919,'Base 23 + Gripper 27 · 20 mm pivots · 4 printed / 19 total parts',ha='center',fontsize=18)
 tips(ax[0,0],BEFORE,9.8);ax[0,0].set_title('Before: distal tips remain apart',fontsize=16)
 tips(ax[0,1],NEW,10);ax[0,1].set_title('After: solid 1.5 mm contact noses meet at 0°',fontsize=16)
 exploded(ax[1,0]);ax[1,0].set_title('Exploded servo connection; no added adapter',fontsize=16)
 stack(ax[1,1]);ax[1,1].set_title('Nominal center-screw depth, checked against STEP',fontsize=16)
 fig.text(.5,.077,'Zero CAD tip gap · 1.229 mm rear gap · opening 0.1° releases contact · no commanded over-close',ha='center',fontsize=16)
 fig.text(.5,.035,'Actual plate revision / threads / driver fit unverified. Whole-hand acceptance still FAILS.',ha='center',fontsize=15,color='#a12b24')
 fig.savefig(HERE/'comparison.png',dpi=100);(NEW/'previews').mkdir(exist_ok=True);fig.savefig(NEW/'previews/comparison.png',dpi=100);plt.close(fig)
def pattern():
 h=json.loads((NEW/'hardware_checks.json').read_text());fig,axes=plt.subplots(1,2,figsize=(14,7),facecolor='#f8fafc')
 ax=axes[0];ax.add_patch(plt.Circle((0,0),9,color='#aebdce'));ax.add_patch(plt.Circle((0,0),1.175,color='white'))
 for q in h['plate']['holes']:
  used=abs(abs(q['x'])-4.245334)<.01 and q['x']*q['z']>0
  ax.add_patch(plt.Circle((q['x'],q['z']),1,color='#187e60' if used else 'white',ec='#3e5769'))
 ax.set_xlim(-11,11);ax.set_ylim(-11,11);ax.set_aspect('equal');ax.set_title('Aero metal plate: 8 modeled holes\n2 opposed M2×4 screws used',fontsize=18);ax.set_xlabel('Native X (mm)');ax.set_ylabel('Native Z (mm)');ax.text(0,-10.6,'Ø18 plate · Ø12.007619 PCD · green = used',ha='center',fontsize=11)
 ax=axes[1];m=trimesh.load_mesh(NEW/'reference/servo.stl');outline=projection(m)
 for poly in ([outline] if outline.geom_type=='Polygon' else outline.geoms):
  x,z=poly.exterior.xy;ax.fill(x,z,color='#b9c5d3')
 for x,z in h['case']['cad_centers']:ax.add_patch(plt.Circle((x,z),1.25,color='white',ec='#187e60',lw=2))
 ax.set_aspect('equal');ax.set_xlim(-13,24);ax.set_ylim(-11,11);ax.set_xlabel('Along motor U (mm)');ax.set_ylabel('Across motor (mm)');ax.set_title('HLS3606M case: 4 ear holes\n4 separate M2×6 case screws retained',fontsize=18)
 fig.suptitle('Two different interfaces on the selected HLS3606M-C001',fontsize=22,weight='bold');fig.text(.5,.04,'Measured from pinned STEP. Smooth CAD holes do not prove thread pitch or Jake’s plate revision.',ha='center',fontsize=13,color='#9d3328');fig.subplots_adjust(top=.80,bottom=.15,wspace=.25);fig.savefig(HERE/'hardware-pattern.png',dpi=110);plt.close(fig)
if __name__=='__main__':main();pattern()
