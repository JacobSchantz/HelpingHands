#!/usr/bin/env python3
"""Generate CAD assets only. Does not build, install, or deploy the app."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
SCAD = os.environ.get('OPENSCAD', '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD')
SOURCE = ROOT / 'demo_gripper.scad'

def run(output, *args):
    result = subprocess.run([SCAD, '-o', str(output), *args, str(SOURCE)], capture_output=True, text=True)
    if result.returncode or 'WARNING:' in result.stderr or 'ERROR:' in result.stderr:
        raise RuntimeError(result.stderr)
    return result.stderr

def main():
    for directory in ('export', 'render'):
        (ROOT / directory).mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='demo-gripper-') as tmp:
        tmp = Path(tmp)
        run(tmp / 'parts.echo', '-D', 'part="parts"')
        rows = [json.loads(line.removeprefix('ECHO: '))
                for line in (tmp / 'parts.echo').read_text().splitlines() if line.startswith('ECHO: [')]
        manifest = {'parts': [dict(file=q+'.stl', name=name, color=color, explode=explode)
                              for q, name, color, explode in rows]}
        def mesh(row):
            q = row[0]
            run(ROOT / 'export' / (q+'.stl'), '--export-format', 'binstl', '-D', f'part="{q}"')
            if q.startswith(('a_', 'b_')):
                run(tmp / (q+'.stl'), '--export-format', 'binstl', '-D', f'part="{q}"', '-D', 'print_pose=true')
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(mesh, rows))
        (ROOT / 'export' / 'parts.json').write_text(json.dumps(manifest, indent=2)+'\n')
        with zipfile.ZipFile(ROOT / 'jaws_print_ready.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for p in sorted(tmp.glob('*.stl')):
                info = zipfile.ZipInfo(p.name, (2026,10,14,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, p.read_bytes())
    for name, part, variant, camera in [
        ('assembled','assembly','A','0,0,0,65,0,30,0'),
        ('exploded','exploded','A','0,0,0,65,0,30,0'),
        ('in_hand','in_hand','A','0,0,0,70,0,215,0'),
        ('crow_in_hand','in_hand','B','0,0,0,70,0,215,0'),
        ('crow_on_arm','on_arm','B','0,0,0,65,0,30,0'),
    ]:
        run(ROOT/'render'/(name+'.png'), '--render', '-D', f'part="{part}"', '-D', f'variant="{variant}"',
            '--viewall','--autocenter','--imgsize=1400,1050','--colorscheme=Tomorrow', '--camera='+camera)
    print('Exported 7 distinct pieces, four bed-oriented jaws in ZIP, and five renders.')

if __name__ == '__main__':
    main()
