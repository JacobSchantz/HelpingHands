#!/usr/bin/env python3
"""The Gen 13 review sheet against the CLOSED photo: the photo's fingers | the model closed (top.png)
| the points up close (closed.png) | the closed gap, photo vs model. Writes previews/compare_closed.png.
Run after export_models.py and check_geometry.py."""
from pathlib import Path
import json
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
PHOTO=HERE.parents[2]/'cad/reference/generalist_gripper_gen6_closed.png'
H=620


def gap_plot(path):
    gp=next(r for r in json.loads((HERE/'geometry_checks.json').read_text())['results'] if 'rows' in r)
    t=json.loads((HERE/'closed_trace.json').read_text())
    fig,ax=plt.subplots(figsize=(4.4,H/150),dpi=150)
    ax.plot([r['d_mm'] for r in t['seam']],[r['gap_mm'] for r in t['seam']],'o',ms=3,color='#c0308a',label='closed photo (seam)')
    ax.plot([r['d_mm'] for r in gp['rows']],[r['model_gap'] for r in gp['rows']],'-s',ms=3,color='#b07a00',label='Gen 13 model')
    ax.set_xlim(0,24);ax.set_ylim(0,3);ax.set_xlabel('mm behind the point');ax.set_ylabel('closed gap, mm')
    ax.set_title('Closed: they touch at the point only',fontsize=9);ax.grid(alpha=.3);ax.legend(fontsize=7)
    fig.tight_layout();fig.savefig(path);plt.close(fig)


def main():
    tmp=HERE/'previews/_gap.png';gap_plot(tmp)
    photo=Image.open(PHOTO).convert('RGB').crop((95,190,235,345))
    tiles=[photo,*(Image.open(HERE/'previews'/n).rotate(180) for n in ('top.png','closed.png')),Image.open(tmp)]   # tips down, as in the photo
    tiles=[t.convert('RGB') for t in tiles];tiles=[t.resize((round(t.width*H/t.height),H),Image.LANCZOS) for t in tiles]
    out=Image.new('RGB',(sum(t.width for t in tiles)+10*(len(tiles)-1),H),'white');x=0
    for t in tiles:out.paste(t,(x,0));x+=t.width+10
    out.save(HERE/'previews/compare_closed.png');tmp.unlink();print(HERE/'previews/compare_closed.png')
if __name__=='__main__':main()
