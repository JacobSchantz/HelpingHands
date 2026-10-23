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


# Runs under Node: the real hand (its GLB parsed from disk instead of fetched) holding Base 14's handles, its solids as boxes.
GRIP_SCRIPT = '''
import fs from 'fs';
import * as THREE from 'three';
globalThis.readGlb = side => { const b = fs.readFileSync(%r + side + '.glb'); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength); };
const {makeHand, sizeHand, gripHand, fingerContacts, handClearance} = await import('./human_hand.js');
const box = (a, b) => new THREE.Box3(new THREE.Vector3(...a), new THREE.Vector3(...b));
const solids = [box([-11.5, -12.7, -54.2], [21.3, 6, -21.3]), box([-42.4, -15.5, -62], [42.4, -6.4, 11]),
  box([-42.8, -11, -55.3], [42.8, 10.3, 11.5]), box([-7.5, -49.4, -48], [17.3, -11.2, -2.6])];
const spot = x => ({point: new THREE.Vector3(x, -1.6, 28), normal: new THREE.Vector3(Math.sign(x), 0, 0)});
const out = [];
for (const [side, x] of [['right', 46], ['right', 33], ['left', 46]]) {
  const root = await makeHand(side), scene = new THREE.Scene(); scene.add(root); sizeHand(root, 187.2);
  const near = side === 'right' ? x : -x, miss = gripHand(root, spot(near), spot(-near), solids);
  scene.updateMatrixWorld(true);
  const joint = name => new THREE.Vector3().setFromMatrixPosition(root.userData.bones[name].matrixWorld);
  const buried = Object.keys(root.userData.bones).filter(name => solids.some(b => b.clone().expandByScalar(-3).containsPoint(joint(name))));
  out.push({side, x, miss, buried, thumb: joint('thumb-tip').x, index: joint('index-finger-tip').x});
  gripHand(root, spot(near), spot(-near), solids, {indexOnly:true, radius:8});
  const wrist = root.userData.grip.slice(0, 6), rotation = root.quaternion.toArray();
  const tilted = spot(-near * 10); tilted.point.z += 100;
  gripHand(root, spot(near * 10), tilted, solids, {indexOnly:true, radius:8, lockWrist:true});
  out[out.length - 1].fixed = {before:wrist, after:root.userData.grip.slice(0, 6), rotationBefore:rotation, rotationAfter:root.quaternion.toArray(), ...root.userData.fit};
  // Deliberately bury the entire hand; diagnostic must report overlap, rather than claiming a fit.
  gripHand(root, spot(near), spot(-near), [box([-1000,-1000,-1000],[1000,1000,1000])], {indexOnly:true, lockWrist:true});
  out[out.length - 1].buriedFit = root.userData.fit;

}
// Real contact selection contract: outside each finger, never the bulky handle;
// same material station and normal through motion, mirrored for the left hand.
const namedBox = (name, x, width) => {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, 12, 100));
  mesh.position.x = x; mesh.userData.name = name; return mesh;
};
const right = namedBox('Right finger — test', 20, 10), left = namedBox('Left finger — test', -20, 10);
const decoy = namedBox('Right handle — must never target', 60, 30);
const meshes = [decoy, right, left], contacts = [];
for (const angle of [0, .3, -.4]) {
  right.rotation.y = angle; left.rotation.y = -angle;
  for (const side of ['right', 'left']) {
    const pair = fingerContacts(meshes, side, 30);
    contacts.push({side, angle, local:pair.map((spot,i) => {
      const mesh = side === 'right' ? [right,left][i] : [left,right][i];
      return {point:mesh.worldToLocal(spot.point.clone()).toArray(),
        normal:spot.normal.clone().transformDirection(mesh.matrixWorld.clone().invert()).toArray()};
    })});
  }
}
// Whole posed skin, including wrist/palm and unused digits, must be screened.
const complete = await makeHand('right'); sizeHand(complete,187.2);
const {poseHand} = await import('./human_hand.js');
poseHand(complete,{thumb:.2,index:.3,middle:.4,ring:.5,pinky:.6});
complete.updateMatrixWorld(true);
const skin=[]; complete.traverse(m=>{if(m.isSkinnedMesh){m.skeleton.update();for(let i=0;i<m.geometry.attributes.position.count;i++)skin.push(m.getVertexPosition(i,new THREE.Vector3()).applyMatrix4(m.matrixWorld));}});
const envelope=new THREE.Box3().setFromPoints(skin).expandByScalar(1);
out[0].whole=handClearance(complete,[envelope]);
// Thin obstacle in a triangle interior, away from all its vertices.
let thin;
complete.traverse(m=>{if(m.isSkinnedMesh&&!thin){const g=m.geometry,ix=g.index;for(let i=0;i<(ix?ix.count:skin.length);i+=3){const ids=[0,1,2].map(j=>ix?ix.getX(i+j):i+j);const center=new THREE.Vector3().add(skin[ids[0]]).add(skin[ids[1]]).add(skin[ids[2]]).multiplyScalar(1/3);const b=new THREE.Box3().setFromCenterAndSize(center,new THREE.Vector3(.001,.001,.001));if(!skin.some(v=>b.containsPoint(v))){thin=b;break;}}}});
out[0].thin=handClearance(complete,[thin]);
const contact=x=>({point:new THREE.Vector3(x,0,30),normal:new THREE.Vector3(Math.sign(x),0,0)});
const curled=[];
for(const freeCurl of [.2,.8]){gripHand(complete,contact(30),contact(-30),[],{indexOnly:true,lockWrist:true,freeCurl});complete.updateMatrixWorld(true);curled.push({wrist:complete.userData.grip.slice(0,6),tips:['middle','ring','pinky'].map(f=>new THREE.Vector3().setFromMatrixPosition(complete.userData.bones[f+'-finger-tip'].matrixWorld).toArray())});}
out[0].curled=curled;
out[0].clear=handClearance(complete,[box([10000,10000,10000],[10001,10001,10001])]);
out[0].contacts = contacts;
out[0].missingFinger = fingerContacts([decoy, left], 'right', 30);
console.log(JSON.stringify(out));
'''


