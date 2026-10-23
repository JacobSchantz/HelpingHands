from pathlib import Path
import json,subprocess
from concurrent.futures import ThreadPoolExecutor
import params
HERE=Path(__file__).resolve().parent
SCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
PARTS=[('left','Left finger — miniature tweezer — Gripper 23, integral 20-tooth gear','#e7b842'),
('right','Right finger — miniature tweezer — Gripper 23, integral 20-tooth gear','#e7b842'),
('base','Base 16 — narrow servo frame and captured follower axle','#353e48'),
('cap','Base 16 cap — supports both gear axes','#697581'),
('coupler','Left drive coupler — 4 M3 into stock servo horn','#cc8e32'),
('horn_heads','Left horn screws — four M3 countersunk, head envelope','#999999'),
('case_heads','Case screws — four M2 head envelopes','#999999'),
('cap_heads','Cap screws — two M2 head envelopes','#999999'),
('cable','Cable plug and bend — keep-out, not printed','#586b64'),
('motor','STS3215 servo envelope — reference only, not printed','#353535')]
def export(part,angle,out):
    run=subprocess.run([SCAD,'--export-format','binstl','-D',f'part="{part}"','-D',f'angle={angle}','-o',str(out),str(HERE/'gripper.scad')],capture_output=True,text=True)
    if run.returncode and 'top level object is empty' not in run.stderr:raise RuntimeError(run.stderr)
    return run
def main():
    params.write_scad()
    folder=HERE/'exports/parts';folder.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(lambda p:export(p[0],0,folder/(p[0]+'.stl')),PARTS))
    (HERE/'viewer_parts.json').write_text(json.dumps({'no_handles':True,'parts':[dict(path=f'exports/parts/{key}.stl',name=name,color=color,explode=[0,-10*i,0]) for i,(key,name,color) in enumerate(PARTS)]},indent=2)+'\n')
    export('assembly',0,HERE/'exports/assembly.stl')
    prints=HERE/'exports/print';prints.mkdir(exist_ok=True)
    for key in ('left','right','base','cap','coupler'):export('print_'+key,0,prints/(key+'.stl'))
    folder=HERE/'previews';folder.mkdir(exist_ok=True)
    for name,a in [('closed',0),('open',9)]:
        subprocess.run([SCAD,'--imgsize=1400,1100','--viewall','--autocenter','--projection=o',
            '--camera=0,0,0,65,0,20,180','-D',f'angle={a}','-o',str(folder/(name+'.png')),str(HERE/'gripper.scad')],check=True,capture_output=True)
if __name__=='__main__':main()
