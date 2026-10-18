#!/usr/bin/env python3
"""Trace the lower finger of the left-hand device in the two-hands photo by colour, not by
eye: yellow pixels -> one finger silhouette -> simplified outline, and every dark blob inside
it -> a hole (centre + size). Writes trace_px.scad, which gripper.scad includes.

Generation 9 (Sonnet 5.5): smooth resampled contour instead of a coarse polygon, a sharp pointed
tip, round holes only, a robust patch splice. Things the photo cannot give are patched by hand, and marked below:
  * the upper finger's blade touches this one near the tips, so a seam line separates them;
  * the device body hides the top-left corner of the root, so that edge is a straight line
    and the hidden top-left root hole is added on the hex grid of its neighbours.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
PHOTO=HERE.parents[2]/'cad/reference/generalist_gripper_gen6_two_hands.png'
SEAM=[(690,500),(705,512),(770,545),(835,575),(890,595)]   # dark gap between the two blades
ROOT_EDGE=((354,366),(405,339))   # hidden by the body: replace the trace between these by a line
HIDDEN_HOLES=[(388,364.5,13.5,13.5,0)]   # top-left root hole, on the hex grid (x, y, major, minor px, angle deg)
DOT_D=17                                # the blade dot's dark ring blurs to ~21 px; the dot itself is ~17
RESIZED={(626,493):(10,10,0),          # half-hidden in blur: the colour mask reads it at 6 px, the eye at 10
         (391,396):(10,10,0)}           # half under the carrier tongue: round, not an oval (r3 review)
MISSED_HOLES=[(657,511,8,8,0)]          # faint in the colour mask, visible by eye (round-2 review)
# Where the photo is blurred, a hand-drawn run replaces the contour between its first and last point
# (both snap to the nearest contour points; the shorter arc between them is replaced). A run is a list of
# segments; each is a smooth spline through its points, and the joins between segments are corners.
# r2 review (checked against top/robot/target/closed): the distal blade is about shank-width with a nearly
# straight jaw edge and a long taper to a needle point under 1 mm. The two_hands photo shows a wider blade
# (the finger is nearer the camera there), so a compromise: ~1.2x shank at the dot, ~1x further out.
JAW=[(733.7,536.3),(754,543),(775,555.6),(800,570.6),(822,583.8),(840,594.6),(852,601.8),(861.5,607.5)]   # inner (gripping) edge: straight from (754,543) to the point, so the closed jaws lie flush (r3)
OUTER=[(861.5,607.5),(848,608.5),(830,609),(810,608.5),(790,606),(770,601.5),(748,594),(728,587),(706.6,581.7)]   # convex belly from the dot to ~60% of the blade, then the taper (r3)
PATCHES=[
  [JAW,OUTER],
  # inner-edge shoulders mid-shank: swell, then a ramped step (r2 review: no blocky jog / dark wall)
  [[(619.9,454.9),(633,458.5),(639,467),(642.3,478),(646,488.5),(655,496),(670,499.5),(683,498),(689,499.5),(694,505),(698,511.5),(702,518),(708,524),(717,529.5),(727,533),(733.7,536.3)]],
  # blade root: smooth S-curve from the shank's outer edge into the dot swell, no jog
  [[(629.6,517.2),(645,523),(657,531.5),(664.5,543),(671,554),(681,564),(693,572.5),(706.6,581.7)]],
  # base hook: a rounded J-claw with a round bowl and a fat rounded toe
  [[(392.3,408.3),(376,399.5),(363,393.2),(355,391.2),(349.5,394),(347.2,400.5),(348.4,407.5),(351,413)],
   [(351,413),(350,418),(345,420.2),(338.5,418),(331.5,412),(326.5,404.5),(324.4,396.5),(325.5,390.5),(327.1,388.7)]],
]
SMOOTH_SIGMA=4.0                        # px, periodic gaussian along the contour: smooth shoulders (r2 review)
SLOT_ROW=dict(first=(749.5,554.0),step=(13.1,6.5),count=6)  # three are visible; the upper finger shows six


def rdp(pts,eps):
    a,b=pts[0],pts[-1];ab=b-a;L=np.hypot(*ab)
    if len(pts)<3 or L==0:return np.vstack([a,b])
    d=np.abs(ab[0]*(pts[:,1]-a[1])-ab[1]*(pts[:,0]-a[0]))/L;i=d.argmax()
    return np.vstack([rdp(pts[:i+1],eps)[:-1],rdp(pts[i:],eps)]) if d[i]>eps else np.vstack([a,b])


def resample(P,step):
    P=np.vstack([P,P[:1]]);d=np.r_[0,np.cumsum(np.hypot(*np.diff(P,axis=0).T))]
    t=np.arange(0,d[-1],step);return np.c_[np.interp(t,d,P[:,0]),np.interp(t,d,P[:,1])]


def smooth(P,sigma):
    return np.c_[nd.gaussian_filter1d(P[:,0],sigma,mode='wrap'),nd.gaussian_filter1d(P[:,1],sigma,mode='wrap')]


def splice(Q,run,a,b):
    """Replace the shorter arc of closed contour Q between indices a and b by the points of run."""
    n=len(Q)
    if (b-a)%n>(a-b)%n:a,b=b,a;run=run[::-1]      # make the arc a->b the short one, running forward
    # orient run so its start is nearer Q[a]
    if np.hypot(*(run[0]-Q[a]))>np.hypot(*(run[-1]-Q[a])):run=run[::-1]
    idx=[(a+i)%n for i in range((b-a)%n+1)]
    keep=[i for i in range(n) if i not in set(idx)]
    k0=keep.index((a-1)%n) if (a-1)%n in keep else len(keep)-1
    rot=np.vstack([Q[keep[k0+1:]] if k0+1<len(keep) else np.empty((0,2)),Q[keep[:k0+1]]]) # contour after b ... before a
    return np.vstack([run,rot])


def rdp_closed(Q,eps):
    j=len(Q)//2
    return np.vstack([rdp(Q[:j+1],eps)[:-1],rdp(np.vstack([Q[j:],Q[:1]]),eps)[:-1]])


def curve(pts,step=2.0):
    from scipy.interpolate import splprep,splev
    p=np.array(pts,float)
    if len(p)<3:return p
    tck,_=splprep([p[:,0],p[:,1]],s=0,k=min(3,len(p)-1))
    L=np.hypot(*np.diff(p,axis=0).T).sum();u=np.linspace(0,1,max(4,int(L/step)))
    x,y=splev(u,tck);return np.c_[x,y]


def edge_dist(Q,p):
    b=np.roll(Q,-1,0);ab=b-Q;t=np.clip(((p-Q)*ab).sum(1)/(ab**2).sum(1),0,1);return np.hypot(*(Q+ab*t[:,None]-p).T).min()


def regularise(holes,Q):
    """Head honeycomb snapped toward a hex lattice and as large as the walls allow; shank holes in one regular
    taper that is big enough to read as a nearly continuous chain (r3 review)."""
    out=[];dot=[h for h in holes if np.hypot(h[0]-724.2,h[1]-561.9)<5];holes=[h for h in holes if h not in dot]
    head=[h for h in holes if h[0]<460];bar=[h for h in holes if h[0]>=460]
    A=np.array([23.2,-0.55]);B=np.array([11.5,19.2]);M=np.c_[A,B];o=np.array(head[0][:2])
    ij=[np.round(np.linalg.solve(M,np.array(h[:2])-o)) for h in head]
    lat=[o+M@c for c in ij];off=np.mean([np.array(h[:2])-l for h,l in zip(head,lat)],axis=0)
    snapped=[]
    for h,l in zip(head,lat):
        w=0.0 if h[2]<12 else 0.6     # the half-hidden hole under the carrier tongue stays where it was traced
        p=np.array(h[:2])+w*((l+off)-np.array(h[:2]));snapped.append((p[0],p[1]))
    for k,(x,y) in enumerate(snapped):
        nn=min(np.hypot(x-u,y-v) for j,(u,v) in enumerate(snapped) if j!=k)
        d=min(18.0,nn-3.0,2*(edge_dist(Q,np.array([x,y]))-4.0))
        if head[k][2]<12:d=10.0
        out.append((x,y,d,d,0.0))
    for h in bar:   # 15 px at the head down to 9.5 px at the blade
        d=15.0+(9.5-15.0)*(h[0]-467.6)/(700.6-467.6);out.append((h[0],h[1],d,d,0.0))
    return out+dot


def trace():
    im=Image.open(PHOTO).convert('RGB');hsv=np.array(im.convert('HSV')).astype(int)
    yel=(hsv[...,0]>=18)&(hsv[...,0]<=40)&(hsv[...,1]>=120)&(hsv[...,2]>=150)
    cut=Image.new('L',im.size,0);ImageDraw.Draw(cut).line(SEAM,fill=255,width=4)
    lab,_=nd.label(yel&(np.array(cut)==0))
    ys,xs=np.nonzero(lab[455:475,540:560])           # a yellow pixel on the bar
    finger=lab==lab[455+ys[0],540+xs[0]]
    filled=nd.binary_fill_holes(nd.binary_closing(finger,iterations=2))
    P=max(plt.contour(nd.gaussian_filter(filled.astype(float),1.6),[0.5]).allsegs[0],key=len)[:-1]
    P=resample(P,1.0)
    Q=smooth(P,SMOOTH_SIGMA)
    # hand patch: straight root edge where the body hides it
    a,b=(np.argmin(np.hypot(*(Q-np.array(p)).T)) for p in ROOT_EDGE)
    Q=splice(Q,np.array(ROOT_EDGE,float),a,b)
    holes=[];hl,n=nd.label(nd.binary_opening(filled&~finger,iterations=1))
    for i in range(1,n+1):
        yy,xx=np.nonzero(hl==i)
        if len(yy)<20:continue           # slots handled as a row; specks are blur
        w,v=np.linalg.eigh(np.cov(np.vstack([xx,yy])))   # a uniform disc of diameter d has 4*sqrt(var) = d
        holes.append((xx.mean(),yy.mean(),4*np.sqrt(w[1]),4*np.sqrt(w[0]),np.degrees(np.arctan2(v[1,1],v[0,1]))))
    for i,h in enumerate(holes):
        for (x,y),r in RESIZED.items():
            if np.hypot(h[0]-x,h[1]-y)<4:holes[i]=h[:2]+r
    holes+=HIDDEN_HOLES+MISSED_HOLES
    for segs in PATCHES:
        run=np.vstack([curve(sg)[(0 if i==0 else 1):] for i,sg in enumerate(segs)])
        a,b=(np.argmin(np.hypot(*(Q-np.array(p)).T)) for p in (run[0],run[-1]))
        Q=splice(Q,run,a,b)
    Q=rdp_closed(Q,0.12)
    # every hole is round (r4 review: the 'ovals' read round in the photo); area-preserving diameter
    holes=[(h[0],h[1],float(np.sqrt(h[2]*h[3])),float(np.sqrt(h[2]*h[3])),0.0) for h in holes]
    holes=regularise(holes,Q)
    s=SLOT_ROW;slots=[(s['first'][0]+s['step'][0]*i,s['first'][1]+s['step'][1]*i) for i in range(s['count'])]
    return Q,holes,slots


def main():
    Q,holes,slots=trace()
    dot=min(holes,key=lambda h:np.hypot(h[0]-724.2,h[1]-561.9))
    holes=[h for h in holes if h is not dot and min(np.hypot(h[0]-x,h[1]-y) for x,y in slots)>6]
    f=lambda l:',\n    '.join(', '.join(f'[{", ".join(f"{v:.1f}" for v in p)}]' for p in l[i:i+6]) for i in range(0,len(l),6))
    tip=max(Q.tolist(),key=lambda p:p[0])
    (HERE/'trace_px.scad').write_text(
        '// GENERATED by trace_photo.py from cad/reference/generalist_gripper_gen6_two_hands.png. Do not edit;\n'
        '// change the hand patches in trace_photo.py and re-run.\n'
        f'outline_px=[\n    {f(Q.tolist())}];\n'
        f'holes_px=[  // [x, y, major, minor, angle] in photo px / image degrees\n    {f(sorted(holes))}];\n'
        f'dot_px=[{dot[0]:.1f}, {dot[1]:.1f}, {DOT_D:.1f}];\n'
        f'slots_px=[\n    {f(slots)}];\n'
        f'tip_px=[{tip[0]:.1f}, {tip[1]:.1f}];\n'
        f'jaw_path_px=[\n    {f([list(p) for p in curve(JAW,3.0)])}];  // the inner edge as drawn, for the ridges\n')
    print(f'{len(Q)} outline points, {len(holes)} holes, dot d={DOT_D}px, {len(slots)} slots')
if __name__=='__main__':main()
