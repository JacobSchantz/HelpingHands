import * as THREE from 'three';
import {STLLoader} from 'three/addons/STLLoader.js';
import {OrbitControls} from 'three/addons/OrbitControls.js';
import POSES from './poses.js';
import PHOTOS from './reference/photos.js';
import {SIZES, FINGERS, makeHand, sizeHand, poseHand, gripHand, attachmentSpot} from './human_hand.js';
import {MIX, MIXES, mixOf, initialPicks, buildMix, optionLabel, partOrder, part} from './model.js';

// The page is two things (voice-1a2680b8): the 3D view, and beside it the parts list, which is also the navigation. A mix family
// (Generalist Gripper, Aero Hand) shows its assembly, one row per part with the version it is at and a selector to switch it
// (model.js builds the assembly and follows or flags the parts a change affects). Any other family lists its versions; tapping
// one shows it alone. Each part's own pieces hang under its row with an eye to hide them.
const $ = id => document.getElementById(id);
const stage = $('stage'), grid = $('viewports');
const views = new Map();
// Design ids hidden from a family's comparison: hidden.json beside the catalog, written by Scripts/design_visibility.py.
let hidden = new Set();
let renderer, catalog, focused = null, currentProject = '', webglError = '', refreshing = false, exploded = false;
// How far apart the parts are right now: 0 assembled, 1 exploded. The Explode button eases it between the two.
let explodeAmount = 0, explodeRun = 0;
const query = new URLSearchParams(location.search);
// ?only=1 shows just the 3D view (Pebbles' Live tile, voice-c78e2494): with #<design id>, that one design fills the page.
if (query.get('only') === '1') document.body.classList.add('only');
// Open/Closed: 0 = closed, 1 = fully open, the same fraction for every design shown. ?open=0..100 presets it (screenshots, links).
const preset = query.get('open');
// ?view=top|front|side|iso lines every model up once each one loads (screenshots, links).
const startView = query.get('view');
let openness = preset !== null && isFinite(preset) ? Math.max(0, Math.min(100, +preset)) / 100 : 1;
const loader = new STLLoader();
// Each mix's picks, per part key: a version, 'none', or null for the newest. ?gripper=21&handles=6&base=none&arm=1 presets them.
const picks = initialPicks(query);
// View presets: the direction the camera looks from, in CAD axes (Z along the fingers).
const PRESETS = {top:[0, -1, 0], front:[0, -.002, 1], side:[1, 0, 0], iso:[.8, -1, .65]};
const mixFamily = project => MIXES.find(item => item.project === project);
// Reference photo (voice-c68a1812): every design has a toggle at the top of its parts list; on, the family's real photo
// (reference/photos.js, make_reference.py) is one more tile beside the 3D views, with a picker for which photo. It stays on
// across families and versions; a family with no photo greys the toggle. ?photo=1 (or ?photo=<id>, e.g. side) presets it.
const photoQuery = query.get('photo');
let photoOn = !!photoQuery && photoQuery !== '0', photoId = photoOn && photoQuery !== '1' ? photoQuery : '';
let photoTile = null;
// Average human hand (voice-bf770cd7, human_hand.js): a row under the reference photo puts it in every 3D view, its fingertips
// level with the gripper's, beside it or over it, or holding it (thumb/index on opposed attachments, fixed wrist by default). On, its controls hang under the row: size (ANSUR II means), which hand, where
// it sits, Open/Close, a slider per finger, and Follow, which bends it with the gripper's Open/Close (curl = 1 - openness).
// ?hand=1|right|left presets it on, ?curl=0..100 the bend (and Follow off), ?handsize=man|woman, ?handat=over|grip.
const handQuery = query.get('hand'), curlQuery = query.get('curl'), curlPreset = curlQuery !== null && isFinite(curlQuery);
const hand = {on: !!handQuery && handQuery !== '0', side: handQuery === 'left' ? 'left' : 'right',
  size: SIZES.some(size => size.id === query.get('handsize')) ? query.get('handsize') : 'adult', at: ['over', 'grip'].includes(query.get('handat')) ? query.get('handat') : 'beside',
  follow: !curlPreset, curls: {}, sliders: [], run: 0, length: null, radius: 8, contact: 50, lockWrist: true};
for (const finger of FINGERS) hand.curls[finger] = curlPreset ? Math.max(0, Math.min(100, +curlQuery)) / 100 : 1 - openness;

