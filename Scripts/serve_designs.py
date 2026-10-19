#!/usr/bin/env python3
"""Serve only curated design artifacts; refresh working CAD exports every five minutes. POST /tune renders a design's
parameters (2.4 on: a version folder with params.json + live_render.py) for the gallery's Tune sliders."""
import argparse
import hashlib
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO.parent / 'HelpingHands-tools/design-gallery'
TUNE_KEEP = 80   # tuned renders kept per design (each ~1 MB); older ones are deleted
tune_locks = {}


def tunable(design_id):
    """The version folder behind a design id when it has a live_render.py + params.json (2.4 on), else None. Ids are
    publish_designs.py's: slug(project + '-' + folder name)."""
    for folder in REPO.glob('*/versions/v[0-9]*'):
        if (folder / 'live_render.py').is_file() and (folder / 'params.json').is_file():
            if re.sub('[^a-z0-9]+', '-', (folder.parents[1].name + '-' + folder.name).lower()).strip('-') == design_id:
                return folder
    return None


def tune(root, design_id, values):
    """Render a design's viewer parts for slider values (the gallery's Tune panel). The output lands under the served
    root at tune/<id>/<hash of the values>/, so dragging back to an earlier value is a cache hit."""
    folder = tunable(design_id)
    if folder is None:
        return 404, {'ok': False, 'error': 'This design has no parameters to tune'}
    key = hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()[:24]
    base = Path(root) / 'tune' / design_id
    out = base / key
    with tune_locks.setdefault(design_id, threading.Lock()):   # one render at a time per design; the page coalesces drags
        try:
            result = json.loads((out / 'result.json').read_text())
        except (OSError, ValueError):
            result = None
        if not result or not result.get('ok'):
            out.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run([sys.executable, str(folder / 'live_render.py'), '--values', json.dumps(values), '--out', str(out),
                                '--cache', str(base / '.trace')], capture_output=True, timeout=90)
                result = json.loads((out / 'result.json').read_text())
            except (OSError, ValueError, subprocess.TimeoutExpired) as error:
                result = {'ok': False, 'error': 'Render failed: ' + str(error)}
        runs = sorted((d for d in base.iterdir() if d.is_dir() and not d.name.startswith('.')), key=lambda d: d.stat().st_mtime)
        for old in runs[:-TUNE_KEEP]:
            if old != out:
                shutil.rmtree(old, ignore_errors=True)
    parts = json.loads((folder / 'viewer_parts.json').read_text())['parts']
    if result.get('ok'):
        result['models'] = [dict(name=p['name'], color=p.get('color'), explode=p.get('explode', [0, 0, 0]),
                                 path=(out / Path(p['path']).name).relative_to(root).as_posix()) for p in parts]
    return 200, result

class GalleryServer(ThreadingHTTPServer):
    # The default backlog of 5 resets connections when a phone loads every
    # generation at once (Gen 8 alone is ~150 STLs), and one reset part fails
    # the whole viewport with "Could not load 3D" (voice-b7ae5fc0).
    request_queue_size = 128


class GalleryHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/health.json':
            catalog = Path(self.directory) / 'catalog.json'
            try:
                data = json.loads(catalog.read_text())
                payload = json.dumps({'ok': True, 'catalog_updated_at': data.get('generated_at')}).encode()
                self.send_response(200)
            except (OSError, ValueError):
                payload = b'{"ok":false,"message":"First design export is still running"}'
                self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers(); self.wfile.write(payload); return
        if path == '/manifest.json':
            self.path = '/catalog.json'
        root = Path(self.directory).resolve()
        requested = (root / unquote(urlsplit(self.path).path).lstrip('/')).resolve()
        if not requested.is_relative_to(root):
            self.send_error(403); return
        super().do_GET()

    def send_json(self, code, data):
        payload = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers(); self.wfile.write(payload)

    def do_POST(self):
        # The Tune panel: {"design": id, "values": {param: number}} -> freshly rendered STLs (tune() above). Numbers
        # only, names checked against the design's params.json by live_render.py; JSON only, like hidden.json.
        if urlsplit(self.path).path == '/tune':
            if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/json':
                self.send_error(415); return
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if 0 < length <= 65536 else None
                design, values = body.get('design'), body.get('values')
            except (ValueError, AttributeError):
                design = values = None
            if not (isinstance(design, str) and re.fullmatch(r'[a-z0-9][a-z0-9-]{0,159}', design) and isinstance(values, dict)
                    and len(values) <= 200 and all(isinstance(k, str) and re.fullmatch(r'[a-z0-9_]{1,40}', k)
                                                   and isinstance(v, (int, float)) and not isinstance(v, bool) for k, v in values.items())):
                self.send_error(400, 'Expected {"design": id, "values": {name: number}}'); return
            self.send_json(*tune(self.directory, design, values)); return
        # The gallery's Shown checklist. The one writable path: a list of design
        # ids in hidden.json, which Scripts/design_visibility.py also edits. JSON
        # only, so a cross-site form can't post here without a CORS preflight.
        if urlsplit(self.path).path != '/hidden.json':
            self.send_error(404); return
        if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/json':
            self.send_error(415); return
        try:
            length = int(self.headers.get('Content-Length', 0))
            hidden = json.loads(self.rfile.read(length)).get('hidden') if 0 < length <= 65536 else None
        except (ValueError, AttributeError):
            hidden = None
        if not isinstance(hidden, list) or not all(isinstance(h, str) and re.fullmatch(r'[a-z0-9][a-z0-9-]{0,159}', h) for h in hidden):
            self.send_error(400, 'Expected {"hidden": [design ids]}'); return
        payload = (json.dumps({'hidden': sorted(set(hidden))}, indent=1) + '\n').encode()
        fd, tmp = tempfile.mkstemp(dir=self.directory, prefix='.hidden-', suffix='.json')
        with os.fdopen(fd, 'wb') as handle:
            handle.write(payload)
        os.chmod(tmp, 0o644)
        os.replace(tmp, Path(self.directory) / 'hidden.json')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers(); self.wfile.write(payload)

    def list_directory(self, path):
        self.send_error(404, 'Only published design files are available')
        return None

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()


def publish_loop(destination, interval):
    while True:
        print(datetime.now(timezone.utc).isoformat(), 'Refreshing design exports', flush=True)
        try:
            result = subprocess.run([sys.executable, str(REPO / 'Scripts/publish_designs.py'), '--output', str(destination)], timeout=1200)
            if result.returncode:
                print('Publisher failed; serving last successful catalog', flush=True)
        except Exception as error:
            print('Publisher error:', error, flush=True)
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--port', type=int, default=8768)
    parser.add_argument('--interval', type=int, default=300)
    parser.add_argument('--no-publish', action='store_true')
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    if not args.no_publish:
        threading.Thread(target=publish_loop, args=(args.directory, max(args.interval, 30)), daemon=True).start()
    server = GalleryServer(('127.0.0.1', args.port), partial(GalleryHandler, directory=str(args.directory)))
    print(f'Design preview: http://127.0.0.1:{args.port}/', flush=True)
    server.serve_forever()

if __name__ == '__main__':
    main()
