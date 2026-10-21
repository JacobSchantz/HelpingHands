"""The live preview's landing page (voice-1a2680b8): the Generalist assembly lists Gripper, Handle, Base, Mount, Arm, each with a
version selector, beside the 3D view, and the Aero Hand is never among its options (it is its own family). model.js is checked
under Node on a fixture catalog; the page itself is checked in headless Chrome against serve_designs.py when Chrome is installed."""
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request

REPO = Path(__file__).resolve().parents[1]
GALLERY = REPO / 'cad/mobile_gallery'
CHROME = next((p for p in ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', shutil.which('google-chrome') or '',
                           shutil.which('chromium') or '') if p and Path(p).exists()), None)


def design(project, name, models, **extra):
    return dict(id=(project + '-' + name).lower().replace(' ', '-'), project=project, name=name,
                models=[dict(name=m, path='assets/' + m.split(' — ')[0].lower().replace(' ', '-') + '.stl', color='#cbd9e2') for m in models], **extra)


CATALOG = {'schema_version': 1, 'generated_at': '2026-10-20T00:00:00Z', 'designs': [
    design('Generalist Gripper', 'Gripper 20', ['Left finger — a', 'Right finger — b']),
    design('Generalist Gripper', 'Handle 5', ['Left finger — a', 'Right finger — b', 'Left strap slide — c', 'Right strap slide — d'], fingers='20'),
    design('Generalist Gripper', 'Handle 6', ['Left finger — a', 'Right finger — b', 'Left strap slide — c', 'Right strap slide — d'], fingers='21'),
    design('Generalist Gripper', 'Base 3', ['Left finger — a', 'Right finger — b', 'Base — plate', 'Gear — drive'], fingers='21'),
    design('Generalist Gripper', 'Base 10', ['Left finger — a', 'Right finger — b', 'Base — plate', 'Motor — RS00', 'Wrist hub — on J6', 'reBot Arm B601-RS — ref'],
           fingers='21', carries={'Mount': '1'}),
    design('Generalist Gripper', 'Mount 1', ['Wrist hub — on J6', 'Tool plate — gripper', 'Aero Hand tool plate — hand'], fits={'Arm': '1'}),
    design('Generalist Gripper', 'Mount 2', ['Wrist hub — on the horn'], fits={'Arm': '2'}, tool_plate='1', builds_on='Mount 1'),
    design('Generalist Gripper', 'Arm 1', ['reBot Arm B601-RS — ref']),
    design('Generalist Gripper', 'Arm 2', ['SO-101 Arm — ref']),
    design('Aero Hand', 'Aero Hand 1 assembly', ['Left finger — a', 'Aero Hand (left) palm — ref']),
    design('Aero Hand', 'Aero Hand 1', ['Aero Hand (left) palm — ref', 'Aero Hand (left) thumb — ref'], fits={'Arm': '1', 'Mount': '1'}, on_mount=[-230, 0, 0]),
    design('Glove Hand', 'Glove Hand gen 01 · fit tray', ['Tray — a']),
]}

