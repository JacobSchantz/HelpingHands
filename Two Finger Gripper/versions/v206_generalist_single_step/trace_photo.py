#!/usr/bin/env python3
"""2.6 (voice-72840084): 2.5's tracer with the top hook moved up to where the outer edge used to start going out again (the
blade-root S-curve), as one step. Jake: "Extend the black piece where my finger rests all the way up to where the profile
starts to go out again. Where it goes out again, make it more of a single jump out: no double indent, just out and then
back in." top_hook() now runs the straight outer edge (RAIL) on up to the top notch (params.json top_notch_u), curls round
the mirrored J-hook's bowl and prong to its crest, and from the crest fills straight on to the beak's outer edge
(top_step_back), so 1.20's top notch, its ramp back in, the dip after it and the S-curve's climb are one step out.

2.5 (voice-56f9d73f): 2.4's parametric tracer plus 1.20's top hook (voice-483f28b9). top_hook() mirrors the base
J-hook's run (PATCHES[1]) end for end about u = top_hook_mirror_u (params.json) on the straight outer edge (RAIL), so the two
notches face each other, and closes its back onto the edge with a short ramp.

Gen 16 (voice-1fc7e062): Gen 15 with Gen 9's roundness. Jake: "combine Gen 15 and Gen 9, taking the best of both."
Gen 15's length, beak, contact and holes stay. From Gen 9:
  * the traced contour is resampled and Gaussian-smoothed (SMOOTH_SIGMA) before the patches, not an RDP polygon, so
    every traced edge is a curve;
  * the two inner-edge knobs (the shoulder steps mid-shank) become one smooth ramp with two rounded swells
    KNOB_SWELL_PX (1 mm) proud of it (KNOBS): "keep the ridges but make them shallower, about 1 mm";
  * the blade root's outer jog is Gen 9's S-curve, and the base hook is Gen 9's rounded J-claw (PATCHES).
The point and the closed contact are Gen 15's (closed_jaw); gripper.scad sharpens the side profile and drops the
dark tip pad.

Gen 14 (a refinement pass on Gen 13): only the very points touch. Gen 13's closed jaws stayed under
0.03 mm apart for the last ~8 mm, so they met along a line, not at the point (Jake: "a little too much
contact leading up to the tip ... not quite a tight, sharp enough contact angle"). closed_gap() below adds
a wedge to the photo's curve: behind the point the two inner edges open at WEDGE['half_deg'] each, and
the wedge levels off at 0.35 mm and the rest of the jaw keeps the photo's curve, 0.1 mm wider.
The photo cannot tell these apart: at ~0.5 mm/px across the jaws, a 0.5 mm gap is one pixel.

Gen 13 (Opus 5.5): the jaw edge comes from the CLOSED photo first. trace_closed.py measures the
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
HIDDEN_HOLES=[(388.5,361.5,10,10,0)] # top-left root hole, nudged in and made smaller so a wall stays around it (Gen 7 r4 review); Gen 16: 1.5 px further in, the smoothed root corner sits closer
DOT_XY=(724.2,561.9)    # blade dot centre, from the colour trace (Gen 7 trace_px.scad)
DOT_D=17                                # the blade dot's dark ring blurs to ~21 px; the dot itself is ~17
RESIZED={(626,493):(10,10,0),          # half-hidden in blur: the colour mask reads it at 6 px, the eye at 10
         (391,396):(10,10,0)}           # half under the carrier tongue: round, not an oval (r3 review)
MISSED_HOLES=[(657,511,8,8,0)]          # faint in the colour mask, visible by eye (round-2 review)
# Where the photo is blurred, a hand-drawn run replaces the trace between its first and last point. Each run is a
# smooth spline through its points (curve()).
PATCHES=[
  # Gen 16: blade root, Gen 9's S-curve from the shank's outer edge into the beak (Gen 15: a 4.6 mm vertical jog at x 664)
  [(629.6,517.2),(645,523),(657,531.5),(664.5,543),(671,554),(681,564),(693,572.5),(706.6,581.7),(713.3,583.8)],
  # Gen 16: base hook, Gen 9's rounded J-claw: a round bowl and a fat rounded toe (Gen 15: a blocky notch)
  [(392.3,408.3),(376,399.5),(363,393.2),(355,391.2),(349.5,394),(347.2,400.5),(348.4,407.5),(351,413),
   (350,418),(345,420.2),(338.5,418),(331.5,412),(326.5,404.5),(324.4,396.5),(325.5,390.5),(327.1,388.7)],
]
# 1.20: the straight outer edge (params.json rail_p, mm in the finger frame): u runs along it toward the tip from p0, w points
# outboard. Straight within 0.3 mm from the base hook (u -10) to u 36.
RAIL=dict(p0=None,p1=None)
# 1.20: the top hook is the base hook's run from where it leaves the edge (from_u) round its bowl and prong to the back of the
# prong, mirrored about u=mirror_u (params.json top_hook_mirror_u), then a ramp (u past the prong's back, w) back onto the
# edge. mirror_u 8.5 puts the top notch's floor at u 28.4 (base: -11.4), 39.8 mm apart; the ramp lands at u 36.5, before the root bend.
# 2.6: mirror_u is halfway between the base floor and params.json top_notch_u (the top floor; 54 mm: where 1.20's edge started going out). The run starts at
# straight_from on the edge, runs it straight (1.20's trace dips 1 mm between u 36 and 56) to the hook, and stops at the prong's
# crest; no ramp. From the crest a cubic fills on to the outer edge where it is back up to the crest's height less top_step_back.
RDP_SPLIT=(720.74,593.13)   # 1.20: px where the outline's two rdp halves meet: 1.19's len(Q)//2 point, so the top hook's extra
                            # points leave the beak half's vertices as 1.19's (a shifted split moved them and left a non-manifold edge)
TOP_HOOK=dict(from_u=-7.86,notch_u=None,straight_from=20.0,back=None)   # 2.6: 1.20's ramp ((1.3,1.4),(3.5,-0.25)) is gone
SMOOTH_SIGMA=None       # params.json outline_smooth (mm -> px in configure()). 2.3: 4.0 px. Gen 16, from Gen 9: px, periodic Gaussian along the traced contour (Gen 15: RDP at 1.5 px, a polygon)
# Gen 16: the inner edge between the head and the beak. Gen 15 had two square knobs there (a 6 mm step at x 637 and a
# bump at x 680-690). Now a smooth ramp (base) with two rounded swells, each KNOB_SWELL_PX proud along the edge's
# normal over a cos^2 window of the given half-width: where Gen 15's knobs were, ~1 mm high instead of ~6.
KNOB_SWELL_PX=None      # params.json knob_swell. 2.3: 6.0 px = 1.2 mm at 0.2 mm/px. r2: 5.0 (1 mm) over a narrow window read as a knob, not a bump
KNOBS=dict(base=[(606,456.3),(618,457.6),(630,462),(641,471),(652,482),(664,491),(677,497),(690,502),(701,510),
                 (710,521),(717,533),(724,544),(732,551.5),(740.6,554.6)],
           swells=[((627,461),None),((687,500.5),None)])   # (centre px, half-width px) along the edge. r2 (Jake: "really
                                                           # rounded"): 30/28, ~2.3x wider, crest radius ~4 mm (r1: 13/11, ~1.4 mm)
KNOB_BASE_SIGMA=None    # params.json knob_ramp_smooth. 2.3: 6.0 px. r2: px, Gaussian along the ramp before the swells, so its own bends don't put corners at their feet
# Needle tip (Gen 10, round 2). Past the black dot the blade is generated, not traced. It
# narrows evenly from the dot to a point on the dot->TIP centreline (top.png: a centred,
# pencil-like point). Half-widths are the traced ones at the dot, times
# g(f)=(1-f)(1+A f), f=s/L, with A per edge: convex, with no corner. It is about 1/3 width just before the
# point, and each edge meets the centreline at ~24 deg (side.png, robot.png).
# TIP is the centre of the photo's dark nub, so the yellow stops where the nub begins.
# Gen 16 r2: outer A 2.8 -> 4.0. The closed photo's outer edge stays full and then rounds in to a thick tip.
NEEDLE=dict(TIP=(846.0,606.0),HALF=(26.5,24.5),A=(1.31,4.0))   # inner, outer: half-width at the dot (px) and fullness
# Gen 15 (voice-8673a6b6): the beak past the black dot is BEAK_STRETCH times longer along the finger, its point at the same
# x, so dot -> point is a third of the finger (Gen 14: 24.8 of 109.4 mm, 23%; the closed photo shows ~38% from the dots).
# Everything behind the dot is Gen 14's. The beak keeps Gen 14's widths at the same fraction of its length, so it is
# slimmer per mm; the slots move with it (stretch_z) and closed_jaw() still shapes the contact in mm, so it is unchanged.
BEAK_STRETCH=None       # params.json beak_stretch. 2.3: 1.70
NEEDLE_Q=(1.05,1.12)   # Gen 11, per edge: g(f)=(1-f)^Q (1+A f). Q>1 sharpens the last few mm into a clean point.
                       # r4: r1-r3 used (1.15,1.35) and A_outer 3.0, a needle that lost Gen 10's full beak (Jake);
                       # this is close to Gen 10's (1, 2.6) over the blade and only slightly sharper at the point.
NEEDLE_TAIL=(0.6,20)    # r3: half-width floor 0.6 d (1-d/20) over the last 20 px (4 mm): >= 0.9 mm across 1 mm back,
                        # where (1-f)^Q alone left a 0.5 mm sliver that prints as one line. Zero further back.
# The slot row sits 4 px outboard of the Gen 7 trace (Gen 10: 2 px), so the narrowed jaw keeps a wall.
# Ridges (Gen 11): a groove every RIDGE_PITCH_PX along the jaw's inner edge, from RIDGE_FROM to where the
# blade gets too narrow to carry one, each across the full thickness. r4: only the gripping jaw/beak, as in
# robot.png. r1-r3 ran them from the head corner down the whole inner edge, which read as a saw (Jake).
RIDGE_PITCH_PX=None    # params.json groove_pitch. 2.3: 5.0 px = 1.0 mm at 0.2 mm/px
RIDGE_FROM=(423.0,336.0)   # Gen 13: the head corner, so the serration spans the whole inner edge (Jake, closed.png); Gen 11 r4: the jaw only (713,524)
RIDGE_CORNER_DEG=100   # skip a groove only at a corner sharper than this within +-1 mm; the ribs carry on over the step faces (robot.png, r2-r3)
GROOVE_PX=None         # params.json groove_width, groove_depth. 2.3: (2.5, 2.0) px: groove width and depth in px, as gripper.scad cuts them (ridge[1], ridge[2]): 0.5 x 0.4 mm, Gen 12's shallow grooves
RIDGE_STOP_PX=None     # params.json groove_stop. 2.3: 17 px. Gen 14 r2: the grooves stop 3.4 mm (arc) short of the point, behind the dark tip pad (gripper.scad pad_len). r1: 4.4; Gen 13: 3 mm
RIDGE_MIN_WIDTH_PX=None # params.json groove_min_width. 2.3: 9 px: stop where the blade is narrower than 1.8 mm across (r3: runs to ~1.5 mm from the point; r1-r2: 2.6 mm). At 1.6 mm two tip grooves left a pinhole
PHOTO_SLOTS=6   # slot blobs in the photo (the upper finger shows six); main() keeps them out of the holes
SLOT_ROW=dict(first=(747.9,557.7),step=(13.1,6.5),count=None)   # count: params.json slot_count.  # three are visible; the upper finger shows six


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


def curve(pts,step=1.0):
    """A smooth spline through pts, a point every ~step px."""
    from scipy.interpolate import splprep,splev
    p=np.array(pts,float);tck,_=splprep([p[:,0],p[:,1]],s=0,k=3)
    u=np.linspace(0,1,max(4,int(np.hypot(*np.diff(p,axis=0).T).sum()/step)));return np.column_stack(splev(u,tck))


def knobs():
    """Gen 16's inner edge mid-shank: the base ramp plus two rounded 1 mm swells, pushed out along the outward normal
    (the finger is below the edge in the photo, so outward is the edge's left-hand normal)."""
    B=curve(KNOBS['base']);k=int(3*KNOB_BASE_SIGMA)
    S=np.c_[nd.gaussian_filter1d(B[:,0],KNOB_BASE_SIGMA,mode='nearest'),nd.gaussian_filter1d(B[:,1],KNOB_BASE_SIGMA,mode='nearest')]
    r=np.clip(np.minimum(np.arange(len(B)),np.arange(len(B))[::-1])/k,0,1);r=r*r*(3-2*r)
    B=B+(S-B)*r[:,None]   # eased in from both ends, so it still joins the trace without a step
    t=np.gradient(B,axis=0);t/=np.hypot(*t.T)[:,None];n=np.c_[t[:,1],-t[:,0]]
    s=np.r_[0,np.cumsum(np.hypot(*np.diff(B,axis=0).T))];lift=np.zeros(len(B))
    for c,w in KNOBS['swells']:
        d=np.abs(s-s[np.argmin(np.hypot(*(B-np.array(c)).T))]);lift+=np.where(d<w,np.cos(np.pi/2*d/w)**2,0)
    return [tuple(p) for p in B+n*KNOB_SWELL_PX*lift[:,None]]


def needle_frame():
    dot=np.array(DOT_XY);tip=np.array(NEEDLE['TIP']);L=np.hypot(*(tip-dot));u=(tip-dot)/L;v=np.array([-u[1],u[0]])
    g=lambda f,k:(1-f)**NEEDLE_Q[k]*(1+NEEDLE['A'][k]*f)
    tail=lambda d:NEEDLE_TAIL[0]*d*(1-d/NEEDLE_TAIL[1]) if d<NEEDLE_TAIL[1] else 0   # d = px to the point
    half=lambda s,k:max(NEEDLE['HALF'][k]*g(s/L,k),tail(L-s))   # r3: the last few mm never thinner than this, so the point prints
    edge=lambda s,side:dot+u*s+v*side*half(s,side>0)   # side -1 inner (jaw), +1 outer
    return L,edge


# Closed contact (Gen 13). Photo px -> finger-frame mm, as px() in gripper.scad.
FRAME=dict(pivot=None,deg=None,mm=None)   # params.json px_pivot, axis_deg, mm_per_px (gripper.scad's px())
TIP_SHIFT_FROM=0.55     # the point moves in to the jaw's innermost reach over the last 45% of the beak (smoothstep), outer edge too
ROUND_BACK=None         # params.json round_back. 2.3: 1.5 mm: Gen 16 r3: the triangle point is sharper in plan, so tip_r rounds it ~1.5 mm back (mesh innermost reach z 122.78, trace point 124.31). Gen 15: 1.0. Gen 15: the slimmer point loses more to the 0.3 mm round (gripper.scad tip_r), so the contact sits ~1.0 mm
                        # behind the trace (measured on the mesh: innermost reach at z 123.35, trace point 124.31). Gen 14: 0.4; Gen 13: 1.8
                        # Gen 13: 1.8 (its 1 mm round left two nubs and a small V in front of the contact)
WEDGE=dict(half_deg=15.0,cap=2.0,over=0.10,k=6)   # Gen 16 r2 (Jake: "the gap opens up rapidly going back from the tip", 6.8 deg
                        # was too narrow; the closed photo, cad/reference/generalist_gripper_gen6_closed.png, is the key reference): 15 deg each
                        # side (30 included) to a 2 mm gap, about what the jaw already has 25 mm back, so the gap never narrows again
                        # (3 mm left a parallel slot that stepped back in at the shoulder).
WEDGE_R1=dict(half_deg=4.5,cap=0.40,over=0.10,k=6)   # Gen 16 r1's wedge; the outer edge moves out by what r2 cuts beyond it (KEEP_WIDTH)
KEEP_WIDTH=1.0          # r2 (Jake: "make the tip thicker"): fraction of the extra inner cut added back on the outer edge, so the beak
                        # keeps r1's width and bends away from the jaw instead of getting thinner
# Gen 15: 4.5 deg to 0.40 mm: 4.5 deg to 0.40 mm (Gen 14: 4 deg to 0.35). Gen 14's model met ~0.6 mm
                        # behind its designed contact, which made its 1-2 mm included angle read 6.6 deg; on target, 4/0.35 gives only 5.7.
                        # Gen 14: each inner edge leaves the contact at 4 deg (8 deg included) and the
                        # wedge levels off at a 0.35 mm gap; further back the gap is the photo's curve + 0.10 mm. A smooth max (power
                        # k) joins the two, so the gap only ever grows. r1 kept the whole wedge on (~0.5 mm over the photo
                        # the length of the jaw); the r1 review read that as a slit and asked for it to fade (r2)
NOSE=dict(mm=7.0,a=0.35,b=0.35,deg=65)   # Gen 16 r2, from the closed photo: "approaching the tip on the outside, the profile rounds inward into
                        # the final tip, but the tip itself stays relatively thick". The last NOSE['mm'] of the outer edge is a cubic
                        # Bezier leaving the edge along its own tangent (handle a x chord) and arriving at the point deg off the
                        # finger's axis (handle b x chord): a full, rounded nose instead of r1's straight 45 deg run in to a needle.
                        # Square on (90 deg) read as a dome, not a point. 7 mm, not 6: gripper.scad tip_zone cuts at 6, and a
                        # shared vertex there left a non-manifold edge
# Gen 16 r3 (Jake: "near the tip the two fingers should never run parallel ... the closed shape reads like a triangle coming
# to the point"; key reference cad/reference/generalist_gripper_gen6_closed.png): r2's wedge levelled off at 2 mm by 6 mm back
# and ran parallel to ~25 mm. Now, closed, each jaw edge runs from the point all the way back to the black dot as
# half_gap = H (d/D)^p: H and D are the crest of the second knob swell, just behind the dot, so the edge runs straight
# into it instead of dipping in at the dot and out again (Jake's indent; the crest is in the knobs() run). p < 1 opens fastest
# right at the point and straightens behind it, so the gap widens at every d (never parallel, never closing).
TRIANGLE=dict(p=None)   # params.json jaw_open_power. 2.3: 0.85
# r3 (Jake: "the outside profile running in toward the tip should be more of a straight line"): r2's outer edge bulged to
# 13.6 mm and then rounded in (NOSE). Now from the dot it is one cubic Bezier: it leaves along the shank (a x chord),
# then runs almost straight to the point, bowed out bow x chord at its far handle.
OUTER=dict(a=None,b=None,bow=None,out_deg=None)   # params.json outer_start_handle, outer_end_handle, outer_bow, outer_lean_deg
                        # (2.3: 0.30, 0.30, 0.04, 0; 1.19: 0.50, 0.25, 0.20, 15: the edge leaves the dot angled outward)
JOIN=dict(half_px=None,sigma=None)   # params.json dot_join_span, dot_join_smooth (2.3: 40, 10 px). Gen 16 r3 r3 (Jake: "at the large circle toward the end of the fingers there's an indent"): where the
                        # generated beak meets the traced shank at the dot, both edges kinked (outer: a 0.6 mm step in). Each
                        # join is Gaussian-smoothed over +-half_px of arc, eased in from both ends
JAW_FOLLOW=(21,26)      # mm behind the contact: the jaw edge IS the closed-gap curve up to 21 mm, blending into Gen 11's shoulder by 26 (r2; r1 18-24 opened too fast at 19-24 mm)
def to_mm(q):
    a=np.radians(FRAME['deg']);d=np.subtract(q,FRAME['pivot'])
    return FRAME['mm']*np.array([-(d[0]*np.sin(a)-d[1]*np.cos(a)),d[0]*np.cos(a)+d[1]*np.sin(a)])
def to_px(m):
    a=np.radians(FRAME['deg']);X,Z=np.asarray(m)/FRAME['mm']
    return np.array([FRAME['pivot'][0]-X*np.sin(a)+Z*np.cos(a),FRAME['pivot'][1]+X*np.cos(a)+Z*np.sin(a)])
def stretch_z(q):   # Gen 15: photo px -> px with the finger stretched BEAK_STRETCH times along z past the dot
    m=to_mm(q);dz=to_mm(DOT_XY)[1]
    return tuple(to_px((m[0],dz+(m[1]-dz)*(BEAK_STRETCH if m[1]>dz else 1))))
HOOK=[tuple(q) for q in PATCHES[1]]   # the base hook as traced (hook_depth 1)
TIP_PHOTO=NEEDLE['TIP']
def configure(v):
    """2.4: set every outline number from params.json values (params.values()), mm -> photo px."""
    global SMOOTH_SIGMA,KNOB_SWELL_PX,KNOB_BASE_SIGMA,BEAK_STRETCH,RIDGE_PITCH_PX,GROOVE_PX,RIDGE_STOP_PX,RIDGE_MIN_WIDTH_PX,ROUND_BACK
    FRAME.update(pivot=tuple(v['px_pivot']),deg=v['axis_deg'],mm=v['mm_per_px']);px=lambda mm:round(mm/FRAME['mm'],9)   # round: 1.2/0.2 is 5.9999...
    SMOOTH_SIGMA=px(v['outline_smooth']);KNOB_SWELL_PX=px(v['knob_swell']);KNOB_BASE_SIGMA=px(v['knob_ramp_smooth'])
    KNOBS['swells']=[(KNOBS['swells'][0][0],px(v['knob1_halfwidth'])),(KNOBS['swells'][1][0],px(v['knob2_halfwidth']))]
    RAIL.update(p0=tuple(v['rail_p'][0]),p1=tuple(v['rail_p'][1]));TOP_HOOK.update(notch_u=v['top_notch_u'],back=v['top_step_back'])
    BEAK_STRETCH=v['beak_stretch'];ROUND_BACK=v['round_back'];TRIANGLE['p']=v['jaw_open_power']
    OUTER.update(a=v['outer_start_handle'],b=v['outer_end_handle'],bow=v['outer_bow'],out_deg=v['outer_lean_deg'])
    JOIN.update(half_px=px(v['dot_join_span']),sigma=px(v['dot_join_smooth']))
    RIDGE_PITCH_PX=px(v['groove_pitch']);GROOVE_PX=(px(v['groove_width']),px(v['groove_depth']))
    RIDGE_STOP_PX=px(v['groove_stop']);RIDGE_MIN_WIDTH_PX=px(v['groove_min_width']);SLOT_ROW['count']=int(v['slot_count'])
    # hook_depth: each hook point moves away from the chord between the hook's two ends by that factor; the ends stay put
    a,b=np.array(HOOK[0]),np.array(HOOK[-1]);t=(b-a)/np.hypot(*(b-a))
    PATCHES[1]=[tuple(a+t*((np.array(q)-a)@t)+((np.array(q)-a)-t*((np.array(q)-a)@t))*v['hook_depth']) for q in HOOK]
    NEEDLE['TIP']=stretch_z(TIP_PHOTO)
import params as _params
configure(_params.values())
GAP=json.loads((HERE/'closed_trace.json').read_text())['gap_fit']
photo_gap=lambda d:GAP['A']*max(0.0,d)**GAP['P']   # mm apart at d mm behind the point, closed, as measured (trace_closed.py)
def triangle():
    """r3: (H, D) of the closed jaw edge, half-gap H mm at D mm behind the contact (the dot), as closed_jaw() builds it."""
    L,edge=needle_frame();xs=[to_mm(edge(s,-1)) for s in np.linspace(0,L,48)];xc=min(x for x,_ in xs)
    k=np.array([to_mm(q) for q in knobs()]);k=k[k[:,1]>to_mm(DOT_XY)[1]-8];c=k[np.argmax(k[:,0])]   # the crest, within 8 mm of the dot
    return c[0]-xc,xs[-1][1]-ROUND_BACK-c[1]
def closed_gap(d,w=None):
    if w is None:   # r3: the triangle (TRIANGLE); WEDGE (r2) and WEDGE_R1 still describe the older beaks for KEEP_WIDTH and the slots
        H,D=triangle();return 2*H*np.clip(max(0.0,d)/D,0,1)**TRIANGLE['p']   # Gen 14's target: opened sharply at the point, the photo's curve further back
    d=max(0.0,d);w=w or WEDGE;d0=w['cap']/(2*np.tan(np.radians(w['half_deg'])))   # slope 2 tan(4 deg) at the contact
    wedge=w['cap']*np.tanh(d/d0);rear=photo_gap(d)+w['over']*np.tanh(d/d0)
    return (wedge**w['k']+rear**w['k'])**(1/w['k'])


def closed_jaw(n=48,r1=False):
    """Gen 11 r4's beak, made to close the way the photo does. The point moves in to x_c, the innermost
    reach of Gen 11's jaw (both edges blend over the last 45%). The jaw edge follows x_c + g(d)/2 up to
    JAW_FOLLOW[0] mm back, then blends into Gen 11's edge, and never comes inside x_c + g(d)/2, so two
    mirrored fingers touch at the point only. r1: Gen 16 r1's beak (its wedge, no KEEP_WIDTH, no nose). Returns (inner, outer) px."""
    L,edge=needle_frame();ss=np.linspace(0,L,n)
    inner=np.array([to_mm(edge(s,-1)) for s in ss]);outer=np.array([to_mm(edge(s,1)) for s in ss])
    xc=inner[:,0].min();tip=inner[-1];dx=xc-tip[0]
    t=np.clip((ss/L-TIP_SHIFT_FROM)/(1-TIP_SHIFT_FROM),0,1);w=t*t*(3-2*t)
    b=np.clip((tip[1]-ROUND_BACK-inner[:,1]-JAW_FOLLOW[0])/(JAW_FOLLOW[1]-JAW_FOLLOW[0]),0,1);b=b*b*(3-2*b)
    def jaw(wedge):
        want=np.array([xc+closed_gap(tip[1]-ROUND_BACK-z,wedge)/2 for z in inner[:,1]])
        return np.maximum(want,want+(inner[:,0]+dx*w-want)*b)
    if r1:
        x=jaw(WEDGE_R1);outer[:,0]+=dx*w;inner[:,0]=x
        return [to_px(m) for m in inner],[to_px(m) for m in outer]
    H,D=triangle();d=np.clip((tip[1]-ROUND_BACK-inner[:,1])/D,0,1)
    inner[:,0]=xc+H*d**TRIANGLE['p'];outer=straight_outer(outer,inner[-1])
    return [to_px(m) for m in inner],[to_px(m) for m in outer]


def straight_outer(outer,tip):
    """r3: the outer edge from the dot to the point, OUTER's near-straight Bezier. mm in, mm out."""
    p0=outer[0];q=np.radians(OUTER['out_deg']);t0=np.array([np.sin(q),np.cos(q)]);c=tip-p0;L=np.hypot(*c);n=np.array([c[1],-c[0]])/L   # n: outward (+x side)
    p1=p0+t0*OUTER['a']*L;p2=tip-c*OUTER['b']+n*OUTER['bow']*L
    u=np.linspace(0,1,len(outer))[:,None];return (1-u)**3*p0+3*(1-u)**2*u*p1+3*(1-u)*u*u*p2+u**3*tip


def soften(Q,centre):
    """r3: Gaussian-smooth the outline over +-JOIN['half_px'] of arc around the point nearest centre."""
    i=np.argmin(np.hypot(*(Q-np.array(centre)).T));s=np.r_[0,np.cumsum(np.hypot(*np.diff(Q,axis=0).T))]
    a,b=np.searchsorted(s,s[i]-JOIN['half_px']),np.searchsorted(s,s[i]+JOIN['half_px'])
    seg=Q[a:b+1];ss=s[a:b+1]-s[a];t=np.arange(0,ss[-1],1.0);P=np.c_[np.interp(t,ss,seg[:,0]),np.interp(t,ss,seg[:,1])]
    S=np.c_[nd.gaussian_filter1d(P[:,0],JOIN['sigma'],mode='nearest'),nd.gaussian_filter1d(P[:,1],JOIN['sigma'],mode='nearest')]
    r=np.clip(np.minimum(t,t[-1]-t)/(2*JOIN['sigma']),0,1);r=r*r*(3-2*r)
    return np.vstack([Q[:a],P+(S-P)*r[:,None],Q[b+1:]])


def nose(outer,tip):
    """Gen 16 r2: replace the outer edge's last NOSE['mm'] (in z) with a rounded nose into the point. mm in, mm out."""
    i=np.searchsorted(outer[:,1],tip[1]-NOSE['mm']);p0=outer[i-1];t0=outer[i]-outer[i-2];t0/=np.hypot(*t0)
    L=np.hypot(*(tip-p0));p1=p0+t0*NOSE['a']*L;q=np.radians(NOSE['deg']);p2=tip+np.array([np.sin(q),-np.cos(q)])*NOSE['b']*L
    u=np.linspace(0,1,40)[1:,None];b=(1-u)**3*p0+3*(1-u)**2*u*p1+3*(1-u)*u*u*p2+u**3*tip
    return np.vstack([outer[:i],b])


def needle(n=48):
    inner,outer=closed_jaw(n)
    return [tuple(p) for p in inner]+[tuple(p) for p in outer[-2::-1]]


def beak_slots(photo):
    """Gen 15: each photo slot keeps its fraction of the beak's length (stretch_z) and of its width at that point,
    measured inner -> outer edge on Gen 14's beak and placed on the longer one. Keeping x alone left the slots
    hugging the jaw, where the beak is slimmer per mm, and the last one broke through."""
    def edges(tip,r1=False):
        keep=NEEDLE['TIP'];NEEDLE['TIP']=tip
        try:inner,outer=(np.array([to_mm(q) for q in e]) for e in closed_jaw(200,r1))
        finally:NEEDLE['TIP']=keep
        x=lambda e,z:np.interp(z,*(e[np.argsort(e[:,1])][:,::-1].T))
        return lambda z:(x(inner,z),x(outer,z))
    old,new=edges(TIP_PHOTO,True),edges(NEEDLE['TIP']);out=[]   # Gen 16 r2: fractions read on r1's beak, so the wider V moves the slots out with the jaw
    for q in photo:
        m=to_mm(q);a,b=old(m[1]);f=(m[0]-a)/(b-a);z=to_mm(stretch_z(q))[1];a,b=new(z)
        a+=GROOVE_PX[1]*FRAME['mm'];f=0.5   # r3: the triangle's beak is slimmer at the point; centred between groove bottoms and outer edge, or they broke through
        out.append(tuple(to_px((a+f*(b-a),z))))
    return out


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


def rail():
    """1.20: (origin, u, w) of RAIL in mm: u along the outer edge toward the tip, w outboard."""
    p0=np.array(RAIL['p0']);u=np.subtract(RAIL['p1'],p0);u/=np.hypot(*u);return p0,u,np.array([u[1],-u[0]])


def hook_uw():
    """1.20: the base hook's run (PATCHES[1]) in rail (u, w) mm."""
    p0,U,W=rail();M=np.array([to_mm(q)-p0 for q in curve(PATCHES[1])]);return M@U,M@W


def hook_floor_u():
    """1.20: u of the base notch's floor (the bowl's lowest point, before the run climbs the prong); the top's is its mirror."""
    H,Wv=hook_uw();return H[:np.argmax(Wv)].min()


def top_hook(Q):
    """2.6: the straight outer edge on up to the top notch, the base J-hook mirrored end for end round its bowl to the prong's
crest (its notch open toward the base), then one fill from the crest to the outer edge of Q (px) beyond. px out."""
    H,Wv=hook_uw();m=(TOP_HOOK['notch_u']+hook_floor_u())/2;p0,U,W=rail()   # the two floors mirror about m
    i0=np.argmax(H<=TOP_HOOK['from_u']);ic=np.argmax(Wv)   # from the edge, round the bowl and up the prong, to its crest
    uw=[(u,0.0) for u in np.arange(TOP_HOOK['straight_from'],2*m-H[i0],1.0)]+[(2*m-u,w) for u,w in zip(H[i0:ic+1],Wv[i0:ic+1])]
    c=np.array(uw[-1]);M=np.array([to_mm(q)-p0 for q in Q]);qu,qw=M@U,M@W
    ok=np.nonzero((qu>c[0]+1)&(qw>=c[1]-TOP_HOOK['back']))[0]   # the outer edge first back up to the crest (less back): the beak
    j=ok[np.argmin(qu[ok])];J=np.array([qu[j],qw[j]])
    k=j+1 if qu[(j+1)%len(Q)]>qu[j-1] else j-1;t=np.array([qu[k%len(Q)],qw[k%len(Q)]])-J;t/=np.hypot(*t)   # the edge's way on, past J
    L=np.hypot(*(J-c));P=[c,c+(L/2,0),J-t*L/6,J]   # leaves the crest level, meets the edge along it (long/short handles: no sag)
    uw+=[tuple(sum(b*q for b,q in zip(((1-f)**3,3*f*(1-f)**2,3*f*f*(1-f),f**3),P))) for f in np.linspace(0,1,int(L/0.5)+2)[1:]]
    return [tuple(to_px(p0+U*u+W*w)) for u,w in uw]


def trace():
    im=Image.open(PHOTO).convert('RGB');hsv=np.array(im.convert('HSV')).astype(int)
    yel=(hsv[...,0]>=18)&(hsv[...,0]<=40)&(hsv[...,1]>=120)&(hsv[...,2]>=150)
    cut=Image.new('L',im.size,0);ImageDraw.Draw(cut).line(SEAM,fill=255,width=4)
    lab,_=nd.label(yel&(np.array(cut)==0))
    ys,xs=np.nonzero(lab[455:475,540:560])           # a yellow pixel on the bar
    finger=lab==lab[455+ys[0],540+xs[0]]
    filled=nd.binary_fill_holes(nd.binary_closing(finger,iterations=2))
    P=max(plt.contour(nd.gaussian_filter(filled.astype(float),1.6),[0.5]).allsegs[0],key=len)[:-1]
    Q=smooth(resample(P,1.0),SMOOTH_SIGMA)   # Gen 16 (Gen 9): a smooth curve, not Gen 15's RDP polygon
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
    for run in [needle(),knobs()]+[[tuple(p) for p in curve(r)] for r in PATCHES]+[top_hook]:   # 2.6: the top step, fitted to the outline so far
        if callable(run):run=run(Q)
        a,b=(np.argmin(np.hypot(*(Q-np.array(p)).T)) for p in (run[0],run[-1]))
        if a>b:run,a,b=run[::-1],b,a   # Gen 11: a run drawn against the outline's direction used to leave a zero-width spur
        Q=np.vstack([Q[:a],np.array(run,float),Q[b+1:]])
    beak=needle();Q=soften(soften(Q,beak[0]),beak[-1])   # r3: the two joins at the dot
    j=np.argmin(np.hypot(*(Q-np.array(RDP_SPLIT)).T));Q=np.vstack([rdp(Q[:j+1],0.12)[:-1],rdp(np.vstack([Q[j:],Q[:1]]),0.12)[:-1]])   # drop collinear points only
    s=SLOT_ROW;slots=beak_slots([(s['first'][0]+s['step'][0]*i,s['first'][1]+s['step'][1]*i) for i in range(s['count'])])
    return Q,holes,slots


def main(out=HERE/'trace_px.scad',quiet=False):
    """Write trace_px.scad (or out) from the current configure() values."""
    Q,holes,slots=trace()
    dot=max(holes,key=lambda h:h[2])
    s=SLOT_ROW;photo_slots=[(s['first'][0]+s['step'][0]*i,s['first'][1]+s['step'][1]*i) for i in range(PHOTO_SLOTS)]
    holes=[h for h in holes if h is not dot and min(np.hypot(h[0]-x,h[1]-y) for x,y in photo_slots)>6]   # Gen 15: the slot blobs where the photo has them, not where the stretch moved them
    f=lambda l:',\n    '.join(', '.join(f'[{", ".join(f"{v:.2f}" for v in p)}]' for p in l[i:i+6]) for i in range(0,len(l),6))
    tip=tip_px()
    grooves=ridges(Q)
    Path(out).write_text(
        '// GENERATED by trace_photo.py from cad/reference/generalist_gripper_gen6_two_hands.png. Do not edit;\n'
        '// change the hand patches in trace_photo.py and re-run.\n'
        f'outline_px=[\n    {f(Q.tolist())}];\n'
        f'holes_px=[  // [x, y, major, minor, angle] in photo px / image degrees\n    {f(sorted(holes))}];\n'
        f'dot_px=[{dot[0]:.1f}, {dot[1]:.1f}, {DOT_D:.1f}];\n'
        f'slots_px=[\n    {f(slots)}];\n'
        f'tip_px=[{tip[0]:.1f}, {tip[1]:.1f}];\n'
        f'rail_mm=[[{RAIL["p0"][0]}, {RAIL["p0"][1]}], [{RAIL["p1"][0]}, {RAIL["p1"][1]}]];  // 1.20: the straight outer edge\n'
        f'hook_floor_u=[{hook_floor_u():.3f}, {TOP_HOOK["notch_u"]:.3f}];  // 1.20: base and top notch floors along it (2.6: top = top_notch_u)\n'
        f'ridges_px=[  // inner-edge groove stations, outward normal [x, y, nx, ny] px\n    {f(grooves)}];\n')
    if not quiet:print(f'{len(Q)} outline points, {len(holes)} holes, dot d={DOT_D}px, {len(slots)} slots, {len(grooves)} grooves')
if __name__=='__main__':main()
