#!/usr/bin/env python3
"""Every comparable 3D design in the repo, by name. Does not build the app.

A design is one generation file, cad/openscad/<family>/gen_NN_<label>.scad.
Its printable truth is the STLs that file exports (export/gen_NN_*.stl, or
export/<stem>.stl for a one-piece design); its vision is the three.js concept
scene beside it, <family>/web/gen_NN.js. render_compare, design.sh, the viewer
and the Mac app all read the list this writes to cad/compare/designs.json, so
a new gen_NN file shows up everywhere without registering it.

    designs.py                 rewrite designs.json, print the ids
    designs.py --json          print the list as JSON
    designs.py --match <name>  the best design for a spoken name ("gripper",
                               "glove hand"), as JSON; exit 1 when none fits
    designs.py --export <id>   re-export that design's STLs with OpenSCAD
"""
import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
OPENSCAD_DIR = REPO / 'cad' / 'openscad'
OUT = REPO / 'cad' / 'compare' / 'designs.json'
SCAD = os.environ.get('OPENSCAD', '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD')
GREY = '#9aa6b8'


def heading(folder):
    """"Robot Glove Hand" out of the README's '# Robot Glove Hand · generations'."""
    readme = folder / 'README.md'
    if readme.exists():
        for line in readme.read_text().splitlines():
            if line.startswith('# '):
                return re.split(r'\s+[·—-]\s+', line[2:].strip())[0]
    return folder.name.replace('_', ' ').capitalize()


def label(source):
    for line in source.read_text().splitlines()[:20]:
        if line.startswith('// label:'):
            return line.removeprefix('// label:').strip()
    return source.stem[7:].replace('_', ' ')


def pieces(folder, source, group):
    """[{file, name, color, explode}] for one generation, assembled position."""
    g = source.stem[:6]
    export = folder / 'export'
    listed = []
    parts_json = export / 'parts.json'
    if parts_json.exists():
        rows = json.loads(parts_json.read_text())
        groups = [x['source'] for x in rows.get('generations', [])]
        index = groups.index(source.name) if source.name in groups else group
        listed = [dict(file=p['file'], name=p['name'], color=p.get('color', GREY),
                       explode=p.get('explode', [0, 0, 0]))
                  for p in rows['parts'] if p.get('group', 0) == index and p['file'].startswith(g)]
    known = {p['file'] for p in listed}
    extra = sorted(p.name for p in export.glob(f'{g}_*.stl') if p.name not in known) if export.is_dir() else []
    listed += [dict(file=f, name=f[7:-4].replace('_', ' '), color=GREY, explode=[0, 0, 0]) for f in extra]
    return [dict(p, path=str((export / p['file']).relative_to(REPO))) for p in listed]


def claimed_pebbles():
    """Pebbles an agent is working on right now: agent/ items with working_on."""
    out = []
    for path in sorted((REPO / 'pebbles' / 'agent').glob('*/pebble.json')):
        try:
            item = json.loads(path.read_text())
        except ValueError:
            continue
        if item.get('working_on'):
            text = ' '.join(str(item.get(k) or '') for k in ('description', 'summary'))
            out.append({'id': item['id'], 'summary': item.get('summary') or item.get('description', '')[:160],
                        'text': text.lower()})
    return out


def working_on(folder, source, newest, claimed):
    """The claimed pebbles about this generation: its pebble id is in the
    design's files, or the pebble names the family ("gripper", "glove hand")
    and this is the newest generation, or names this gen_NN outright."""
    g = source.stem[:6]
    concept = folder / 'web' / f'{g}.js'
    own = source.read_text(errors='ignore') + (concept.read_text(errors='ignore') if concept.exists() else '')
    family = ' '.join(p.read_text(errors='ignore') for p in folder.glob('*') if p.suffix in ('.scad', '.md'))
    phrase = ' '.join(w for w in folder.name.split('_') if w not in ('demo', 'robot'))
    hits = []
    for p in claimed:
        named = phrase in p['text'] or folder.name.replace('_', ' ') in p['text']
        if p['id'] in own or newest and p['id'] in family or named and (newest or g in p['text'] or g.replace('_', ' ') in p['text']):
            hits.append({'id': p['id'], 'summary': p['summary']})
    return hits


