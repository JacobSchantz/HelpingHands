// Robot Glove Hand gen_04 · index finger, first test print: the JavaScript model.
// Built here from the numbers in jake_hand.scad (the hand) and
// gen_04_index_print.scad (the mechanism's own sizes), both read from the
// files, with its own geometry: each saddle is one extruded cross-section
// (the CAD hulls two and trims them), the base pad is an arc, so the diff
// against the STL shows where the two constructions disagree. The joints
// move: `controls` and `update` drive the pose, the line and the elastic,
// and report what the line has to do.
export const controls = [
  { id: 'mode', label: 'Drive', type: 'select', value: 'curl',
    options: [['curl', 'Curl: all joints together'], ['joints', 'Each joint'], ['robot', 'Robot only: the line pulls (predicted)']] },
  { id: 'pull', label: 'Curl / pull', min: 0, max: 100, step: 1, value: 0, unit: '%', play: true },
  { id: 'mcp', label: 'MCP', min: -4, max: 95, step: 1, value: 0, unit: '°' },
  { id: 'pip', label: 'PIP', min: -5, max: 102, step: 1, value: 0, unit: '°' },
  { id: 'dip', label: 'DIP', min: -5, max: 71, step: 1, value: 0, unit: '°' },
  { id: 'finger', label: "Jake's finger", type: 'checkbox', value: false },
  { id: 'neighbours', label: 'Middle finger and thumb (yaw 45°)', type: 'checkbox', value: false },
];

let model = null;

