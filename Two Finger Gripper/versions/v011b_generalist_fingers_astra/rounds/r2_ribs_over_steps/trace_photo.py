#!/usr/bin/env python3
"""Trace the lower finger of the left-hand device in the two-hands photo by colour, not by
eye: yellow pixels -> one finger silhouette -> simplified outline, and every dark blob inside
it -> a hole (centre + size). Writes trace_px.scad, which gripper.scad includes.

Gen 11 (Opus 5.5) starts from Gen 10. It keeps Gen 10's generated needle past the black dot
(the two-hands photo is blurred there) and changes two things Jake asked for:
  * the tip is skinnier and more pointed: the width curve gets a (1-f)^NEEDLE_Q factor, so the
    last few mm narrow to a needle instead of a round spear nose (top.png, robot.png);
  * the ridges are fine, shallow grooves along the WHOLE inner edge, from the head to the
    beak, cut across the full thickness (robot.png, side.png). gripper.scad cuts them;
    this file only places them (RIDGE_*).

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
NEEDLE=dict(TIP=(846.0,606.0),HALF=(26.5,24.5),A=(1.31,3.0))   # inner, outer: half-width at the dot (px) and fullness
NEEDLE_Q=(1.15,1.35)   # Gen 11, per edge: g(f)=(1-f)^Q (1+A f). Q>1 keeps the mid-blade about as full as Gen 10
                       # but narrows the last 3 mm to a needle (Jake: "skinny, pointed tips"). The jaw edge
                       # gets less, so it keeps a wall outside the slot row.
# The slot row sits 4 px outboard of the Gen 7 trace (Gen 10: 2 px), so the narrowed jaw keeps a wall.
# Ridges (Gen 11): a groove every RIDGE_PITCH_PX along the inner edge, from RIDGE_FROM (just past the
# head corner) to where the blade gets too narrow to carry one. The robot photo shows the inner face
# ribbed from the carrier to the beak, across its full thickness.
RIDGE_PITCH_PX=5.0     # 1.0 mm at 0.2 mm/px
RIDGE_FROM=(423.0,335.6)   # r2: from the head corner itself (robot.png ribs run up to the head)
RIDGE_CORNER_DEG=80    # skip a groove only at a corner sharper than this within +-1 mm; r2: the ribs carry on over the step faces (robot.png)
GROOVE_PX=(2.5,2.5)    # groove width and depth in px, as gripper.scad cuts them (ridge[1], ridge[2])
RIDGE_MIN_WIDTH_PX=13  # stop where the blade is narrower than 2.6 mm across, so a groove never nears the outer edge
SLOT_ROW=dict(first=(747.9,557.7),step=(13.1,6.5),count=6)  # three are visible; the upper finger shows six


def rdp(pts,eps):
    a,b=pts[0],pts[-1];ab=b-a;L=np.hypot(*ab)
    if len(pts)<3 or L==0:return np.vstack([a,b])
    d=np.abs(ab[0]*(pts[:,1]-a[1])-ab[1]*(pts[:,0]-a[0]))/L;i=d.argmax()
    return np.vstack([rdp(pts[:i+1],eps)[:-1],rdp(pts[i:],eps)]) if d[i]>eps else np.vstack([a,b])


def needle_frame():
    dot=np.array(DOT_XY);tip=np.array(NEEDLE['TIP']);L=np.hypot(*(tip-dot));u=(tip-dot)/L;v=np.array([-u[1],u[0]])
    g=lambda f,k:(1-f)**NEEDLE_Q[k]*(1+NEEDLE['A'][k]*f)
    edge=lambda s,side:dot+u*s+v*side*NEEDLE['HALF'][side>0]*g(s/L,side>0)   # side -1 inner (jaw), +1 outer
    return L,edge


def needle(n=24):
    L,edge=needle_frame();ss=np.linspace(0,L,n)
    return [tuple(edge(s,-1)) for s in ss]+[tuple(edge(s,1)) for s in ss[-2::-1]]


def ridges(Q):
    """Groove stations along the inner edge: [x, y, nx, ny] px, n the outward normal. gripper.scad
    cuts each one RIDGE depth deep, measured from the finished edge, and keeps a wall to every hole."""
    from matplotlib.path import Path as MPath
    shape=MPath(Q);tip=np.argmin(np.hypot(*(Q-np.array(NEEDLE['TIP'])).T));start=np.argmin(np.hypot(*(Q-np.array(RIDGE_FROM)).T))
    E=Q[start:tip+1];seg=np.hypot(*np.diff(E,axis=0).T);arc=np.concatenate([[0],np.cumsum(seg)])
    at=lambda s:np.array([np.interp(s,arc,E[:,0]),np.interp(s,arc,E[:,1])])
    def tangent(s,h):t=at(s+h)-at(s-h);return t/np.hypot(*t)
    out=[]
    for s in np.arange(RIDGE_PITCH_PX,arc[-1],RIDGE_PITCH_PX):
        t=tangent(s,2.0);n=np.array([t[1],-t[0]]);p=at(s)
        if shape.contains_point(p+n*2):n=-n   # outward
        turn=np.degrees(np.arccos(np.clip(tangent(s-5,1.5)@tangent(s+5,1.5),-1,1)))
        if turn>RIDGE_CORNER_DEG:continue
        if not shape.contains_point(p-n*RIDGE_MIN_WIDTH_PX):break   # the blade is too narrow from here to the point
        if out:   # in a concave corner grooves converge: keep >= 0.3 mm between groove bottoms, or a rib turns into a loose sliver (r2)
            q,m=np.array(out[-1][:2]),np.array(out[-1][2:])
            if min(np.hypot(*((p-n*k)-(q-m*k))) for k in np.linspace(0,GROOVE_PX[1],6))<GROOVE_PX[0]+1.5:continue
        out.append((*p,*n))
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
    for run in [needle()]+PATCHES:
        a,b=(np.argmin(np.hypot(*(Q-np.array(p)).T)) for p in (run[0],run[-1]))
        if a>b:run,a,b=run[::-1],b,a   # Gen 11: a run drawn against the outline's direction used to leave a zero-width spur
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
        f'ridges_px=[  // inner-edge groove stations, outward normal [x, y, nx, ny] px\n    {f(ridges(Q))}];\n')
    print(f'{len(Q)} outline points, {len(holes)} holes, dot d={DOT_D}px, {len(slots)} slots, {len(ridges(Q))} grooves')
if __name__=='__main__':main()
