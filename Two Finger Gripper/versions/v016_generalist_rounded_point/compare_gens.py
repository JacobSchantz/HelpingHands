#!/usr/bin/env python3
"""Gen 9 | Gen 15 | Gen 16 at one scale -> previews/compare_gens.png. Top row: the right finger in plan (the knobs,
hook and blade root); bottom row: edge-on (the taper to the point). Same camera for all three."""
from pathlib import Path
import subprocess, tempfile
from PIL import Image, ImageDraw
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
GENS=[('Gen 9',HERE.parent/'v009_generalist_fingers_sonnet'),('Gen 15',HERE.parent/'v015_generalist_long_jaw'),('Gen 16',HERE)]
VIEWS=[('plan','0,0,62,90,0,180,330',(700,1000)),('edge','0,0,62,90,0,90,330',(700,1000))]


def render(folder,cam,size,out):
    subprocess.run([SCAD,'-D','part="right"','--render','--projection=o',f'--imgsize={size[0]},{size[1]}','--colorscheme=Tomorrow',
                    '--camera='+cam,'-o',str(out),str(folder/'gripper.scad')],check=True,capture_output=True)


def main():
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        for view,cam,size in VIEWS:
            row=[]
            for name,folder in GENS:
                out=Path(tmp)/f'{view}_{folder.name}.png';render(folder,cam,size,out)
                im=Image.open(out).convert('RGB');ImageDraw.Draw(im).text((20,20),f'{name} · {view}',fill=(0,0,0));row.append(im)
            rows.append(row)
    W,H=VIEWS[0][2];sheet=Image.new('RGB',(3*W+20,2*H+10),'white')
    for j,row in enumerate(rows):
        for i,im in enumerate(row):sheet.paste(im,(i*(W+10),j*(H+10)))
    sheet.save(HERE/'previews/compare_gens.png');print(HERE/'previews/compare_gens.png')
if __name__=='__main__':main()