export default async function build(THREE, { material, box }) {
  const read = async (name) => {
    const text = await (await fetch(new URL(`../${name}`, import.meta.url) + `?t=${Date.now()}`)).text();
    const out = {};
    for (const m of text.matchAll(/^(\w+)\s*=\s*([^;]+);/gm)) {
      try { out[m[1]] = JSON.parse(m[2]); } catch { /* an expression: not needed */ }
    }
    return out;
  };
  const h = await read('jake_hand.scad');
  const p = await read('gen_04_index_print.scad');
  const rad = THREE.MathUtils.degToRad;

  // ---------- the index finger (jake_hand.scad's construction) ----------
  const lerp4 = (a, b) => [0, 1, 2, 3].map((k) => a + (b - a) * k / 3);
  const W = lerp4(h.hand_finger_base_w[0], h.hand_finger_tip_w[0]);
  const T = lerp4(h.hand_finger_base_t[0], h.hand_finger_tip_t[0]);
  const L = h.hand_phalanx.map((f) => f * h.hand_finger_len[0]);
  const E = [L[0], L[1], L[2] - Math.min(W[3], T[3]) / 2 + p.tip_room];
  const M = [h.hand_palm_width / 2 - h.hand_finger_base_w[0] / 2, h.hand_palm_length - h.hand_knuckle_drop[0], h.hand_finger_base_t[0] / 2];
  const g = p.clearance;
  const half = (k, y, extra) => {
    const f = Math.max(0, Math.min(1, y / E[k]));
    return [(W[k] + (W[k + 1] - W[k]) * f) / 2 + extra, (T[k] + (T[k + 1] - T[k]) * f) / 2 + extra];
  };
  const low = (k) => p.flap_low * (T[k] + T[k + 1]) / 4;
  const xi = (j) => W[j] / 2 + g + 0.1;
  const topZ = (k, y) => half(k, y, g)[1] + p.top_t;
  const chanZ = (k, y) => half(k, y, g)[1] + p.top_t / 2;

  const petg = material('#d9dde3', { roughness: 0.5 });
  const grey = material('#9aa6b8', { roughness: 0.55 });
  const blue = material('#5b8def', { roughness: 0.5 });
  const steel = material('#6b7380', { roughness: 0.35, metalness: 0.4 });
  const cordMat = new THREE.MeshBasicMaterial({ color: '#e0662a' });
  const elasticMat = new THREE.MeshBasicMaterial({ color: '#3a9d5a' });
  const skin = new THREE.MeshPhysicalMaterial({ color: '#e2b49a', transparent: true, opacity: 0.45, roughness: 0.8, depthWrite: false });
  const skin2 = new THREE.MeshPhysicalMaterial({ color: '#c9a088', transparent: true, opacity: 0.3, roughness: 0.8, depthWrite: false });

  // A flat plate in the y-z plane, th thick from x0 (radial side).
  const toYZ = new THREE.Matrix4().set(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1);
  function plate(shape, x0, th, mat) {
    const geo = new THREE.ExtrudeGeometry(shape, { depth: th, bevelEnabled: false, curveSegments: 20 });
    geo.applyMatrix4(toYZ);
    geo.translate(x0, 0, 0);
    return new THREE.Mesh(geo, mat);
  }
  const poly = (pts) => new THREE.Shape(pts.map(([a, b]) => new THREE.Vector2(a, b)));
  const disc = (r, y = 0, z = 0) => { const s = new THREE.Shape(); s.absarc(y, z, r, 0, Math.PI * 2, false); return s; };
  function rod(c, r, len, axis, mat, seg = 20) {
    const geo = new THREE.CylinderGeometry(r, r, len, seg);
    if (axis === 'x') geo.rotateZ(Math.PI / 2);
    if (axis === 'z') geo.rotateX(Math.PI / 2);
    geo.translate(...c);
    return new THREE.Mesh(geo, mat);
  }

  // A saddle's cross-section at y, in the x-z plane: the flat top, the 45°
  // corners, the radial wall down to low(k), the ulnar edge inside Jake's
  // own width, and the comfort ellipse inside, walked as one outline.
  function section(k, y) {
    const [A, B] = half(k, y, g + 0.1), wh = half(k, y, 0)[0], zt = topZ(k, y), xr = half(k, y, g)[0] + p.shell;
    const c = Math.hypot(half(k, y, g)[0], half(k, y, g)[1]) + Math.SQRT2 * p.corner;
    const zu = B * Math.sqrt(Math.max(0, 1 - ((wh - p.ulnar_wall) / A) ** 2));
    const xl = A * Math.sqrt(Math.max(0, 1 - (low(k) / B) ** 2)) + 1, zl = -B * Math.sqrt(Math.max(0, 1 - (xl / A) ** 2));
    const pts = [[xr, -low(k)], [xr, c - xr], [c - zt, zt], [-(c - zt), zt], [-wh, c - wh], [-wh, zu]];
    // the comfort ellipse from the ulnar edge, over the top, to the radial lip
    const t0 = Math.PI - Math.asin(zu / B), t1 = Math.asin(zl / B);
    for (let i = 0; i <= 24; i++) {
      const t = t0 + (t1 - t0) * i / 24;
      pts.push([A * Math.cos(t), B * Math.sin(t)]);
    }
    pts.push([xl, -low(k)]);
    return poly(pts);
  }
  // Extruded along y from y0 to y1 (section taken at the middle).
  function shell(k, y0, y1, mat) {
    const geo = new THREE.ExtrudeGeometry(section(k, (y0 + y1) / 2), { depth: y1 - y0, bevelEnabled: false });
    geo.applyMatrix4(new THREE.Matrix4().set(1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1));   // shape (x, z), depth +y
    geo.translate(0, y0, 0);
    return new THREE.Mesh(geo, mat);
  }

  // ---------- the cord route, in each body's own frame ----------
  const guideAt = (k, y, z) => [half(k, y, g)[0] + p.shell + 0.7, y, z];
  const guidesOn = [
    [[p.cord_reach[0], p.cord_low[0]], [E[0] - p.cord_reach[1], p.cord_low[1]]],
    [[p.cord_reach[1], p.cord_low[1]], [E[1] - p.cord_reach[2], p.cord_low[2]]],
    [[p.cord_reach[2], p.cord_low[2]]],
  ].map((list, k) => list.map(([y, z]) => guideAt(k, y, -z)));
  // the line wraps the post's back and leaves on the internal tangent to the drum's front
  const rp = p.post_r + p.cord_d / 2, rd = p.drum_r + p.cord_d / 2;
  const D = [p.drum_at[0] - p.post_at[0], p.drum_at[1] - p.post_at[1]], Ld = Math.hypot(...D);
  const psi = Math.atan2(D[1], D[0]) - Math.acos(-(rp + rd) / Ld), n = [Math.cos(psi), Math.sin(psi)];
  const onPost = [p.post_at[0] - rp * n[0], p.post_at[1] - rp * n[1]], onDrum = [p.drum_at[0] + rd * n[0], p.drum_at[1] + rd * n[1]];
  const a0 = Math.atan2(onPost[1] - p.post_at[1], onPost[0] - p.post_at[0]);
  const wrap = Array.from({ length: 7 }, (_, i) => {
    const a = (a0 < 0 ? a0 + 2 * Math.PI : a0) + (1.5 * Math.PI - (a0 < 0 ? a0 + 2 * Math.PI : a0)) * i / 6;
    return [p.cord_x, p.post_at[0] + rp * Math.cos(a), p.post_at[1] + rp * Math.sin(a)];
  });
  const postBottom = wrap.at(-1);
  const exitY = E[2] - 3;
  const anchor = [-4, -p.base_back + 5, 29];
  const eyelet = [0, 0.5, p.pad_top_front];
  const chanOn = [[p.prox_start, E[0] - p.gap / 2], [p.gap / 2, E[1] - p.gap / 2], [p.gap / 2, exitY]]
    .map((ys, k) => ys.map((y) => [0, y, chanZ(k, y)]));
  chanOn[2].push([0, exitY, topZ(2, exitY)]);

  // ---------- bodies ----------
  const root = new THREE.Group();
  root.position.set(...M);
  const seg = [0, 1, 2].map(() => new THREE.Group());
  root.add(seg[0]); seg[0].add(seg[1]); seg[1].add(seg[2]);
  seg[1].position.y = E[0]; seg[2].position.y = E[1];

  const forkIn = (j) => xi(j), lugX = (j) => xi(j) + p.fork_t + p.lug_c;
  const forkOut = (j) => lugX(j) + p.lug_t + p.lug_c;
  for (let k = 0; k < 3; k++) {
    const body = new THREE.Group();
    const y0 = k === 0 ? p.prox_start : p.gap / 2, y1 = k === 2 ? E[2] : E[k] - p.gap / 2;
    // above the axis the full length; below it each end shortened by its V, at the wall's mid-depth
    const va = k === 0 ? 0 : Math.tan(rad(p.vee[k] / 2)) * low(k) / 2, vd = k === 2 ? 0 : Math.tan(rad(p.vee[k + 1] / 2)) * low(k) / 2;
    body.add(shell(k, y0 + va, y1 - vd, petg));
    if (k === 2) {   // the nose: a box tapering over the fingertip
      const [A, B] = half(2, E[2], g), r = Math.min(W[3], T[3]) / 2 + g + p.shell + 1;
      const geo = new THREE.CylinderGeometry(0.68 * (A + p.shell), A + p.shell, r, 4, 1);
      geo.rotateY(Math.PI / 4);
      geo.scale(1, 1, (topZ(2, E[2]) + p.nose_floor) / (2 * (A + p.shell)) * Math.SQRT2);
      geo.translate(0, E[2] + r / 2, (topZ(2, E[2]) - p.nose_floor) / 2);
      body.add(new THREE.Mesh(geo, petg));
    }
    for (const q of guidesOn[k]) body.add(rod(q, (k === 2 ? 5.6 : p.boss_d) / 2, p.boss_len, 'y', petg));
    if (k === 0) {   // the MCP tab (outer), its tail, and its bridge in to the wall
      const tabX = xi(0) + p.mcp_plate + p.lug_c;
      const tab = poly([[0, -p.mcp_r], [p.prox_start + 4, -p.mcp_r], [p.prox_start + 4, p.mcp_r], [0, p.mcp_r]]);
      body.add(plate(tab, tabX, p.mcp_tab, petg));
      body.add(plate(disc(p.mcp_r), tabX, p.mcp_tab, petg));
      body.add(plate(poly([[-p.tail_r, -p.tail_w], [0, -p.tail_w], [0, p.tail_w], [-p.tail_r, p.tail_w]]), tabX, p.mcp_tab, petg));
      body.add(box([xi(0) - 1.5, p.prox_start, -p.mcp_r], [tabX + 0.1, p.prox_start + 4, p.mcp_r], petg));
    }
    if (k > 0) {     // the fork at this saddle's proximal joint: inner disc, outer plate, bridge
      const tall = (y) => p.lug_r + topZ(k, y);
      body.add(plate(disc(p.lug_r), forkIn(k), p.fork_t, petg));
      body.add(plate(poly([[0, -p.lug_r], [p.lug_r + 3, -p.lug_r], [p.lug_r + 6, -p.lug_r], [p.lug_r + 6, tall(7) - p.lug_r], [p.lug_r + 3, tall(7) - p.lug_r], [0, p.lug_r]]), forkOut(k), p.fork_t, petg));
      body.add(plate(disc(p.lug_r), forkOut(k), p.fork_t, petg));
      body.add(box([forkIn(k) - 1, p.lug_r + 3, -p.lug_r], [forkOut(k) + p.fork_t, p.lug_r + 6, topZ(k, 7)], petg));
    }
    if (k < 2) {     // the lug at this saddle's distal joint, and the pin
      const j = k + 1;
      body.add(plate(disc(p.lug_r, E[k]), lugX(j), p.lug_t, petg));
      body.add(plate(poly([[E[k] - p.lug_r - 5, -p.lug_r], [E[k], -p.lug_r], [E[k], topZ(k, E[k])], [E[k] - p.lug_r - 5, topZ(k, E[k] - 9)]]), lugX(j), p.lug_t, petg));
      body.add(box([xi(j) - 1, E[k] - p.lug_r - 5, -p.lug_r], [lugX(j) + 0.1, E[k] - p.lug_r - 2, topZ(k, E[k] - 7)], petg));
      body.add(rod([(forkIn(j) + forkOut(j) + p.fork_t) / 2, E[k], 0], 0.875, forkOut(j) + p.fork_t - forkIn(j) + 0.4, 'x', steel));
    }
    seg[k].add(body);
  }

  // ---------- base ----------
  const base = new THREE.Group();
  const plateX = xi(0), tabX = xi(0) + p.mcp_plate + p.lug_c;
  {
    // the pad: an arc of the back-of-hand shell over the index metacarpal
    const A = h.hand_palm_width / 2 + g + p.pad, B = h.hand_palm_thick / 2 + g + p.pad, cx = -M[0];
    const t0 = Math.asin((p.pad_ulnar - cx) / A), t1 = Math.asin(Math.min(1, (plateX - cx) / A));
    const geo = new THREE.CylinderGeometry(A, A * 0.92, p.base_back + 2, 48, 1, true, t0, t1 - t0);
    geo.scale(1, 1, B / A);
    geo.translate(cx, -p.base_back / 2 + 1, h.hand_palm_thick / 2 - M[2]);
    base.add(new THREE.Mesh(geo, grey));
    // the MCP plate: disc, strut up to the pad, forward arm for the stop block, the post's web
    base.add(plate(poly([[-p.mcp_r, 0], [-10, 6], [-10, 15], [2, 15], [2, 6], [p.mcp_r, 0], [p.mcp_r, -1], [-p.mcp_r, -1]]), plateX, p.mcp_plate, grey));
    base.add(plate(disc(p.mcp_r), plateX, p.mcp_plate, grey));
    base.add(plate(poly([[0, p.mcp_r + 0.6], [9.5, p.mcp_r + 0.6], [9.5, p.mcp_r + 5.5], [0, p.mcp_r + 5.5]]), plateX, p.mcp_plate, grey));
    base.add(plate(poly([[p.post_at[0], p.post_at[1] - p.post_r], [-2.5, -2], [-2.5, 0], [-4.5, 0], [p.post_at[0] - p.post_r, p.post_at[1]]]), plateX, p.mcp_plate, grey));
    base.add(plate(poly([[p.stop_y, p.mcp_r + 0.6], [9.5, p.mcp_r + 0.6], [9.5, p.mcp_r + 5.5], [p.stop_y, p.mcp_r + 5.5]]), plateX + p.mcp_plate, p.mcp_tab + p.lug_c, grey));
    base.add(box([6, -10, 9.5], [plateX + p.mcp_plate, 2, 15], grey));
    base.add(rod([(12.2 + plateX + p.mcp_plate) / 2, p.post_at[0], p.post_at[1]], p.post_r, plateX + p.mcp_plate - 12.2, 'x', grey));
    // eyelet over the knuckle, anchor post at the back
    base.add(rod([0, -1.5, p.pad_top_front], 2.6, 4, 'y', grey));
    base.add(box([-2.6, -1.5, 18], [2.6, 0.5, p.pad_top_front], grey));
    base.add(rod([anchor[0], anchor[1], 26], 2, 6, 'z', grey));
    base.add(rod([anchor[0], anchor[1], 31.75], 3.5, 1.5, 'z', grey));
    // the drum's cheek
    const x0 = p.cord_x - p.drum_w / 2 - p.flange_t - 0.3 - p.cheek_t;
    base.add(rod([x0 + p.cheek_t / 2, p.drum_at[0], p.drum_at[1]], p.flange[0] + 0.5, p.cheek_t, 'x', grey, 40));
    base.add(box([x0, p.drum_at[0] - 9, 16], [x0 + p.cheek_t, p.drum_at[0] + 9, p.drum_at[1]], grey));
    // M3 at the MCP
    base.add(rod([plateX + (p.mcp_plate + p.lug_c + p.mcp_tab) / 2, 0, 0], 1.5, p.mcp_plate + p.lug_c + p.mcp_tab + 1.8, 'x', steel));
  }
  root.add(base);

  const drum = new THREE.Group();
  {
    const x0 = p.cord_x - p.drum_w / 2 - p.flange_t, [y, z] = p.drum_at;
    drum.add(rod([x0 + p.flange_t / 2, y, z], p.flange[0], p.flange_t, 'x', blue, 40));
    drum.add(rod([p.cord_x, y, z], p.drum_r, p.drum_w, 'x', blue, 40));
    drum.add(rod([x0 + p.flange_t + p.drum_w + (p.flange_t + 1) / 2, y, z], p.flange[1], p.flange_t + 1, 'x', blue, 12));
    drum.add(rod([x0 - 3, y, z], 1.5, 18 + p.cheek_t, 'x', steel));
  }
  root.add(drum);

  // ---------- Jake's finger, and the neighbours (not printed, off by default) ----------
  const finger = new THREE.Group();
  finger.position.set(...M);
  const fseg = [0, 1, 2].map(() => new THREE.Group());
  finger.add(fseg[0]); fseg[0].add(fseg[1]); fseg[1].add(fseg[2]);
  fseg[1].position.y = E[0]; fseg[2].position.y = E[1];
  const limb = (group, w0, t0, w1, t1, len, mat) => {
    const geo = new THREE.CylinderGeometry(w1 / 2, w0 / 2, len, 28, 1, false);
    geo.scale(1, 1, ((t0 + t1) / 2) / ((w0 + w1) / 2));
    geo.translate(0, len / 2, 0);
    group.add(new THREE.Mesh(geo, mat));
    const knuckle = new THREE.SphereGeometry(1, 24, 12);
    knuckle.scale(w0 / 2, Math.min(w0, t0) / 2, t0 / 2);
    group.add(new THREE.Mesh(knuckle, mat));
  };
  for (let k = 0; k < 3; k++) limb(fseg[k], W[k], T[k], W[k + 1], T[k + 1], E[k], skin);
  finger.visible = false;
  const neighbours = new THREE.Group();
  {
    const mw = lerp4(h.hand_finger_base_w[1], h.hand_finger_tip_w[1]), mt = lerp4(h.hand_finger_base_t[1], h.hand_finger_tip_t[1]);
    const mx = h.hand_palm_width / 2 - h.hand_finger_base_w[0] - h.hand_finger_base_w[1] / 2;
    const ml = h.hand_phalanx.map((f) => f * h.hand_finger_len[1]);
    let y = h.hand_palm_length - h.hand_knuckle_drop[1];
    for (let k = 0; k < 3; k++) {
      const grp = new THREE.Group();
      grp.position.set(mx, y, h.hand_finger_base_t[1] / 2);
      limb(grp, mw[k], mt[k], mw[k + 1], mt[k + 1], ml[k], skin2);
      neighbours.add(grp);
      y += ml[k];
    }
    // the thumb at yaw 45, as two tapered limbs from its base joint
    const thumb = new THREE.Group();
    thumb.position.set(h.hand_thumb_cmc[0], h.hand_thumb_cmc[1], h.hand_thumb_t[0] / 2);
    thumb.rotation.z = -rad(45);
    const tl = h.hand_thumb_len;
    limb(thumb, h.hand_thumb_w[0], h.hand_thumb_t[0], h.hand_thumb_w[1], h.hand_thumb_t[1], tl[0], skin2);
    const t2 = new THREE.Group();
    t2.position.y = tl[0];
    limb(t2, h.hand_thumb_w[1], h.hand_thumb_t[1], h.hand_thumb_w[3], h.hand_thumb_t[3], tl[1] + tl[2], skin2);
    thumb.add(t2);
    neighbours.add(thumb);
  }
  neighbours.visible = false;

  // ---------- the line and the elastic: one rod per straight run, re-aimed every pose ----------
  const runs = (count, r, mat) => Array.from({ length: count }, () => {
    const geo = new THREE.CylinderGeometry(r, r, 1, 8);
    geo.translate(0, 0.5, 0);
    const mesh = new THREE.Mesh(geo, mat);
    root.add(mesh);
    return mesh;
  });
  const cordRoute = [[p.cord_x, ...onDrum], ...wrap, ...guidesOn.flatMap((list, k) => list.map((q) => [k, q]))];
  const elasticRoute = [anchor, eyelet, ...chanOn.flatMap((list, k) => list.map((q) => [k, q]))];
  const cordRuns = runs(cordRoute.length - 1, p.cord_d / 2, cordMat);
  const elasticRuns = runs(elasticRoute.length - 1, p.elastic_d / 2, elasticMat);
  const up = new THREE.Vector3(0, 1, 0);
  function lay(rods, route) {
    root.updateMatrixWorld(true);
    const pts = route.map((q) => Array.isArray(q[1])
      ? root.worldToLocal(seg[q[0]].localToWorld(new THREE.Vector3(...q[1])))
      : new THREE.Vector3(...q));
    rods.forEach((rodMesh, i) => {
      const d = pts[i + 1].clone().sub(pts[i]);
      rodMesh.position.copy(pts[i]);
      rodMesh.scale.set(1, Math.max(d.length(), 1e-3), 1);
      rodMesh.quaternion.setFromUnitVectors(up, d.normalize());
    });
  }

  // ---------- what the line does, joint by joint ----------
  const turn = ([x, y, z], t) => [x, y * Math.cos(t) + z * Math.sin(t), -y * Math.sin(t) + z * Math.cos(t)];
  const inJoint = (k, q) => [q[0], q[1] - (k > 0 ? E[k - 1] : 0), q[2]];
  const crossing = (route, j) => {
    const before = j === 0 ? route.prox : route.on[j - 1].at(-1);
    return [j === 0 ? before : inJoint(j, before), route.on[j][0]];
  };
  const cordJ = { prox: postBottom, on: guidesOn };
  const elasticJ = { prox: eyelet, on: chanOn };
  const span = (route, j, t) => { const [a, b] = crossing(route, j); return Math.hypot(...turn(b, t).map((v, i) => v - a[i])); };
  const lever = (route, j, t) => {
    const [a, b0] = crossing(route, j), b = turn(b0, t);
    return Math.abs(a[1] * b[2] - a[2] * b[1]) / Math.hypot(b[1] - a[1], b[2] - a[2]);
  };
  const limit = [95, 101, 70];   // the measured stops (check_gen_04.py)
  const table = (route, sign) => limit.map((lim, j) => Array.from({ length: lim + 1 }, (_, d) => sign * (span(route, j, 0) - span(route, j, rad(d)))));
  const wound = table(cordJ, 1), stretch = table(elasticJ, -1);
  const fullPull = wound.reduce((s, c) => s + c.at(-1), 0);
  function predict(target) {
    let best = null;
    for (let a = 0; a <= limit[0]; a += 2) for (let b = 0; b <= limit[1]; b += 2) {
      const ab = wound[0][a] + wound[1][b];
      if (ab > target + 0.5) break;
      for (let c = 0; c <= limit[2]; c += 2) {
        const w = ab + wound[2][c];
        if (Math.abs(w - target) > 0.6) continue;
        const e = stretch[0][a] + stretch[1][b] + stretch[2][c];
        if (!best || e < best.e) best = { e, pose: [a, b, c] };
      }
    }
    return best ? best.pose : [0, 0, 0];
  }

  model = { seg, fseg, finger, neighbours, lay, cordRuns, elasticRuns, cordRoute, elasticRoute, span, lever, fullPull, predict, limit, rad, cordJ, elasticJ, drumR: rd };
  update(Object.fromEntries(controls.map((c) => [c.id, c.value])));

  const piece = (object) => { const wrap2 = new THREE.Group(); wrap2.add(object); return wrap2; };
  return [
    { name: 'Index finger, first test print', object: piece(root), explode: [0, 0, 0] },
    { name: "Jake's finger (not printed)", object: piece(finger), explode: [0, 0, 0] },
    { name: 'Middle finger and thumb (not printed)', object: piece(neighbours), explode: [0, 0, 0] },
  ];
}

