"""The gallery's Open/Closed slider covers every gripper, about its real hinge.

cad/mobile_gallery/poses.js is hand-written, so it goes stale when a generation is
added or its .scad changes (voice-b7ae5fc0: Gen 7's pivot drifted 4.5 mm and Gens 9
and 10 had no entry). This fails when that happens.

    python3 -m unittest Scripts/test_gripper_poses.py
"""
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
CATALOG = Path.home() / 'HelpingHands-tools/design-gallery/catalog.json'
VERSIONS = REPO / 'Two Finger Gripper/versions'
OPENSCAD = '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'


def poses():
    text = (REPO / 'cad/mobile_gallery/poses.js').read_text()
    return {k: v for k, v in json.loads(text[text.index('{'):text.rindex('}') + 1]).items() if not k.startswith('_')}


def scad_values(source, names):
    """The values OpenSCAD computes for top-level variables of a .scad (its defaults)."""
    with tempfile.TemporaryDirectory() as tmp:
        wrapper, out = Path(tmp) / 'w.scad', Path(tmp) / 'out.echo'
        wrapper.write_text(f'include <{source}>\n' + ''.join(f'echo({n}={n});\n' for n in names))
        subprocess.run([OPENSCAD, '-D', 'part="none"', '-o', str(out), str(wrapper)], capture_output=True, timeout=120)
        echoed = dict(re.findall(r'ECHO: (\w+) = (\S+)', out.read_text() if out.exists() else ''))
    return {n: float(echoed[n]) for n in names if n in echoed}


class GripperPoseTests(unittest.TestCase):
    def test_every_gripper_in_the_gallery_opens_and_closes(self):
        if not CATALOG.exists():
            self.skipTest('no published catalog on this machine')
        table = poses()
        for design in json.loads(CATALOG.read_text())['designs']:
            if design['project'] != 'Generalist Gripper' or not design.get('models') or design['id'].startswith('three-finger'):
                continue
            with self.subTest(design['id']):
                self.assertTrue(design['id'] in table, 'no hinge entry in poses.js, so its fingers will not move')
                names = [m['name'] for m in design['models']]
                for hinge in table[design['id']]['hinges']:
                    self.assertTrue(any(re.search(hinge['match'], n) for n in names), f"hinge {hinge['match']!r} moves no part")

    def test_hinges_match_the_scad(self):
        if not Path(OPENSCAD).exists():
            self.skipTest('OpenSCAD not installed')
        for design_id, pose in poses().items():
            match = re.match(r'two-finger-gripper-(v\d+)', design_id)
            folder = next(VERSIONS.glob(match.group(1) + '_*'), None) if match else None
            source = folder / 'gripper.scad' if folder else None
            if not source or not source.exists() or 'module placed' not in source.read_text():
                continue  # Gen 8 is placed from its URDF; demo grippers live elsewhere
            with self.subTest(design_id):
                values = scad_values(source, ['pivot', 'angle'])
                self.assertAlmostEqual(pose['hinges'][0]['pivot'][0], values['pivot'], delta=0.01)
                self.assertEqual(pose['exported'], values['angle'], 'STLs are exported at the .scad default angle')


if __name__ == '__main__':
    unittest.main()
