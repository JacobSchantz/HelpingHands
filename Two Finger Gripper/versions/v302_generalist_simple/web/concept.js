// 2.6: 2.5 on 1.21's single-step fingers (the handle plate now runs 67.4 mm up to the top step, voice-72840084). 2.5 (2.4's params on 1.20's fingers; one black handle per finger spanning the base and top hooks, voice-56f9d73f) · the
// VISION, not the print. The plan outline and holes gripper.scad traces (web/concept.json, written by export_models.py),
// extruded to the plate; past the taper start the dorsal (+Y) face drops to tip_thick while the ventral face stays flat (1.18).
// Both fingers at the gallery's 15 deg. On each, the handle plate with its two loop slots as a plain box from one notch floor
// to the other (+span_over). No rounding, grooves, feet or stop strip: render_compare shows what the solid adds and loses.

export default async function build(THREE, { material }) {
  const c = await (await fetch(new URL('./concept.json', import.meta.url))).json();
  const top = (z) => {
    const f = Math.min(1, Math.max(0, (z - c.taper_z) / (c.tip_z - c.taper_z)));
    return -c.plate / 2 + c.plate - (c.plate - c.tip_thick) * f ** c.taper_power;   // gripper.scad thick(), from the flat ventral face
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
  const yellow = material('#efb83b'), black = material('#26272b');
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
  // A (w, u) point in the rail frame -> finger-frame (x, z): gripper.scad rail_frame()
  const [rx, rz, rdeg] = c.rail, ra = (rdeg * Math.PI) / 180;
  const rail = (w, u) => new THREE.Vector2(rx + w * Math.cos(ra) + u * Math.sin(ra), rz - w * Math.sin(ra) + u * Math.cos(ra));
  // 2.2: the slide plate stands in (y, u), sw0..sw1 in w: a (y, u) shape extruded along w, then mapped like the rest.
  const [sw0, sw1, su0, su1, sh] = c.slide;
  const yu = (y0, y1, u0, u1, P = THREE.Shape) => new P([[y0, u0], [y1, u0], [y1, u1], [y0, u1]].map(([y, u]) => new THREE.Vector2(y, u)));
  const plate = yu(-sh / 2, sh / 2, su0, su1);
  for (const [y, u, dy, du] of c.strap_slots) plate.holes.push(yu(y, y + dy, u + du, u, THREE.Path));
  const handle = (s) => {
    const g = new THREE.ExtrudeGeometry(plate, { depth: sw1 - sw0, bevelEnabled: false });
    const p = g.attributes.position, a = (s * c.angle * Math.PI) / 180;
    for (let i = 0; i < p.count; i++) {
      const v = rail(sw0 + p.getZ(i), p.getY(i)), x = s * v.x, z = v.y, y = p.getX(i);
      p.setXYZ(i, s * c.pivot + x * Math.cos(a) + z * Math.sin(a), y, -x * Math.sin(a) + z * Math.cos(a));
    }
    g.computeVertexNormals();
    return new THREE.Mesh(g, black);
  };
  return [
    { name: 'Left finger', object: finger(-1), explode: [-30, 0, 0] },
    { name: 'Right finger', object: finger(1), explode: [30, 0, 0] },
    { name: 'Left handle', object: handle(-1), explode: [-60, 0, 0] },
    { name: 'Right handle', object: handle(1), explode: [60, 0, 0] },
  ];
}