// Poses the model and says what the line and the elastic are doing.
export function update(v) {
  if (!model) return '';
  const { limit, rad } = model;
  const pose = v.mode === 'joints' ? [v.mcp, v.pip, v.dip]
    : v.mode === 'robot' ? model.predict(v.pull / 100 * model.fullPull)
    : [90, 98, 68].map((l) => l * v.pull / 100);
  pose.forEach((a, k) => { model.seg[k].rotation.x = -rad(a); model.fseg[k].rotation.x = -rad(a); });
  model.finger.visible = !!v.finger;
  model.neighbours.visible = !!v.neighbours;
  model.lay(model.cordRuns, model.cordRoute);
  model.lay(model.elasticRuns, model.elasticRoute);
  let line = 0, elastic = 0;
  const arms = pose.map((a, j) => {
    line += model.span(model.cordJ, j, 0) - model.span(model.cordJ, j, rad(a));
    elastic += model.span(model.elasticJ, j, rad(a)) - model.span(model.elasticJ, j, 0);
    return [model.lever(model.cordJ, j, rad(a)), model.lever(model.elasticJ, j, rad(a))];
  });
  const names = ['MCP', 'PIP', 'DIP'];
  const stops = pose.map((a, j) => (a >= limit[j] ? ` ${names[j]} on its stop` : '')).join('');
  return [
    `Pose  MCP ${pose[0].toFixed(0)}°  PIP ${pose[1].toFixed(0)}°  DIP ${pose[2].toFixed(0)}°${v.mode === 'robot' ? '  (predicted, untested)' : ''}${stops}`,
    `Line wound in ${line.toFixed(1)} mm = drum ${(line / model.drumR * 180 / Math.PI).toFixed(0)}° (lock: 20° a hole)   elastic stretched ${elastic.toFixed(1)} mm (chord; it lies on the knuckles near full curl)`,
    ...arms.map(([c, e], j) => `${names[j]}  line arm ${c.toFixed(1)} mm → ${(10 * c).toFixed(0)} N·mm per 10 N   elastic arm ${e.toFixed(1)} mm`),
  ].join('\n');
}
