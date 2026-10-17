// Robot Glove Hand gen_02 · tendon exoskeleton — the VISION. Rigid saddles
// over the back and sides of every phalanx, pinned beside Jake's own finger
// joints; one cord loop per digit running below the joint axes, through the
// web posts, over the back plate to seven servos on a forearm deck; a thin
// TPU pad is all that sits under the palm. Built from the jake_hand.scad
// numbers (read from the file) in the gen_02 pose, so the diff measures the
// exoskeleton, not the hand.
export default async function build(THREE, { material, box }) {
  const text = await (await fetch(new URL('../jake_hand.scad', import.meta.url) + `?t=${Date.now()}`)).text();
  const h = {};
  for (const m of text.matchAll(/^(hand_\w+)\s*=\s*([^;]+);/gm)) {
    try { h[m[1]] = JSON.parse(m[2]); } catch { /* expressions: not needed here */ }
  }
  // gen_02's own numbers
  const splay = [22, 4, -14, -32], thumbYaw = 40, tipRoom = 3;
  const gF = 1.5 + 0.8, gP = 2.0 + 0.8, gT = 2.0 + 0.8, shell = 1.6, lugR = 4, gap = 1.2;
  const servo = [24.7, 45.2, 35], deckY = -22, pitch = servo[0] + 2;
  const plateFront = 81, web = 18;

  const petg = material('#d9dde3', { roughness: 0.5 });
  const back = material('#9aa6b8', { roughness: 0.55 });
  const tpu = material('#2b2f36', { roughness: 0.9 });
  const cordMat = new THREE.MeshBasicMaterial({ color: '#e0662a' });
  const ghost = new THREE.MeshPhysicalMaterial({ color: '#444a55', transparent: true, opacity: 0.35 });
  const deg = THREE.MathUtils.degToRad;

  // A shell segment along +y of a digit frame: covers the top and the sides
  // (open underneath), tapering w0/t0 -> w1/t1, from y0 to y1.
  function saddle(y0, y1, w0, t0, w1, t1, g, mat, under = false) {
    const len = y1 - y0, sweep = deg(under ? 110 : 296);
    const geo = new THREE.CylinderGeometry(w1 / 2 + g + shell, w0 / 2 + g + shell, len, 28, 1, true,
      under ? Math.PI - sweep / 2 : -sweep / 2, sweep);
    geo.scale(1, 1, ((t0 + t1) / 2 + 2 * g) / ((w0 + w1) / 2 + 2 * g));
    geo.translate(0, y0 + len / 2, 0);
    return new THREE.Mesh(geo, mat);
  }
  function lug(x, y, mat) {
    const geo = new THREE.CylinderGeometry(lugR, lugR, 2, 24);
    geo.rotateZ(Math.PI / 2);
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, 0);
    return m;
  }

  // Digit d: base position, yaw, segment lengths, widths and thicknesses at the four joints.
  function digit(d) {
    if (d < 4) {
      const W = h.hand_palm_width, bw = h.hand_finger_base_w;
      const x = W / 2 - bw.slice(0, d).reduce((s, v) => s + v, 0) - bw[d] / 2;
      const lerp = (a, b) => [0, 1, 2, 3].map((k) => a + (b - a) * k / 3);
      const w = lerp(bw[d], h.hand_finger_tip_w[d]), t = lerp(h.hand_finger_base_t[d], h.hand_finger_tip_t[d]);
      const L = h.hand_phalanx.map((p) => p * h.hand_finger_len[d]);
      return { at: [x, h.hand_palm_length - h.hand_knuckle_drop[d], h.hand_finger_base_t[d] / 2], yaw: splay[d],
               e: [L[0], L[1], L[2] - Math.min(w[3], t[3]) / 2 + tipRoom], w, t, g: gF };
    }
    const L = h.hand_thumb_len, w = h.hand_thumb_w, t = h.hand_thumb_t;
    return { at: [h.hand_thumb_cmc[0], h.hand_thumb_cmc[1], t[0] / 2], yaw: thumbYaw,
             e: [L[0], L[1], L[2] - Math.min(w[3], t[3]) / 2 + tipRoom], w, t, g: gT };
  }
  function frame(D) {
    const g = new THREE.Group();
    g.position.set(...D.at);
    g.rotation.z = -deg(D.yaw);
    return g;
  }
  const local = (D, p) => new THREE.Vector3(...p).applyAxisAngle(new THREE.Vector3(0, 0, 1), -deg(D.yaw)).add(new THREE.Vector3(...D.at));

  const saddles = new THREE.Group(), pad = new THREE.Group(), plate = new THREE.Group(), cords = new THREE.Group();
  for (let d = 0; d < 5; d++) {
    const D = digit(d), f = frame(D), p = frame(D), fixed = frame(D);
    let y = 0;
    for (let k = 0; k < 3; k++) {
      const y0 = y + (k === 0 ? (d < 4 ? 15 : 0) : lugR + gap), y1 = y + D.e[k] - (k === 2 ? -2 : lugR + gap);
      (d === 4 && k === 0 ? fixed : f).add(saddle(y0, y1, D.w[k], D.t[k], D.w[k + 1], D.t[k + 1], D.g, d === 4 && k === 0 ? back : petg));
      p.add(saddle(y, y + D.e[k], D.w[k], D.t[k], D.w[k + 1], D.t[k + 1], D.g - 0.8, tpu, true));
      if (k < 2) for (const s of [-1, 1]) f.add(lug(s * (D.w[k + 1] / 2 + D.g + shell + 1), y + D.e[k], petg));
      y += D.e[k];
    }
    saddles.add(f);
    pad.add(p);
    if (d === 4) plate.add(fixed);   // the thumb's metacarpal shell is part of the back
    // the cord loop: over the tip, down both sides below the axes, back to the web
    for (const s of [-1, 1]) {
      const side = (k) => s * (D.w[k] / 2 + D.g + shell + 1);
      const pts = [local(D, [0, y - 6, D.t[3] / 2 + D.g + shell]), local(D, [side(3), y - 6, -0.7 * D.t[3] / 2]),
                   local(D, [side(1), D.e[0], -0.7 * D.t[1] / 2]), local(D, [side(0), 28, -0.7 * D.t[0] / 2])];
      if (d < 4) {
        const post = local(D, [s * (D.w[0] / 2 + D.g + 1.8), web, -0.7 * D.t[0] / 2]);
        pts.push(post, new THREE.Vector3(post.x, post.y, h.hand_palm_thick + gP + shell + 1));
      }
      const n = d, row = n < 4 ? 0 : 1, i = n < 4 ? n : n - 4;
      const spool = new THREE.Vector3(pitch * ((row ? 1 : 1.5) - i), deckY - 11 - row * (servo[1] + 2), h.hand_wrist_thick + gP + shell + 6 + servo[2] - 4);
      pts.push(new THREE.Vector3(spool.x * 0.6 + pts.at(-1).x * 0.4, 8, h.hand_wrist_thick + gP + shell + 3), spool);
      cords.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, false, 'catmullrom', 0.1), 80, 0.5, 6), cordMat));
    }
  }

  // back plate over the hand, forearm saddle, deck and servo envelopes
  const W = h.hand_palm_width / 2 + gP + shell, T = h.hand_palm_thick / 2 + gP + shell;
  const palmGeo = new THREE.CylinderGeometry(W, h.hand_wrist_width / 2 + gP + shell, plateFront + 5, 32, 1, true, -deg(100), deg(200));
  palmGeo.scale(1, 1, T / W);
  palmGeo.translate(0, (plateFront - 5) / 2, 0);
  const palm = new THREE.Mesh(palmGeo, back);
  palm.position.z = h.hand_palm_thick / 2;
  plate.add(palm);
  const deckLen = 2 * (servo[1] + 2) + 6, deckW = 4 * pitch + 6, deckZ = h.hand_wrist_thick + gP + shell + 6;
  const armGeo = new THREE.CylinderGeometry(h.hand_wrist_width / 2 + gP + shell, h.hand_wrist_width / 2 + gP + shell, deckLen - deckY, 32, 1, true, -deg(100), deg(200));
  armGeo.scale(1, 1, (h.hand_wrist_thick / 2 + gP + shell) / (h.hand_wrist_width / 2 + gP + shell));
  armGeo.translate(0, deckY - deckLen + (deckLen - deckY) / 2, 0);
  const arm = new THREE.Mesh(armGeo, back);
  arm.position.z = h.hand_wrist_thick / 2;
  plate.add(arm);
  plate.add(box([-deckW / 2, deckY - deckLen, deckZ], [deckW / 2, deckY, deckZ + 4], back));
  for (let p = 0; p < 5; p++) {
    const D = digit(Math.min(p, 3)), s = p === 4 ? -1 : 1;
    const at = local(D, [s * (D.w[0] / 2 + D.g + 1.8), web, 0]);
    plate.add(box([at.x - 1.2, at.y - 2.5, 1], [at.x + 1.2, at.y + 2.5, h.hand_palm_thick + gP + shell + 1], back));
  }
  const servos = new THREE.Group();
  for (let n = 0; n < 7; n++) {
    const row = n < 4 ? 0 : 1, i = n < 4 ? n : n - 4, x = pitch * ((row ? 1 : 1.5) - i), y = deckY - 11 - row * (servo[1] + 2);
    servos.add(box([x - servo[0] / 2, y - servo[1] + 11, deckZ - 4], [x + servo[0] / 2, y + 11, deckZ - 4 + servo[2]], ghost));
  }

  return [
    { name: 'Pad (TPU)', object: pad, explode: [0, 0, -40] },
    { name: 'Saddles', object: saddles, explode: [0, 40, 25] },
    { name: 'Back', object: plate, explode: [0, -20, 45] },
    { name: 'Cords', object: cords, explode: [0, 0, 45] },
    { name: 'Servos (envelopes)', object: servos, explode: [0, -20, 90] },
  ];
}