function message(text = '') { $('message').textContent = text; $('message').hidden = !text; }
function makeMesh(model, geometry, motion) {
  const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({color:model.color || '#cbd9e2', roughness:.65, metalness:.08}));
  mesh.userData.explode = new THREE.Vector3(...(model.explode || [0, 0, 0]));
  mesh.userData.shift = new THREE.Vector3(...(model.shift || [0, 0, 0]));
  mesh.userData.motion = motion; mesh.userData.name = model.name; mesh.userData.color = model.color || '#cbd9e2';
  return mesh;
}
function disposeMeshes(view) {
  for (const mesh of [...view.group.children]) {
    view.group.remove(mesh); mesh.geometry.dispose(); mesh.material.map?.dispose(); mesh.material.dispose();
  }
}
function removeView(view) {
  view.token++; view.controls?.dispose(); disposeMeshes(view); view.element.remove();
}
function frame(view) {
  if (!view.group.children.length || !view.element.clientWidth || !view.element.clientHeight) return;
  view.camera.aspect = view.element.clientWidth / view.element.clientHeight;
  const bounds = new THREE.Box3().setFromObject(view.group);
  if (view.hand?.visible) bounds.expandByObject(view.hand);
  const center = bounds.getCenter(new THREE.Vector3());
  const radius = Math.max(bounds.getSize(new THREE.Vector3()).length() / 2, 1);
  const distance = radius / Math.sin(THREE.MathUtils.degToRad(17.5)) / Math.min(view.camera.aspect, 1) * 1.08;
  view.camera.position.copy(center).add(new THREE.Vector3(.8, -1, .65).normalize().multiplyScalar(distance));
  view.camera.near = Math.max(.01, radius / 1000); view.camera.far = distance * 30;
  view.camera.updateProjectionMatrix(); view.controls?.target.copy(center); view.controls?.update();
}
// Look from `direction` at `bounds`, close enough that its extent across the screen fills the view.
function placeCamera(view, direction, bounds) {
  const {camera, element} = view, look = new THREE.Vector3(...direction).normalize();
  if (!element.clientWidth || !element.clientHeight) return;
  camera.aspect = element.clientWidth / element.clientHeight;
  const center = bounds.getCenter(new THREE.Vector3());
  camera.position.copy(center).add(look); camera.lookAt(center); camera.updateMatrixWorld();
  const right = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0);
  const up = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
  let width = 0, height = 0, depth = 0;
  for (const x of [bounds.min.x, bounds.max.x]) for (const y of [bounds.min.y, bounds.max.y]) for (const z of [bounds.min.z, bounds.max.z]) {
    const corner = new THREE.Vector3(x, y, z).sub(center);
    width = Math.max(width, Math.abs(corner.dot(right))); height = Math.max(height, Math.abs(corner.dot(up)));
    depth = Math.max(depth, Math.abs(corner.dot(look)));
  }
  const tan = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  const distance = depth + Math.max(height / tan, width / (tan * camera.aspect), 1) * 1.1;
  camera.position.copy(center).addScaledVector(look, distance);
  camera.near = Math.max(.01, distance / 1000); camera.far = distance * 30;
  camera.updateProjectionMatrix(); view.controls?.target.copy(center); view.controls?.update();
}
// ?view=: snap every tile on screen to one camera, same direction, centre and scale, framed on all the models together.
function alignAll(name) {
  const shown = [...views.values()].filter(view => !view.element.hidden && view.group.children.length);
  const bounds = new THREE.Box3();
  for (const view of shown) { bounds.expandByObject(view.group); if (view.hand?.visible) bounds.expandByObject(view.hand); }
  if (!bounds.isEmpty()) for (const view of shown) placeCamera(view, PRESETS[name], bounds);
}
// The photo tile sits after the shown views; the grid counts it as one more tile (focused: the one view and the photo side by side).
function placePhoto() {
  const photos = PHOTOS[currentProject] || [], show = photoOn && photos.length > 0;
  if (show && !photoTile) {
    photoTile = document.createElement('section'); photoTile.className = 'viewport photo-tile'; photoTile.dataset.photo = '';
    const label = document.createElement('span'), img = document.createElement('img'), select = document.createElement('select');
    label.className = 'label'; label.textContent = 'Reference photo'; select.setAttribute('aria-label', 'Which reference photo');
    select.onchange = () => { photoId = select.value; placePhoto(); };
    photoTile.append(img, label, select);
  }
  if (photoTile) {
    if (show) {
      const photo = photos.find(item => item.id === photoId) || photos[0], [img, , select] = photoTile.children;
      select.replaceChildren(...photos.map(item => new Option(item.label, item.id))); select.value = photo.id;
      if (img.getAttribute('src') !== photo.src) img.src = photo.src;
      img.alt = currentProject + ' reference photo: ' + photo.label; photoTile.dataset.photo = photo.id;
      grid.append(photoTile);
    } else photoTile.remove();
  }
  const count = (focused ? 1 : views.size) + (show ? 1 : 0) || 1;
  grid.style.setProperty('--columns', count === 4 ? 2 : Math.min(count, 3));
  grid.style.setProperty('--rows', count);
}
function photoRow() {
  const photos = PHOTOS[currentProject] || [], row = document.createElement('div'), label = document.createElement('span');
  row.className = 'part-row photo-row'; label.className = 'name'; label.textContent = 'Reference photo';
  const eye = eyeButton(!photoOn || !photos.length, 'reference photo', () => { photoOn = !photoOn; placePhoto(); renderPanel(); });
  eye.disabled = !photos.length;
  if (!photos.length) { label.textContent = 'No reference photo yet'; row.title = 'Add ' + currentProject + ' photos in cad/mobile_gallery/reference/make_reference.py'; }
  row.append(eye, label);
  return row;
}
// Put the hand in one view (loading its own clone the first time, or when the side changes), sized, bent and lined up: fingertips
// level with the gripper's fingers (the whole model when it has none), beside them in +X with a gap for a fist, or over them.
async function placeHand(view, preserveWrist = false) {
  if (!hand.on || !renderer) { if (view.hand) view.hand.visible = false; return; }
  if (view.hand?.userData.side !== hand.side) {
    const token = view.handToken = (view.handToken || 0) + 1;
    let made;
    try { made = await makeHand(hand.side); } catch (error) { message('Could not load the human hand. ' + error.message); return; }
    if (token !== view.handToken) return;
    if (view.hand) view.scene.remove(view.hand);
    view.hand = made; view.scene.add(made);
    if (!hand.on) { made.visible = false; return; }
  }
  const root = view.hand, length = hand.length || SIZES.find(size => size.id === hand.size).length;
  root.visible = true; sizeHand(root, length);
  root.userData.material.opacity = hand.at === 'over' ? .55 : 1;
  if (hand.at === 'grip') { if (!preserveWrist) root.userData.grip = null; if (holdGripper(view)) return; }
  poseHand(root, hand.curls); root.quaternion.identity();
  const fingers = view.group.children.filter(mesh => mesh.visible && /finger/i.test(mesh.userData.name || ''));
  const bounds = new THREE.Box3();
  for (const mesh of fingers.length ? fingers : view.group.children) bounds.expandByObject(mesh);
  if (bounds.isEmpty()) bounds.setFromCenterAndSize(new THREE.Vector3(), new THREE.Vector3());
  const center = bounds.getCenter(new THREE.Vector3());
  root.position.set(hand.at === 'over' ? center.x : bounds.max.x + 110, center.y, bounds.max.z - length);
}
// Holding: thumb and index on opposing attachment faces. Never substitute a jaw for a missing attachment.
// The fixed wrist exposes reach lost over the stroke; unsupported combinations stay explicitly unverified.
function holdGripper(view) {
  const shown = view.group.children.filter(mesh => mesh.visible && mesh.geometry), named = (side, part) => shown.find(mesh => {
    const name = mesh.userData.name || ''; return name.startsWith(side) && part.test(name);
  });
  const near = hand.side === 'right' ? 'Right' : 'Left', far = near === 'Right' ? 'Left' : 'Right';
  view.group.updateMatrixWorld(true);
  if (explodeAmount) { view.fit = {error:'Assemble the parts before checking fit.'}; fitReadout(); return false; }
  const out = near === 'Right' ? 1 : -1, spots = [/handle|strap slide|_Driver.*cradle/i].map(part => [named(near, part), named(far, part)])
    .map(([a, b]) => a && b && [attachmentSpot(a, out, hand.contact), attachmentSpot(b, -out, hand.contact)]).find(pair => pair?.[0] && pair[1]);
  if (!spots) { view.fit = {error:'No thumb/index attachment pair at this station. This combination needs a dedicated adapter.'}; fitReadout(); return false; }
  const [fingers, thumb] = spots;
  // Check all physical tool parts, even hidden ones, including jaws and wrist brackets; omit the remote arm reference.
  const solids = view.group.children.filter(mesh => mesh.geometry).filter(mesh => !/arm/i.test(mesh.userData.name || '')).map(mesh => new THREE.Box3().setFromObject(mesh));
  gripHand(view.hand, fingers, thumb, solids, {indexOnly:true, radius:hand.radius, lockWrist:hand.lockWrist});
  view.fit = {...view.hand.userData.fit}; fitReadout();
  return true;
}
async function showHand(reframe = false, preserveWrist = false) {
  await Promise.all([...views.values()].map(view => placeHand(view, preserveWrist)));
  if (reframe) { if (PRESETS[startView]) alignAll(startView); else fitVisible(); }
}
function bendHand() { for (const view of views.values()) if (view.hand?.visible) poseHand(view.hand, hand.curls); showCurls(); }
function showCurls() {
  for (const {finger, input, out} of hand.sliders) {
    const value = finger ? hand.curls[finger] : FINGERS.reduce((sum, name) => sum + hand.curls[name], 0) / FINGERS.length;
    input.value = Math.round(value * 100); out.textContent = Math.round(value * 100) + '%';
  }
  const button = $('panel-list').querySelector('.hand-pose');
  if (button) button.textContent = handClosed() ? 'Open hand' : 'Close hand';
}
const handClosed = () => FINGERS.reduce((sum, name) => sum + hand.curls[name], 0) / FINGERS.length > .5;
// The hand's own Open/Close: every finger eases from where it is to straight or to a fist.
function animateHand() {
  const from = {...hand.curls}, to = handClosed() ? 0 : 1, run = ++hand.run;
  const ms = matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 900, began = performance.now();
  const step = now => {
    if (run !== hand.run) return;
    const t = ms ? Math.min(1, (now - began) / ms) : 1, ease = t < .5 ? 4 * t ** 3 : 1 - (-2 * t + 2) ** 3 / 2;
    for (const finger of FINGERS) hand.curls[finger] = from[finger] + (to - from[finger]) * ease;
    bendHand();
    if (t < 1) requestAnimationFrame(step);
  };
  step(began);
}
function fitReadout() {
  const output = document.querySelector('.hand-fit'); if (!output) return;
  output.textContent = hand.summary || [...views.values()].filter(v => v.hand?.visible).map(v => v.fit?.error || (v.fit ?
    `Pad span ${v.fit.span.toFixed(1)} mm; miss ${v.fit.miss.toFixed(1)} mm; box overlap ${v.fit.penetration.toFixed(1)} mm. Fit unverified.` : 'Choose an attachment station.')).join(' ');
}
function handRows() {
  const row = document.createElement('div'), label = document.createElement('span');
  row.className = 'part-row photo-row'; label.className = 'name'; label.textContent = 'Average human hand';
  row.title = 'WebXR generic hand (MIT), scaled to the ANSUR II mean hand length';
  row.append(eyeButton(!hand.on, 'average human hand', () => { hand.on = !hand.on; renderPanel(); showHand(true); }), label);
  hand.sliders = [];
  if (!hand.on) return [row];
  const controls = document.createElement('div'); controls.className = 'hand-controls';
  const pick = (name, options, key, reframe = false) => {
    const select = document.createElement('select'); select.setAttribute('aria-label', name);
    select.append(...options.map(([value, text]) => new Option(text, value))); select.value = hand[key];
    select.onchange = () => { hand[key] = select.value; if (key === 'size') hand.length = null; hand.summary = null; hand.report = null; if (key === 'at') renderPanel(); showHand(reframe); };
    return select;
  };
  const follow = document.createElement('label'), box = document.createElement('input'), pose = document.createElement('button');
  follow.className = 'check'; box.type = 'checkbox'; box.checked = hand.follow; box.onchange = () => { hand.follow = box.checked; };
  follow.append(box, 'Bend with the gripper’s Open/Close');
  pose.className = 'hand-pose'; pose.onclick = animateHand;
  controls.append(pick('Hand size', SIZES.map(size => [size.id, size.label]), 'size'),
    pick('Which hand', [['right', 'Right hand'], ['left', 'Left hand']], 'side'),
    pick('Where the hand sits', [['beside', 'Beside the gripper'], ['over', 'Over the gripper (see-through)'], ['grip', 'Holding the gripper']], 'at', true));
  if (hand.at === 'grip') {
    const note = document.createElement('p'); note.className = 'hand-note';
    note.textContent = 'Thumb and index on opposing attachments. The wrist stays fixed through Open/Close. Generic hand and box envelopes are a fit study; pressure, retention and release need a physical trial.';
    const number = (label, value, min, max, change) => {
      const row = document.createElement('label'), input = document.createElement('input');
      row.className = 'fit-number'; input.type = 'number'; input.min = min; input.max = max; input.step = .1; input.value = value;
      input.setAttribute('aria-label', label); row.append(label + ' ', input);
      input.onchange = () => { const v = +input.value; if (Number.isFinite(v) && v >= min && v <= max) { change(v); hand.summary = null; hand.report = null; showHand(); } };
      return row;
    };
    const lock = document.createElement('label'), checked = document.createElement('input');
    lock.className = 'check'; checked.type = 'checkbox'; checked.checked = hand.lockWrist;
    checked.onchange = () => { hand.lockWrist = checked.checked; hand.summary = null; hand.report = null; showHand(); };
    lock.append(checked, 'Fix wrist through stroke');
    const readout = document.createElement('p'); readout.className = 'hand-fit hand-note'; readout.setAttribute('role', 'status');
    const sweep = document.createElement('button'); sweep.textContent = 'Check 13 stroke positions';
    sweep.onclick = async () => {
      openRun++; hand.summary = null; hand.report = null;
      const inputs = [...document.querySelectorAll('button, select, input')];
      const disabled = inputs.map(input => input.disabled); inputs.forEach(input => { input.disabled = true; });
      const saved = openness, results = [];
      const checkedViews = [...views.values()].filter(v => v.hand?.visible && !v.element.hidden);
      try {
        for (const view of checkedViews) view.hand.userData.grip = null;
        for (let i = 0; i <= 12; i++) {
          openness = i / 12;
          for (const view of checkedViews) {
            applyExplosion(view);
            if (view.hand?.visible) { holdGripper(view); results.push({design:view.design.name, open:Math.round(100 * openness), ...view.fit}); }
          }
          await new Promise(resolve => setTimeout(resolve, 0));
        }
        hand.report = JSON.stringify({assumptions:{length:hand.length || SIZES.find(s => s.id === hand.size).length, radius:hand.radius, contact:hand.contact, fixedWrist:hand.lockWrist, side:hand.side}, samples:results}, null, 2);
        hand.summary = !results.length ? 'Enable a hand on a loaded assembly first.' : results.some(r => r.error) ? 'Missing attachment at one or more positions; copy the report.' :
          `13 positions: worst pad miss ${Math.max(...results.map(r => r.miss)).toFixed(1)} mm; box overlap ${Math.max(...results.map(r => r.penetration)).toFixed(1)} mm. Physical fit unverified.`;
      readout.textContent = hand.summary;
      } finally { openness = saved; for (const view of views.values()) applyExplosion(view); await showHand(false, true); inputs.forEach((input, i) => { input.disabled = disabled[i]; }); }
    };
    const copy = document.createElement('button'); copy.textContent = 'Copy fit report';
    copy.onclick = async () => { try { await navigator.clipboard.writeText(hand.report || 'Run the stroke check first.'); copy.textContent = 'Copied'; } catch { message('Clipboard unavailable. Run in Pebbles or a secure browser.'); } };
    controls.append(note, number('Hand length (mm)', hand.length || SIZES.find(s => s.id === hand.size).length, 140, 230, v => { hand.length = v; }),
      number('Digit pad radius (mm)', hand.radius, 4, 14, v => { hand.radius = v; }),
      number('Contact down attachment (%)', hand.contact, 10, 90, v => { hand.contact = v; }), lock, readout, sweep, copy);
    return [row, controls];
  }
  controls.append(follow, pose);
  for (const finger of [null, ...FINGERS]) {
    const knob = document.createElement('label'), name = document.createElement('span'), out = document.createElement('output'), input = document.createElement('input');
    knob.className = 'knob'; name.textContent = finger ? finger[0].toUpperCase() + finger.slice(1) : 'All fingers';
    Object.assign(input, {type:'range', min:0, max:100, step:1}); input.setAttribute('aria-label', name.textContent + ' bend');
    input.oninput = () => { hand.run++; for (const which of finger ? [finger] : FINGERS) hand.curls[which] = input.value / 100; bendHand(); };
    knob.append(name, out, input); controls.append(knob); hand.sliders.push({finger, input, out});
  }
  return [row, controls];
}
function fitVisible() { for (const view of views.values()) if (!view.element.hidden) frame(view); }

