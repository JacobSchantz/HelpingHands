// 1.18 · the VISION, not the print. The plan outline and holes gripper.scad traces (web/concept.json, written by
// export_models.py), extruded to the plate; past the dot the dorsal (+Y) face drops on a parabola to tip_thick while the
// ventral face stays flat (Jake: taper from one side only, flat bottom to print on). Both fingers at the gallery's 15 deg.
// No rounding or grooves: render_compare shows what the solid adds and loses.

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
  return [
    { name: 'Left finger', object: finger(-1), explode: [-30, 0, 0] },
    { name: 'Right finger', object: finger(1), explode: [30, 0, 0] },
  ];
}
