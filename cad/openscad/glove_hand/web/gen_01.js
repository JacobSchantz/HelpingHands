// Robot Glove Hand gen_01 · fit-test surround — the VISION. Jake's hand inside
// a thin shell that follows it, open at the wrist. Built from the same
// numbers as jake_hand.scad (read from the file), in the try-on pose the
// gen_01 file uses, so the diff measures the shell, not the hand.
export default async function build(THREE, { material }) {
  const text = await (await fetch(new URL('../jake_hand.scad', import.meta.url) + `?t=${Date.now()}`)).text();
  const h = {};
  for (const m of text.matchAll(/^(hand_\w+)\s*=\s*([^;]+);/gm)) {
    try { h[m[1]] = JSON.parse(m[2]); } catch { /* expressions: not needed here */ }
  }
  const splay = [6, 0, -6, -13], thumbYaw = 30, clearance = 1.75, wall = 1.2;

  const skin = material('#e2b49a', { roughness: 0.8 });
  const shell = new THREE.MeshPhysicalMaterial({ color: '#9aa6b8', roughness: 0.6, transparent: true, opacity: 0.45, side: THREE.DoubleSide });

  // A tapered capsule from a to b (both THREE.Vector3), radius r0 -> r1.
  function limb(a, b, r0, r1, mat) {
    const len = a.distanceTo(b);
    const geo = new THREE.CylinderGeometry(r1, r0, len, 20, 1, true);
    const g = new THREE.Group();
    const body = new THREE.Mesh(geo, mat);
    body.position.copy(a.clone().add(b).multiplyScalar(0.5));
    body.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
    g.add(body);
    for (const [p, r] of [[a, r0], [b, r1]]) {
      const s = new THREE.Mesh(new THREE.SphereGeometry(r, 20, 12), mat);
      s.position.copy(p);
      g.add(s);
    }
    return g;
  }

  // Hand centrelines, as in jake_hand.scad (z = 0 palm surface, +y fingers, thumb +x).
  function hand(grow, mat) {
    const g = new THREE.Group();
    const W = h.hand_palm_width, bw = h.hand_finger_base_w;
    let edge = W / 2;
    for (let i = 0; i < 4; i++) {
      const x = edge - bw[i] / 2; edge -= bw[i];
      const base = new THREE.Vector3(x, h.hand_palm_length - h.hand_knuckle_drop[i], h.hand_finger_base_t[i] / 2);
      const a = THREE.MathUtils.degToRad(splay[i]);
      const len = h.hand_finger_len[i] - h.hand_finger_tip_w[i] / 2;
      const tip = base.clone().add(new THREE.Vector3(Math.sin(a) * len, Math.cos(a) * len, (h.hand_finger_tip_t[i] - h.hand_finger_base_t[i]) / 2));
      g.add(limb(base, tip, bw[i] / 2 + grow, h.hand_finger_tip_w[i] / 2 + grow, mat));
    }
    const palm = new THREE.Mesh(new THREE.BoxGeometry(W + 2 * grow, h.hand_palm_length, h.hand_palm_thick + 2 * grow, 1, 1, 1), mat);
    palm.position.set(0, h.hand_palm_length / 2, h.hand_palm_thick / 2);
    g.add(palm);
    const [cx, cy] = h.hand_thumb_cmc, t = THREE.MathUtils.degToRad(thumbYaw);
    const L = h.hand_thumb_len.reduce((s, v) => s + v, 0) - h.hand_thumb_w[3] / 2;
    const a = new THREE.Vector3(cx, cy, h.hand_thumb_t[0] / 2);
    g.add(limb(a, a.clone().add(new THREE.Vector3(Math.sin(t) * L, Math.cos(t) * L, -4)), h.hand_thumb_w[1] / 2 + grow, h.hand_thumb_w[3] / 2 + grow, mat));
    return g;
  }

  return [
    { name: "Jake's hand", object: hand(0, skin), explode: [0, 0, 0] },
    { name: 'Glove shell', object: hand(clearance + wall, shell), explode: [0, 0, 45] },
  ];
}