try {
  renderer = new THREE.WebGLRenderer({antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setClearColor('#13232f'); stage.prepend(renderer.domElement);
  // Sidebar/window resizing must preserve the orbit and zoom the user chose.
  const resize = () => { renderer.setSize(stage.clientWidth, stage.clientHeight); };
  new ResizeObserver(resize).observe(stage);
  renderer.setAnimationLoop(() => {
    const root = stage.getBoundingClientRect();
    renderer.setScissorTest(false); renderer.clear(); renderer.setScissorTest(true);
    for (const view of views.values()) {
      if (view.element.hidden) continue;
      const rect = view.element.getBoundingClientRect();
      if (!rect.width || !rect.height) continue;
      view.camera.aspect = rect.width / rect.height; view.camera.updateProjectionMatrix();
      renderer.setViewport(rect.left - root.left, root.bottom - rect.bottom, rect.width, rect.height);
      renderer.setScissor(rect.left - root.left, root.bottom - rect.bottom, rect.width, rect.height);
      view.controls.update(); renderer.render(view.scene, view.camera);
    }
  });
} catch (error) { webglError = '3D is unavailable on this device. Showing exported previews.'; }

function shortLabel(design) {
  const match = (design.name || '').match(/(?:generation|gen)\s+(\d+[a-z]?)\b/i);
  return match ? 'Gen ' + match[1] : design.name || design.version || design.id;
}
// What a family shows: a mix family its assembly (its versions are reached through the part rows), any other every version
// that is not hidden, oldest generation first.
function projectDesigns(project) {
  const which = mixFamily(project), mixed = which && buildMix(catalog, picks, which);
  if (mixed) return [mixed];
  const list = catalog.designs.filter(design => design.project === project && !hidden.has(design.id));
  if (list.every(design => /(?:generation|gen)\s+\d+/i.test(design.name || ''))) {
    list.sort((a, b) => Number(a.name.match(/(?:generation|gen)\s+(\d+)/i)[1]) - Number(b.name.match(/(?:generation|gen)\s+(\d+)/i)[1]));
  }
  return list;
}
async function loadHidden() {
  try {
    const response = await fetch('hidden.json', {cache:'no-store'});
    const list = response.ok ? (await response.json()).hidden : [];
    hidden = new Set(Array.isArray(list) ? list : []);
  } catch { hidden = new Set(); }
}
function setFocus(id, updateHash = true) {
  focused = views.has(id) ? id : null;
  grid.classList.toggle('focused', !!focused);
  for (const [key, view] of views) {
    view.element.hidden = !!focused && key !== focused;
    view.element.setAttribute('aria-label', (focused ? '' : 'Open ') + (view.design.name || key));
    view.element.setAttribute('role', focused ? 'img' : 'button');
  }
  if (updateHash) history.replaceState(null, '', location.pathname + location.search + (focused ? '#' + encodeURIComponent(focused) : ''));
  placePhoto(); updateExplodeControl(); updatePoseControl(); updateTuneControl(); renderPanel();
  requestAnimationFrame(fitVisible);
  document.title = focused ? 'HelpingHands · ' + views.get(focused).design.name : 'HelpingHands · ' + currentProject;
}
function updateExplodeControl() {
  $('explode').hidden = ![...views.values()].some(view => !view.element.hidden && view.group.children.some(mesh => mesh.userData.explode?.lengthSq() > 0));
}
// How one model moves with Open/Close (cad/mobile_gallery/poses.js): a hinge turns it about Y through its pivot, a slide or
// crank follows the drive. Null = fixed. pivot: the right hinge's X when a Tune render moved it (the outline sets it), else poses.js's.
function motionFor(design, name, pivot = null) {
  const pose = POSES[design.pose || design.id];
  if (!pose) return null;
  const sin = deg => Math.sin(THREE.MathUtils.degToRad(deg));
  const crank = (c, a) => -THREE.MathUtils.radToDeg(Math.asin(Math.max(-1, Math.min(1, (2 + 20 * sin(a) - c.mid) / c.radius))));
  const find = list => (list || []).find(item => new RegExp(item.match).test(name));
  const hinge = find(pose.hinges), slide = find(pose.slides), turn = find(pose.cranks);
  if (!hinge && !slide && !turn) return null;
  return angle => {
    if (hinge) return {deg: hinge.sign * (angle - pose.exported), pivot: pivot === null ? hinge.pivot : pose.uniform_scale ? hinge.pivot.map(v => v * pivot / pose.hinges[0].pivot[0]) : [Math.sign(hinge.pivot[0]) * pivot, 0, 0], offset: [0, 0, 0]};
    if (turn) return {deg: crank(turn, angle) - crank(turn, pose.exported), pivot: turn.pivot, offset: [0, 0, 0]};
    const k = sin(angle) - sin(pose.exported);
    return {deg: 0, pivot: [0, 0, 0], offset: slide.dir.map(v => v * k)};
  };
}
function poseAngle(design) {
  const pose = POSES[design.pose || design.id];
  return pose ? pose.min + (pose.max - pose.min) * openness : 0;
}
function applyExplosion(view) {
  const angle = poseAngle(view.design);
  for (const mesh of view.group.children) {
    const move = mesh.userData.motion?.(angle) || {deg: 0, pivot: [0, 0, 0], offset: [0, 0, 0]};
    mesh.rotation.set(0, THREE.MathUtils.degToRad(move.deg), 0);
    const pivot = new THREE.Vector3(...move.pivot);
    mesh.position.copy(pivot).sub(pivot.clone().applyEuler(mesh.rotation)).add(new THREE.Vector3(...move.offset))
      .add(mesh.userData.shift || new THREE.Vector3()).addScaledVector(mesh.userData.explode, explodeAmount);
  }
}
function updatePoseControl() {
  $('pose').hidden = ![...views.values()].some(view => !view.element.hidden && view.group.children.some(mesh => mesh.userData.motion));
}
// One tap toggles the jaws: the button names the move it will make, and the fingers swing there smoothly.
// Tapping mid-swing turns them round from wherever they are.
let openTarget = openness, openRun = 0;
function showOpenTarget() {
  $('pose').textContent = openTarget ? 'Close' : 'Open';
  $('pose').setAttribute('aria-pressed', String(!openTarget));
}
$('pose').onclick = () => {
  hand.summary = null; hand.report = null;
  const from = openness, to = openTarget = openTarget ? 0 : 1, run = ++openRun;
  showOpenTarget();
  const ms = matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 900 * Math.abs(to - from), began = performance.now();
  const step = now => {
    if (run !== openRun) return;
    const t = ms ? Math.min(1, (now - began) / ms) : 1, ease = t < .5 ? 4 * t ** 3 : 1 - (-2 * t + 2) ** 3 / 2;
    openness = from + (to - from) * ease;
    for (const view of views.values()) applyExplosion(view);
    if (hand.on && hand.at === 'grip') { for (const view of views.values()) if (view.hand?.visible) holdGripper(view); }
    else if (hand.on && hand.follow) { hand.run++; for (const finger of FINGERS) hand.curls[finger] = 1 - openness; bendHand(); }
    if (t < 1) requestAnimationFrame(step);
  };
  step(began);
};
showOpenTarget();
$('explode').onclick = () => {
  hand.summary = null; hand.report = null;
  exploded = !exploded;
  if (hand.on && hand.at === 'grip') message(exploded ? 'Assemble the parts before checking human fit.' : '');
  $('explode').textContent = exploded ? 'Assemble' : 'Explode';
  $('explode').setAttribute('aria-pressed', String(exploded));
  animateExplosion(exploded ? 1 : 0);
};
// Fly the parts apart (or back together) and glide each visible camera from where it is to the framing of the
// new layout, so nothing jumps. Reduced motion (or no 3D) still lands in one step.
function animateExplosion(to) {
  const from = explodeAmount, run = ++explodeRun;
  const glides = [...views.values()].filter(view => !view.element.hidden && view.controls).map(view => {
    const start = {position: view.camera.position.clone(), target: view.controls.target.clone()};
    explodeAmount = to; applyExplosion(view); frame(view);
    return {view, start, end: {position: view.camera.position.clone(), target: view.controls.target.clone()}};
  });
  const ms = matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 650, began = performance.now();
  const step = now => {
    if (run !== explodeRun) return;
    const t = ms ? Math.min(1, (now - began) / ms) : 1, ease = t < .5 ? 4 * t ** 3 : 1 - (-2 * t + 2) ** 3 / 2;
    explodeAmount = from + (to - from) * ease;
    for (const view of views.values()) applyExplosion(view);
    for (const {view, start, end} of glides) {
      view.camera.position.lerpVectors(start.position, end.position, ease);
      view.controls.target.lerpVectors(start.target, end.target, ease); view.controls.update();
    }
    if (t < 1) requestAnimationFrame(step);
  };
  step(began);
}

function createView(design) {
  const element = document.createElement('section'); element.className = 'viewport'; element.tabIndex = 0;
  element.dataset.designId = design.id;
  const preview = document.createElement('img'); preview.className = 'preview'; preview.alt = 'Exported preview'; preview.hidden = true;
  const label = document.createElement('span'); label.className = 'label';
  const loading = document.createElement('span'); loading.className = 'loading'; loading.textContent = 'Loading 3D…'; loading.setAttribute('role','status');
  element.append(preview, label, loading); grid.append(element);
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#13232f');
  scene.add(new THREE.HemisphereLight(0xffffff, 0x51687a, 2.5));
  const light = new THREE.DirectionalLight(0xffffff, 3); light.position.set(150, -200, 300); scene.add(light);
  const camera = new THREE.PerspectiveCamera(35, 1, .1, 10000); camera.up.set(0, 0, 1);
  const group = new THREE.Group(); scene.add(group);
  const controls = renderer ? new OrbitControls(camera, element) : null;
  if (controls) controls.enableDamping = true;
  const view = {design, element, preview, label, loading, scene, camera, group, controls, token:0, signature:null, hiddenParts:new Set()};
  let start = null, moved = false; const pointers = new Set();
  element.addEventListener('pointerdown', event => {
    pointers.add(event.pointerId);
    if (pointers.size === 1) { start = [event.clientX, event.clientY]; moved = false; }
    else moved = true;
  });
  element.addEventListener('pointermove', event => {
    if (start && Math.hypot(event.clientX - start[0], event.clientY - start[1]) > (event.pointerType === 'mouse' ? 6 : 16)) moved = true;
  });
  element.addEventListener('pointerup', event => {
    pointers.delete(event.pointerId);
    if (!pointers.size) {
      if (!focused && start && !moved) setFocus(design.id);
      start = null;
    }
  });
  element.addEventListener('pointercancel', () => { pointers.clear(); start = null; moved = true; });
  element.addEventListener('keydown', event => {
    if (!focused && (event.key === 'Enter' || event.key === ' ')) { event.preventDefault(); setFocus(design.id); }
    else if (event.key === 'Escape' && views.size > 1) setFocus(null);
  });
  element.addEventListener('dblclick', () => frame(view));
  return view;
}

async function updateView(view, design) {
  view.design = design; view.label.textContent = shortLabel(design);
  if (design.mix) { view.element.setAttribute('aria-label', design.name); if (focused === design.id) document.title = 'HelpingHands · ' + design.name; }
  if (view.tuned) return;   // Tune meshes stay until Reset; a catalog refresh must not swap them for the exported ones
  const signature = JSON.stringify(design.models || []);
  if (design.preview) view.preview.src = design.preview;
  if (view.signature === signature) {
    if (view.element.classList.contains('has-model')) {
      view.loading.hidden = !design.export_error;
      view.loading.textContent = design.export_error ? 'Latest export failed; showing last model' : '';
      view.loading.title = design.export_error || '';
    }
    return; // Keep meshes, orbit and in-flight load on ordinary refresh.
  }
  view.signature = signature; const token = ++view.token;
  disposeMeshes(view); view.element.classList.remove('has-model');
  view.preview.hidden = !design.preview; view.loading.hidden = false;
  if (!renderer || !(design.models || []).length) {
    view.loading.textContent = webglError || (design.export_error ? '3D export unavailable' : '3D export pending');
    view.loading.title = design.export_error || ''; return;
  }
  view.loading.textContent = 'Loading 3D…';
  const meshes = [];
  try {
    for (const model of design.models) {
      const geometry = await loader.loadAsync(model.path);
      if (token !== view.token) { geometry.dispose(); for (const mesh of meshes) { mesh.geometry.dispose(); mesh.material.dispose(); } return; }
      meshes.push(makeMesh(model, geometry, motionFor(design, model.name)));
    }
    for (const mesh of meshes) view.group.add(mesh);
    applyExplosion(view); showParts(view);
    updateExplodeControl(); updatePoseControl();
    hand.summary = null; hand.report = null;
    await placeHand(view); if (token !== view.token) return;
    frame(view); view.element.classList.add('has-model'); view.loading.hidden = !design.export_error;
    if (PRESETS[startView]) alignAll(startView);
    view.loading.textContent = design.export_error ? 'Latest export failed; showing last model' : '';
    view.loading.title = design.export_error || '';
  } catch (error) {
    for (const mesh of meshes) { mesh.geometry.dispose(); mesh.material.dispose(); }
    if (token !== view.token) return;
    view.loading.textContent = 'Could not load 3D'; view.loading.title = error.message;
  }
}

// Show a family: its assembly (a mix family) or every version side by side, or one design alone when `focusId` names one
// that is not in that list (a link to a version of a mix family, or Tune from its row): the panel's first row then returns.
function showProject(project, focusId = null) {
  currentProject = project; $('project').value = project;
  let list = projectDesigns(project);
  const single = focusId && !list.some(design => design.id === focusId) && catalog.designs.find(design => design.id === focusId);
  if (single) list = [single];
  const ids = new Set(list.map(design => design.id));
  for (const [id, view] of views) if (!ids.has(id)) { removeView(view); views.delete(id); }
  for (const design of list) {
    let view = views.get(design.id);
    if (!view) { view = createView(design); views.set(design.id, view); }
    grid.append(view.element); updateView(view, design);
  }
  message(list.length ? webglError : 'Every ' + project + ' version is hidden (hidden.json). Scripts/design_visibility.py show all brings them back.');
  setFocus(focusId || (list.length === 1 ? list[0].id : null));
}
$('project').onchange = () => showProject($('project').value);
function hashDesign() { try { return decodeURIComponent(location.hash.slice(1)); } catch { return ''; } }
window.addEventListener('hashchange', () => {
  const target = mixOf({id:hashDesign()}) || catalog?.designs.find(design => design.id === hashDesign());
  if (target) showProject(target.project, target.id); else setFocus(null, false);
});

async function refresh() {
  if (refreshing) return; refreshing = true;
  try {
    const response = await fetch('catalog.json', {cache:'no-store'});
    if (!response.ok) throw Error('Catalog unavailable (' + response.status + ')');
    const next = await response.json();
    if (!Array.isArray(next.designs)) throw Error('Invalid catalog');
    const initial = !catalog; catalog = next;
    await loadHidden();
    // The mix families first (the Generalist assembly is the landing), then the rest as the catalog lists them.
    const projects = [...new Set([...MIXES.map(item => item.project), ...catalog.designs.map(design => design.project)])]
      .filter(project => catalog.designs.some(design => design.project === project));
    $('project').replaceChildren(...projects.map(project => new Option(project, project)));
    // A first load with no #design opens on the Generalist assembly (the newest of each part unless ?gripper/?handles/?base say otherwise).
    const wanted = focused || (initial ? hashDesign() || MIX.id : '');
    const target = mixOf({id:wanted}) || catalog.designs.find(design => design.id === wanted);
    const project = target?.project || (projects.includes(currentProject) ? currentProject : projects[0]);
    const sameLayout = !initial && project === currentProject && JSON.stringify([...views.keys()]) === JSON.stringify(projectDesigns(project).map(d => d.id));
    if (sameLayout) {
      for (const view of views.values()) updateView(view, view.design.mix ? buildMix(catalog, picks, mixOf(view.design)) : catalog.designs.find(d => d.id === view.design.id) || view.design);
      renderPanel();   // No layout/frame reset: preserve focused model and camera on unchanged refresh.
    } else showProject(project, target?.id || null);
  } catch (error) { message('Could not refresh. ' + error.message); }
  finally { refreshing = false; }
}

// The panel: the parts list, and the way around. For a mix it is one row per part (eye, version selector, Tune when that version
// has parameters, then any note model.js attached: a part that followed the change, or a pair that does not fit) with the part's
// own pieces under it. For one design alone it is a row back to the assembly (mix families) or the family's versions, then its
// pieces. The eye hides a piece (mesh.visible only, so Open/Close and Explode keep moving it; the Only isolate button and the ✓ on
// follow notes are gone, voice-b1dacbad). Each tile keeps its hidden names across picker changes, catalog refreshes and Tune re-renders. ?hide=top plate,base
// presets it: any piece whose name contains one of the words (voice-2308ade1).
const hideQuery = (query.get('hide') || '').toLowerCase().split(',').map(word => word.trim()).filter(Boolean);
const EYE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>';
const EYE_OFF = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7c2 0 3.7.7 5.1 1.6M22 12s-3.6 7-10 7c-2 0-3.7-.7-5.1-1.6M3 3l18 18"/></svg>';
const pieceNames = models => [...new Set((models || []).map(model => model.name).filter(Boolean))];
function showParts(view) {
  const names = pieceNames(view.design.models);
  if (hideQuery.length && !view.hideApplied && names.some(name => hideQuery.some(word => name.toLowerCase().includes(word)))) {
    view.hideApplied = true;
    for (const name of names) if (hideQuery.some(word => name.toLowerCase().includes(word))) view.hiddenParts.add(name);
  }
  for (const mesh of view.group.children) mesh.visible = !view.hiddenParts.has(mesh.userData.name);
  renderPanel();
}
function eyeButton(off, what, onclick) {
  const eye = document.createElement('button');
  eye.className = 'eye'; eye.innerHTML = off ? EYE_OFF : EYE; eye.setAttribute('aria-pressed', String(!off));
  eye.setAttribute('aria-label', (off ? 'Show ' : 'Hide ') + what); eye.onclick = onclick;
  return eye;
}
function pieceRows(view, models) {
  const names = pieceNames(models);
  return names.map(name => {
    const row = document.createElement('div'), swatch = document.createElement('span'), label = document.createElement('span');
    const off = view.hiddenParts.has(name);
    row.className = 'piece-row' + (off ? ' off' : ''); swatch.className = 'swatch'; swatch.style.background = models.find(model => model.name === name).color || '#cbd9e2';
    label.className = 'name'; label.textContent = part({name}); label.title = name;
    row.append(eyeButton(off, part({name}), () => { if (off) view.hiddenParts.delete(name); else view.hiddenParts.add(name); showParts(view); }), swatch, label);
    return row;
  });
}
function partRow(view, row) {
  const design = view.design, models = design.models.filter(model => model.part === row.key), names = pieceNames(models);
  const head = document.createElement('div'), select = document.createElement('select');
  head.className = 'part-row';
  const off = names.length > 0 && names.every(name => view.hiddenParts.has(name));
  const eye = eyeButton(off, row.label, () => { for (const name of names) if (off) view.hiddenParts.delete(name); else view.hiddenParts.add(name); showParts(view); });
  eye.disabled = !names.length;
  select.setAttribute('aria-label', row.label + ' version');
  if (row.sitsOut) { select.append(new Option(row.sitsOut, 'sits-out')); select.disabled = true; }
  else {
    select.append(...(row.optional ? [new Option('No ' + row.label.toLowerCase(), 'none')] : []), ...row.options.map(item => new Option(optionLabel(row.label, item), item.version)));
    select.value = row.chosen ? row.chosen.version : 'none';
    select.onchange = () => { picks[design.id][row.key] = select.value; updateView(view, buildMix(catalog, picks, mixOf(design), row.key)); renderPanel(); };
  }
  select.title = select.selectedOptions[0]?.textContent || '';
  head.append(eye, select);
  if (tuneParams(row.chosen?.design).length) {
    const tuneButton = document.createElement('button'); tuneButton.className = 'tune'; tuneButton.textContent = 'Tune';
    tuneButton.title = 'Slide ' + row.label + ' ' + row.chosen.version + "'s parameters";
    tuneButton.onclick = () => { showProject(currentProject, row.chosen.design.id); openTune(views.get(row.chosen.design.id)); };
    head.append(tuneButton);
  }
  const notes = row.notes.map(note => { const line = document.createElement('div'); line.className = 'note' + (note.follow ? ' follow' : ''); line.textContent = (note.follow ? '' : '⚠ ') + note.text; return line; });
  return [head, ...notes, ...pieceRows(view, models)];
}
function linkRow(text, onclick, current = false) {
  const row = document.createElement('button'); row.className = 'version-row'; row.textContent = text;
  if (current) row.setAttribute('aria-current', 'true'); row.onclick = onclick;
  return row;
}
function renderPanel() {
  if (!catalog) return;
  const view = focused && views.get(focused), design = view?.design, which = mixFamily(currentProject);
  const rows = [photoRow(), ...handRows()];
  if (design?.mix) rows.push(...design.rows.flatMap(row => partRow(view, row)));
  else {
    if (which && design) rows.push(linkRow('‹ ' + (buildMix(catalog, picks, which)?.name || which.project), () => showProject(currentProject, which.id)));
    if (!which) {
      const list = projectDesigns(currentProject);
      if (list.length > 1) rows.push(linkRow('All ' + currentProject + ' versions', () => setFocus(null), !focused));
      rows.push(...list.map(item => linkRow(item.name, () => setFocus(item.id), focused === item.id)));
    }
    if (design) rows.push(...pieceRows(view, design.models || []));
  }
  $('panel-list').replaceChildren(...rows); showCurls();
}

// Tune (Handle 4 on): a design whose catalog entry carries `params` (its params.json) gets a slider per parameter. Each change
// posts {design, values} to serve_designs.py /tune, which renders the real OpenSCAD parts with those values (a solid-only
// change is ~0.1 s, an outline change ~1 s) and the view swaps them in, camera untouched. One request is in flight at a
// time; while it runs, only the newest values wait, so a drag always ends on what the slider shows. ?tune=name:value,...
// presets the values (links, screenshots); Copy puts the changed values on the clipboard for the next version.
const tune = {view:null, values:{}, busy:false, again:false};
const tuneQuery = query.get('tune');
function tuneParams(design) { return (design?.params || []).flatMap(group => group.params); }
// The focused design when it has params, else the newest tunable one on screen (a family compared side by side).
function tuneTarget() {
  const view = focused && views.get(focused);
  if (view && tuneParams(view.design).length) return view;
  const order = other => partOrder(other.design);
  return [...views.values()].filter(other => tuneParams(other.design).length).sort((a, b) => order(b) - order(a))[0] || null;
}
function updateTuneControl() {
  const view = tuneTarget(), jump = view && view.design.id !== focused;
  $('tune-open').hidden = !view;
  $('tune-open').textContent = jump ? 'Tune ' + shortLabel(view.design) : 'Tune';
  if (!$('tune').hidden && tune.view?.design.id !== focused) closeTune();
}
function tuneStatus(text, kind = '') { $('tune-status').textContent = text; $('tune-status').className = kind; }
function decimals(step) { return Math.max(0, (String(step).split('.')[1] || '').length); }
function formatValue(param, value) { return (+value).toFixed(decimals(param.step)) + (param.unit ? ' ' + param.unit : ''); }
function writeTuneQuery() {
  const params = new URLSearchParams(location.search), list = Object.entries(tune.values).map(([k, v]) => k + ':' + v).join(',');
  if (list) params.set('tune', list); else params.delete('tune');
  history.replaceState(null, '', location.pathname + (params.toString() ? '?' + params : '') + location.hash);
}
function openTune(view) {
  tune.view = view; $('tune').hidden = false; $('panel').hidden = true; $('tune-open').setAttribute('aria-expanded', 'true');
  $('tune-title').textContent = 'Tune ' + shortLabel(view.design);
  if (tuneQuery && !Object.keys(tune.values).length) for (const pair of tuneQuery.split(',')) {
    const [k, v] = pair.split(':'); if (tuneParams(view.design).some(p => p.name === k) && isFinite(v)) tune.values[k] = +v;
  }
  $('tune-list').replaceChildren(...view.design.params.flatMap(group => {
    const heading = document.createElement('h3'); heading.textContent = group.name;
    return [heading, ...group.params.map(param => {
      const row = document.createElement('label'), name = document.createElement('span'), out = document.createElement('output'), input = document.createElement('input');
      row.className = 'knob'; row.title = param.doc; name.textContent = param.label || param.name;
      Object.assign(input, {type:'range', min:param.min, max:param.max, step:param.step, value:tune.values[param.name] ?? param.value});
      input.setAttribute('aria-label', param.label || param.name);
      const show = () => { out.textContent = formatValue(param, input.value); row.classList.toggle('changed', param.name in tune.values); };
      input.oninput = () => {
        if (+input.value === param.value) delete tune.values[param.name]; else tune.values[param.name] = +input.value;
        show(); requestTune();
      };
      out.title = 'Tap to reset to ' + formatValue(param, param.value);
      out.onclick = event => { event.preventDefault(); input.value = param.value; input.oninput(); };
      show(); row.append(name, out, input); return row;
    })];
  }));
  if (Object.keys(tune.values).length) requestTune(); else tuneStatus('Drag a slider: the real CAD re-renders. Tap a value to reset it.');
}
function closeTune() { $('tune').hidden = true; $('panel').hidden = false; $('tune-open').setAttribute('aria-expanded', 'false'); }
$('tune-open').onclick = () => {
  if (!$('tune').hidden) return closeTune();
  const view = tuneTarget(); if (!view) return;
  if (view.design.id !== focused) setFocus(view.design.id);
  openTune(view); updateTuneControl();
};
$('tune-close').onclick = closeTune;
$('tune-reset').onclick = () => { tune.values = {}; openTune(tune.view); requestTune(); };
$('tune-copy').onclick = async () => {
  const text = JSON.stringify(tune.values, null, 1);
  try { await navigator.clipboard.writeText(text); tuneStatus('Copied ' + Object.keys(tune.values).length + ' changed values. Paste them into a pebble to make the next version.'); }
  catch { tuneStatus(text); }
};
async function requestTune() {
  if (tune.busy) { tune.again = true; return; }
  const view = tune.view, values = {...tune.values};
  if (!view) return;
  writeTuneQuery();
  tune.busy = true; tune.again = false; tuneStatus('Rendering…', 'busy');
  try {
    const response = await fetch('tune', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({design:view.design.id, values})});
    const result = await response.json().catch(() => ({ok:false, error:'server said ' + response.status}));
    if (!result.ok) throw Error(result.error || 'render failed');
    const meshes = [];
    for (const model of result.models) {
      const geometry = await loader.loadAsync(model.path);
      meshes.push(makeMesh(model, geometry, motionFor(view.design, model.name, result.pivot ?? null)));
    }
    // Swapped in even when newer values are waiting: mid-drag the model keeps up instead of freezing.
    disposeMeshes(view); for (const mesh of meshes) view.group.add(mesh); applyExplosion(view); showParts(view); placeHand(view);
    view.tuned = Object.keys(values).length > 0; view.signature = view.tuned ? 'tuned' : view.signature;
    view.element.classList.add('has-model'); view.loading.hidden = true;
    const count = Object.keys(values).length;
    tuneStatus((count ? count + ' changed · ' : 'This version’s values · ') + 'rendered in ' + result.seconds + ' s' + (result.retraced ? ' (outline re-traced)' : ''));
  } catch (error) {
    tuneStatus('Not rendered: ' + error.message + '. Showing the last good model.', 'error');
  } finally {
    tune.busy = false;
    if (tune.again) requestTune();
  }
}

await refresh();
if (tuneQuery && tuneTarget()) $('tune-open').click();
setInterval(refresh, 300000);
