// Draws a design's concept scene (web/gen_NN.js, the vision) and its OpenSCAD
// STLs (the printable truth) with the same orthographic camera, lights and
// framing, so any difference on screen is a difference in the geometry. The
// diff is silhouette against silhouette: magenta is in the vision but missing
// from the print, cyan is in the print but not the vision, grey is shared.
import * as THREE from 'three';
import { STLLoader } from 'three/addons/STLLoader.js';
import { OrbitControls } from 'three/addons/OrbitControls.js';
import * as shapes from './shapes.js';

const query = new URLSearchParams(location.search);
const live = query.has('live');
let mode = query.get('mode') || 'web';
let view = query.get('view') || 'iso';

// CAD frame: millimetres, Z up, the gripper's jaws open along X, front is -Y.
const VIEWS = {
  front: { dir: [0, -1, 0], up: [0, 0, 1] },
  side: { dir: [1, 0, 0], up: [0, 0, 1] },
  top: { dir: [0, 0, 1], up: [0, 1, 0] },
  iso: { dir: [1, -1.3, 0.9], up: [0, 0, 1] },
  exploded: { dir: [1, -1.3, 0.9], up: [0, 0, 1], explode: true },
};
const BACKGROUND = new THREE.Color('#0d1a22');
const SHARED = new THREE.Color('#5d6878');
const WEB_ONLY = new THREE.Color('#ff4fa3');
const STL_ONLY = new THREE.Color('#2fd3dd');

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = BACKGROUND;
scene.add(new THREE.HemisphereLight('#ffffff', '#30404c', 1.4));
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10000);
const key = new THREE.DirectionalLight('#ffffff', 2.2);
key.position.set(0.4, 0.6, 1);
camera.add(key);
scene.add(camera);

const web = new THREE.Group();
const stl = new THREE.Group();
scene.add(web, stl);
let design = null;
let exploded = false;
let controls = null;
let concept = null;      // the concept module: it may export `controls` and `update(values)` to move
const values = {};       // the slider values, kept across live reloads; &set=pull:60,mode:robot presets them
for (const pair of (query.get('set') || '').split(',').filter(Boolean)) {
  const [id, value] = pair.split(':');
  values[id] = value === 'true' ? true : value === 'false' ? false : isNaN(+value) ? value : +value;
}

const message = (text) => {
  const el = document.getElementById('message');
  el.style.display = text ? 'flex' : 'none';
  el.innerHTML = text || '';
};
const bust = () => `?t=${Date.now()}`;
// A local server answering a burst of STL requests now and then drops one; ask again.
async function get(url, tries = 4) {
  for (let i = 1; ; i++) {
    try { return await fetch(url); } catch (error) { if (i >= tries) throw error; }
    await new Promise((r) => setTimeout(r, 150 * i));
  }
}

function clear(group) {
  for (const child of [...group.children]) {
    group.remove(child);
    child.traverse((o) => { o.geometry?.dispose(); });
  }
}

async function loadDesign() {
  const list = await (await get(`./designs.json${bust()}`)).json();
  design = list.designs.find((d) => d.id === query.get('design')) || null;
  if (!design) throw new Error(`No design "${query.get('design')}" in designs.json`);
}

async function loadSTL() {
  clear(stl);
  const loader = new STLLoader();
  const missing = [];
  await Promise.all(design.parts.map(async (part) => {
    const response = await get(`/${part.path}${bust()}`);
    if (!response.ok) { missing.push(part.path); return; }
    const geometry = loader.parse(await response.arrayBuffer());
    geometry.computeVertexNormals();
    const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({
      color: part.color, roughness: 0.6, metalness: 0.05, side: THREE.DoubleSide,
    }));
    const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geometry, 35),
      new THREE.LineBasicMaterial({ color: '#0b141a', transparent: true, opacity: 0.35 }));
    edges.userData.decoration = true;
    mesh.add(edges);
    mesh.name = part.name;
    mesh.userData.explode = new THREE.Vector3(...part.explode);
    stl.add(mesh);
  }));
  return missing;
}

async function loadConcept() {
  clear(web);
  if (!design.concept) return false;
  let module;
  for (let i = 1; !module; i++) {
    try { module = await import(`/${design.concept}${bust()}`); } catch (error) { if (i >= 4) throw error; }
  }
  // Bind the helpers to THREE so a concept calls box(min, max, mat).
  const helpers = Object.fromEntries(Object.entries(shapes).map(([k, f]) => [k, (...a) => f(THREE, ...a)]));
  for (const piece of await module.default(THREE, helpers)) {
    piece.object.name = piece.name || '';
    piece.object.userData.explode = new THREE.Vector3(...(piece.explode || [0, 0, 0]));
    web.add(piece.object);
  }
  concept = module;
  posePanel();
  return true;
}

