#!/usr/bin/env python3
"""Publish a finite, incremental OpenSCAD design catalog to a curated static tree.

No repository snapshots are edited. Existing positioned STL exports are reused;
missing exports are rendered into the staging directory only. Concept JavaScript
is never a geometry source. The gallery server may invoke this command on refresh.
"""
import argparse
import concurrent.futures
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import struct
import time
import zipfile

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = Path.home() / 'HelpingHands-tools/design-gallery'
OPENSCAD = os.environ.get('OPENSCAD', '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD')
CACHE_VERSION = 1


def slug(text):
    return re.sub('[^a-z0-9]+', '-', text.lower()).strip('-')


def inside(path, root):
    path = Path(path).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Path outside curated repository: {path}')
    return path


def read_notes(folder):
    for name in ('README.txt', 'README.md'):
        path = folder / name
        if path.is_file():
            return path.read_text(errors='replace')[:3000]
    return 'OpenSCAD geometry study; mechanical operation and print readiness are not established.'


def version_entry(folder):
    """This folder's VERSIONS.txt entry (its heading line and the lines under it), or ''."""
    path = Path(folder).parent / 'VERSIONS.txt'
    text = path.read_text(errors='replace') if path.is_file() else ''
    found = re.search(r'^' + re.escape(Path(folder).name) + r'\b(.*?)(?=^v\d|\Z)', text, re.M | re.S)
    return found.group(1) if found else ''


def finger_version(folder):
    """', Gripper 21' in this folder's VERSIONS.txt heading (up to its first ':'): the fingers a Handle/Base design carries,
    so the gallery's mix-and-match can offer fingers that exist only inside a later design (voice-bbe0e945)."""
    match = re.search(r',\s*Gripper (\d+[a-z]?)\b', version_entry(folder).split(':')[0])
    return match.group(1) if match else None


# Parts that ride inside a Base design but count on their own (AGENTS.md: Arm N, Mount N, Aero Hand N). A heading naming
# ', Arm 1, Mount 1, Aero Hand 1' publishes those of its parts as their own catalog designs (the first heading to name a
# version owns it), so each part is published separately and the gallery picks it independently (voice-a5d65841).
CARRIED = {'Arm': r'^(reBot Arm|SO-101 Arm)', 'Mount': r'^(Wrist hub|Tool plate|Aero Hand tool plate)\b', 'Aero Hand': r'^Aero Hand \(left\)'}


def own_part(folder):
    """The part a folder's VERSIONS.txt heading leads with: ('Base', '14'), ('Mount', '2') (v315: Mount 2 on the SO-101), or None."""
    m = re.match(r'\W*(Gripper|Handle|Base|Arm|Mount|Aero Hand) (\d+[a-z]?)\b', version_entry(folder).split(':')[0])
    return (m.group(1), m.group(2)) if m else None


def tool_plates_of(folder):
    """'Mount 1's tool plate' in the entry of a folder that leads with a new Mount: that Mount takes Mount 1's tool plates, so
    every tool built for Mount 1 fits it (the gallery's compatibility flags)."""
    own = own_part(folder)
    m = re.search(r"\bMount (\d+[a-z]?)['’]s\s+tool\s+plates?\b", version_entry(folder))
    return m.group(1) if own and own[0] == 'Mount' and m and m.group(1) != own[1] else None


def carried_parts(folder):
    """', Arm 1, Mount 1' in the heading, and the part it leads with when that is one of them (v315: 'Mount 2 (…), Arm 2')."""
    heading = version_entry(folder).split(':')[0]
    found = {kind: m.group(1) for kind in CARRIED if (m := re.search(r',\s*' + kind + r' (\d+[a-z]?)\b', heading))}
    if (own := own_part(folder)) and own[0] in CARRIED:
        found[own[0]] = own[1]
    return {kind: found[kind] for kind in CARRIED if kind in found}   # Arm, Mount, Aero Hand: the order fits leans on


