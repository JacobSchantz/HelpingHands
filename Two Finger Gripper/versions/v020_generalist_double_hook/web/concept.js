// 1.20 (1.19 + a second hook at the top of the outer face; a black handle blank between the two hooks) · the VISION, not the print. The plan outline and holes gripper.scad traces (web/concept.json, written by
// export_models.py), extruded to the plate; past the dot the dorsal (+Y) face drops on a parabola to tip_thick while the
// ventral face stays flat (Jake: taper from one side only, flat bottom to print on). Both fingers at the gallery's 15 deg.
// The handle blank is a plain box between the notch floors (the solid's feet fill the notches). No rounding or grooves:
// render_compare shows what the solid adds and loses.

export default async function build(THREE, { material }) {
  const c = await (await fetch(new URL('./concept.json', import.meta.url))).json();
  const top = (z) => {
    const f = Math.min(1, Math.max(0, (z - c.dot_z) / (c.tip_z - c.dot_z)));
    return -c.plate / 2 + c.plate - (c.plate - c.tip_thick) * f * f;   // gripper.scad thick(), from the flat ventral face
  };
  const shape = new THREE.Shape(c.outline.map(([x, z]) => new THREE.Vector2(x, z)));
  for (const [x, z, d] of c.holes) shape.holes.push(new THREE.Path().absarc(x, z, d / 2, 0, 2 * Math.PI, true));
  for (const [x, z, deg, len, w] of c.slots) {
    const a = (deg * Math.PI) / 180, u = [Math.cos(a), Math.sin(a)], r = w / 2, k = (len - w) / 2;
    const slot = new THREE.Path();
    slot.absarc(x + u[0] * k, z + u[1] * k, r, a - Math.PI / 2, a + Math.PI / 2, false);
    slot.absarc(x - u[0] * k, z - u[1] * k, r, a + Math.PI / 2, a + 1.5 * Math.PI, false);
    shape.holes.push(slot);
  }
  const yellow = material('#efb83b');
  const finger = (s) => {
    const g = new THREE.ExtrudeGeometry(shape, { depth: c.plate, bevelEnabled: false, curveSegments: 24 });
    const p = g.attributes.position, a = (s * c.angle * Math.PI) / 180;
    for (let i = 0; i < p.count; i++) {
      const x0 = p.getX(i), z = p.getY(i);
      const y = Math.min(top(z), p.getZ(i) - c.plate / 2);   // shape y is CAD z, the extrusion is CAD y; only the top moves
      const x = s * x0;                                       // the left finger is the mirror image
      p.setXYZ(i, s * c.pivot + x * Math.cos(a) + z * Math.sin(a), y, -x * Math.sin(a) + z * Math.cos(a));
    }
    g.computeVertexNormals();
    return new THREE.Mesh(g, yellow);
  };
  // 1.20: a (w, u) rectangle in the rail frame -> finger-frame (x, z), as gripper.scad rail_frame(); extruded h in y
  const [rx, rz, rdeg] = c.rail, ra = (rdeg * Math.PI) / 180;
  const rail = (w, u) => new THREE.Vector2(rx + w * Math.cos(ra) + u * Math.sin(ra), rz - w * Math.sin(ra) + u * Math.cos(ra));
  const [w0, w1, u0, u1, h] = c.handle;
  const blank = new THREE.Shape([rail(w0, u0), rail(w1, u0), rail(w1, u1), rail(w0, u1)]);
  const handle = (s) => {
    const g = new THREE.ExtrudeGeometry(blank, { depth: h, bevelEnabled: false });
    const p = g.attributes.position, a = (s * c.angle * Math.PI) / 180;
    for (let i = 0; i < p.count; i++) {
      const x = s * p.getX(i), z = p.getY(i), y = p.getZ(i) - h / 2;
      p.setXYZ(i, s * c.pivot + x * Math.cos(a) + z * Math.sin(a), y, -x * Math.sin(a) + z * Math.cos(a));
    }
    g.computeVertexNormals();
    return new THREE.Mesh(g, black);
  };
  const black = material('#26272b');
  return [
    { name: 'Left finger', object: finger(-1), explode: [-30, 0, 0] },
    { name: 'Right finger', object: finger(1), explode: [30, 0, 0] },
    { name: 'Left handle blank', object: handle(-1), explode: [-60, 0, 0] },
    { name: 'Right handle blank', object: handle(1), explode: [60, 0, 0] },
  ];
}
