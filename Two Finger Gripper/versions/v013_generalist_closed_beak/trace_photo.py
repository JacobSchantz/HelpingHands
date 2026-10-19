#!/usr/bin/env python3
"""Gen 13 (Opus 5.5): the jaw edge comes from the CLOSED photo first. trace_closed.py measures the
closed gap g(d) between the two jaws in generalist_gripper_gen6_closed.png and writes closed_trace.json;
closed_jaw() below reshapes Gen 11 r4's beak with it so that, closed, the two fingers meet only at the
point and back off along g(d) behind it (Gen 11's innermost reach was ~9 mm behind its point, so closed
it would have met mid-jaw). The rest of this file is Gen 11 r4's trace, used for the plan-view shape.

Trace the lower finger of the left-hand device in the two-hands photo by colour, not by
eye: yellow pixels -> one finger silhouette -> simplified outline, and every dark blob inside
it -> a hole (centre + size). Writes trace_px.scad, which gripper.scad includes.

Gen 11 (Opus 5.5) starts from Gen 10. It keeps Gen 10's generated needle past the black dot
(the two-hands photo is blurred there) and changes two things Jake asked for:
  * the tip comes to a cleaner point: the width curve gets a (1-f)^NEEDLE_Q factor, so the
    last few mm sharpen while the beak keeps Gen 10's fullness (r4);
  * the ridges are fine, shallow grooves on the gripping jaw only, from the beak shoulder to
    the point, cut across the full thickness (robot.png, side.png). gripper.scad cuts them;
    this file only places them (RIDGE_*).

Two things the photo cannot give are patched by hand, and marked below:
  * the upper finger's blade touches this one near the tips, so a seam line separates them;
  * the device body hides the top-left corner of the root, so that edge is a straight line
    and the hidden top-left root hole is added on the hex grid of its neighbours.
"""
from pathlib import Path
import json
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
NEEDLE=dict(TIP=(846.0,606.0),HALF=(26.5,24.5),A=(1.31,2.8))   # inner, outer: half-width at the dot (px) and fullness
NEEDLE_Q=(1.05,1.12)   # Gen 11, per edge: g(f)=(1-f)^Q (1+A f). Q>1 sharpens the last few mm into a clean point.
                       # r4: r1-r3 used (1.15,1.35) and A_outer 3.0, a needle that lost Gen 10's full beak (Jake);
                       # this is close to Gen 10's (1, 2.6) over the blade and only slightly sharper at the point.
NEEDLE_TAIL=(0.6,20)    # r3: half-width floor 0.6 d (1-d/20) over the last 20 px (4 mm): >= 0.9 mm across 1 mm back,
                        # where (1-f)^Q alone left a 0.5 mm sliver that prints as one line. Zero further back.
# The slot row sits 4 px outboard of the Gen 7 trace (Gen 10: 2 px), so the narrowed jaw keeps a wall.
# Ridges (Gen 11): a groove every RIDGE_PITCH_PX along the jaw's inner edge, from RIDGE_FROM to where the
# blade gets too narrow to carry one, each across the full thickness. r4: only the gripping jaw/beak, as in
# robot.png. r1-r3 ran them from the head corner down the whole inner edge, which read as a saw (Jake).
RIDGE_PITCH_PX=5.0     # 1.0 mm at 0.2 mm/px
RIDGE_FROM=(423.0,336.0)   # Gen 13: the head corner, so the serration spans the whole inner edge (Jake, closed.png); Gen 11 r4: the jaw only (713,524)
RIDGE_CORNER_DEG=100   # skip a groove only at a corner sharper than this within +-1 mm; the ribs carry on over the step faces (robot.png, r2-r3)
GROOVE_PX=(2.5,2.0)    # groove width and depth in px, as gripper.scad cuts them (ridge[1], ridge[2]): 0.5 x 0.4 mm, Gen 12's shallow grooves
RIDGE_STOP_PX=15       # Gen 13 r2: the grooves stop 3 mm (arc) short of the point, so the contact stretch stays smooth and solid
RIDGE_MIN_WIDTH_PX=9    # stop where the blade is narrower than 1.8 mm across (r3: runs to ~1.5 mm from the point; r1-r2: 2.6 mm). At 1.6 mm two tip grooves left a pinhole
SLOT_ROW=dict(first=(747.9,557.7),step=(13.1,6.5),count=6)  # three are visible; the upper finger shows six


def rdp(pts,eps):
    a,b=pts[0],pts[-1];ab=b-a;L=np.hypot(*ab)
    if len(pts)<3 or L==0:return np.vstack([a,b])
    d=np.abs(ab[0]*(pts[:,1]-a[1])-ab[1]*(pts[:,0]-a[0]))/L;i=d.argmax()
    return np.vstack([rdp(pts[:i+1],eps)[:-1],rdp(pts[i:],eps)]) if d[i]>eps else np.vstack([a,b])


def needle_frame():
    dot=np.array(DOT_XY);tip=np.array(NEEDLE['TIP']);L=np.hypot(*(tip-dot));u=(tip-dot)/L;v=np.array([-u[1],u[0]])
    g=lambda f,k:(1-f)**NEEDLE_Q[k]*(1+NEEDLE['A'][k]*f)
    tail=lambda d:NEEDLE_TAIL[0]*d*(1-d/NEEDLE_TAIL[1]) if d<NEEDLE_TAIL[1] else 0   # d = px to the point
    half=lambda s,k:max(NEEDLE['HALF'][k]*g(s/L,k),tail(L-s))   # r3: the last few mm never thinner than this, so the point prints
    edge=lambda s,side:dot+u*s+v*side*half(s,side>0)   # side -1 inner (jaw), +1 outer
    return L,edge