def param_value(folder, name):
    """A params.json value (Handle 4 on), or None when the folder has no such parameter."""
    path = Path(folder) / 'params.json'
    groups = json.loads(path.read_text())['groups'] if path.is_file() else []
    return next((q['value'] for g in groups for q in g['params'] if q['name'] == name), None)


def lineage(folder):
    """What this version builds on, from its VERSIONS.txt entry: 'Base 12 (…): Base 11 on the STS3215 only, made compact.'
    -> ('Base 11', 'on the STS3215 only'). The first other '<Kind> N' after the heading is the parent; the words after it,
    up to the next stop, say what changed. ('', '') when the entry names none (Base 1, Base 3)."""
    heading, _, body = version_entry(folder).partition(':')
    own = re.search(r'\b(Gripper|Handle|Base|Arm|Mount) (\d+[a-z]?)\b', heading)
    if not own:
        return '', ''
    body = ' '.join(re.sub(r'\([^)]*\)', '', body).split())   # '(Base 2: 29)' is a comparison, not the parent
    for m in re.finditer(r'\b' + own.group(1) + r' (\d+[a-z]?)\b', body):
        if m.group(1) != own.group(2):
            gist = re.split(r'[,;:]|\.(?=\s|$)', body[m.end():])[0].strip()
            gist = re.sub(r"^['’]s\s+", '', gist)
            if len(gist) > 48:
                gist = gist[:48].rsplit(' ', 1)[0] + '…'
            return f'{own.group(1)} {m.group(1)}', gist
    return '', ''


def public_fields(row):
    fields = {k: row[k] for k in ('id', 'project', 'version', 'name', 'status', 'notes', 'license')}
    for key in ('fingers', 'carries', 'fits', 'builds_on', 'gist', 'on_mount', 'tool_plate', 'no_handles', 'finger_lineage'):
        if row.get(key):
            fields[key] = row[key]
    return fields


def entry(project, version, source, folder, **extra):
    return dict(id=slug(project + '-' + version), project=project, version=version,
                name=version.replace('_', ' '), status='in progress — design study', notes=read_notes(folder),
                license='Project-specific; inspect included source notices', source_path=source,
                folder=folder, defines=[], existing=[], **extra)