class HandGripTests(unittest.TestCase):
    """human_hand.js's gripHand (Holding the gripper): thumb and index pads on the two handles' outer faces, no joint in the base."""

    @classmethod
    def setUpClass(cls):
        if not shutil.which('node'):
            raise unittest.SkipTest('node is not installed')
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        three = root / 'node_modules/three'
        (three / 'addons').mkdir(parents=True)
        vendor = REPO / 'cad/compare/vendor'
        for name in ('three.module.min.js', 'three.core.min.js'):
            shutil.copy2(vendor / name, three / name)
        for name in ('loaders', 'utils'):
            shutil.copytree(vendor / name, three / 'addons' / name)
        (three / 'package.json').write_text(json.dumps({'name': 'three', 'type': 'module', 'exports': {'.': './three.module.min.js', './addons/*': './addons/*'}}))
        (root / 'package.json').write_text('{"type": "module"}')
        source = (GALLERY / 'human_hand.js').read_text()
        fetch = "loader.loadAsync('reference/human_hand/' + side + '.glb')"
        assert fetch in source
        (root / 'human_hand.js').write_text(source.replace(fetch, "loader.parseAsync(globalThis.readGlb(side), '')"))
        script = GRIP_SCRIPT % (str(GALLERY / 'reference/human_hand') + '/')
        run = subprocess.run(['node', '--input-type=module', '-e', script], capture_output=True, text=True, cwd=root, timeout=120)
        assert run.returncode == 0, run.stderr
        cls.out = json.loads(run.stdout)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_pads_land_on_the_handles_open_and_closed_either_hand(self):
        for grip in self.out:
            self.assertLess(grip['miss'], 6, grip)

    def test_thumb_and_fingers_are_on_opposite_handles(self):
        for grip in self.out:
            sign = 1 if grip['side'] == 'right' else -1
            self.assertGreater(sign * grip['index'], 30, grip)
            self.assertLess(sign * grip['thumb'], -25, grip)

    def test_contacts_follow_outer_finger_faces_without_handles(self):
        for sample in self.out[0]['contacts']:
            sign = 1 if sample['side'] == 'right' else -1
            for i, contact in enumerate(sample['local']):
                outward = sign if i == 0 else -sign
                self.assertAlmostEqual(contact['point'][0], outward * 5)
                self.assertAlmostEqual(contact['point'][1], 0)
                self.assertAlmostEqual(contact['point'][2], 20)
                self.assertAlmostEqual(contact['normal'][0], outward)
        self.assertIsNone(self.out[0]['missingFinger'])

    def test_fixed_wrist_exposes_unreachable_opening(self):
        for grip in self.out:
            fit = grip['fixed']
            self.assertEqual(fit['before'], fit['after'])
            self.assertTrue(fit['wristLocked'])
            self.assertGreater(fit['miss'], 100)
            self.assertAlmostEqual(fit['span'], ((grip['x'] * 20) ** 2 + 100 ** 2) ** .5)
            self.assertEqual(fit['rotationBefore'], fit['rotationAfter'])

    def test_complete_skin_is_screened_by_region(self):
        whole = self.out[0]['whole']
        self.assertGreater(whole['vertices'], 100)
        self.assertGreater(whole['triangles'], 100)
        self.assertEqual(whole['intersectingTriangles'], whole['triangles'])
        for region in ('wrist', 'palm', 'thumb', 'index', 'middle', 'ring', 'pinky'):
            self.assertGreater(whole['regions'][region], 0, region)
        self.assertEqual(self.out[0]['clear']['intersectingTriangles'], 0)

    def test_thin_obstacle_between_skin_vertices_is_detected(self):
        self.assertGreater(self.out[0]['thin']['intersectingTriangles'], 0)

    def test_other_three_digits_move_without_moving_wrist(self):
        before, after = self.out[0]['curled']
        self.assertEqual(before['wrist'], after['wrist'])
        for a, b in zip(before['tips'], after['tips']):
            self.assertGreater(sum((x-y)**2 for x,y in zip(a,b)), 25)

    def test_collision_diagnostic_has_a_positive_control(self):
        for grip in self.out:
            self.assertGreater(grip['buriedFit']['penetration'], 100)

    def test_no_joint_is_inside_the_base(self):
        for grip in self.out:
            self.assertEqual(grip['buried'], [], grip)

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

    def test_holding_the_gripper_swaps_the_bend_sliders_for_a_note(self):
        dom = self.dom('?hand=1&handat=grip')
        self.assertIn('Holding the gripper', dom)
        self.assertIn('class="hand-note"', dom)
        self.assertNotIn('aria-label="Thumb bend"', dom)
        for label in ('Hand length (mm)', 'Digit pad radius (mm)', 'Contact down finger (%)', 'Other digits curl open (%)', 'Other digits curl closed (%)'):
            self.assertIn(f'aria-label="{label}"', dom)
        self.assertIn('Check 13 stroke positions', dom)
        self.assertIn('Copy fit report', dom)
        self.assertIn('Fix wrist through stroke', dom)


if __name__ == '__main__':
    unittest.main()
