import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import publish_designs as publisher


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.repo, self.out = self.root / 'repo', self.root / 'out'
        self.repo.mkdir()
        self.out.mkdir()

    def row(self):
        folder = self.repo / 'Study'
        folder.mkdir(exist_ok=True)
        source = folder / 'main.scad'
        source.write_text('include <dimensions.scad>\ncube(size);')
        (folder / 'dimensions.scad').write_text('size=10;')
        return publisher.entry('Study', 'v001', source, folder)

    def test_discovers_new_versions_without_promoting_helpers(self):
        base = self.repo / 'Two Finger Gripper/versions'
        first = base / 'v001_before_cad'
        first.mkdir(parents=True)
        (first / 'README.txt').write_text('Superseded before CAD')
        second = base / 'v002_actual'
        second.mkdir()
        (second / 'gripper.scad').write_text('cube(2);')
        (second / 'helper.scad').write_text('module helper(){}')
        rows = publisher.discover(self.repo)
        self.assertEqual(len(rows), 2)
        self.assertEqual(next(r for r in rows if r['version'] == second.name)['source_path'].name, 'gripper.scad')
        third = base / 'v003_in_progress'
        third.mkdir()
        (third / 'gripper.scad').write_text('cube(3);')
        self.assertEqual(len(publisher.discover(self.repo)), 3)

    def test_public_families_keep_versions_and_exclude_deleted_prototypes(self):
        for project in ('ORCA CC-BY Prototype', 'Two Finger Gripper', 'Three Finger Gripper'):
            folder = self.repo / project / 'versions/v001_study'
            folder.mkdir(parents=True)
            (folder / 'main.scad').write_text('cube(1);')
        for project, filename in [('Aero Derived Prototype', 'assembly/assembled_hand.scad'),
                                  ('MIT Hand Prototype', 'openscad/inspect_parts.scad')]:
            source = self.repo / project / filename
            source.parent.mkdir(parents=True)
            source.write_text('cube(2);')
        rows = publisher.discover(self.repo)
        self.assertEqual(len(rows), 3)
        self.assertEqual({r['project'] for r in rows}, {'Orca Hand', 'Generalist Gripper'})
        self.assertEqual(len({r['id'] for r in rows}), 3)
        self.assertEqual(sum(r['project'] == 'Generalist Gripper' for r in rows), 2)
        self.assertTrue(all(r['source_path'].is_file() for r in rows))

    def test_retired_gripper_branches_stay_out_of_live(self):
        for project, version in [('Two Finger Gripper', 'v001_motor_force_layout'),
                                 ('Two Finger Gripper', 'v002_two_parallel_modules'),
                                 ('Three Finger Gripper', 'v001_dorsal_linkage'),
                                 ('Two Finger Gripper', 'v003_single_pincher')]:
            folder = self.repo / project / 'versions' / version
            folder.mkdir(parents=True)
            (folder / 'gripper.scad').write_text('cube(1);')
        rows = publisher.discover(self.repo)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], 'Gen 3')
        self.assertEqual(rows[0]['version'], 'gen_03')
        self.assertTrue((self.repo / 'Two Finger Gripper/versions/v002_two_parallel_modules/gripper.scad').exists())

    def test_positioned_parts_keep_authored_explode_offsets(self):
        folder = self.repo / 'Two Finger Gripper/versions/v003_single_pincher'
        folder.mkdir(parents=True)
        (folder / 'gripper.scad').write_text('cube(1);')
        (folder / 'jaw.stl').write_bytes(b'positioned part')
        (folder / 'viewer_parts.json').write_text(json.dumps({'parts': [
            {'path': 'jaw.stl', 'name': 'Jaw', 'color': '#ffaa00', 'explode': [20, 0, 15]}]}))
        row, = publisher.discover(self.repo)
        with patch.object(publisher, 'run_scad', side_effect=lambda source, target, *a, **k: target.write_bytes(b'preview')):
            result = publisher.publish_entry(row, self.out, self.repo)
        self.assertEqual(result['models'][0]['explode'], [20, 0, 15])
        self.assertEqual(result['models'][0]['name'], 'Jaw')

    def test_declared_parts_survive_a_source_saved_after_export(self):
        # voice-caae8e01: gripper.scad saved a minute after its parts were exported published one merged mesh,
        # so the slider's ^Left/^Right hinges matched nothing and Gen 16 could not close.
        import os
        folder = self.repo / 'Two Finger Gripper/versions/v016_generalist_rounded_point'
        (folder / 'exports/parts').mkdir(parents=True)
        for side in ('left', 'right'):
            (folder / f'exports/parts/{side}.stl').write_bytes(b'finger')
            os.utime(folder / f'exports/parts/{side}.stl', (1, 1))
        (folder / 'gripper.scad').write_text('cube(1);')
        (folder / 'web').mkdir()
        (folder / 'web/concept.js').write_text('')
        (folder / 'viewer_parts.json').write_text(json.dumps({'parts': [
            {'path': 'exports/parts/left.stl', 'name': 'Left finger'}, {'path': 'exports/parts/right.stl', 'name': 'Right finger'}]}))
        compare = self.repo / 'cad/compare'
        compare.mkdir(parents=True)
        (compare / 'designs.py').write_text((publisher.REPO / 'cad/compare/designs.py').read_text())
        (self.repo / 'cad/openscad').mkdir()
        rows = publisher.discover(self.repo)
        self.assertEqual([r['name'] for r in rows], ['Gen 16'])   # designs.py lists the concept folder too; once only
        with patch.object(publisher, 'run_scad', side_effect=lambda source, target, *a, **k: target.write_bytes(b'merged')):
            result = publisher.publish_entry(rows[0], self.out, self.repo)
        self.assertEqual([m['name'] for m in result['models']], ['Left finger', 'Right finger'])
        self.assertTrue(result['parts_older_than_source'])

    def test_every_posed_gripper_publishes_its_hinge_parts(self):
        """Every poses.js gripper the repo publishes is served as parts its hinges move, under one id."""
        import re
        text = (publisher.REPO / 'cad/mobile_gallery/poses.js').read_text()
        poses = json.loads(text[text.index('{'):text.rindex('}') + 1])
        rows = publisher.discover()
        ids = [r['id'] for r in rows]
        self.assertEqual(len(ids), len(set(ids)), 'duplicate catalog ids')
        for row in rows:
            if row['id'] not in poses or not row['existing']:
                continue   # STLs are gitignored: a fresh checkout has none to check
            with self.subTest(row['id']):
                self.assertTrue(row.get('declared_parts'), 'served as one merged assembly; the slider cannot move it')
                names = [m['name'] for m in row['existing']]
                for hinge in poses[row['id']]['hinges']:
                    self.assertTrue(any(re.search(hinge['match'], n) for n in names), f"hinge {hinge['match']!r} moves no part")

    def test_recursive_dynamic_dependencies_and_reject_external_paths(self):
        row = self.row()
        source = row['source_path']
        meshdir = source.parent / 'source'
        meshdir.mkdir()
        mesh = meshdir / 'part.stl'
        mesh.write_text('mesh')
        source.write_text(source.read_text() + '\nimport(str("source/", part, ".stl"));')
        self.assertIn(mesh, publisher.dependencies(source, self.repo))
        external = self.root / 'private.scad'
        external.write_text('secret')
        source.write_text('include <../../private.scad>')
        with self.assertRaisesRegex(ValueError, 'outside curated'):
            publisher.dependencies(source, self.repo)

    def test_cache_invalidates_dependency_not_readme_and_keeps_good_on_failure(self):
        row = self.row()
        calls = []
        def render(source, target, defines, timeout, preview=False):
            calls.append(target.suffix)
            target.write_bytes(b'preview' if preview else b'good mesh')
        with patch.object(publisher, 'run_scad', side_effect=render):
            first = publisher.publish_entry(row, self.out, self.repo)
            self.assertEqual(calls, ['.stl', '.png'])
            second = publisher.publish_entry(row, self.out, self.repo)
            self.assertEqual(len(calls), 2)
            (row['folder'] / 'README.md').write_text('New progress notes')
            publisher.publish_entry(row, self.out, self.repo)
            self.assertEqual(len(calls), 2)
            (row['folder'] / 'dimensions.scad').write_text('size=20;')
            latest = publisher.publish_entry(row, self.out, self.repo)
            self.assertEqual(len(calls), 4)
        (row['folder'] / 'dimensions.scad').write_text('size=broken;')
        pending = publisher.publish_entry(row, self.out, self.repo, build=False)
        self.assertEqual(pending['export_status'], 'pending export')
        self.assertEqual(pending['models'], latest['models'])
        self.assertEqual(pending['preview'], latest['preview'])
        with patch.object(publisher, 'run_scad', side_effect=RuntimeError('unfinished source')):
            failed = publisher.publish_entry(row, self.out, self.repo)
        self.assertEqual(failed['export_status'], 'export failed')
        self.assertEqual(failed['models'], latest['models'])
        self.assertEqual((self.out / failed['models'][0]['path']).read_bytes(), b'good mesh')
        self.assertTrue(failed['last_success_at'])
        self.assertTrue((self.out / failed['source']).is_file())
        self.assertEqual((row['folder'] / 'dimensions.scad').read_text(), 'size=broken;')

    def test_preview_failure_keeps_previous_mesh_and_preview_pair(self):
        row = self.row()
        def render(source, target, defines, timeout, preview=False):
            target.write_bytes(b'old preview' if preview else b'old mesh')
        with patch.object(publisher, 'run_scad', side_effect=render):
            first = publisher.publish_entry(row, self.out, self.repo)
        (row['folder'] / 'dimensions.scad').write_text('size=30;')
        def broken_preview(source, target, defines, timeout, preview=False):
            if preview:
                raise RuntimeError('preview unfinished')
            target.write_bytes(b'new mesh')
        with patch.object(publisher, 'run_scad', side_effect=broken_preview):
            failed = publisher.publish_entry(row, self.out, self.repo)
        self.assertEqual(failed['models'], first['models'])
        self.assertEqual(failed['preview'], first['preview'])
        self.assertEqual((self.out / first['models'][0]['path']).read_bytes(), b'old mesh')
        self.assertEqual((self.out / first['preview']).read_bytes(), b'old preview')

    def test_failed_openscad_never_replaces_good_artifact(self):
        row = self.row()
        target = self.out / 'assembly.stl'
        target.write_bytes(b'previous good mesh')
        def execute(command, **kwargs):
            Path(command[2]).write_bytes(b'partial damaged mesh')
            return SimpleNamespace(returncode=0, stderr='ERROR: nonmanifold')
        with patch.object(publisher.subprocess, 'run', side_effect=execute):
            with self.assertRaises(RuntimeError):
                publisher.run_scad(row['source_path'], target, [], 1)
        self.assertEqual(target.read_bytes(), b'previous good mesh')
        self.assertFalse((self.out / 'assembly.building.stl').exists())

    def test_binary_encoding_preserves_triangle_and_is_idempotent(self):
        import struct
        path = self.out / 'triangle.stl'
        path.write_text('solid test\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendloop\nendfacet\nendsolid test\n')
        publisher.compact_stl(path)
        data = path.read_bytes()
        self.assertEqual(len(data), 134)
        self.assertEqual(struct.unpack_from('<I', data, 80)[0], 1)
        self.assertEqual(struct.unpack_from('<12fH', data, 84),
                         (0., 0., 1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0))
        publisher.compact_stl(path)
        self.assertEqual(path.read_bytes(), data)

    def test_bundle_contains_only_needed_source_and_not_private_repo_files(self):
        row = self.row()
        (self.repo / 'private-key.txt').write_text('private')
        result = publisher.publish_entry(row, self.out, self.repo, build=False)
        import zipfile
        with zipfile.ZipFile(self.out / result['source_bundle']) as archive:
            self.assertEqual(set(archive.namelist()), {'Study/main.scad', 'Study/dimensions.scad'})
        self.assertFalse(any(p.name == 'private-key.txt' for p in self.out.rglob('*')))


if __name__ == '__main__':
    unittest.main()
