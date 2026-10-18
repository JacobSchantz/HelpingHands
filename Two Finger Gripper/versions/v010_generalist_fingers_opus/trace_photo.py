#!/usr/bin/env python3
"""Trace the lower finger of the left-hand device in the two-hands photo by colour, not by
eye: yellow pixels -> one finger silhouette -> simplified outline, and every dark blob inside
it -> a hole (centre + size). Writes trace_px.scad, which gripper.scad includes.

Gen 10 (Opus 5.5) starts from the Gen 7 trace and replaces the blade past the slot row with a
needle tip (NEEDLE below). The two-hands photo is too blurred there, and the blur reads the
tip as a blunt round nose. The side and robot photos are sharp at the tip: the inner (jaw) edge
runs straight to the point, and the outer edge sweeps in to meet it.

Two things the photo cannot give are patched by hand, and marked below:
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
HIDDEN_HOLES=[(387,360,10,10,0)]     # top-left root hole, nudged in and made smaller so a wall stays around it (Gen 7 r4 review)
DOT_XY=(724.2,561.9)    # blade dot centre, from the colour trace (Gen 7 trace_px.scad)
DOT_D=17                                # the blade dot's dark ring blurs to ~21 px; the dot itself is ~17
RESIZED={(626,493):(10,10,0),          # half-hidden in blur: the colour mask reads it at 6 px, the eye at 10
         (391,396):(10,10,0)}           # half under the carrier tongue: round, not an oval (r3 review)
MISSED_HOLES=[(657,511,8,8,0)]          # faint in the colour mask, visible by eye (round-2 review)
# Where the photo is blurred, a hand-drawn run replaces the trace between its first and last point.
PATCHES=[
  [(663.3,535),(665.5,552),(664,558),(668,565),(676,569.5),(690,571.1)],           # blade root: smooth concave blend, not a jog (r3 review)
]
# Needle tip (Gen 10, round 2). Past the black dot the blade is generated, not traced. It
# narrows evenly from the dot to a point on the dot->TIP centreline (top.png: a centred,
# pencil-like point). Half-widths are the traced ones at the dot, times
# g(f)=(1-f)(1+A f), f=s/L, with A per edge: convex, with no corner. It is about 1/3 width just before the
# point, and each edge meets the centreline at ~24 deg (side.png, robot.png).
# TIP is the centre of the photo's dark nub, so the yellow stops where the nub begins.
NEEDLE=dict(TIP=(846.0,606.0),HALF=(26.5,24.5),A=(1.31,2.6))   # inner, outer: half-width at the dot (px) and fullness
# (r3/r4: the outer edge is fuller over slots 3-5, two_hands.png; the jaw edge stays leaner).
# The slot row sits 2 px outboard of the Gen 7 trace, so the narrowed jaw keeps a wall and its grooves.
RIDGE_PITCH_PX=8.0    # 1.6 mm at 0.2 mm/px; grooves on the inner face from s=RIDGE_S[0] to RIDGE_S[1]
RIDGE_S=(36,118)   # r3: run the texture almost to the nub (side.png)
SLOT_ROW=dict(first=(748.8,555.9),step=(13.1,6.5),count=6)  # three are visible; the upper finger shows six


def rdp(pts,eps):
    a,b=pts[0],pts[-1];ab=b-a;L=np.hypot(*ab)
    if len(pts)<3 or L==0:return np.vstack([a,b])
    d=np.abs(ab[0]*(pts[:,1]-a[1])-ab[1]*(pts[:,0]-a[0]))/L;i=d.argmax()
    return np.vstack([rdp(pts[:i+1],eps)[:-1],rdp(pts[i:],eps)]) if d[i]>eps else np.vstack([a,b])


def needle_frame():
    dot=np.array(DOT_XY);tip=np.array(NEEDLE['TIP']);L=np.hypot(*(tip-dot));u=(tip-dot)/L;v=np.array([-u[1],u[0]])
    g=lambda f,k:(1-f)*(1+NEEDLE['A'][k]*f)
    edge=lambda s,side:dot+u*s+v*side*NEEDLE['HALF'][side>0]*g(s/L,side>0)   # side -1 inner (jaw), +1 outer
    return L,edge


def needle(n=24):
    L,edge=needle_frame();ss=np.linspace(0,L,n)
    return [tuple(edge(s,-1)) for s in ss]+[tuple(edge(s,1)) for s in ss[-2::-1]]


SLOT_PX=(15.0,6.75,120)   # slot length, width (px) and photo direction (deg), as gripper.scad cuts them (slot, frame_deg(120))
RIDGE_PX=(4.0,2.5,1.5)    # groove width, full depth, and the least wall left to a slot (px)


def ridges(slots):
    """Groove centres on the inner edge, outward normal and depth: [x, y, nx, ny, depth] px.
    Where a slot is close, a groove is made shallower so at least RIDGE_PX[2] of wall is
    left. Grooves that would end up shallower than half depth are skipped. The r3 review saw
    a pinhole where full-depth grooves met the slots, and genus.py counted two extra holes."""
    L,edge=needle_frame();out=[];d=np.radians(SLOT_PX[2]);sd=np.array([np.cos(d),np.sin(d)])
    caps=[(c+sd*h*sc*(SLOT_PX[0]-SLOT_PX[1])/2,sc*SLOT_PX[1]/2) for i,c in enumerate(np.array(slots))
          for sc in [0.7 if i==len(slots)-1 else 1] for h in np.linspace(-1,1,9)]
    for s in np.arange(RIDGE_S[0],RIDGE_S[1],RIDGE_PITCH_PX):
        p=edge(s,-1);t=edge(s+0.5,-1)-edge(s-0.5,-1);t/=np.hypot(*t);n=np.array([t[1],-t[0]])
        def clear(depth):
            groove=[p-n*k*depth+t*w for k in np.linspace(0,1,6) for w in (-RIDGE_PX[0]/2,RIDGE_PX[0]/2)]
            return min(np.hypot(*(g-c))-r for c,r in caps for g in groove)
        depth=next((dd for dd in np.linspace(RIDGE_PX[1],RIDGE_PX[1]/2,6) if clear(dd)>=RIDGE_PX[2]),None)
        if depth:out.append((*p,*n,depth))
    return out


def trace():
    im=Image.open(PHOTO).convert('RGB');hsv=np.array(im.convert('HSV')).astype(int)
    yel=(hsv[...,0]>=18)&(hsv[...,0]<=40)&(hsv[...,1]>=120)&(hsv[...,2]>=150)
    cut=Image.new('L',im.size,0);ImageDraw.Draw(cut).line(SEAM,fill=255,width=4)
    lab,_=nd.label(yel&(np.array(cut)==0))
    ys,xs=np.nonzero(lab[455:475,540:560])           # a yellow pixel on the bar
    finger=lab==lab[455+ys[0],540+xs[0]]
    filled=nd.binary_fill_holes(nd.binary_closing(finger,iterations=2))
    P=max(plt.contour(nd.gaussian_filter(filled.astype(float),1.6),[0.5]).allsegs[0],key=len)[:-1]
    j=np.argmax(np.hypot(*(P-P[0]).T))
    Q=np.vstack([rdp(P[:j+1],1.5)[:-1],rdp(np.vstack([P[j:],P[:1]]),1.5)[:-1]])
    # hand patch: straight root edge where the body hides it
    a,b=(np.argmin(np.hypot(*(Q-np.array(p)).T)) for p in ROOT_EDGE)
    keep=[i for i in range(len(Q)) if not (min(a,b)<i<max(a,b))]
    Q=Q[keep]
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
    for run in PATCHES+[needle()]:
        a,b=(np.argmin(np.hypot(*(Q-np.array(p)).T)) for p in (run[0],run[-1]))
        Q=np.vstack([Q[:a],np.array(run,float),Q[b+1:]])
    s=SLOT_ROW;slots=[(s['first'][0]+s['step'][0]*i,s['first'][1]+s['step'][1]*i) for i in range(s['count'])]
    return Q,holes,slots


def main():
    Q,holes,slots=trace()
    dot=max(holes,key=lambda h:h[2])
    holes=[h for h in holes if h is not dot and min(np.hypot(h[0]-x,h[1]-y) for x,y in slots)>6]
    f=lambda l:',\n    '.join(', '.join(f'[{", ".join(f"{v:.1f}" for v in p)}]' for p in l[i:i+6]) for i in range(0,len(l),6))
    tip=NEEDLE['TIP']
    (HERE/'trace_px.scad').write_text(
        '// GENERATED by trace_photo.py from cad/reference/generalist_gripper_gen6_two_hands.png. Do not edit;\n'
        '// change the hand patches in trace_photo.py and re-run.\n'
        f'outline_px=[\n    {f(Q.tolist())}];\n'
        f'holes_px=[  // [x, y, major, minor, angle] in photo px / image degrees\n    {f(sorted(holes))}];\n'
        f'dot_px=[{dot[0]:.1f}, {dot[1]:.1f}, {DOT_D:.1f}];\n'
        f'slots_px=[\n    {f(slots)}];\n'
        f'tip_px=[{tip[0]:.1f}, {tip[1]:.1f}];\n'
        f'ridges_px=[  // inner-face groove centres, outward normal, depth [x, y, nx, ny, depth px]\n    {f(ridges(slots))}];\n')
    print(f'{len(Q)} outline points, {len(holes)} holes, dot d={DOT_D}px, {len(slots)} slots')
if __name__=='__main__':main()
