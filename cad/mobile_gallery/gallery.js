import * as THREE from 'three';
import {STLLoader} from 'three/addons/STLLoader.js';
import {OrbitControls} from 'three/addons/OrbitControls.js';
import POSES from './poses.js';
import PHOTOS from './reference/photos.js';

const $ = id => document.getElementById(id);
const stage = $('stage'), grid = $('viewports');
const views = new Map();
// Design ids hidden from the comparison: hidden.json beside the catalog, written
// by the Shown checklist (through serve_designs.py) and by design_visibility.py.
let hidden = new Set();
let renderer, catalog, focused = null, currentProject = '', webglError = '', refreshing = false, exploded = false;
// Open/Closed slider: 0 = closed, 1 = fully open, the same fraction for every generation shown.
// ?open=0..100 presets it (screenshots, links).
const preset = new URLSearchParams(location.search).get('open');
// ?view=top|front|side|iso lines every model up once each one loads (screenshots, links).
const startView = new URLSearchParams(location.search).get('view');
let openness = preset !== null && isFinite(preset) ? Math.max(0, Math.min(100, +preset)) / 100 : 1;
const loader = new STLLoader();
// The real Generalist gripper, shown as one more tile in its project. Its first photo is
// resampled into the gripper's CAD millimetres (reference/make_reference.py) and laid on the
// Y=0 plane, so the Top view lines the photo up with every model; the others show flat.
const ACTUAL = {id:'generalist-actual', project:'Generalist Gripper', name:'Actual (Generalist)', actual:true};
// Mix and match (Generalist Gripper only): any 1.x gripper with any 2.x version's handles, assembled
// in one tile. A handle is a model named like a strap slide; everything else in a design is its gripper.
// It opens on the newest gripper + newest handles (1.17 + 2.1 = 2.1). ?gripper=1.1&handles=2.1|none presets it.
const MIX = {id:'generalist-mix', project:'Generalist Gripper', mix:true};
const HANDLE = /strap slide|handle/i;
const query = new URLSearchParams(location.search);
const mix = {gripper:query.get('gripper'), handles:query.get('handles')};
const FINGERS = new THREE.Box3(new THREE.Vector3(-40, -6, -4), new THREE.Vector3(40, 6, 116));
// View presets: the direction the camera looks from, in CAD axes (Z along the fingers).
// Top is the photo's viewpoint: from -Y, +X to the right, fingertips up.
const PRESETS = {top:[0, -1, 0], front:[0, -.002, 1], side:[1, 0, 0], iso:[.8, -1, .65]};