# Runs under Node (cad/mobile_gallery/package.json makes it an ES module) and prints what the page would show.
SCRIPT = '''
import {MIX, AERO_MIX, buildMix, initialPicks} from %r;
const catalog = JSON.parse(process.argv[1]), out = {parts: MIX.parts, aero_parts: AERO_MIX.parts, steps: {}};
const picks = initialPicks(new URLSearchParams(''));
const snap = mix => ({name: mix.name, rows: mix.rows.map(row => ({key: row.key, version: row.chosen ? row.chosen.version : null,
  options: row.options.map(item => item.design.name), notes: row.notes.map(note => note.text)})), parts: mix.models.map(model => model.name)});
out.steps.landing = snap(buildMix(catalog, picks, MIX));
out.steps.aero = snap(buildMix(catalog, picks, AERO_MIX));
picks[AERO_MIX.id].arm = '1'; out.steps.aero_arm1 = snap(buildMix(catalog, picks, AERO_MIX, 'arm'));
const step = (key, value) => { picks[MIX.id][key] = value; out.steps[key + '=' + value] = snap(buildMix(catalog, picks, MIX, key)); };
step('arm', '1'); step('arm', '2'); step('mount', 'none'); step('mount', '2'); step('base', '3'); step('base', '10'); step('gripper', '20');
picks[MIX.id].mount = '1';   // a refresh (no change) keeps a pick that does not fit, with its flag
out.steps.refresh = snap(buildMix(catalog, picks, MIX));
console.log(JSON.stringify(out));
'''


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('node'):
            raise unittest.SkipTest('node is not installed')
        script = SCRIPT % str(GALLERY / 'model.js')
        run = subprocess.run(['node', '--input-type=module', '-e', script, json.dumps(CATALOG)], capture_output=True, text=True, cwd=GALLERY)
        assert run.returncode == 0, run.stderr
        cls.out = json.loads(run.stdout)

    def test_landing_lists_gripper_handle_base_mount_arm_in_that_order(self):
        self.assertEqual(self.out['parts'], ['gripper', 'handles', 'base', 'mount', 'arm'])
        landing = self.out['steps']['landing']
        self.assertEqual([row['key'] for row in landing['rows']], ['gripper', 'handles', 'base', 'mount', 'arm'])
        self.assertEqual([row['version'] for row in landing['rows']], ['21', '6', '10', None, None])   # newest of each, hand-held
        self.assertEqual(landing['name'], 'Gripper 21 + Handle 6 + Base 10')

    def test_aero_hand_is_not_a_generalist_option(self):
        for name, step in self.out['steps'].items():
            if name.startswith('aero'):
                continue
            offered = [option for row in step['rows'] for option in row['options']]
            self.assertFalse([o for o in offered if o.startswith('Aero Hand')], (name, offered))
            self.assertFalse([p for p in step['parts'] if p.startswith('Aero Hand')], (name, step['parts']))   # nor its tool plate
        aero = self.out['steps']['aero']
        self.assertEqual(self.out['aero_parts'], ['aero', 'mount', 'arm'])
        # the newest of each; Aero Hand 1 fits Mount 2 through Mount 1's tool plate, so nothing is flagged
        self.assertEqual([(row['key'], row['version'], row['notes']) for row in aero['rows']], [('aero', '1', []), ('mount', '2', []), ('arm', '2', [])])
        on_arm1 = self.out['steps']['aero_arm1']   # Arm 1 brings Mount 1, whose plate for the hand is drawn (the gripper's is not)
        self.assertEqual([(row['key'], row['version']) for row in on_arm1['rows']], [('aero', '1'), ('mount', '1'), ('arm', '1')])
        self.assertIn('Aero Hand tool plate — hand', on_arm1['parts'])
        self.assertNotIn('Tool plate — gripper', on_arm1['parts'])
        self.assertEqual(aero['rows'][0]['options'], ['Aero Hand 1'])

    def test_mount_follows_the_arm_and_other_parts_are_flagged(self):
        steps = self.out['steps']
        rows = lambda name: {row['key']: row for row in steps[name]['rows']}
        self.assertEqual((rows('arm=1')['mount']['version'], rows('arm=1')['mount']['notes']), ('1', ['Mount 1 follows Arm 1.']))
        self.assertEqual((rows('arm=2')['mount']['version'], rows('arm=2')['mount']['notes']), ('2', ['Mount 2 follows Arm 2.']))
        # dropping the Mount flags the Arm (nothing is switched off for the user) and leaves it on
        self.assertEqual((rows('mount=none')['arm']['version'], rows('mount=none')['arm']['notes']), ('2', ['Base 10 needs a Mount to sit on Arm 2.']))
        self.assertEqual(rows('mount=2')['base']['notes'], [])   # Mount 2 takes Mount 1's tool plate, so Base 10 fits
        # a hand-held Base is flagged against the Mount it was just put under, not swapped for one with a bracket
        self.assertEqual(rows('base=3')['base']['version'], '3')
        self.assertEqual(rows('base=3')['mount']['notes'], ["Base 3 has no wrist bracket (hand-held), so it does not fit Mount 2's tool plate."])
        # Gripper 20: the Handle (an adapter) follows to the one built on it, the Base keeps a flag
        self.assertEqual((rows('gripper=20')['handles']['version'], rows('gripper=20')['handles']['notes']), ('5', ['Handle 5 follows Gripper 20.']))
        self.assertEqual(rows('gripper=20')['base']['notes'], ["Base 10 was built on Gripper 21; Gripper 20's hinges may not line up."])
        self.assertEqual((rows('refresh')['mount']['version'], rows('refresh')['mount']['notes']), ('1', ['Mount 1 fits Arm 1, not Arm 2.']))


