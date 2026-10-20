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


def finger_version(folder):
    """', Gripper 21' in this folder's VERSIONS.txt heading (up to its first ':'): the fingers a Handle/Base design carries,
    so the gallery's mix-and-match can offer fingers that exist only inside a later design (voice-bbe0e945)."""
    path = Path(folder).parent / 'VERSIONS.txt'
    text = path.read_text(errors='replace') if path.is_file() else ''
    found = re.search(r'^' + re.escape(Path(folder).name) + r'\b(.*?)(?=^v\d|\Z)', text, re.M | re.S)
    match = found and re.search(r',\s*Gripper (\d+[a-z]?)\b', found.group(1).split(':')[0])
    return match.group(1) if match else None


def public_fields(row):
    fields = {k: row[k] for k in ('id', 'project', 'version', 'name', 'status', 'notes', 'license')}
    if row.get('fingers'):
        fields['fingers'] = row['fingers']
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
            row = entry(project, folder.name, source, folder, fingers=finger_version(folder))
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
                parts = json.loads(parts_file.read_text())['parts']
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
                   "two-finger-gripper-v308-generalist-handle-gear": "Base 8"}
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
    if tuning.is_file() and (Path(row['folder']) / 'live_render.py').is_file():
        # Handle 4 on: the gallery's Tune panel draws a slider for each of these; serve_designs.py POST /tune renders them
        public['params'] = [dict(name=g['name'], params=[q for q in g['params'] if q['stage'] != 'calibration'])
                            for g in json.loads(tuning.read_text())['groups'] if any(q['stage'] != 'calibration' for q in g['params'])]
    source = inside(row['source_path'], repo) if row['source_path'] else None
    asset = out / 'assets' / row['id']
    asset.mkdir(parents=True, exist_ok=True)
    deps = dependencies(source, repo)
    docs = documentation(row, repo)
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
    previous_preview = out / cache['preview'] if cache.get('preview') else asset / 'preview.png'
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
        if (not cached or not preview.exists()) and build:
            # Preview the very same exported geometry the mobile viewer loads.
            wrapper = asset / '_preview.scad'
            wrapper.write_text('\n'.join('import(' + json.dumps(str(out / m['path'])) + ');' for m in public['models']))
            try:
                run_scad(wrapper, preview, [], timeout, preview=True)
            finally:
                wrapper.unlink(missing_ok=True)
        if preview.is_file():
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
                if path.is_file() and not path.is_symlink() and path.suffix.lower() in ('.html', '.js', '.css', '.svg', '.png', '.ico'):
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
