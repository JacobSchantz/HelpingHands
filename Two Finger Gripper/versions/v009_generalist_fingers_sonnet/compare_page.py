#!/usr/bin/env python3
"""Build compare.html: every build-review round of the Gen 9 finger beside the Generalist
photos. One self-contained page (photos and STLs inlined) so it can be opened anywhere.

Per round folder (rounds/<name>/): gripper.scad, right.stl, round.json
  {"title", "changes": [...], "score", "verdict", "review": [...]}
"""
from pathlib import Path
import base64, io, json, subprocess
from PIL import Image
from photo_match import BOX, K, PHOTO, render
HERE=Path(__file__).resolve().parent
REF=HERE.parents[2]/'cad/reference'
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'


def data_url(img,fmt='JPEG',q=82):
    b=io.BytesIO();img.save(b,fmt,**({'quality':q} if fmt=='JPEG' else {'optimize':True}))
    return f'data:image/{fmt.lower()};base64,'+base64.b64encode(b.getvalue()).decode()


def photos():
    crop=Image.open(PHOTO).convert('RGB').crop(BOX);crop=crop.resize((crop.width*K,crop.height*K))
    out=dict(two_hands=data_url(crop))
    for n in ('robot','side','top','closed'):out[n]=data_url(Image.open(REF/f'generalist_gripper_gen6_{n}.png').convert('RGB'))
    return out,crop.size


def rounds(size):
    rows=[]
    for d in sorted(p for p in (HERE/'rounds').iterdir() if (p/'round.json').is_file()):
        meta=json.loads((d/'round.json').read_text())
        if not (d/'right.stl').is_file():   # STLs are gitignored; rebuild from the round's own source
            subprocess.run([SCAD,'--export-format','binstl','-D','part="right"','-o',str(d/'right.stl'),str(d/'gripper.scad')],check=True,capture_output=True)
        model=render(d/'right.stl',size,d/'gripper.scad')
        rows.append(dict(meta,id=d.name,overlay=data_url(model,'PNG'),
                         stl=base64.b64encode((d/'right.stl').read_bytes()).decode()))
    return rows


def main():
    ph,size=photos();rs=rounds(size)
    page=(HERE/'compare_template.html').read_text()
    page=page.replace('/*DATA*/null',json.dumps(dict(photos=ph,rounds=rs,size=size)))
    (HERE/'compare.html').write_text(page)
    print(f'compare.html: {len(rs)} rounds, {len(page)//1024} KB')
if __name__=='__main__':main()
