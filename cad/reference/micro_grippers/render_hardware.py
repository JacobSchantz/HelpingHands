"""Render original source meshes separated for inspection, not manufacturing CAD.
Run with cad/blender/.venv/bin/python ... /tmp/ef49247b-sts.stl.
"""
from pathlib import Path
import sys
import numpy as np,trimesh,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
ROOT=Path(__file__).resolve().parents[3];F=ROOT/'Two Finger Gripper/versions/v326_generalist_small_drive'
OUT=ROOT/'cad/mobile_gallery/micro_grippers/hardware.png'
def project(p):return np.stack([p[...,0]+.55*p[...,2],p[...,1]+.4*p[...,2]],axis=-1)
def draw(ax,items):
 triangles=[];depth=[];colors=[];points={}
 light=np.array([.3,.4,1.]);light/=np.linalg.norm(light)
 for label,m,offset,color in items:
  m=m.copy();m.vertices+=offset
  points[label]=project(m.centroid)
  triangles.extend(project(m.triangles));depth.extend(m.triangles[:,:,2].mean(1))
  rgb=np.array(matplotlib.colors.to_rgb(color));shade=.42+.58*np.maximum(0,m.face_normals@light)
  colors.extend(np.clip(shade[:,None]*rgb,0,1))
 order=np.argsort(depth);ax.add_collection(PolyCollection(np.array(triangles)[order],facecolors=np.array(colors)[order],edgecolors='none'))
 a=np.concatenate(triangles);lo=a.min(axis=0)-7;hi=a.max(axis=0)+7
 ax.set_xlim(lo[0]-15,hi[0]+10);ax.set_ylim(lo[1]-4,hi[1]+4);ax.set_aspect('equal');ax.axis('off')
 return points

def callout(ax,point,text,pos):
 ax.annotate(text,xy=point,xytext=pos,textcoords='axes fraction',fontsize=12,color='#132a3a',bbox=dict(boxstyle='round,pad=.35',fc='#f2f6fa',ec='#a3bdce'),arrowprops=dict(arrowstyle='-',color='#466a80',lw=1.5))

def hls_mesh(name):
 path=F/('exports/parts' if name in ['motor','stock_plate','pinion'] else 'exports/reference')/(name+'.stl')
 m=trimesh.load_mesh(path);m.vertices=m.vertices[:,[0,2,1]];return m
fig,axes=plt.subplots(1,2,figsize=(16,12),facecolor='#fafcff');fig.subplots_adjust(top=.84,bottom=.20,left=.025,right=.975,wspace=.03)
fig.suptitle('Two motors. Separate mounting interfaces.',fontsize=29,weight='bold',y=.975)
fig.text(.5,.92,'Source mesh closeups, separated for inspection. Exploded distances are illustrative.',ha='center',fontsize=17)
items=[]
for name,height,color in [('motor',0,'#778b9c'),('stock_plate',32,'#c3d4df'),('pinion',68,'#ac8bd9'),('plate_screws',100,'#e5ac50'),('center_screw',132,'#64bca6'),('case_screws',7,'#de8b80')]:
 items.append((name,hls_mesh(name),[0,0,height],color))
p=draw(axes[0],items);axes[0].set_title('Current HLS3606M-C001 / Base 25',fontsize=19,weight='bold')
callout(axes[0],p['center_screw'],'1 × M2.3×5\nAxial spline retention',(.00,.89))
callout(axes[0],p['plate_screws'],'2 × M2×4 used\n8 holes on Ø12',(.00,.66))
callout(axes[0],p['pinion'],'Printed pinion\nIntegral capture web',(.55,.78))
callout(axes[0],p['stock_plate'],'Bought Ø18 plate\n25T / Ø4.95 spline',(.55,.46))
callout(axes[0],p['case_screws'],'4 × M2×6 case screws\nSeparate stationary ears',(.04,.11))
m=trimesh.load_mesh(sys.argv[1]);top=m.slice_plane([0,0,18.7001],[0,0,1]);horn=m.slice_plane([0,0,16.1999],[0,0,1]).slice_plane([0,0,18.7001],[0,0,-1]);body=m.slice_plane([0,0,16.1999],[0,0,-1])
items=[('case',body,[0,0,0],'#778b9c'),('horn',horn,[0,0,20],'#c3d4df'),('center',top,[0,0,40],'#64bca6')]
p=draw(axes[1],items);axes[1].set_title('SO-101 uses STS3215 / different horn',fontsize=19,weight='bold')
callout(axes[1],p['center'],'1 × M3×6 center screw\nGuide specification',(.03,.90))
callout(axes[1],p['horn'],'Ø20 front horn\n4 × M3 on Ø14\n2.5 mm disk',(.45,.78))
callout(axes[1],p['case'],'M2 case mounting\n4 screws in gripper guide\nNot the horn circle',(.00,.16))
fig.text(.5,.155,'HLS: 2 plate + 1 center + 4 case = 7 motor screws. Add 2 pivot bolts = 9 screws/bolts total.',ha='center',fontsize=17,weight='bold')
fig.text(.5,.112,'Delivered before / after: 9 / 9. No fasteners removed; Base 25 + Gripper 29 stays unchanged.',ha='center',fontsize=17)
fig.text(.5,.067,'HLS geometry: pinned Aero STEP + existing print exports. STS: pinned SO-ARM100 servo STEP, visually sectioned.',ha='center',fontsize=13)
fig.text(.5,.035,'Smooth STEP holes do not certify threads or real engagement. Physical horn revision, driver fit and screw lengths still need checking.',ha='center',fontsize=13,color='#9d392b')
fig.savefig(OUT,dpi=100);plt.close(fig)
