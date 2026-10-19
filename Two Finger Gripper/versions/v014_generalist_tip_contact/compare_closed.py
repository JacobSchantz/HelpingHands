#!/usr/bin/env python3
"""The Gen 14 review sheet against the CLOSED photo: the photo's fingers | the model closed (top.png)
| Gen 13's points | Gen 14's points (same camera) | the closed gap: photo, Gen 13, Gen 14 target and model.
Writes previews/compare_closed.png. Run after export_models.py and check_geometry.py."""
from pathlib import Path
import json, subprocess
from PIL import Image, ImageDraw, ImageFont
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
GEN13=HERE.parent/'v013_generalist_closed_beak'
PHOTO=HERE.parents[2]/'cad/reference/generalist_gripper_gen6_closed.png'
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
H=620


def rows(folder):
    return next(r for r in json.loads((folder/'geometry_checks.json').read_text())['results'] if 'rows' in r)['rows']


def gap_plot(path):
    t=json.loads((HERE/'closed_trace.json').read_text());g14=rows(HERE);g13=rows(GEN13)
    fig,ax=plt.subplots(figsize=(4.4,H/150),dpi=150)
    ax.plot([r['d_mm'] for r in t['seam']],[r['gap_mm'] for r in t['seam']],'o',ms=3,color='#c0308a',label='closed photo (seam)')
    ax.plot([r['d_mm'] for r in g13],[r['model_gap'] for r in g13],'--',color='#888888',label='Gen 13 model')
    ax.plot([r['d_mm'] for r in g14],[r['target_gap'] for r in g14],':',color='#1d1f22',label='Gen 14 target (photo + 4° wedge)')
    ax.plot([r['d_mm'] for r in g14],[r['model_gap'] for r in g14],'-s',ms=3,color='#b07a00',label='Gen 14 model')
    ax.set_xlim(0,24);ax.set_ylim(0,3);ax.set_xlabel('mm behind the point');ax.set_ylabel('closed gap, mm')
    ax.set_title('Closed: only the points touch',fontsize=9);ax.grid(alpha=.3);ax.legend(fontsize=6.5)
    fig.tight_layout();fig.savefig(path);plt.close(fig)


def tip(folder,out):   # plan view of the last ~14 mm, closed, the same camera for both gens
    subprocess.run([SCAD,'-D','angle=0','--render','--projection=o','--imgsize=600,900','--colorscheme=Tomorrow',
                    '--camera=0,0,101,90,0,0,34','-o',str(out),str(folder/'gripper.scad')],capture_output=True,check=True)
    im=Image.open(out).convert('RGB').rotate(180);d=ImageDraw.Draw(im)
    d.text((16,16),folder.name.split('_')[0].replace('v0','Gen '),fill=(0,0,0),font=ImageFont.load_default(size=40))
    return im


def main():
    tmp=HERE/'previews/_gap.png';gap_plot(tmp)
    photo=Image.open(PHOTO).convert('RGB').crop((95,190,235,345))
    tiles=[photo,Image.open(HERE/'previews/top.png').rotate(180),   # tips down, as in the photo
           tip(GEN13,HERE/'previews/_t13.png'),tip(HERE,HERE/'previews/_t14.png'),Image.open(tmp)]
    tiles=[t.convert('RGB') for t in tiles];tiles=[t.resize((round(t.width*H/t.height),H),Image.LANCZOS) for t in tiles]
    out=Image.new('RGB',(sum(t.width for t in tiles)+10*(len(tiles)-1),H),'white');x=0
    for t in tiles:out.paste(t,(x,0));x+=t.width+10
    out.save(HERE/'previews/compare_closed.png')
    for n in ('_gap','_t13','_t14'):(HERE/f'previews/{n}.png').unlink()
    print(HERE/'previews/compare_closed.png')
if __name__=='__main__':main()
