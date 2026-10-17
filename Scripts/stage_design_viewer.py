#!/usr/bin/env python3
"""Bundle the shared interactive viewer and its referenced models for offline iOS use."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys


def stage(destination):
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('design_registry', root / 'cad/compare/designs.py')
    registry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(registry)
    designs = registry.discover()
    destination = Path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    compare = destination / 'cad/compare'
    compare.mkdir(parents=True)
    for name in ('viewer.html', 'viewer.js', 'shapes.js'):
        shutil.copy2(root / 'cad/compare' / name, compare / name)
    shutil.copytree(root / 'cad/compare/vendor', compare / 'vendor')
    for design in designs:
        # Concepts read dimensions and outlines from their sibling SCAD sources.
        for source in (root / design['folder']).rglob('*.scad'):
            target = destination / source.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        # Include sibling JS modules so a concept can share geometry helpers.
        if design.get('concept'):
            source = root / design['concept']
            shutil.copytree(source.parent, destination / source.parent.relative_to(root), dirs_exist_ok=True)
        for part in design['parts']:
            source = root / part['path']
            if not source.is_file():
                raise FileNotFoundError(f"Missing model for {design['id']}: {source}")
            target = destination / part['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    (compare / 'designs.json').write_text(json.dumps({'designs': designs}))
    print(f'Staged interactive viewer: {len(designs)} designs into {destination}')


if __name__ == '__main__':
    stage(sys.argv[1] if len(sys.argv) > 1 else Path(os.environ['BUILT_PRODUCTS_DIR']) / os.environ['UNLOCALIZED_RESOURCES_FOLDER_PATH'] / 'DesignViewer')
