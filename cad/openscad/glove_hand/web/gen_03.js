// Robot Glove Hand gen_03 · index finger mechanism: the JavaScript model.
// Built here from the numbers in jake_hand.scad (the hand) and
// gen_03_index_finger.scad (the mechanism's own sizes), both read from the
// files, with its own geometry: simpler shapes than the CAD (flat side walls,
// arcs for the shells), so the diff against the STL shows where the two
// constructions disagree. The joints move: `controls` and `update` drive the
// pose, the line and the elastic, and report what the line has to do.
export const controls = [
  { id: 'mode', label: 'Drive', type: 'select', value: 'curl',
    options: [['curl', 'Curl: all joints together'], ['joints', 'Each joint'], ['robot', 'Robot only: the line pulls (predicted)']] },
  { id: 'pull', label: 'Curl / pull', min: 0, max: 100, step: 1, value: 0, unit: '%', play: true },
  { id: 'mcp', label: 'MCP', min: -5, max: 90, step: 1, value: 0, unit: '°' },
  { id: 'pip', label: 'PIP', min: -5, max: 100, step: 1, value: 0, unit: '°' },
  { id: 'dip', label: 'DIP', min: -5, max: 70, step: 1, value: 0, unit: '°' },
  { id: 'finger', label: "Jake's finger", type: 'checkbox', value: false },
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
  const p = await read('gen_03_index_finger.scad');
  const rad = THREE.MathUtils.degToRad;

  // The index finger (jake_hand.scad's construction, measured numbers).
  const lerp4 = (a, b) => [0, 1, 2, 3].map((k) => a + (b - a) * k / 3);
  const W = lerp4(h.hand_finger_base_w[0], h.hand_finger_tip_w[0]);
  const T = lerp4(h.hand_finger_base_t[0], h.hand_finger_tip_t[0]);
  const L = h.hand_phalanx.map((f) => f * h.hand_finger_len[0]);
  const E = [L[0], L[1], L[2] - Math.min(W[3], T[3]) / 2 + p.tip_room];
  const M = [h.hand_palm_width / 2 - h.hand_finger_base_w[0] / 2, h.hand_palm_length - h.hand_knuckle_drop[0], h.hand_finger_base_t[0] / 2];
  const g = p.clearance, shell = p.shell;
  const half = (k, y, extra) => {
    const f = Math.max(0, Math.min(1, y / E[k]));
    return [(W[k] + (W[k + 1] - W[k]) * f) / 2 + extra, (T[k] + (T[k + 1] - T[k]) * f) / 2 + extra];
  };
  const side = (k, y, z, extra) => { const [a, b] = half(k, y, extra); return a * Math.sqrt(Math.max(0, 1 - (z / b) ** 2)); };
  const top = (k, y) => half(k, y, g + shell)[1];
  const low = (k) => p.flap_low * (T[k] + T[k + 1]) / 4;
  const xi = (j) => W[j] / 2 + g + 0.1;

  const petg = material('#d9dde3', { roughness: 0.5 });
  const grey = material('#9aa6b8', { roughness: 0.55 });
  const blue = material('#5b8def', { roughness: 0.5 });
  const steel = material('#6b7380', { roughness: 0.35, metalness: 0.4 });
  const cordMat = new THREE.MeshBasicMaterial({ color: '#e0662a' });
  const elasticMat = new THREE.MeshBasicMaterial({ color: '#3a9d5a' });
  const skin = new THREE.MeshPhysicalMaterial({ color: '#e2b49a', transparent: true, opacity: 0.45, roughness: 0.8, depthWrite: false });

  // A flat plate in the y-z plane, `th` thick from x0 on side s (+1 radial, -1 ulnar).
  const toYZ = new THREE.Matrix4().set(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1);
  function plate(shape, s, x0, th, mat) {
    const geo = new THREE.ExtrudeGeometry(shape, { depth: th, bevelEnabled: false, curveSegments: 20 });
    geo.applyMatrix4(toYZ);
    geo.translate(s > 0 ? x0 : -x0 - th, 0, 0);
    return new THREE.Mesh(geo, mat);
  }
  const poly = (pts) => new THREE.Shape(pts.map(([y, z]) => new THREE.Vector2(y, z)));
  // Two discs of radius r at y = a and y = b (b < a) and the band between them.
  function stadium(a, b, r) {
    const s = new THREE.Shape();
    s.moveTo(b, -r); s.lineTo(a, -r); s.absarc(a, 0, r, -Math.PI / 2, Math.PI / 2, false);
    s.lineTo(b, r); s.absarc(b, 0, r, Math.PI / 2, Math.PI * 1.5, false);
    return s;
  }
  function rodY(c, r, len, mat) {
    const geo = new THREE.CylinderGeometry(r, r, len, 20);
    geo.translate(...c);
    return new THREE.Mesh(geo, mat);
  }
  function rodX(c, r, len, mat) {
    const geo = new THREE.CylinderGeometry(r, r, len, 20);
    geo.rotateZ(Math.PI / 2);
    geo.translate(...c);
    return new THREE.Mesh(geo, mat);
  }
  function rodZ(c, r, len, mat) {
    const geo = new THREE.CylinderGeometry(r, r, len, 40);
    geo.rotateX(Math.PI / 2);
    geo.translate(...c);
    return new THREE.Mesh(geo, mat);
  }
  // The shell over the top of segment k from y0 to y1: an elliptic half tube.
  function arc(k, y0, y1, mat) {
    const [a0, b0] = half(k, y0, g + shell), [a1, b1] = half(k, y1, g + shell);
    const geo = new THREE.CylinderGeometry(a1, a0, y1 - y0, 32, 1, true, -Math.PI / 2, Math.PI);
    geo.scale(1, 1, (b0 + b1) / (a0 + a1));
    geo.translate(0, (y0 + y1) / 2, 0);
    return new THREE.Mesh(geo, mat);
  }

  // ---------- the cord route, in each body's own frame ----------
  const guideAt = (k, y, z) => [side(k, y, z, g + shell) + 1.2, y, z];
  const guidesOn = [
    [[p.cord_reach[0], p.cord_low[0]], [E[0] - p.cord_reach[1], p.cord_low[1]]],
    [[p.cord_reach[1], p.cord_low[1]], [E[1] - p.cord_reach[2], p.cord_low[2]]],
    [[p.cord_reach[2], p.cord_low[2]]],
  ].map((list, k) => list.map(([y, z]) => guideAt(k, y, -z)));
  const tunnelsOn = [[p.prox_start + 2.5, E[0] - 5], [4, E[1] - 4], [4]].map((list, k) => list.map((y) => [0, y, top(k, y) + 1.6]));
  const plateX = xi(0) + p.mcp_tab + p.lug_c, guideX = plateX + p.mcp_plate + 1.2;
  const drumZ = p.spool_z + 0.3 + 1.5 + 2.5;
  const baseGuide = [guideX, -p.cord_reach[0], -p.cord_low[0]];
  const topGuide = [guideX, p.spool_at[1] + 4, drumZ];
  const toGuide = [topGuide[0] - p.spool_at[0], topGuide[1] - p.spool_at[1]], n = Math.hypot(...toGuide), rs = p.spool_r + 0.6;
  const spoolPoint = [p.spool_at[0] + rs * toGuide[0] / n, p.spool_at[1] + rs * toGuide[1] / n, drumZ];
  const hook = [0, -0.5, 23];

  // ---------- bodies ----------
  const root = new THREE.Group();
  root.position.set(...M);
  const seg = [0, 1, 2].map(() => new THREE.Group());
  root.add(seg[0]); seg[0].add(seg[1]); seg[1].add(seg[2]);
  seg[1].position.y = E[0]; seg[2].position.y = E[1];

  for (let k = 0; k < 3; k++) {
    const body = new THREE.Group();
    const y0 = k === 0 ? p.prox_start : p.gap / 2, y1 = k === 2 ? E[2] : E[k] - p.gap / 2;
    body.add(arc(k, y0, y1, petg));
    if (k === 2) {   // the fingertip cap
      const [a, b] = half(2, E[2], g + shell), r = Math.min(W[3], T[3]) / 2 + g + shell;
      const cap = new THREE.SphereGeometry(1, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2);   // the +y half
      cap.scale(a, r, b);
      const mesh = new THREE.Mesh(cap, petg);
      mesh.position.y = E[2];
      body.add(mesh);
    }
    // side walls, cut in a V below the axis at each joint
    const Z = low(k), va = k === 0 ? 0 : rad(p.vee[k] / 2), vd = k === 2 ? 0 : rad(p.vee[k + 1] / 2);
    const end = k === 2 ? E[2] + 2 : y1;
    const wall = poly([[y0, 0], [y0 + Z * Math.tan(va), -Z], [end - Z * Math.tan(vd), -Z], [end, 0]]);
    const a = (half(k, 0, g)[0] + half(k, E[k], g)[0]) / 2;
    for (const s of [-1, 1]) body.add(plate(wall, s, a, shell, petg));
    // hinge tabs at the proximal joint, lugs at the distal one
    if (k === 0) body.add(plate(stadium(p.prox_start + 3, 0, p.mcp_r), 1, xi(0), p.mcp_tab, petg));
    for (const s of [-1, 1]) {
      if (k > 0) body.add(plate(stadium(p.lug_r + 2, 0, p.lug_r), s, xi(k), shell, petg));
      if (k < 2) {
        body.add(plate(stadium(E[k], E[k] - p.lug_r - 4, p.lug_r), s, xi(k + 1) + shell + p.lug_c, p.lug_t, petg));
        body.add(rodX([s * (xi(k + 1) + shell / 2 + p.lug_t / 2 + p.lug_c / 2), E[k], 0], 0.875, shell + p.lug_t + 2, steel));
      }
    }
    for (const q of guidesOn[k]) body.add(rodY(q, p.boss_d / 2, p.boss_len, petg));
    for (const [, y] of tunnelsOn[k]) body.add(box([-2.6, y - 1.5, top(k, y) - 1.4], [2.6, y + 1.5, top(k, y) + 3.2], petg));
    seg[k].add(body);
  }

  // base: a strip of the back-of-hand shell over the index metacarpal, the
  // radial MCP plate with its stop rib, the guides, the hook and the spool boss
  const base = new THREE.Group();
  {
    const A = h.hand_palm_width / 2 + g + shell, B = h.hand_palm_thick / 2 + g + shell, cx = -M[0];
    const t0 = Math.asin((-13 - cx) / A), t1 = Math.asin(Math.min(1, (xi(0) - 0.3 - cx) / A));
    const geo = new THREE.CylinderGeometry(A, A * 0.9, p.base_back + 2, 48, 1, true, t0, t1 - t0);
    geo.scale(1, 1, B / A);
    geo.translate(cx, -p.base_back / 2 + 1, h.hand_palm_thick / 2 - M[2]);
    base.add(new THREE.Mesh(geo, grey));
    const plateShape = new THREE.Shape();
    plateShape.moveTo(-30, -4); plateShape.lineTo(-14, -4); plateShape.lineTo(0, -p.mcp_r);
    plateShape.absarc(0, 0, p.mcp_r, -Math.PI / 2, Math.PI / 2, false);
    plateShape.lineTo(-14, drumZ - 1.5); plateShape.lineTo(-30, drumZ - 1.5);
    base.add(plate(plateShape, 1, plateX, p.mcp_plate, grey));
    base.add(plate(poly([[0, p.mcp_r], [9, p.mcp_r + 0.6], [9, p.mcp_r + 4], [0, p.mcp_r + 4]]), 1, plateX, p.mcp_plate, grey));
    base.add(plate(poly([[3, p.mcp_r + 0.6], [9, p.mcp_r + 0.6], [9, p.mcp_r + 4], [3, p.mcp_r + 4]]), 1, xi(0) + 0.3, p.mcp_tab, grey));
    base.add(box([6, -30, -4], [plateX, -p.mcp_r - 1.5, drumZ - 1.5], grey));
    base.add(box([plateX, -p.cord_reach[0] - 2, -p.cord_low[0] + 1], [plateX + p.mcp_plate, -p.cord_reach[0] + 2, -p.cord_low[0] + 4], grey));
    base.add(rodY(baseGuide, p.boss_d / 2, p.boss_len, grey));
    base.add(rodY(topGuide, p.boss_d / 2, 5, grey));
    base.add(box([-2.5, -3, 17], [2.5, 2, 24.5], grey));
    base.add(rodZ([p.spool_at[0], p.spool_at[1], (8 + p.spool_z) / 2], 6, p.spool_z - 8, grey));
    base.add(rodX([xi(0) + (p.mcp_tab + p.mcp_plate + p.lug_c) / 2, 0, 0], 1.5, p.mcp_tab + p.mcp_plate + 4, steel));
  }
  root.add(base);

  const spool = new THREE.Group();
  {
    const [x, y] = p.spool_at, z = p.spool_z + 0.3;
    spool.add(rodZ([x, y, z + 0.75], p.spool_r + 3, 1.5, blue));
    spool.add(rodZ([x, y, z + 3.25], p.spool_r, 6.5, blue));
    spool.add(rodZ([x, y, z + 7.25], p.spool_r + 3, 1.5, blue));
    spool.add(rodZ([x, y, z + 10.5], p.spool_r + 3, 5, blue));
  }
  root.add(spool);

  // the finger itself, for looking at the fit (not printed, off by default)
  const finger = new THREE.Group();
  finger.position.set(...M);
  const fseg = [0, 1, 2].map(() => new THREE.Group());
  finger.add(fseg[0]); fseg[0].add(fseg[1]); fseg[1].add(fseg[2]);
  fseg[1].position.y = E[0]; fseg[2].position.y = E[1];
  for (let k = 0; k < 3; k++) {
    const geo = new THREE.CylinderGeometry(W[k + 1] / 2, W[k] / 2, E[k], 28, 1, false);
    geo.scale(1, 1, ((T[k] + T[k + 1]) / 2) / ((W[k] + W[k + 1]) / 2));
    geo.translate(0, E[k] / 2, 0);
    fseg[k].add(new THREE.Mesh(geo, skin));
    const knuckle = new THREE.SphereGeometry(1, 24, 12);
    knuckle.scale(W[k] / 2, Math.min(W[k], T[k]) / 2, T[k] / 2);
    fseg[k].add(new THREE.Mesh(knuckle, skin));
  }
  const tip = new THREE.SphereGeometry(1, 24, 12);
  tip.scale(W[3] / 2, Math.min(W[3], T[3]) / 2, T[3] / 2);
  const tipMesh = new THREE.Mesh(tip, skin);
  tipMesh.position.y = E[2];
  fseg[2].add(tipMesh);
  finger.visible = false;

  // the line and the elastic: one rod per straight run, re-aimed every pose
  const runs = (count, r, mat) => Array.from({ length: count }, () => {
    const geo = new THREE.CylinderGeometry(r, r, 1, 8);
    geo.translate(0, 0.5, 0);
    const mesh = new THREE.Mesh(geo, mat);
    root.add(mesh);
    return mesh;
  });
  const cordRoute = [spoolPoint, topGuide, baseGuide, ...guidesOn.flatMap((list, k) => list.map((q) => [k, q]))];
  const elasticRoute = [hook, ...tunnelsOn.flatMap((list, k) => list.map((q) => [k, q]))];
  const cordRuns = runs(cordRoute.length - 1, p.cord_d / 2, cordMat);
  const elasticRuns = runs(elasticRoute.length - 1, 1, elasticMat);
  const up = new THREE.Vector3(0, 1, 0);
  function lay(rods, route) {
    root.updateMatrixWorld(true);
    const pts = route.map((q) => Array.isArray(q[1])
      ? root.worldToLocal(seg[q[0]].localToWorld(new THREE.Vector3(...q[1])))
      : new THREE.Vector3(...q));
    rods.forEach((rod, i) => {
      const d = pts[i + 1].clone().sub(pts[i]);
      rod.position.copy(pts[i]);
      rod.scale.set(1, d.length(), 1);
      rod.quaternion.setFromUnitVectors(up, d.normalize());
    });
  }

  // ---------- what the line does, joint by joint ----------
  // A point on the body past joint j, in joint j's frame, after it flexes by t.
  const turn = ([x, y, z], t) => [x, y * Math.cos(t) + z * Math.sin(t), -y * Math.sin(t) + z * Math.cos(t)];
  const inJoint = (k, q) => [q[0], q[1] - (k > 0 ? E[k - 1] : 0), q[2]];   // body k-1's point, joint k's frame
  // The run that crosses joint j: [proximal point, distal point], each in joint j's frame.
  const crossing = (route, j) => {
    const before = j === 0 ? route.prox : route.on[j - 1].at(-1);
    return [j === 0 ? before : inJoint(j, before), route.on[j][0]];
  };
  const cordJ = { prox: baseGuide, on: guidesOn };
  const elasticJ = { prox: hook, on: tunnelsOn };
  const span = (route, j, t) => { const [a, b] = crossing(route, j); return Math.hypot(...turn(b, t).map((v, i) => v - a[i])); };
  const lever = (route, j, t) => {
    const [a, b0] = crossing(route, j), b = turn(b0, t);
    return Math.abs(a[1] * b[2] - a[2] * b[1]) / Math.hypot(b[1] - a[1], b[2] - a[2]);
  };
  const limit = p.limit;
  const table = (route, sign) => limit.map((lim, j) => Array.from({ length: lim + 1 }, (_, d) => sign * (span(route, j, rad(0)) - span(route, j, rad(d)))));
  const wound = table(cordJ, 1), stretch = table(elasticJ, -1);
  const fullPull = wound.reduce((s, c) => s + c.at(-1), 0);

  // Robot only: the spool sets how much line is in; with friction and
  // gravity ignored the finger settles where the elastic is least stretched
  // for that much line. Brute force over the three joints, 2 degree steps.
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

  model = { seg, fseg, finger, lay, cordRuns, elasticRuns, cordRoute, elasticRoute, span, lever, fullPull, predict, limit, rad, cordJ, elasticJ, spoolR: p.spool_r };
  update(Object.fromEntries(controls.map((c) => [c.id, c.value])));

  // The viewer sets each piece's own position (explode), so the pieces wrap the posed groups.
  const piece = (object) => { const wrap = new THREE.Group(); wrap.add(object); return wrap; };
  return [
    { name: 'Index finger mechanism', object: piece(root), explode: [0, 0, 0] },
    { name: "Jake's finger (not printed)", object: piece(finger), explode: [0, 0, 0] },
  ];
}