function message(text = '') { $('message').textContent = text; $('message').hidden = !text; }
function disposeMeshes(view) {
  for (const mesh of [...view.group.children]) {
    view.group.remove(mesh); mesh.geometry.dispose(); mesh.material.map?.dispose(); mesh.material.dispose();
  }
}
function removeView(view) {
  view.token++; view.controls?.dispose(); disposeMeshes(view); view.element.remove();
}
function frame(view) {
  if (view.design.actual) { if (view.group.children.length) placeCamera(view, PRESETS.top, FINGERS); return; }
  if (!view.group.children.length || !view.element.clientWidth || !view.element.clientHeight) return;
  view.camera.aspect = view.element.clientWidth / view.element.clientHeight;
  const bounds = new THREE.Box3().setFromObject(view.group);
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
// Snap every tile on screen to one camera: same direction, centre and scale, framed on all the
// models together. Top also closes the jaws, the pose the photo was traced in.
function alignAll(name) {
  const shown = [...views.values()].filter(view => !view.element.hidden && view.group.children.length);
  if (name === 'top' && shown.some(view => view.design.actual) && openness) { $('openness').value = 0; $('openness').oninput(); }
  const bounds = new THREE.Box3();
  for (const view of shown) if (!view.design.actual) bounds.expandByObject(view.group);
  if (bounds.isEmpty()) bounds.copy(FINGERS);
  for (const view of shown) placeCamera(view, PRESETS[name], bounds);
}
for (const button of document.querySelectorAll('#presets button')) button.onclick = () => alignAll(button.dataset.view);
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
  const match = (design.name || '').match(/(?:generation|gen)\s+(\d+(?:\.\d+)?[a-z]?)\b/i);   // 'Gen 2.4', not 'Gen 2'
  return match ? 'Gen ' + match[1] : design.name || design.version || design.id;
}
// 'Gen 16' -> '1.16', 'Gen 2.1' -> '2.1' (AGENTS.md: 1.x gripper only, 2.x gripper plus handles).
function lineVersion(design) {
  const match = (design.name || '').match(/(?:generation|gen)\s+(\d+(?:\.\d+)?[a-z]?)\b/i);
  return match ? (match[1].includes('.') ? match[1] : '1.' + match[1]) : null;
}
function versionOrder(version) { const [line, minor] = version.split('.'); return +line * 1000 + parseFloat(minor); }
function mixOptions() {
  const family = catalog.designs.filter(design => design.project === MIX.project && lineVersion(design) && design.models?.length)
    .sort((a, b) => versionOrder(lineVersion(a)) - versionOrder(lineVersion(b)) || a.id.localeCompare(b.id));
  return {grippers: family.filter(design => lineVersion(design).startsWith('1.') && design.models.some(model => !HANDLE.test(model.name))),
          handles: family.filter(design => lineVersion(design).startsWith('2.') && design.models.some(model => HANDLE.test(model.name)))};
}
function buildMix() {
  const {grippers, handles} = mixOptions();
  if (!grippers.length) return null;
  const gripper = grippers.find(design => lineVersion(design) === mix.gripper) || grippers.at(-1);
  const handle = mix.handles === 'none' ? null : handles.find(design => lineVersion(design) === mix.handles) || handles.at(-1) || null;
  mix.gripper = lineVersion(gripper); mix.handles = handle ? lineVersion(handle) : 'none';
  // The handles ride the gripper's hinges (poses.js, keyed by the gripper), placed where their own design put them.
  return {...MIX, grippers, handles, pose:gripper.id,
    name:handle ? mix.gripper + ' gripper + ' + mix.handles + ' handles' : mix.gripper + ' gripper, no handles',
    models:[...gripper.models.filter(model => !HANDLE.test(model.name)), ...(handle ? handle.models.filter(model => HANDLE.test(model.name)) : [])]};
}
function projectDesigns(project) {
  const list = catalog.designs.filter(design => design.project === project);
  if (list.every(design => /(?:generation|gen)\s+\d+/i.test(design.name || ''))) {
    list.sort((a, b) => Number(a.name.match(/(?:generation|gen)\s+(\d+)/i)[1]) - Number(b.name.match(/(?:generation|gen)\s+(\d+)/i)[1]));
  }
  if (project === ACTUAL.project) list.unshift(ACTUAL);
  const mixed = project === MIX.project && buildMix();
  if (mixed) list.unshift(mixed);
  return list;
}
function visibleDesigns(project) { return projectDesigns(project).filter(design => !hidden.has(design.id)); }
async function loadHidden() {
  try {
    const response = await fetch('hidden.json', {cache:'no-store'});
    const list = response.ok ? (await response.json()).hidden : [];
    hidden = new Set(Array.isArray(list) ? list : []);
  } catch { hidden = new Set(); }
}
async function saveHidden() {
  try {
    const response = await fetch('hidden.json', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({hidden:[...hidden]})});
    if (!response.ok) throw Error('server said ' + response.status);
    status();
  } catch (error) { message('Could not save which generations are hidden (' + error.message + '). It will reset on refresh.'); }
}
function status() {
  message(visibleDesigns(currentProject).length ? webglError
    : 'Every ' + currentProject + ' generation is hidden. Tap “' + $('shown').textContent + '” to bring one back.');
}
function updateShownButton() {
  const count = projectDesigns(currentProject).filter(design => hidden.has(design.id)).length;
  $('shown').textContent = count ? count + ' hidden' : 'Hide…';
}
function openVisibility() {
  $('visibility-list').replaceChildren(...projectDesigns(currentProject).map(design => {
    const row = document.createElement('label'), box = document.createElement('input');
    box.type = 'checkbox'; box.checked = !hidden.has(design.id);
    box.onchange = () => {
      if (box.checked) hidden.delete(design.id); else hidden.add(design.id);
      showProject(currentProject, focused && !hidden.has(focused) ? focused : null);
      saveHidden();
    };
    row.append(box, shortLabel(design) === design.name ? design.name : shortLabel(design) + ' · ' + design.name);
    return row;
  }));
  $('visibility').showModal();
}
$('shown').onclick = openVisibility;
function setFocus(id, updateHash = true) {
  focused = views.has(id) ? id : null;
  grid.classList.toggle('focused', !!focused); $('back').hidden = !focused;
  for (const [key, view] of views) {
    view.element.hidden = !!focused && key !== focused;
    view.element.setAttribute('aria-label', (focused ? '' : 'Open ') + (view.design.name || key));
    view.element.setAttribute('role', focused ? 'img' : 'button');
  }
  if (updateHash) history.replaceState(null, '', location.pathname + location.search + (focused ? '#' + encodeURIComponent(focused) : ''));
  updateExplodeControl(); updatePoseControl(); updateTuneControl();
  requestAnimationFrame(fitVisible);
  document.title = focused ? 'HelpingHands · ' + views.get(focused).design.name : 'HelpingHands · ' + currentProject;
}
$('back').onclick = () => setFocus(null);
function showPhoto(view, id) {
  const photo = PHOTOS.find(item => item.id === id) || PHOTOS[0];
  view.photo = view.select.value = photo.id;
  disposeMeshes(view); view.loading.hidden = true;
  if (photo.bounds && renderer) {
    const [x0, x1, z0, z1] = photo.bounds;
    const texture = new THREE.TextureLoader().load(photo.src); texture.colorSpace = THREE.SRGBColorSpace;
    const geometry = new THREE.PlaneGeometry(x1 - x0, z1 - z0).rotateX(Math.PI / 2).translate((x0 + x1) / 2, 0, (z0 + z1) / 2);
    const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({map:texture, transparent:true, side:THREE.DoubleSide}));
    mesh.userData.explode = new THREE.Vector3();
    view.group.add(mesh); view.preview.hidden = true; view.element.classList.add('has-model'); frame(view);
  } else {
    view.preview.src = photo.src; view.preview.hidden = false; view.element.classList.remove('has-model');
  }
}
function updateExplodeControl() {
  $('explode').hidden = ![...views.values()].some(view => !view.element.hidden && view.group.children.some(mesh => mesh.userData.explode?.lengthSq() > 0));
}
// How one model moves with the slider (cad/mobile_gallery/poses.js): a hinge turns
// it about Y through its pivot, a slide or crank follows the drive. Null = fixed.
// pivot: the right hinge's X when a Tune render moved it (the outline sets it), else poses.js's.
function motionFor(design, name, pivot = null) {
  const pose = POSES[design.pose || design.id];
  if (!pose) return null;
  const sin = deg => Math.sin(THREE.MathUtils.degToRad(deg));
  const crank = (c, a) => -THREE.MathUtils.radToDeg(Math.asin(Math.max(-1, Math.min(1, (2 + 20 * sin(a) - c.mid) / c.radius))));
  const find = list => (list || []).find(item => new RegExp(item.match).test(name));
  const hinge = find(pose.hinges), slide = find(pose.slides), turn = find(pose.cranks);
  if (!hinge && !slide && !turn) return null;
  return angle => {
    if (hinge) return {deg: hinge.sign * (angle - pose.exported), pivot: pivot === null ? hinge.pivot : [Math.sign(hinge.pivot[0]) * pivot, 0, 0], offset: [0, 0, 0]};
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
      .addScaledVector(mesh.userData.explode, exploded ? 1 : 0);
  }
}
function updatePoseControl() {
  $('pose').hidden = ![...views.values()].some(view => !view.element.hidden && view.group.children.some(mesh => mesh.userData.motion));
}
$('openness').value = openness * 100;
$('openness').oninput = () => {
  openness = $('openness').value / 100;
  $('openness-value').textContent = openness ? Math.round(openness * 100) + '% open' : 'Closed';
  for (const view of views.values()) applyExplosion(view);
};
$('openness').oninput();
$('explode').onclick = () => {
  exploded = !exploded;
  $('explode').textContent = exploded ? 'Assemble' : 'Explode';
  $('explode').setAttribute('aria-pressed', String(exploded));
  for (const view of views.values()) applyExplosion(view);
  fitVisible();
};