// A concept that moves (exports `controls` + `update`) gets sliders in the
// live web pane. update(values) poses the model and returns a readout. The
// sheet and the STL pane always show its default pose.
function posePanel() {
  document.getElementById('pose')?.remove();
  if (!concept?.update || !concept.controls) return;
  for (const c of concept.controls) if (!(c.id in values)) values[c.id] = c.value;
  const apply = () => { readout.textContent = concept.update({ ...values }) || ''; draw(); };
  if (!live || mode !== 'web') {
    concept.update(Object.fromEntries(concept.controls.map((c) => [c.id, mode === 'sheet' ? c.value : values[c.id]])));
    return;
  }
  const panel = document.createElement('div');
  panel.id = 'pose';
  const readout = document.createElement('pre');
  let playing = null;
  for (const c of concept.controls) {
    const row = document.createElement('label');
    row.append(Object.assign(document.createElement('span'), { textContent: c.label }));
    let input;
    if (c.type === 'select') {
      input = document.createElement('select');
      for (const [value, text] of c.options) input.append(new Option(text, value, false, value === values[c.id]));
      input.onchange = () => { values[c.id] = input.value; apply(); };
    } else if (c.type === 'checkbox') {
      input = Object.assign(document.createElement('input'), { type: 'checkbox', checked: !!values[c.id] });
      input.onchange = () => { values[c.id] = input.checked; apply(); };
    } else {
      input = Object.assign(document.createElement('input'), { type: 'range', min: c.min, max: c.max, step: c.step || 1, value: values[c.id] });
      const shown = Object.assign(document.createElement('b'), { textContent: `${values[c.id]}${c.unit || ''}` });
      input.oninput = () => { values[c.id] = +input.value; shown.textContent = `${input.value}${c.unit || ''}`; apply(); };
      row.append(input, shown);
      if (c.play) {
        const button = Object.assign(document.createElement('button'), { textContent: '▶' });
        button.onclick = (event) => {
          event.preventDefault();
          if (playing) { cancelAnimationFrame(playing); playing = null; button.textContent = '▶'; return; }
          button.textContent = '❚❚';
          const start = performance.now();
          const step = (now) => {
            const phase = ((now - start) / 4000) % 1;   // 4 s: open, closed, open
            input.value = c.min + (c.max - c.min) * (1 - Math.cos(phase * 2 * Math.PI)) / 2;
            input.oninput();
            playing = requestAnimationFrame(step);
          };
          playing = requestAnimationFrame(step);
        };
        row.append(button);
      }
      panel.append(row);
      continue;
    }
    row.append(input);
    panel.append(row);
  }
  panel.append(readout);
  document.body.append(panel);
  apply();
}

function setExploded(on) {
  exploded = on;
  for (const group of [web, stl]) {
    for (const child of group.children) child.position.copy(child.userData.explode).multiplyScalar(on ? 1 : 0);
  }
}

// One framing for both models, so the web and STL panes line up pixel for pixel.
function frame(name, aspect) {
  const v = VIEWS[name] || VIEWS.iso;
  setExploded(!!v.explode);
  const box = new THREE.Box3();
  for (const group of [web, stl]) {
    group.visible = true;
    group.updateMatrixWorld(true);
    group.traverse((o) => { if (o.isMesh) box.expandByObject(o); });
  }
  if (box.isEmpty()) box.set(new THREE.Vector3(-50, -50, -50), new THREE.Vector3(50, 50, 50));
  const center = box.getCenter(new THREE.Vector3());
  const radius = box.getSize(new THREE.Vector3()).length() / 2;
  const dir = new THREE.Vector3(...v.dir).normalize();
  camera.up.set(...v.up);
  camera.position.copy(center).addScaledVector(dir, radius * 4);
  camera.lookAt(center);
  camera.updateMatrixWorld(true);
  // Tight fit: the box corners in camera space.
  const inverse = camera.matrixWorldInverse;
  let w = 0, h = 0;
  for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) {
    const p = new THREE.Vector3(x, y, z).applyMatrix4(inverse);
    p.sub(center.clone().applyMatrix4(inverse));
    w = Math.max(w, Math.abs(p.x)); h = Math.max(h, Math.abs(p.y));
  }
  const half = Math.max(h, w / aspect) * 1.08;
  Object.assign(camera, { left: -half * aspect, right: half * aspect, top: half, bottom: -half,
                          near: radius * 0.5, far: radius * 8, zoom: 1 });
  camera.updateProjectionMatrix();
  if (controls) { controls.target.copy(center); controls.update(); }
}

