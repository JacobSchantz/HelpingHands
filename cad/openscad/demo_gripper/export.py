#!/usr/bin/env python3
"""Generate CAD assets only. Does not build, install, or deploy the app.

Every gen_NN_<label>.scad in this folder is one generation of the gripper.
Each is exported into export/ with its pieces prefixed gen_NN_, and one
export/parts.json lists them all, grouped by generation, so the app lines the
generations up side by side. Generations are never edited once a newer one
exists: copy the newest file to the next number and change the copy.
"""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
SCAD = os.environ.get('OPENSCAD', '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD')

def generations():
    return sorted(ROOT.glob('gen_[0-9][0-9]_*.scad'))

def tag(source):
    return source.stem[:6]

def label(source):
    """A '// label: ...' line in the file, else the file name after gen_NN_."""
    for line in source.read_text().splitlines()[:20]:
        if line.startswith('// label:'):
            return tag(source) + ' · ' + line.removeprefix('// label:').strip()
    return tag(source) + ' · ' + source.stem[7:].replace('_', ' ')

def run(source, output, *args):
    result = subprocess.run([SCAD, '-o', str(output), *args, str(source)], capture_output=True, text=True)
    if result.returncode or 'WARNING:' in result.stderr or 'ERROR:' in result.stderr:
        raise RuntimeError(f'{source.name}: {result.stderr}')
    return result.stderr

def rows(source, tmp):
    """[piece, name, colour, explode, material, bed]. gen_00 predates the last
    two columns: its jaws were PLA and are the bed-oriented prints."""
    echo = Path(tmp) / (source.stem + '.echo')
    run(source, echo, '-D', 'part="parts"')
    out = []
    for line in echo.read_text().splitlines():
        if line.startswith('ECHO: ['):
            r = json.loads(line.removeprefix('ECHO: '))
            if len(r) == 4:
                r += ['PLA', r[0].startswith(('a_', 'b_'))]
            out.append(r)
    return out

def renders(pieces):
    shots = [('assembled', 'assembly', 'A', '0,0,0,65,0,30,0'),
             ('exploded', 'exploded', 'A', '0,0,0,65,0,30,0'),
             ('in_hand', 'in_hand', 'A', '0,0,0,70,0,215,0')]
    if any(r[0] == 'b_left' for r in pieces):
        shots += [('crow_in_hand', 'in_hand', 'B', '0,0,0,70,0,215,0'),
                  ('crow_on_arm', 'on_arm', 'B', '0,0,0,65,0,30,0')]
    else:
        shots += [('on_arm', 'on_arm', 'A', '0,0,0,65,0,30,0')]
    return shots

def lineup(images, out):
    """One picture of every generation's in-hand render, labelled, left to right."""
    from PIL import Image, ImageDraw, ImageFont
    tiles = [Image.open(p).convert('RGB') for _, p in images]
    w, h = tiles[0].size
    sheet = Image.new('RGB', (w * len(tiles), h + 90), 'white')
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 54)
    except OSError:
        font = ImageFont.load_default()
    for i, ((text, _), tile) in enumerate(zip(images, tiles)):
        sheet.paste(tile, (i * w, 90))
        draw.text((i * w + 40, 20), text, fill='black', font=font)
    sheet.save(out)

def main():
    for directory in ('export', 'render'):
        (ROOT / directory).mkdir(exist_ok=True)
    written = set()
    parts, groups, in_hand = [], [], []
    with tempfile.TemporaryDirectory(prefix='demo-gripper-') as tmp:
        tmp = Path(tmp)
        for index, source in enumerate(generations()):
            g = tag(source)
            pieces = rows(source, tmp)
            groups.append({'id': g, 'label': label(source), 'source': source.name})
            parts += [dict(file=f'{g}_{q}.stl', name=name, color=color, explode=explode,
                           material=material, group=index)
                      for q, name, color, explode, material, _ in pieces]
            bed = tmp / g
            bed.mkdir()
            def mesh(row):
                q, printed = row[0], row[5]
                run(source, ROOT / 'export' / f'{g}_{q}.stl', '--export-format', 'binstl', '-D', f'part="{q}"')
                if printed:
                    run(source, bed / f'{g}_{q}.stl', '--export-format', 'binstl',
                        '-D', f'part="{q}"', '-D', 'print_pose=true')
            def shot(s):
                name, part, variant, camera = s
                out = ROOT / 'render' / f'{g}_{name}.png'
                run(source, out, '--render', '-D', f'part="{part}"', '-D', f'variant="{variant}"',
                    '--viewall', '--autocenter', '--imgsize=1400,1050', '--colorscheme=Tomorrow',
                    '--camera=' + camera)
                return out
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(mesh, pieces))
                shots = list(pool.map(shot, renders(pieces)))
            written |= {f'{g}_{r[0]}.stl' for r in pieces} | {p.name for p in shots}
            in_hand.append((label(source), ROOT / 'render' / f'{g}_in_hand.png'))
            with zipfile.ZipFile(ROOT / f'{g}_print_ready.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
                for p in sorted(bed.glob('*.stl')):
                    info = zipfile.ZipInfo(p.name, (2026, 10, 16, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, p.read_bytes())
    lineup(in_hand, ROOT / 'render' / 'generations.png')
    written |= {'generations.png', 'parts.json'}
    (ROOT / 'export' / 'parts.json').write_text(
        json.dumps({'generations': groups, 'parts': parts}, indent=2) + '\n')
    # Drop exports and renders left over from a renamed or older layout.
    for directory in ('export', 'render'):
        for stale in (ROOT / directory).iterdir():
            # compare_gen_NN.png is render_compare's (web vs STL), not ours.
            if stale.suffix in ('.stl', '.png', '.json') and stale.name not in written \
                    and not stale.name.startswith('compare_'):
                stale.unlink()
    print(f'Exported {len(groups)} generations, {len(parts)} pieces.')

if __name__ == '__main__':
    main()