// Poses the model and says what the line and the elastic are doing.
export function update(v) {
  if (!model) return '';
  const { limit, rad } = model;
  const pose = v.mode === 'joints' ? [v.mcp, v.pip, v.dip]
    : v.mode === 'robot' ? model.predict(v.pull / 100 * model.fullPull)
    : limit.map((l) => l * v.pull / 100);
  pose.forEach((a, k) => { model.seg[k].rotation.x = -rad(a); model.fseg[k].rotation.x = -rad(a); });
  model.finger.visible = !!v.finger;
  model.lay(model.cordRuns, model.cordRoute);
  model.lay(model.elasticRuns, model.elasticRoute);
  let line = 0, elastic = 0;
  const arms = pose.map((a, j) => {
    line += model.span(model.cordJ, j, 0) - model.span(model.cordJ, j, rad(a));
    elastic += model.span(model.elasticJ, j, rad(a)) - model.span(model.elasticJ, j, 0);
    return [model.lever(model.cordJ, j, rad(a)), model.lever(model.elasticJ, j, rad(a))];
  });
  const names = ['MCP', 'PIP', 'DIP'];
  return [
    `Pose  MCP ${pose[0].toFixed(0)}°  PIP ${pose[1].toFixed(0)}°  DIP ${pose[2].toFixed(0)}°${v.mode === 'robot' ? '  (predicted, untested)' : ''}`,
    `Line wound in ${line.toFixed(1)} mm = spool ${(line / model.spoolR * 180 / Math.PI).toFixed(0)}°   elastic stretched ${elastic.toFixed(1)} mm`,
    ...arms.map(([c, e], j) => `${names[j]}  line arm ${c.toFixed(1)} mm → ${(10 * c).toFixed(0)} N·mm per 10 N   elastic arm ${e.toFixed(1)} mm`),
  ].join('\n');
}