function createView(design) {
  const element = document.createElement('section'); element.className = 'viewport'; element.tabIndex = 0;
  element.dataset.designId = design.id;
  const preview = document.createElement('img'); preview.className = 'preview'; preview.alt = 'Exported preview'; preview.hidden = true;
  const label = document.createElement('span'); label.className = 'label';
  const loading = document.createElement('span'); loading.className = 'loading'; loading.textContent = 'Loading 3D…'; loading.setAttribute('role','status');
  element.append(preview, label, loading); grid.append(element);
  let select = null;
  if (design.actual) {
    select = document.createElement('select'); select.className = 'photo'; select.setAttribute('aria-label', 'Reference photo');
    select.append(...PHOTOS.map(photo => new Option(photo.label, photo.id)));
    for (const type of ['pointerdown', 'pointerup', 'click', 'keydown']) select.addEventListener(type, event => event.stopPropagation());
    select.onchange = () => showPhoto(view, select.value);
    element.append(select); preview.alt = 'Generalist reference photo';
  }
  if (design.mix) {
    select = document.createElement('div'); select.className = 'mixer';
    for (const [key, label] of [['gripper', 'Gripper version'], ['handles', 'Handles version']]) {
      const choice = document.createElement('select'); choice.setAttribute('aria-label', label); choice.dataset.part = key;
      for (const type of ['pointerdown', 'pointerup', 'click', 'keydown']) choice.addEventListener(type, event => event.stopPropagation());
      choice.onchange = () => { mix[key] = choice.value; updateView(view, buildMix()); };
      select.append(choice);
    }
    element.append(select);
  }
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#13232f');
  scene.add(new THREE.HemisphereLight(0xffffff, 0x51687a, 2.5));
  const light = new THREE.DirectionalLight(0xffffff, 3); light.position.set(150, -200, 300); scene.add(light);
  const camera = new THREE.PerspectiveCamera(35, 1, .1, 10000); camera.up.set(0, 0, 1);
  const group = new THREE.Group(); scene.add(group);
  const controls = renderer ? new OrbitControls(camera, element) : null;
  if (controls) controls.enableDamping = true;
  const view = {design, element, preview, label, loading, select, scene, camera, group, controls, token:0, signature:null};
  let start = null, moved = false; const pointers = new Set();
  element.addEventListener('pointerdown', event => {
    pointers.add(event.pointerId);
    if (pointers.size === 1) { start = [event.clientX, event.clientY]; moved = false; }
    else moved = true;
  });
  element.addEventListener('pointermove', event => {
    if (start && Math.hypot(event.clientX - start[0], event.clientY - start[1]) > 6) moved = true;
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
    else if (event.key === 'Escape') setFocus(null);
  });
  element.addEventListener('dblclick', () => frame(view));
  return view;
}

