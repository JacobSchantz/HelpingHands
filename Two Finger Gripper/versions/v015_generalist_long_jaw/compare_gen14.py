#!/usr/bin/env python3
"""Gen 14 | Gen 15, closed, same camera and scale -> previews/compare_gen14.png. A line marks each one's black dot,
where the beak begins, and the label gives dot -> point as a share of the finger."""
from pathlib import Path
import subprocess, tempfile
from PIL import Image, ImageDraw
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
GENS=[('Gen 14',HERE.parent/'v014_generalist_tip_contact'),('Gen 15',HERE)]
CAM='0,0,62,90,0,180,330'   # straight onto the hand plane (dorsal), tips up
W,H=900,1300


def render(folder,out):
    subprocess.run([SCAD,'-D','angle=0','--render','--projection=o',f'--imgsize={W},{H}','--colorscheme=Tomorrow',
                    '--camera='+CAM,'-o',str(out),str(folder/'gripper.scad')],check=True,capture_output=True)


def share(folder):
    import importlib.util, sys
    spec=importlib.util.spec_from_file_location(f'tp_{folder.name}',folder/'trace_photo.py');tp=importlib.util.module_from_spec(spec)
    sys.path.insert(0,str(folder));spec.loader.exec_module(tp);sys.path.pop(0)
    dot=tp.to_mm(tp.DOT_XY)[1];tip=tp.to_mm(tp.tip_px())[1];base=-2.454   # the root's lowest point, unchanged since Gen 11
    return dot,tip,(tip-dot)/(tip-base)


def main():
    tiles=[]
    with tempfile.TemporaryDirectory() as tmp:
        for name,folder in GENS:
            out=Path(tmp)/f'{folder.name}.png';render(folder,out);im=Image.open(out).convert('RGB')
            dot,tip,f=share(folder);d=ImageDraw.Draw(im);k=H/(330*2*0.19891)   # px per mm: an ortho view is distance * 2 tan(22.5/2 deg) high
            y=lambda z:H/2-(z-62)*k
            for z,c in ((dot,(200,30,30)),(tip,(30,30,200))):d.line([(0,y(z)),(W,y(z))],fill=c,width=2)
            d.text((20,20),f'{name}: dot -> point {tip-dot:.1f} mm = {f:.0%} of the finger',fill=(0,0,0))
            tiles.append(im)
    sheet=Image.new('RGB',(W*2+10,H),'white');sheet.paste(tiles[0],(0,0));sheet.paste(tiles[1],(W+10,0))
    sheet.save(HERE/'previews/compare_gen14.png');print(HERE/'previews/compare_gen14.png')
if __name__=='__main__':main()
