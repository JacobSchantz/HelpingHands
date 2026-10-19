#!/usr/bin/env python3
"""Draw the exported right finger back into the two-hands photo's own pixel frame, so photo
and model can be compared at the same scale and pose: photo | model | 50% blend.
Writes previews/photo_match.png. Run after export_models.py."""
from pathlib import Path
import math, re, struct, sys
from PIL import Image, ImageDraw
HERE=Path(__file__).resolve().parent
PHOTO=HERE.parents[2]/'cad/reference/generalist_gripper_gen6_two_hands.png'
BOX=(290,300,880,640);K=2


def frame(scad=HERE/'gripper.scad'):
    s=Path(scad).read_text()
    num=lambda n:float(re.search(n+r'=([-\d.]+);',s).group(1))
    piv=[float(v) for v in re.search(r'px_pivot=\[([-\d.]+),([-\d.]+)\]',s).groups()]
    return num('mm_per_px'),piv,math.radians(num('axis_deg'))


def to_px(X,Z,mm,piv,a):
    # inverse of px() in gripper.scad
    return piv[0]+(-X*math.sin(a)+Z*math.cos(a))/mm, piv[1]+(X*math.cos(a)+Z*math.sin(a))/mm


def render(stl,out_size,scad=HERE/'gripper.scad'):
    mm,piv,a=frame(scad);raw=stl.read_bytes();n=struct.unpack_from('<I',raw,80)[0]
    img=Image.new('RGBA',out_size,(0,0,0,0));d=ImageDraw.Draw(img);tris=[]
    for i in range(n):
        q=struct.unpack_from('<12f',raw,84+i*50);nrm=q[:3];v=[q[3:6],q[6:9],q[9:12]]
        tris.append((sum(p[1] for p in v)/3,nrm,v))
    for y,nrm,v in sorted(tris):              # far (−Y, palm side) first; the photo shows the dorsal +Y face
        if nrm[1]>0.9: col=(239,184,59,255)
        elif nrm[1]<-0.9: continue
        else:
            sh=0.45+0.35*max(0,(nrm[0]-nrm[2])/1.5);col=tuple(int(c*sh) for c in (239,184,59))+(255,)
        P=[to_px(p[0],p[2],mm,piv,a) for p in v]
        d.polygon([((x-BOX[0])*K,(yy-BOX[1])*K) for x,yy in P],fill=col)
    return img


def main(out=HERE/'previews/photo_match.png'):
    photo=Image.open(PHOTO).convert('RGB').crop(BOX);photo=photo.resize((photo.width*K,photo.height*K))
    model=render(HERE/'exports/print/right.stl',photo.size)
    flat=Image.new('RGB',photo.size,(245,245,245));flat.paste(model,(0,0),model)
    blend=Image.blend(photo,flat,0.5)
    sheet=Image.new('RGB',(photo.width*3+20,photo.height),'white')
    for i,t in enumerate((photo,flat,blend)):sheet.paste(t,(i*(photo.width+10),0))
    sheet.save(out);print(out)
if __name__=='__main__':main(*(Path(p) for p in sys.argv[1:]))