async function updateView(view, design) {
  view.design = design; view.label.textContent = shortLabel(design);
  if (design.actual) { if (!view.photo) showPhoto(view, PHOTOS[0].id); return; }
  if (view.tuned) return;   // Tune meshes stay until Reset; a catalog refresh must not swap them for the exported ones
  if (design.mix) {
    const [gripper, handles] = view.select.children;
    gripper.replaceChildren(...design.grippers.map(item => new Option('Gripper ' + lineVersion(item), lineVersion(item))));
    handles.replaceChildren(new Option('No handles', 'none'), ...design.handles.map(item => new Option('Handles ' + lineVersion(item), lineVersion(item))));
    gripper.value = mix.gripper; handles.value = mix.handles;
    view.element.setAttribute('aria-label', design.name); if (focused === MIX.id) document.title = 'HelpingHands · ' + design.name;
  }
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
      const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({color:model.color || '#cbd9e2', roughness:.65, metalness:.08}));
      mesh.userData.explode = new THREE.Vector3(...(model.explode || [0, 0, 0]));
      mesh.userData.motion = motionFor(design, model.name);
      meshes.push(mesh);
    }
    for (const mesh of meshes) view.group.add(mesh);
    applyExplosion(view);
    updateExplodeControl(); updatePoseControl();
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

