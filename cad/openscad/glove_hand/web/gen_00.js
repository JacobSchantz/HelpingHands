// Robot Glove Hand — the VISION for where gen_00 is heading, drawn around the
// same photo outline the fit tray uses (hand_outline.scad), so the two line
// up. A hollow hand-shaped glove Jake's hand slides into: one thin TPU layer
// under palm and fingers, and everything else — the servo pack, the tendon
// runs, the wrist cuff — on the back. gen_00 prints only the flat bottom of
// this (the fit tray), so the diff is expected to be mostly magenta for now.
export default async function build(THREE) {
  const source = await (await fetch(new URL('../hand_outline.scad', import.meta.url) + `?t=${Date.now()}`)).text();
  const points = [...source.matchAll(/\[\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\]/g)].map((m) => new THREE.Vector2(+m[1], +m[2]));
  const above = points.filter((p) => p.y >= 0);

  const skin = new THREE.MeshPhysicalMaterial({ color: '#d9cbb8', roughness: 0.8, transparent: true, opacity: 0.92, side: THREE.DoubleSide });
  const tpu = new THREE.MeshPhysicalMaterial({ color: '#2b2f36', roughness: 0.9, side: THREE.DoubleSide });
  const metal = new THREE.MeshPhysicalMaterial({ color: '#8a96a6', metalness: 0.6, roughness: 0.35 });
  const tendon = new THREE.MeshPhysicalMaterial({ color: '#ff8a3d', roughness: 0.4 });

  // The glove body: the outline with 1.5 mm clearance, 22 mm tall, rounded.
  const shape = new THREE.Shape(above);
  const body = new THREE.Mesh(new THREE.ExtrudeGeometry(shape, {
    depth: 14, bevelEnabled: true, bevelThickness: 4, bevelSize: 2.5, bevelSegments: 4, curveSegments: 4,
  }), skin);
  body.position.z = 4;
  const sole = new THREE.Mesh(new THREE.ExtrudeGeometry(shape, { depth: 0.8, bevelEnabled: false }), tpu);

  // On the back: a servo pack over the back of the hand and a tendon to each fingertip.
  const back = new THREE.Group();
  const pack = new THREE.Mesh(new THREE.BoxGeometry(70, 46, 16), metal);
  pack.position.set(-5, 35, 30);
  back.add(pack);
  const tips = [];
  for (let i = 1; i < above.length - 1; i++) {
    const p = above[i];
    if (p.y > 60 && p.y >= above[i - 1].y && p.y >= above[i + 1].y && !tips.some((t) => t.distanceTo(p) < 25)) tips.push(p);
  }
  for (const tip of tips) {
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(-5 + Math.sign(tip.x) * 10, 55, 30),
      new THREE.Vector3((tip.x - 5) / 2, (tip.y + 55) / 2, 23),
      new THREE.Vector3(tip.x * 0.98, tip.y - 8, 20),
    ]);
    back.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 24, 1.2, 8), tendon));
  }
  const cuff = new THREE.Mesh(new THREE.CylinderGeometry(34, 34, 30, 48, 1, true, 0, Math.PI), tpu);
  cuff.rotation.x = Math.PI / 2;
  cuff.scale.set(1.2, 1, 0.55);
  cuff.position.set(-5, -12, 4);

  return [
    { name: 'Glove shell', object: body, explode: [0, 0, 30] },
    { name: 'TPU palm layer', object: sole, explode: [0, 0, 0] },
    { name: 'Servo pack + tendons', object: back, explode: [0, 0, 70] },
    { name: 'Wrist cuff', object: cuff, explode: [0, -40, 0] },
  ];
}