// Silhouettes into two targets, then one quad colours where they disagree.
const silhouette = new THREE.MeshBasicMaterial({ color: '#ffffff', side: THREE.DoubleSide });
const targets = [new THREE.WebGLRenderTarget(4, 4), new THREE.WebGLRenderTarget(4, 4)];
const composite = new THREE.ShaderMaterial({
  uniforms: { a: { value: null }, b: { value: null }, shared: { value: SHARED }, webOnly: { value: WEB_ONLY },
              stlOnly: { value: STL_ONLY }, background: { value: BACKGROUND } },
  vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }',
  fragmentShader: `uniform sampler2D a, b; uniform vec3 shared, webOnly, stlOnly, background; varying vec2 vUv;
    void main() {
      float w = texture2D(a, vUv).r, s = texture2D(b, vUv).r;
      vec3 c = w > 0.5 && s > 0.5 ? shared : w > 0.5 ? webOnly : s > 0.5 ? stlOnly : background;
      gl_FragColor = vec4(c, 1.0);
      #include <colorspace_fragment>
    }`,
  depthTest: false,
});
const quadScene = new THREE.Scene();
quadScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), composite));

function withOnly(group, draw) {
  web.visible = group === web; stl.visible = group === stl;
  const hidden = [];
  scene.traverse((o) => { if (o.userData.decoration && o.visible) { o.visible = false; hidden.push(o); } });
  draw();
  hidden.forEach((o) => { o.visible = true; });
  web.visible = stl.visible = true;
}

// Returns {web, stl, shared} pixel counts when `measure` is set.
function drawDiff(width, height, viewport, measure) {
  for (const [i, group] of [web, stl].entries()) {
    targets[i].setSize(width, height);
    renderer.setRenderTarget(targets[i]);
    renderer.setViewport(0, 0, width, height);
    renderer.setScissorTest(false);
    scene.overrideMaterial = silhouette;
    scene.background = new THREE.Color('#000000');
    withOnly(group, () => renderer.render(scene, camera));
  }
  scene.overrideMaterial = null;
  scene.background = BACKGROUND;
  let counts = null;
  if (measure) {
    const pixels = [new Uint8Array(width * height * 4), new Uint8Array(width * height * 4)];
    targets.forEach((t, i) => renderer.readRenderTargetPixels(t, 0, 0, width, height, pixels[i]));
    counts = { web: 0, stl: 0, shared: 0 };
    for (let p = 0; p < width * height * 4; p += 4) {
      const w = pixels[0][p] > 127, s = pixels[1][p] > 127;
      if (w && s) counts.shared++; else if (w) counts.web++; else if (s) counts.stl++;
    }
  }
  renderer.setRenderTarget(null);
  composite.uniforms.a.value = targets[0].texture;
  composite.uniforms.b.value = targets[1].texture;
  viewport();
  renderer.render(quadScene, camera);
  return counts;
}

function draw() {
  const width = innerWidth, height = innerHeight;
  renderer.setSize(width, height);
  renderer.setScissorTest(false);
  const px = renderer.getPixelRatio();
  if (mode === 'diff') {
    drawDiff(Math.round(width * px), Math.round(height * px), () => renderer.setViewport(0, 0, width, height));
  } else {
    withOnly(mode === 'stl' ? stl : web, () => renderer.render(scene, camera));
  }
}

function tag(text, x, y, cls = '') {
  const el = document.createElement('div');
  el.className = `tag ${cls}`;
  el.textContent = text;
  Object.assign(el.style, { left: `${x}px`, top: `${y}px` });
  document.body.appendChild(el);
  labels.push({ text, x, y, color: { web: '#ff7cc0', stl: '#6fe3ea' }[cls] || '#dfe7ef' });
}
const labels = [];

// The sheet as one PNG, labels burnt in, so render_compare needs no screenshot.
function flatten() {
  const out = document.createElement('canvas');
  out.width = renderer.domElement.width; out.height = renderer.domElement.height;
  const ctx = out.getContext('2d');
  ctx.drawImage(renderer.domElement, 0, 0);
  ctx.font = '600 13px -apple-system, Helvetica, sans-serif';
  ctx.textBaseline = 'top';
  for (const l of labels) {
    ctx.fillStyle = 'rgba(0,0,0,0.45)';
    ctx.fillRect(l.x, l.y, ctx.measureText(l.text).width + 16, 24);
    ctx.fillStyle = l.color;
    ctx.fillText(l.text, l.x + 8, l.y + 5);
  }
  return out.toDataURL('image/png');
}