class LandingPageTests(unittest.TestCase):
    """serve_designs.py serving the real page over a fixture catalog, rendered by headless Chrome."""

    @classmethod
    def setUpClass(cls):
        if CHROME is None:
            raise unittest.SkipTest('Chrome is not installed')
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name) / 'gallery'
        root.mkdir()
        for name in ('index.html', 'gallery.js', 'model.js', 'poses.js', 'human_hand.js'):
            shutil.copy2(GALLERY / name, root / name)
        shutil.copytree(GALLERY / 'reference', root / 'reference', ignore=shutil.ignore_patterns('*.py'))
        shutil.copytree(REPO / 'cad/compare/vendor', root / 'vendor')
        (root / 'catalog.json').write_text(json.dumps(CATALOG))
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            cls.port = probe.getsockname()[1]
        cls.server = subprocess.Popen([sys.executable, str(REPO / 'Scripts/serve_designs.py'), '--no-publish', '--directory', str(root),
                                       '--port', str(cls.port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(50):
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{cls.port}/health.json', timeout=1)
                break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError('serve_designs.py did not start')

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait()
        cls.tmp.cleanup()

    def dom(self, query=''):
        profile = Path(self.tmp.name) / 'chrome'
        run = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--virtual-time-budget=10000',
                              f'--user-data-dir={profile}', '--dump-dom', f'http://127.0.0.1:{self.port}/{query}'],
                             capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        return run.stdout

    def test_landing_is_the_parts_list_and_the_3d_view(self):
        dom = self.dom()
        selectors = [label for label in ('Gripper', 'Handle', 'Base', 'Mount', 'Arm', 'Aero Hand') if f'aria-label="{label} version"' in dom]
        self.assertEqual(selectors, ['Gripper', 'Handle', 'Base', 'Mount', 'Arm'])
        self.assertEqual([dom.index(f'aria-label="{label} version"') for label in selectors], sorted(dom.index(f'aria-label="{label} version"') for label in selectors))
        self.assertIn('aria-label="Design family"', dom)
        self.assertIn('data-design-id="generalist-mix"', dom)
        for clutter in ('<header', 'id="presets"', 'id="shown"', 'id="back"', 'id="refresh"', 'class="mixer"'):
            self.assertNotIn(clutter, dom)

    def test_a_mount_that_does_not_fit_the_arm_is_flagged_in_its_row(self):
        dom = self.dom('?arm=2&mount=1')
        self.assertIn('⚠ Mount 1 fits Arm 1, not Arm 2.', dom)

    def test_every_design_has_a_reference_photo_toggle_off_by_default(self):
        dom = self.dom()
        self.assertIn('aria-label="Show reference photo"', dom)
        self.assertNotIn('class="viewport photo-tile"', dom)

    def test_photo_on_shows_it_inline_beside_the_views(self):
        dom = self.dom('?photo=side')
        self.assertIn('aria-label="Hide reference photo"', dom)
        self.assertIn('data-photo="side"', dom)
        self.assertIn('src="reference/side.png"', dom)
        self.assertLess(dom.index('data-design-id="generalist-mix"'), dom.index('class="viewport photo-tile"'))

    def test_a_family_with_no_photo_still_has_the_toggle_greyed(self):
        dom = self.dom('?photo=1#glove-hand-glove-hand-gen-01-·-fit-tray')
        self.assertIn('No reference photo yet', dom)
        self.assertNotIn('class="viewport photo-tile"', dom)

    def test_the_average_human_hand_is_off_by_default_and_its_controls_show_when_on(self):
        dom = self.dom()
        self.assertIn('aria-label="Show average human hand"', dom)
        self.assertNotIn('aria-label="Thumb bend"', dom)
        dom = self.dom('?hand=left&curl=40')
        self.assertIn('aria-label="Hide average human hand"', dom)
        for finger in ('All fingers', 'Thumb', 'Index', 'Middle', 'Ring', 'Pinky'):
            self.assertIn(f'aria-label="{finger} bend"', dom)


if __name__ == '__main__':
    unittest.main()