# Closed contact (Gen 13). Photo px -> finger-frame mm, as px() in gripper.scad.
FRAME=dict(pivot=(337,395),deg=36.5,mm=0.2)
TIP_SHIFT_FROM=0.55     # the point moves in to the jaw's innermost reach over the last 45% of the beak (smoothstep), outer edge too
ROUND_BACK=1.8          # mm: gripper.scad's corner rounding ends the point ~1 mm short of the trace, and the contact (where the
                        # photo's seam ends) is where that round meets the jaw, ~1.8 mm back, so g(d) is measured from there
JAW_FOLLOW=(21,26)      # mm behind the contact: the jaw edge IS the closed-gap curve up to 21 mm, blending into Gen 11's shoulder by 26 (r2; r1 18-24 opened too fast at 19-24 mm)
def to_mm(q):
    a=np.radians(FRAME['deg']);d=np.subtract(q,FRAME['pivot'])
    return FRAME['mm']*np.array([-(d[0]*np.sin(a)-d[1]*np.cos(a)),d[0]*np.cos(a)+d[1]*np.sin(a)])
def to_px(m):
    a=np.radians(FRAME['deg']);X,Z=np.asarray(m)/FRAME['mm']
    return np.array([FRAME['pivot'][0]-X*np.sin(a)+Z*np.cos(a),FRAME['pivot'][1]+X*np.cos(a)+Z*np.sin(a)])
GAP=json.loads((HERE/'closed_trace.json').read_text())['gap_fit']
closed_gap=lambda d:GAP['A']*max(0.0,d)**GAP['P']   # mm apart at d mm behind the point, closed (trace_closed.py)


def closed_jaw(n=48):
    """Gen 11 r4's beak, made to close the way the photo does. The point moves in to x_c, the innermost
    reach of Gen 11's jaw (both edges blend over the last 45%). The jaw edge follows x_c + g(d)/2 up to
    JAW_FOLLOW[0] mm back, then blends into Gen 11's edge, and never comes inside x_c + g(d)/2, so two
    mirrored fingers touch at the point only. Returns (inner, outer) px."""
    L,edge=needle_frame();ss=np.linspace(0,L,n)
    inner=np.array([to_mm(edge(s,-1)) for s in ss]);outer=np.array([to_mm(edge(s,1)) for s in ss])
    xc=inner[:,0].min();tip=inner[-1];dx=xc-tip[0]
    t=np.clip((ss/L-TIP_SHIFT_FROM)/(1-TIP_SHIFT_FROM),0,1);w=t*t*(3-2*t)
    want=np.array([xc+closed_gap(tip[1]-ROUND_BACK-z)/2 for z in inner[:,1]])
    b=np.clip((tip[1]-ROUND_BACK-inner[:,1]-JAW_FOLLOW[0])/(JAW_FOLLOW[1]-JAW_FOLLOW[0]),0,1);b=b*b*(3-2*b)
    inner[:,0]=np.maximum(want,want+(inner[:,0]+dx*w-want)*b)
    outer[:,0]+=dx*w
    return [to_px(m) for m in inner],[to_px(m) for m in outer]


def needle(n=48):
    inner,outer=closed_jaw(n)
    return [tuple(p) for p in inner]+[tuple(p) for p in outer[-2::-1]]


def tip_px():
    return tuple(closed_jaw()[0][-1])


def ridges(Q):
    """Groove stations along the inner edge: [x, y, nx, ny] px, n the outward normal. gripper.scad
    cuts each one RIDGE depth deep, measured from the finished edge, and keeps a wall to every hole."""
    from matplotlib.path import Path as MPath
    shape=MPath(Q);tip=np.argmin(np.hypot(*(Q-np.array(tip_px())).T));start=np.argmin(np.hypot(*(Q-np.array(RIDGE_FROM)).T))
    E=Q[start:tip+1];seg=np.hypot(*np.diff(E,axis=0).T);arc=np.concatenate([[0],np.cumsum(seg)])
    at=lambda s:np.array([np.interp(s,arc,E[:,0]),np.interp(s,arc,E[:,1])])
    def tangent(s,h):t=at(s+h)-at(s-h);return t/np.hypot(*t)
    out=[]
    for s in np.arange(RIDGE_PITCH_PX,arc[-1],RIDGE_PITCH_PX):
        t=tangent(s,2.0);n=np.array([t[1],-t[0]]);p=at(s)
        if shape.contains_point(p+n*2):n=-n   # outward
        turn=np.degrees(np.arccos(np.clip(tangent(s-5,1.5)@tangent(s+5,1.5),-1,1)))
        if turn>RIDGE_CORNER_DEG:continue
        if arc[-1]-s<RIDGE_STOP_PX or not shape.contains_point(p-n*RIDGE_MIN_WIDTH_PX):break   # the blade is too narrow from here to the point
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
    f=lambda l:',\n    '.join(', '.join(f'[{", ".join(f"{v:.2f}" for v in p)}]' for p in l[i:i+6]) for i in range(0,len(l),6))
    tip=tip_px()
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
