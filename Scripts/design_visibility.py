#!/usr/bin/env python3
"""Hide or show designs in the Live Preview gallery. The voice session runs
this for "hide gripper gen 1 and 2" / "show gen 1 again". Does not build.

The hidden list is <gallery>/hidden.json, next to the published catalog. The
gallery's Shown checklist writes the same file through serve_designs.py, so
the phone, the Mac and voice all agree, and it survives republishing.

    design_visibility.py hide gripper gen 1 2    # one design per number
    design_visibility.py show gripper gen 1
    design_visibility.py show all                # unhide everything
    design_visibility.py list
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

DEFAULT_GALLERY = Path.home() / 'HelpingHands-tools/design-gallery'
NUMBERS = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
           'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
FILLER = {'the', 'a', 'and', 'design', 'designs', 'gen', 'gens', 'generation', 'generations', 'version', 'v'}
ID = re.compile(r'^[a-z0-9][a-z0-9-]{0,159}$')


def words(text):
    return re.findall(r'[a-z]+|[0-9]+', text.lower())


def generation(design):
    """Its number: "Gen 3" or "v003" out of the name."""
    found = re.search(r'\b(?:generation|gen|v)\s*0*(\d+)', design.get('name', ''), re.I)
    return int(found.group(1)) if found else None


def load(gallery):
    catalog = json.loads((gallery / 'catalog.json').read_text())['designs']
    try:
        hidden = json.loads((gallery / 'hidden.json').read_text()).get('hidden', [])
    except (OSError, ValueError, AttributeError):
        hidden = []
    return catalog, [h for h in hidden if isinstance(h, str) and ID.match(h)]


def save(gallery, hidden):
    gallery.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=gallery, prefix='.hidden-', suffix='.json')
    with os.fdopen(fd, 'w') as handle:
        json.dump({'hidden': sorted(set(hidden))}, handle, indent=1)
        handle.write('\n')
    os.chmod(tmp, 0o644)
    os.replace(tmp, gallery / 'hidden.json')


def resolve(query, catalog):
    """The designs a spoken phrase names. Every word must start a word of the
    project, name or id; each number picks one generation of that family."""
    if query.strip().lower() in ('all', 'everything', 'all designs'):
        return list(catalog)
    tokens = words(query)
    numbers = [int(t) if t.isdigit() else NUMBERS[t] for t in tokens if t.isdigit() or t in NUMBERS]
    terms = [t for t in tokens if t not in FILLER and not t.isdigit() and t not in NUMBERS]
    exact = [d for d in catalog if d['id'] == query.strip()]
    if exact:
        return exact

    def fits(design):
        hay = words(' '.join((design.get('project', ''), design.get('name', ''), design['id'])))
        return all(any(h.startswith(t) for h in hay) for t in terms)

    pool = [d for d in catalog if fits(d)]
    if not numbers:
        if len(pool) != 1:
            raise LookupError(f'"{query}" matches {len(pool)} designs' + (':\n  ' + '\n  '.join(label(d) for d in pool) if pool else ''))
        return pool
    picked = []
    for n in numbers:
        hits = [d for d in pool if generation(d) == n]
        if len(hits) != 1:
            raise LookupError(f'"{query}": gen {n} matches {len(hits)} designs' + (':\n  ' + '\n  '.join(label(d) for d in hits) if hits else ''))
        picked += hits
    return picked


def label(design):
    return f"{design.get('project', '?')} · {design.get('name', design['id'])}  ({design['id']})"


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', choices=('hide', 'show', 'list'))
    parser.add_argument('name', nargs='*', help='spoken design name, e.g. "gripper gen 1 2"')
    parser.add_argument('--gallery', type=Path, default=DEFAULT_GALLERY)
    args = parser.parse_args(argv)
    try:
        catalog, hidden = load(args.gallery)
    except (OSError, ValueError, KeyError) as error:
        print(f'No published catalog in {args.gallery}: {error}', file=sys.stderr)
        return 1

    if args.action != 'list':
        if not args.name:
            parser.error(f'{args.action} needs a design name')
        try:
            targets = resolve(' '.join(args.name), catalog)
        except LookupError as error:
            print(error, file=sys.stderr)
            return 1
        ids = {d['id'] for d in targets}
        hidden = sorted(set(hidden) | ids) if args.action == 'hide' else [h for h in hidden if h not in ids]
        save(args.gallery, hidden)
        for d in targets:
            print(('Hid ' if args.action == 'hide' else 'Showing ') + label(d))

        return 0

    project = None
    for d in catalog:
        if d.get('project') != project:
            project = d.get('project')
            print(project)
        print(f"  {'hidden' if d['id'] in hidden else 'shown '}  {d.get('name', d['id'])}  ({d['id']})")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
