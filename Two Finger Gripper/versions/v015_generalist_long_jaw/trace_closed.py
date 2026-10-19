#!/usr/bin/env python3
"""Gen 13 starts here: trace the two CLOSED fingers in cad/reference/generalist_gripper_gen6_closed.png
(Jake: "design it from a closed position first ... how it contacts is key").

  * outline: both yellow fingers by colour (they merge where the jaws meet, so it is one silhouette);
  * seam: the dark line between the two jaws, row by row. Where it is narrower than a pixel the photo
    still shows how dark it is, so its width is read from that: width = sum(max(0, FACE - v)) / (FACE - GAP),
    FACE the grey level of the right jaw's side face beside the seam, GAP the level of a wide-open gap;
  * contact: the point where the seam disappears, at the beaks.

The closed gap g(d), d = mm behind the contact point, is fitted as g = A d^P and written to
closed_trace.json, which trace_photo.py reads to shape the jaw edge. closed_sketch.png is the sketch:
the photo with the trace drawn on it, and the gap curve.

Scale: the photo is a perspective view, so it gets two scales from Gen 11's own geometry: across the
jaws, the two black dots' spacing (16.9 mm closed); along them, dot to point (24.8 mm). Both are
estimates; no part was measured.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
PHOTO=HERE.parents[2]/'cad/reference/generalist_gripper_gen6_closed.png'
DOTS=((161.0,285.0),(196.0,286.0))   # the two black dots (photo px, read on a 11x grid)
CONTACT=(184.5,327.0)                 # where the seam ends: the two beaks meet (the grey nubs sit just past it)
SEAM_ROWS=(288,323)                   # above 288 the seam opens into the shoulder gap; below 323 it is gone
SEAM_X=(166,192)                      # search window for the seam in each row
FACE,GAP=120,10                       # grey levels: the right jaw's side face, and the open gap (row 282)
DOT_SPACING_MM,DOT_TO_TIP_MM=16.9,24.8   # Gen 11 closed: 2*(27.67-19.23) and 106.9-82.1
BOX=(95,190,235,345)                  # sketch crop
K=6


def seam():
    g=np.array(Image.open(PHOTO).convert('L')).astype(float)
    rows=[];x=None
    for y in range(*SEAM_ROWS):   # follow the seam down: each row looks within 3 px of the last one
        a,b=SEAM_X if x is None else (x-3,x+4)
        r=g[y,a:b];x=a+int(r.argmin());row=g[y]
        w=float(np.clip(FACE-row[x-5:x+6],0,None).sum()/(FACE-GAP))
        rows.append(dict(y=y,x=x,width_px=round(w,3)))
    return rows


def outline():
    hsv=np.array(Image.open(PHOTO).convert('HSV')).astype(int)
    yel=(hsv[...,0]>=18)&(hsv[...,0]<=45)&(hsv[...,1]>=100)&(hsv[...,2]>=120)
    lab,n=nd.label(yel);big=1+int(np.argmax(nd.sum(yel,lab,range(1,n+1))))
    filled=nd.binary_fill_holes(nd.binary_closing(lab==big,iterations=2))
    P=max(plt.contour(nd.gaussian_filter(filled.astype(float),1.0),[0.5]).allsegs[0],key=len);plt.close('all')
    return P


def main():
    across=DOT_SPACING_MM/np.hypot(*np.subtract(*DOTS))
    mid=np.mean(DOTS,axis=0);along=DOT_TO_TIP_MM/np.hypot(*(np.array(CONTACT)-mid))
    rows=seam()
    for r in rows:r.update(d_mm=round((CONTACT[1]-r['y'])*along,2),gap_mm=round(r['width_px']*across,3))
    fit=[(r['d_mm'],r['gap_mm']) for r in rows if r['gap_mm']>0.02 and r['d_mm']<22]
    P,lnA=np.polyfit(np.log([d for d,_ in fit]),np.log([g for _,g in fit]),1);A=float(np.exp(lnA))
    out=dict(photo=str(PHOTO.relative_to(HERE.parents[2])),contact_px=CONTACT,dots_px=DOTS,
             mm_per_px=dict(across=round(across,4),along=round(along,4)),
             gap_fit=dict(A=round(A,7),P=round(float(P),3),formula='gap_mm = A * d_mm^P, d = mm behind the contact point'),
             seam=rows,outline_px=[[round(float(x),1),round(float(y),1)] for x,y in outline()[::3]])
    (HERE/'closed_trace.json').write_text(json.dumps(out,indent=1)+'\n')

    # the sketch: photo + trace, and the gap curve beside it
    im=Image.open(PHOTO).convert('RGB').crop(BOX);im=im.resize((im.width*K,im.height*K),Image.LANCZOS)
    d=ImageDraw.Draw(im);font=ImageFont.load_default(size=17);X=lambda x:(x-BOX[0])*K;Y=lambda y:(y-BOX[1])*K
    ol=[(X(x),Y(y)) for x,y in out['outline_px']];d.line(ol+ol[:1],fill=(0,200,255),width=3)
    sm=[(X(r['x']+0.5),Y(r['y']+0.5)) for r in rows];d.line(sm,fill=(255,0,200),width=3)
    for r in rows[::5]:
        half=max(1.5,r['width_px']*K/2);cx,cy=X(r['x']+0.5),Y(r['y']+0.5)
        d.line([(cx-half-14,cy),(cx-half,cy)],fill=(255,0,200),width=2);d.line([(cx+half,cy),(cx+half+14,cy)],fill=(255,0,200),width=2)
        d.text((cx+half+18,cy-6),f"{r['gap_mm']:.2f} mm gap, {r['d_mm']:.0f} mm back",fill=(255,255,255),font=font)
    cx,cy=X(CONTACT[0]),Y(CONTACT[1]);d.ellipse([cx-9,cy-9,cx+9,cy+9],outline=(0,255,0),width=3)
    d.text((cx+14,cy+4),'contact: the beaks meet here only',fill=(0,255,0),font=font)
    for x,y in DOTS:d.ellipse([X(x)-7,Y(y)-7,X(x)+7,Y(y)+7],outline=(255,255,0),width=2)
    fig,ax=plt.subplots(figsize=(4.2,im.height/150),dpi=150)
    dd=[r['d_mm'] for r in rows];ax.plot(dd,[r['gap_mm'] for r in rows],'o',ms=3,color='#c0308a',label='photo seam')
    s=np.linspace(0,26,100);ax.plot(s,A*s**P,'-',color='#1d1f22',label=f'fit {A:.2e}·d^{P:.2f}')
    ax.set_xlabel('mm behind the contact point');ax.set_ylabel('closed gap, mm');ax.set_title('Closed jaw gap (Gen 13 target)',fontsize=9)
    ax.legend(fontsize=7);ax.grid(alpha=.3);fig.tight_layout();fig.savefig(HERE/'previews/_gap.png');plt.close(fig)
    plot=Image.open(HERE/'previews/_gap.png').convert('RGB');(HERE/'previews/_gap.png').unlink()
    sheet=Image.new('RGB',(im.width+plot.width+10,max(im.height,plot.height)),'white');sheet.paste(im,(0,0));sheet.paste(plot,(im.width+10,0))
    sheet.save(HERE/'closed_sketch.png')
    print(f'gap = {A:.3g} d^{P:.2f}; mm/px across {across:.3f}, along {along:.3f}; {len(rows)} seam rows')
if __name__=='__main__':
    (HERE/'previews').mkdir(exist_ok=True);main()