function showProject(project, focusId = null) {
  currentProject = project; $('project').value = project;
  const list = visibleDesigns(project);
  updateShownButton(); status();
  const ids = new Set(list.map(design => design.id));
  for (const [id, view] of views) if (!ids.has(id)) { removeView(view); views.delete(id); }
  grid.style.setProperty('--columns', list.length === 4 ? 2 : Math.min(list.length || 1, 3));
  grid.style.setProperty('--rows', list.length || 1);
  for (const design of list) {
    let view = views.get(design.id);
    if (!view) { view = createView(design); views.set(design.id, view); }
    grid.append(view.element); updateView(view, design);
  }
  setFocus(focusId);
}
$('project').onchange = () => showProject($('project').value);
function hashDesign() { try { return decodeURIComponent(location.hash.slice(1)); } catch { return ''; } }
window.addEventListener('hashchange', () => {
  const target = hashDesign() === MIX.id ? MIX : catalog?.designs.find(design => design.id === hashDesign());
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
    const projects = [...new Set(catalog.designs.map(design => design.project))];
    $('project').replaceChildren(...projects.map(project => { const option = document.createElement('option'); option.value = option.textContent = project; return option; }));
    // A first load with no #design opens on the mix-and-match tile (2.1 unless ?gripper/?handles say otherwise).
    const wanted = focused || (initial ? hashDesign() || MIX.id : '');
    const target = wanted === MIX.id ? MIX : catalog.designs.find(design => design.id === wanted);
    const project = target?.project || (projects.includes(currentProject) ? currentProject : projects.find(p => p === 'Generalist Gripper') || projects[0]);
    const sameLayout = !initial && project === currentProject && JSON.stringify([...views.keys()]) === JSON.stringify(visibleDesigns(project).map(d => d.id));
    if (sameLayout) {
      $('project').value = project;
      for (const view of views.values()) updateView(view, view.design.actual ? ACTUAL : view.design.mix ? buildMix() : catalog.designs.find(d => d.id === view.design.id));
      // No layout/frame reset: preserve focused model and camera on unchanged refresh.
      updateShownButton();
    } else showProject(project, target?.id || null);
    status();
  } catch (error) { message('Could not refresh. ' + error.message); }
  finally { refreshing = false; }
}
// Tune (2.4 on): a design whose catalog entry carries `params` (its params.json) gets a slider per parameter. Each change
// posts {design, values} to serve_designs.py /tune, which renders the real OpenSCAD parts with those values (a solid-only
// change is ~0.1 s, an outline change ~1 s) and the view swaps them in, camera untouched. One request is in flight at a
// time; while it runs, only the newest values wait, so a drag always ends on what the slider shows. ?tune=name:value,...
// presets the values (links, screenshots); Copy puts the changed values on the clipboard for the next version.
const tune = {view:null, values:{}, busy:false, again:false};
const tuneQuery = query.get('tune');
function tuneParams(design) { return (design?.params || []).flatMap(group => group.params); }
function updateTuneControl() {
  const view = focused && views.get(focused);
  $('tune-open').hidden = !view || !tuneParams(view.design).length;
  if ($('tune-open').hidden && !$('tune').hidden) closeTune();
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
  tune.view = view; $('tune').hidden = false; $('tune-open').setAttribute('aria-expanded', 'true');
  requestAnimationFrame(fitVisible);   // a phone's sheet takes the bottom half
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
  for (const type of ['pointerdown', 'pointerup', 'click', 'keydown', 'wheel']) $('tune').addEventListener(type, event => event.stopPropagation());
  if (Object.keys(tune.values).length) requestTune(); else tuneStatus('Drag a slider: the real CAD re-renders. Tap a value to reset it.');
}
function closeTune() { $('tune').hidden = true; $('tune-open').setAttribute('aria-expanded', 'false'); requestAnimationFrame(fitVisible); }
$('tune-open').onclick = () => $('tune').hidden ? openTune(views.get(focused)) : closeTune();
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
      const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({color:model.color || '#cbd9e2', roughness:.65, metalness:.08}));
      mesh.userData.explode = new THREE.Vector3(...(model.explode || [0, 0, 0]));
      mesh.userData.motion = motionFor(view.design, model.name, result.pivot ?? null);
      meshes.push(mesh);
    }
    // Swapped in even when newer values are waiting: mid-drag the model keeps up instead of freezing.
    disposeMeshes(view); for (const mesh of meshes) view.group.add(mesh); applyExplosion(view);
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

$('refresh').onclick = refresh;
await refresh();
if (tuneQuery && focused && tuneParams(views.get(focused)?.design).length) openTune(views.get(focused));
setInterval(refresh, 300000);