// Every view as a row of web | STL | diff, for render_compare.
function sheet() {
  const cell = 420, header = 56, rows = Object.keys(VIEWS);
  const width = cell * 3, height = header + cell * rows.length;
  renderer.setPixelRatio(1);
  renderer.setSize(width, height);
  document.body.style.overflow = 'visible';
  renderer.setClearColor(BACKGROUND);
  renderer.setScissorTest(false);
  renderer.clear();
  renderer.setScissorTest(true);
  tag(design.name, 12, 14);
  const result = { design: design.id, views: {} };
  rows.forEach((name, r) => {
    frame(name, 1);
    const y = height - header - (r + 1) * cell; // GL origin is bottom-left
    [['web', web], ['stl', stl]].forEach(([, group], c) => {
      renderer.setViewport(c * cell, y, cell, cell);
      renderer.setScissor(c * cell, y, cell, cell);
      withOnly(group, () => renderer.render(scene, camera));
    });
    const counts = drawDiff(cell, cell, () => {
      renderer.setScissorTest(true);
      renderer.setViewport(2 * cell, y, cell, cell);
      renderer.setScissor(2 * cell, y, cell, cell);
    }, true);
    const union = counts.web + counts.stl + counts.shared;
    const iou = union ? counts.shared / union : 1;
    result.views[name] = { iou: +iou.toFixed(3), web_only_px: counts.web, stl_only_px: counts.stl, shared_px: counts.shared };
    const top = header + r * cell + 8;
    tag(`${name} · web concept`, 8, top, 'web');
    tag(`${name} · OpenSCAD STL`, cell + 8, top, 'stl');
    tag(`${name} · diff  IoU ${(iou * 100).toFixed(0)}%`, 2 * cell + 8, top);
  });
  tag('magenta: vision only   cyan: STL only   grey: both', 2 * cell + 8, header + rows.length * cell - 34);
  return result;
}

async function load() {
  await loadDesign();
  const [missing, hasConcept] = await Promise.all([loadSTL(), loadConcept()]);
  const notes = [];
  if (!hasConcept) notes.push(`No web concept yet: add <b>${design.folder}/web/${design.generation}.js</b>`);
  if (missing.length) notes.push(`STL not exported yet: ${missing.join(', ')}`);
  return notes;
}

// keep: a live reload after a save leaves the camera where the user orbited it.
async function refresh(keep = false) {
  const saved = keep && controls && { position: camera.position.clone(), up: camera.up.clone(),
                                      target: controls.target.clone(), zoom: camera.zoom };
  const notes = await load();
  const empty = mode === 'web' ? !web.children.length : mode === 'stl' ? !stl.children.length : false;
  message(empty ? notes.join('<br>') : '');
  frame(view, innerWidth / innerHeight);
  if (saved) {
    applying = true;
    camera.position.copy(saved.position); camera.up.copy(saved.up); camera.zoom = saved.zoom;
    controls.target.copy(saved.target);
    camera.updateProjectionMatrix();
    controls.update();
    applying = false;
  }
  draw();
}

const native = window.webkit?.messageHandlers?.hh;
let applying = false;

window.hh = {
  reload: () => refresh(true).catch(fail),
  setView: (name) => { view = name; frame(view, innerWidth / innerHeight); draw(); },
  setMode: (name) => { mode = name; refresh().catch(fail); },
  // Camera sync between the app's panes: the other pane's orbit, verbatim.
  setCamera: (c) => {
    applying = true;
    camera.position.fromArray(c.position); camera.up.fromArray(c.up); camera.zoom = c.zoom;
    if (c.exploded !== exploded) setExploded(c.exploded);
    controls?.target.fromArray(c.target);
    camera.lookAt(new THREE.Vector3().fromArray(c.target));
    camera.updateProjectionMatrix();
    controls?.update();
    draw();
    applying = false;
  },
};

function fail(error) {
  message(`Couldn't draw this design:<br>${error.message}`);
  document.getElementById('result').textContent = JSON.stringify({ error: error.message });
  document.title = 'error';
}

if (mode === 'sheet') {
  load().then((notes) => {
    const result = sheet();
    result.notes = notes;
    result.png = flatten();
    document.getElementById('result').textContent = JSON.stringify(result);
    document.title = 'ready';
  }).catch(fail);
} else {
  if (live) {
    controls = new OrbitControls(camera, renderer.domElement);
    controls.addEventListener('change', () => {
      draw();
      if (!applying) {
        native?.postMessage({ camera: { position: camera.position.toArray(), up: camera.up.toArray(),
          target: controls.target.toArray(), zoom: camera.zoom, exploded } });
      }
    });
  }
  addEventListener('resize', () => { frame(view, innerWidth / innerHeight); draw(); });
  refresh().then(() => { document.title = 'ready'; }).catch(fail);
}