def discover():
    found = []
    claimed = claimed_pebbles()
    for folder in sorted(p for p in OPENSCAD_DIR.iterdir() if p.is_dir()):
        sources = sorted(folder.glob('gen_[0-9][0-9]_*.scad'))
        family = heading(folder)
        for index, source in enumerate(sources):
            g = source.stem[:6]
            concept = folder / 'web' / f'{g}.js'
            notes = folder / 'compare' / f'{g}.md'
            found.append({
                'id': f'{folder.name}-{g}'.replace('_', '-'),
                'name': f'{family} {g.replace("_", " ")} · {label(source)}',
                'family': family,
                'generation': g,
                'newest': index == len(sources) - 1,
                'folder': str(folder.relative_to(REPO)),
                'scad': str(source.relative_to(REPO)),
                'concept': str(concept.relative_to(REPO)) if concept.exists() else None,
                'notes': str(notes.relative_to(REPO)),
                'sheet': str((folder / 'render' / f'compare_{g}.png').relative_to(REPO)),
                'parts': pieces(folder, source, index),
                'in_progress': working_on(folder, source, index == len(sources) - 1, claimed),
            })
    return found


def words(text):
    return re.findall(r'[a-z0-9]+', text.lower().replace('_', ' '))


def score(query, design):
    """How well a spoken name fits: every query word should start a word of the
    id, family or label; "gen 1" / "generation one" pick the generation."""
    numbers = {'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5'}
    q = [numbers.get(w, w) for w in words(query) if w not in ('the', 'a', 'design', 'generation', 'gen')]
    hay = words(design['id'] + ' ' + design['name'])
    gen = str(int(design['generation'][4:]))
    total = 0
    for w in q:
        if w.isdigit():
            total += 3 if int(w) == int(gen) else -3
        elif any(h == w for h in hay):
            total += 3
        elif any(h.startswith(w) or w.startswith(h) and len(h) > 2 for h in hay):
            total += 2
        else:
            total -= 1
    # A family name alone means its newest generation.
    return total + (0.5 if design['newest'] else 0)


def match(query, found):
    exact = [d for d in found if d['id'] == query.strip()]
    if exact or not found:
        return exact[0] if exact else None
    best = max(found, key=lambda d: score(query, d))
    return best if score(query, best) > 0.5 else None


def echo_rows(source):
    """The generation's own piece list, when it has a part="parts" mode."""
    with tempfile.TemporaryDirectory() as tmp:
        echo = Path(tmp) / 'parts.echo'
        subprocess.run([SCAD, '-o', str(echo), '-D', 'part="parts"', str(source)], capture_output=True)
        lines = echo.read_text().splitlines() if echo.exists() else []
    rows = []
    for line in lines:
        if line.startswith('ECHO: ['):
            try:
                rows.append(json.loads(line.removeprefix('ECHO: '))[0])
            except (ValueError, IndexError):
                pass
    return [r for r in rows if isinstance(r, str)]


def export(design):
    """Re-export just this generation's STLs (no renders), so a save shows up
    in a second or two. Pieces when the file lists them, else the whole file."""
    source = REPO / design['scad']
    folder = source.parent
    (folder / 'export').mkdir(exist_ok=True)
    g = source.stem[:6]
    names = echo_rows(source)
    jobs = ([(f'{g}_{q}.stl', ['-D', f'part="{q}"']) for q in names] if names
            else [(f'{source.stem}.stl', [])])

    def run(job):
        name, args = job
        result = subprocess.run([SCAD, '--export-format', 'binstl', '-o', str(folder / 'export' / name), *args, str(source)],
                                capture_output=True, text=True)
        return name, result.returncode, result.stderr

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(run, jobs))
    failed = [f'{n}: {e.strip().splitlines()[-1] if e.strip() else "failed"}' for n, code, e in results if code]
    for line in failed:
        print(line, file=sys.stderr)
    return not failed


def main(argv):
    found = discover()
    OUT.write_text(json.dumps({'designs': found}, indent=1) + '\n')
    if argv[:1] == ['--json']:
        print(json.dumps(found))
    elif argv[:1] == ['--match']:
        best = match(' '.join(argv[1:]), found)
        if not best:
            print('No design matches "%s". Designs:\n  %s' % (' '.join(argv[1:]), '\n  '.join(d['id'] for d in found)),
                  file=sys.stderr)
            return 1
        print(json.dumps(best))
    elif argv[:1] == ['--export']:
        design = match(' '.join(argv[1:]), found)
        if not design:
            return 1
        ok = export(design)
        OUT.write_text(json.dumps({'designs': discover()}, indent=1) + '\n')
        return 0 if ok else 1
    else:
        for d in found:
            print(f"{d['id']:28} {d['name']}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