def discover(repo=REPO):
    result = []
    path = repo / 'cad/compare/designs.py'
    if path.exists():
        spec = importlib.util.spec_from_file_location('gallery_designs', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for design in module.discover():
            if '/versions/' in design['folder']:
                continue   # discovered below; listing it twice published Gripper 16 twice under one id (voice-caae8e01)
            row = entry(design['family'], design['generation'], repo / design['scad'], repo / design['folder'])
            row.update(id=design['id'], name=design['name'], notes='Historical OpenSCAD design study. ' + row['notes'])
            row['existing'] = [dict(path=repo / p['path'], name=p['name'], color=p.get('color'), explode=p.get('explode', [0, 0, 0]))
                               for p in design['parts'] if (repo / p['path']).is_file()]
            row['declared_parts'] = True
            result.append(row)
    for project in ('ORCA CC-BY Prototype', 'Two Finger Gripper', 'Three Finger Gripper'):
        base = repo / project
        for folder in sorted((base / 'versions').glob('v[0-9]*')):
            if not folder.is_dir():
                continue
            choices = [folder / p for p in ('index.scad', 'gripper.scad', 'main.scad',
                       'assembly/wearable_channel_concept.scad', 'assembled_hand.scad')]
            source = next((p for p in choices if p.is_file()), None)
            if source is None:
                direct = list(folder.glob('*.scad'))
                source = direct[0] if len(direct) == 1 else None
            builds_on, gist = lineage(folder)
            row = entry(project, folder.name, source, folder, fingers=finger_version(folder),
                        carries=carried_parts(folder), builds_on=builds_on, gist=gist)
            if project == 'ORCA CC-BY Prototype':
                row['license'] = 'CC BY 4.0 — ORCA Dexterity, Inc.'
                if 'shell' in folder.name:
                    row.update(status='unassembled section inspection', notes='Separate shell sections; not an assembled or wearable finger. ' + row['notes'])
            if project == 'Three Finger Gripper':
                row.update(status='stopped / archived', notes='Stopped direction, retained for reference. ' + row['notes'])
            if source is None:
                row.update(status='superseded before CAD', notes=read_notes(folder))
            assembly = folder / 'exports/assembly.stl'
            if assembly.is_file():
                row['existing'] = [dict(path=assembly, name='OpenSCAD assembly')]
            parts_file = folder / 'viewer_parts.json'
            if parts_file.is_file():
                part_data = json.loads(parts_file.read_text())
                parts = part_data['parts']
                if part_data.get('preview'):
                    row['existing_preview'] = inside(folder / part_data['preview'], repo)
                row['no_handles'] = bool(part_data.get('no_handles'))
                row['finger_lineage'] = part_data.get('finger_lineage')
                row['existing'] = [dict(path=inside(folder / p['path'], repo), name=p['name'],
                                        color=p.get('color'), explode=p.get('explode', [0, 0, 0]))
                                   for p in parts]
                row['declared_parts'] = True
            result.append(row)
    specials = [
        ('ORCA CC-BY Prototype', 'full_hand', 'full_hand/assembled_hand.scad', 'full_hand', 'assembled visual reference', 'MIT (official simulation visual meshes; separate hardware CAD remains CC BY 4.0)'),
    ]
    for project, version, filename, subfolder, status, license_text in specials:
        base = repo / project
        source = base / filename
        if not source.is_file():
            continue
        row = entry(project, version, source, base / subfolder)
        row.update(status=status, license=license_text)
        if version == 'full_hand':
            model = base / 'full_hand/orca_v2_assembled_visual.stl'
            if model.is_file():
                row['existing'] = [dict(path=model, name='Official zero-pose visual assembly')]
        result.append(row)
    # Retire superseded branches from Live while keeping source history.
    retired = {
        "two-finger-gripper-v001-motor-force-layout",
        "two-finger-gripper-v002-two-parallel-modules",
        "three-finger-gripper-v001-dorsal-linkage",
    }
    result = [row for row in result if row["id"] not in retired]
    # AGENTS.md: each part keeps its own counter (Gripper N fingers, Handle N, Base N); ids stay the folder's.
    generations = {"demo-gripper-gen-00": "Gripper 1", "demo-gripper-gen-01": "Gripper 2",
                   "two-finger-gripper-v003-single-pincher": "Gripper 3",
                   "two-finger-gripper-v004-symmetric-pincher": "Gripper 4",
                   "two-finger-gripper-v005-mirrored-gears": "Gripper 5",
                   "two-finger-gripper-v006-dorsal-drive": "Gripper 6",
                   "two-finger-gripper-v007-generalist-fingers": "Gripper 7",
                   "two-finger-gripper-v008-pollen-grabette": "Gripper 8",
                   "two-finger-gripper-v009-generalist-fingers-sonnet": "Gripper 9",
                   "two-finger-gripper-v010-generalist-fingers-opus": "Gripper 10",
                   "two-finger-gripper-v011-generalist-fingers-opus": "Gripper 11",
                   "two-finger-gripper-v011b-generalist-fingers-astra": "Gripper 11b",
                   "two-finger-gripper-v012-generalist-tweezer": "Gripper 12",
                   "two-finger-gripper-v013-generalist-closed-beak": "Gripper 13",
                   "two-finger-gripper-v014-generalist-tip-contact": "Gripper 14",
                   "two-finger-gripper-v015-generalist-long-jaw": "Gripper 15",
                   "two-finger-gripper-v016-generalist-rounded-point": "Gripper 16",
                   "two-finger-gripper-v017-generalist-strap-slide": "Gripper 17",
                   "two-finger-gripper-v018-generalist-flat-taper": "Gripper 18",
                   "two-finger-gripper-v019-generalist-wide-beak": "Gripper 19",
                   "two-finger-gripper-v020-generalist-double-hook": "Gripper 20",
                   "two-finger-gripper-v201-generalist-strap-loops": "Handle 1",
                   "two-finger-gripper-v202-generalist-flush-loops": "Handle 2",
                   "two-finger-gripper-v203-generalist-tongue-pocket": "Handle 3",
                   "two-finger-gripper-v204-generalist-parametric": "Handle 4",
                   "two-finger-gripper-v205-generalist-spanning-handle": "Handle 5",
                   "two-finger-gripper-v206-generalist-single-step": "Handle 6",
                   "two-finger-gripper-v207-generalist-flush-handle": "Handle 7",
                   "two-finger-gripper-v301-generalist-base": "Base 1",
                   "two-finger-gripper-v302-generalist-simple": "Base 2",
                   "two-finger-gripper-v303-generalist-inplane": "Base 3",
                   "two-finger-gripper-v304-generalist-one-piece-drive": "Base 4",
                   "two-finger-gripper-v305-generalist-single-gear": "Base 5",
                   "two-finger-gripper-v307-generalist-printable": "Base 7",
                   "two-finger-gripper-v308-generalist-handle-gear": "Base 8",
                   "two-finger-gripper-v309-generalist-top-plate": "Base 9",
                   "two-finger-gripper-v310-generalist-arm-mount": "Base 10",
                   "two-finger-gripper-v311-generalist-motor-choice": "Base 11",
                   "two-finger-gripper-v312-generalist-compact-drive": "Base 12",
                   "two-finger-gripper-v313-generalist-aero-full-hand": "Base 13",
                   "two-finger-gripper-v314-generalist-sts-arm-mount": "Base 14",
                   "two-finger-gripper-v316-generalist-post-cap": "Base 15",
                   "two-finger-gripper-v317-generalist-micro-tweezers": "Base 16",
                   "two-finger-gripper-v318-generalist-tiny-v2": "Base 17",
                   "two-finger-gripper-v319-generalist-hls3606m": "Base 18",
                   "two-finger-gripper-v320-generalist-overhead-drive": "Base 19",
                   "two-finger-gripper-v321-generalist-compact-overhead": "Base 20",
                   "two-finger-gripper-v322-generalist-two-pivot-support": "Base 21",
                   "two-finger-gripper-v323-generalist-centered-drive": "Base 22"}   # v315 leads with Mount 2: "Mount 2 assembly" below
    # Public families group related studies; stable IDs preserve saved links
    # and the original numbered source versions.
    families = {'ORCA CC-BY Prototype': 'Orca Hand',
                'Robot Glove Hand': 'Glove Hand',
                'Two Finger Gripper': 'Generalist Gripper',
                'Three Finger Gripper': 'Generalist Gripper',
                'Demo gripper': 'Generalist Gripper'}
    for row in result:
        old = row['project']
        row['project'] = families.get(old, old)
        if row['name'].startswith(old):
            row['name'] = row['project'] + row['name'][len(old):]
    for row in result:
        if row["id"] in generations:
            kind, number = generations[row["id"]].split()
            row.update(name=f"{kind} {number}", version=f"{kind.lower()}_{number:0>2}")   # "11b": the Astra pass beside Gripper 11
    # A folder that leads with an Arm or a Mount (v315: Mount 2, Base 14 on the SO-101) changed only those parts: it is their
    # assembly, not a Base, so it keeps its tile but no Base number (AGENTS.md: never bump one part for another).
    for row in result:
        if (own := own_part(row['folder'])) and own[0] in ('Arm', 'Mount'):
            row.update(name=f'{own[0]} {own[1]} assembly', version=f'{own[0].lower()}_{own[1]:0>2}_assembly')
    # The Aero Hand is its own end effector (AGENTS.md), so a folder whose heading carries one (v313) is that hand's assembly, not
    # a Base: it keeps its tile and Tune panel but leaves the Base picker (voice-a5d65841).
    for row in result:
        if hand := (row.get('carries') or {}).get('Aero Hand'):
            row.update(name=f'Aero Hand {hand} assembly', version=f'aero_hand_{hand:0>2}_assembly')
    claimed = set()
    for row in sorted(result, key=lambda row: Path(row['folder']).name):   # Base 10 owns Arm 1 and Mount 1; v313 adds Aero Hand 1
        for kind, number in (row.get('carries') or {}).items():
            existing = [m for m in row['existing'] if re.search(CARRIED[kind], m['name'])]
            if (kind, number) in claimed or not existing:
                continue
            claimed.add((kind, number))
            name = f'{kind} {number}'
            own = own_part(row['folder']) == (kind, number)   # Mount 2's folder leads with it, so its lineage is Mount 2's
            result.append(dict(row, id=slug(row['project'] + '-' + name), name=name, version=f"{slug(kind).replace('-', '_')}_{number:0>2}",
                               notes=f"{name}, published from {row['name']} ({Path(row['folder']).name}). " + row['notes'],
                               existing=existing, fingers=None, carries={}, carried_from=row['id'],
                               builds_on=row['builds_on'] if own else '', gist=row['gist'] if own else '',
                               tool_plate=tool_plates_of(row['folder']) if own and kind == 'Mount' else None,
                               # what it sits on, as carried beside it: Mount 1 on Arm 1, Aero Hand 1 on Mount 1 + Arm 1
                               fits={k: v for k, v in row['carries'].items() if list(CARRIED).index(k) < list(CARRIED).index(kind)}))
            if kind == 'Aero Hand' and (x := param_value(row['folder'], 'aero_view_x')) is not None:
                result[-1]['on_mount'] = [-x, 0, 0]   # exported on the rack beside the arm; this moves it (and its plate) onto the hub
    # The Aero Hand is its own design family beside Generalist Gripper, Glove Hand and Orca Hand (voice-a87f8d20): its versions
    # and its assembly leave the Generalist line. Ids stay as published, so saved links keep working.
    for row in result:
        if 'Aero Hand' in (row.get('carries') or {}) or row['name'].startswith('Aero Hand '):
            row['project'] = 'Aero Hand'
    # Latest generations first; source folders retain original version names.
    return sorted(result, key=lambda row: (row['project'], row['version']), reverse=True)


def dependencies(source, repo=REPO):
    """SCAD include/use/import dependencies, including dynamic mesh-directory imports.

    Only files under the repository are permitted. Quoted directory prefixes used
    in str("source/", variable, ".stl") include that directory's CAD assets.
    """
    if source is None:
        return []
    pending, found = [inside(source, repo)], set()
    while pending:
        path = inside(pending.pop(), repo)
        if path in found or not path.is_file():
            continue
        found.add(path)
        if path.suffix.lower() != '.scad':
            continue
        text = path.read_text(errors='replace')
        names = re.findall(r'(?:include|use)\s*<([^>]+)>', text)
        names += re.findall(r'"([^"\n]+)"', text)
        for name in names:
            candidate = path.parent / name
            # Ignore labels, expressions and filenames without a matching file.
            if candidate.is_file() and candidate.suffix.lower() in ('.scad', '.stl', '.off', '.dxf', '.svg', '.dat'):
                pending.append(inside(candidate, repo))
            elif name.endswith('/') and candidate.is_dir():
                pending.extend(inside(p, repo) for p in candidate.rglob('*')
                               if p.is_file() and p.suffix.lower() in ('.scad', '.stl', '.off', '.dxf', '.svg'))
    return sorted(found)


def documentation(row, repo):
    found = set()
    folder = row['folder']
    project_root = repo / row['project']
    roots = {folder}
    if project_root.is_dir():
        roots.add(project_root)
    for root in roots:
        for name in ('README.md', 'README.txt', 'LICENSE', 'CITATION.cff', 'BOM.md', 'SOURCE_MANIFEST.json', 'manifest.json', 'viewer_parts.json'):
            p = root / name
            if p.is_file():
                found.add(inside(p, repo))
        for sub in ('source', 'upstream'):
            for name in ('LICENSE', 'HARDWARE_LICENSE.txt', 'UPSTREAM_LICENSING.md', 'CC-BY-NC-SA-4.0.txt'):
                p = root / sub / name
                if p.is_file():
                    found.add(inside(p, repo))
    return sorted(found)


def atomic_json(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


def copy_changed(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or source.stat().st_size != target.stat().st_size or source.stat().st_mtime_ns != target.stat().st_mtime_ns:
        temporary = target.with_name(target.name + '.copying')
        shutil.copy2(source, temporary)
        temporary.replace(target)


def compact_stl(path):
    """Encode ASCII STL as binary without changing its triangles; atomic staging only."""
    with path.open('rb') as stream:
        header = stream.read(84)
    if len(header) >= 84 and path.stat().st_size == 84 + 50 * struct.unpack_from('<I', header, 80)[0]:
        return
    if not header.lstrip().startswith(b'solid'):
        return
    temporary = path.with_name(path.name + '.binary')
    count, normal, vertices = 0, None, []
    try:
        with path.open() as source, temporary.open('wb') as output:
            output.write(b'OpenSCAD geometry; binary encoding for mobile'.ljust(80, b'\0') + struct.pack('<I', 0))
            for line in source:
                fields = line.split()
                if fields[:2] == ['facet', 'normal']:
                    normal, vertices = list(map(float, fields[2:])), []
                elif fields[:1] == ['vertex']:
                    vertices.extend(map(float, fields[1:]))
                elif fields[:1] == ['endfacet']:
                    if normal is None or len(normal) != 3 or len(vertices) != 9:
                        raise ValueError('Invalid ASCII STL triangle')
                    output.write(struct.pack('<12fH', *(normal + vertices), 0))
                    count += 1
            if not count:
                raise ValueError('STL has no triangles')
            output.seek(80)
            output.write(struct.pack('<I', count))
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def run_scad(source, target, defines, timeout, preview=False):
    temp = target.with_name(target.stem + '.building' + target.suffix)
    command = [OPENSCAD, '-o', str(temp)]
    if target.suffix == '.stl':
        command += ['--export-format', 'binstl']
    if preview:
        command += ['--imgsize=1100,800', '--viewall', '--autocenter']
    for define in defines:
        command += ['-D', define]
    command.append(str(source))
    try:
        result = subprocess.run(command, cwd=source.parent, capture_output=True, text=True, timeout=timeout)
        if result.returncode or not temp.is_file() or temp.stat().st_size == 0 or 'ERROR:' in result.stderr:
            raise RuntimeError(result.stderr[-1800:] or 'OpenSCAD produced no geometry')
        temp.replace(target)
    finally:
        temp.unlink(missing_ok=True)


def publish_entry(row, out, repo=REPO, build=True, timeout=180):
    repo, out = repo.resolve(), out.resolve()
    public = public_fields(row)
    public.update(models=[], source=None, source_bundle=None, preview=None, export_status='no CAD source')
    tuning = Path(row['folder']) / 'params.json'
    if tuning.is_file() and (Path(row['folder']) / 'live_render.py').is_file() and not row.get('carried_from'):
        # Handle 4 on: the gallery's Tune panel draws a slider for each of these; serve_designs.py POST /tune renders them
        public['params'] = [dict(name=g['name'], params=[q for q in g['params'] if q['stage'] != 'calibration'])
                            for g in json.loads(tuning.read_text())['groups'] if any(q['stage'] != 'calibration' for q in g['params'])]
    source = inside(row['source_path'], repo) if row['source_path'] else None
    asset = out / 'assets' / row['id']
    asset.mkdir(parents=True, exist_ok=True)
    deps = dependencies(source, repo)
    docs = documentation(row, repo)
    if row.get('existing_preview'):
        docs.append(row['existing_preview'])
    files = sorted(set(deps + docs))
    h = hashlib.sha256(json.dumps([CACHE_VERSION, row['defines']]).encode())
    for p in deps:
        h.update(str(p.relative_to(repo)).encode())
        h.update(p.read_bytes())
    for model in row['existing']:
        p = inside(model['path'], repo)
        h.update(str(p.relative_to(repo)).encode())
        h.update(p.read_bytes())
        h.update(json.dumps({k: v for k, v in model.items() if k != 'path'}, sort_keys=True).encode())
    fingerprint = h.hexdigest()
    artifact_tag = fingerprint[:16]
    preview = asset / f'preview-{artifact_tag}.png'
    bundle_hash = hashlib.sha256(fingerprint.encode())
    for p in docs:
        bundle_hash.update(p.read_bytes())
    bundle_fingerprint = bundle_hash.hexdigest()
    cache_path = asset / 'build.json'
    try:
        cache = json.loads(cache_path.read_text())
    except (OSError, ValueError):
        cache = {}
    cached = cache.get('fingerprint') == fingerprint
    def url(path):
        return path.relative_to(out).as_posix()
    previous_models = cache.get('models', [])
    if previous_models and all((out / m['path']).is_file() for m in previous_models):
        public['models'] = previous_models
        public['last_success_at'] = cache.get('last_success_at')
    if row.get('existing_preview'):
        copy_changed(row['existing_preview'], asset / 'preview.png')
    previous_preview = asset / 'preview.png' if row.get('existing_preview') else out / cache['preview'] if cache.get('preview') else asset / 'preview.png'
    if previous_preview.is_file():
        public['preview'] = url(previous_preview)
    for p in files:
        copy_changed(p, asset / 'source' / p.relative_to(repo))
    if source:
        public['source'] = url(asset / 'source' / source.relative_to(repo))
    if files:
        bundle = asset / 'source.zip'
        if cache.get('bundle_fingerprint') != bundle_fingerprint or not bundle.exists():
            with zipfile.ZipFile(bundle.with_suffix('.building.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
                for p in files:
                    archive.write(p, p.relative_to(repo))
            bundle.with_suffix('.building.zip').replace(bundle)
        public['source_bundle'] = url(bundle)
    if source is None:
        atomic_json(cache_path, dict(fingerprint=fingerprint, bundle_fingerprint=bundle_fingerprint))
        return public
    if row['status'].startswith('archived') and cache.get('failed_fingerprint') == fingerprint:
        public.update(export_status='export failed', export_error=cache.get('export_error'))
        return public
    try:
        newest_dependency = max(p.stat().st_mtime_ns for p in deps)
        existing_fresh = row['existing'] and all(m['path'].stat().st_mtime_ns + 100_000_000 >= newest_dependency for m in row['existing'])
        # Declared parts (viewer_parts.json, designs.py) are served even when older than the source: they are what the
        # Open/Closed slider's hinges move, and mtime order is noise (a .scad saved after export, a git checkout).
        # Rendering the .scad whole merged Gripper 16's fingers into one mesh that could not close (voice-caae8e01).
        existing_valid = existing_fresh or row['existing'] and row.get('declared_parts')
        if existing_valid and not existing_fresh:
            public['parts_older_than_source'] = True
        kind = 'inspection' if 'unassembled' in public['status'] else 'assembly'
        if existing_valid:
            public['models'] = []
            for i, model in enumerate(row['existing']):
                dest = asset / f'model-{i}-{artifact_tag}.stl'
                if not cached or not dest.exists():
                    copy_changed(model['path'], dest)
                public['models'].append(dict(name=model['name'], path=url(dest), kind=kind,
                                             color=model.get('color') or '#aab6c8', explode=model.get('explode', [0, 0, 0])))
        else:
            mesh = asset / f'assembly-{artifact_tag}.stl'
            if (not cached or not mesh.exists()) and build:
                run_scad(source, mesh, row['defines'], timeout)
            if not mesh.exists() or not cached and not build:
                public['export_status'] = 'pending export'
                return public
            public['models'] = [dict(name=public['name'], path=url(mesh), kind=kind, color='#aab6c8')]
        for model in public['models']:
            compact_stl(out / model['path'])
        if (not cached or not preview.exists()) and build and not row.get('existing_preview'):
            # Preview the very same exported geometry the mobile viewer loads.
            wrapper = asset / '_preview.scad'
            wrapper.write_text('\n'.join('import(' + json.dumps(str(out / m['path'])) + ');' for m in public['models']))
            try:
                run_scad(wrapper, preview, [], timeout, preview=True)
            finally:
                wrapper.unlink(missing_ok=True)
        if preview.is_file() and not row.get('existing_preview'):
            public['preview'] = url(preview)
        public['export_status'] = 'ready'
        public['last_success_at'] = (cache.get('last_success_at') if cached else None) or datetime.now(timezone.utc).isoformat()
        atomic_json(cache_path, dict(fingerprint=fingerprint, bundle_fingerprint=bundle_fingerprint, models=public['models'], preview=public['preview'], last_success_at=public['last_success_at']))
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        public['export_status'] = 'export failed'
        public['export_error'] = str(error)[-1800:]
        # Retain the last complete geometry and thumbnail while source is being edited.
        old_models = cache.get('models', [])
        if old_models and all((out / m['path']).is_file() for m in old_models):
            public['models'] = old_models
            public['last_success_at'] = cache.get('last_success_at')
        if not public.get('preview') and not preview.is_file() and build:
            # A nonmanifold visual mesh may still be inspectable in OpenSCAD's
            # preview. Do not publish its repaired/partial STL as the assembly.
            try:
                run_scad(source, preview, row['defines'], timeout, preview=True)
            except (OSError, RuntimeError, subprocess.TimeoutExpired):
                pass
        if not public.get('preview') and preview.is_file():
            public['preview'] = url(preview)
        if row['status'].startswith('archived'):
            cache.update(failed_fingerprint=fingerprint, export_error=public['export_error'], preview=public['preview'])
            atomic_json(cache_path, cache)
    return public


def publish(repo=REPO, out=DEFAULT_OUT, build=True, workers=2, timeout=180):
    repo, out = repo.resolve(), out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    # Never expose a broad repository root; only explicitly staged static artifacts.
    if out == repo or repo.is_relative_to(out):
        raise ValueError('Output must be a separate curated directory, not a repository ancestor')
    lock = (out / '.publish.lock').open('w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('Publisher already running; keeping current catalog')
        return None
    with lock:
        viewer = repo / 'cad/mobile_gallery'
        if viewer.is_dir():
            for path in viewer.rglob('*'):
                if path.is_file() and not path.is_symlink() and path.suffix.lower() in ('.html', '.js', '.css', '.svg', '.png', '.ico', '.glb'):
                    copy_changed(path, out / path.relative_to(viewer))
        vendor = repo / 'cad/compare/vendor'
        if vendor.is_dir():
            for path in vendor.rglob('*'):
                if path.is_file() and not path.is_symlink() and (path.suffix.lower() in ('.js', '.wasm', '.txt', '.md') or path.name == 'LICENSE'):
                    copy_changed(path, out / 'vendor' / path.relative_to(vendor))
        rows = discover(repo)
        try:
            previous = {item['id']: item for item in json.loads((out / 'catalog.json').read_text())['designs']}
        except (OSError, ValueError, KeyError):
            previous = {}
        published = {}
        for row in rows:
            item = dict(previous.get(row['id'], {}))
            item.update(public_fields(row))
            item.setdefault('models', [])
            item.setdefault('export_status', 'pending export')
            published[row['id']] = item
        catalog = dict(schema_version=1, generated_at=datetime.now(timezone.utc).isoformat(),
                       designs=[published[row['id']] for row in rows])
        atomic_json(out / 'catalog.json', catalog)
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(publish_entry, row, out, repo, build, timeout): row for row in rows}
            for future in concurrent.futures.as_completed(futures):
                row = futures[future]
                try:
                    item = future.result()
                except Exception as error:
                    item = public_fields(row)
                    item.update(models=[], export_status='export failed', export_error=str(error))
                published[row['id']] = item
                catalog['designs'] = [published[r['id']] for r in rows]
                atomic_json(out / 'catalog.json', catalog)
                print(json.dumps(dict(id=row['id'], status=item['export_status'])), flush=True)
        catalog['designs'] = [published[row['id']] for row in rows]
        atomic_json(out / 'catalog.json', catalog)
        return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--no-build', action='store_true', help='stage existing exports and discovery only')
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--timeout', type=int, default=180)
    args = parser.parse_args()
    publish(out=args.output, build=not args.no_build, workers=max(1, args.workers), timeout=args.timeout)


if __name__ == '__main__':
    main()
