// 2.2 (2.1 with each strap slide's plate turned flush against the finger's outer edge, voice-f7f729ac) · the VISION, not the print. The plan outline and holes gripper.scad traces (web/concept.json, written by
// export_models.py), extruded to the full plate with no taper (Jake: the same thickness the whole length), both fingers at
// the gallery's 15 deg; on each, the yellow lug and the black strap slide with its two loop slots as plain blocks. No
// rounding, grooves, dovetail groove or tongue: render_compare shows what the solid adds and loses.

export default async function build(THREE, { material }) {
  const c = await (await fetch(new URL('./concept.json', import.meta.url))).json();
  const shape = new THREE.Shape(c.outline.map(([x, z]) => new THREE.Vector2(x, z)));
  for (const [x, z, d] of c.holes) shape.holes.push(new THREE.Path().absarc(x, z, d / 2, 0, 2 * Math.PI, true));
  for (const [x, z, deg, len, w] of c.slots) {
    const a = (deg * Math.PI) / 180, u = [Math.cos(a), Math.sin(a)], r = w / 2, k = (len - w) / 2;
    const slot = new THREE.Path();
    slot.absarc(x + u[0] * k, z + u[1] * k, r, a - Math.PI / 2, a + Math.PI / 2, false);
    slot.absarc(x - u[0] * k, z - u[1] * k, r, a + Math.PI / 2, a + 1.5 * Math.PI, false);
    shape.holes.push(slot);
  }
  // A (w, u) rectangle in the rail frame -> finger-frame (x, z): gripper.scad rail_frame()
  const [rx, rz, rdeg] = c.rail, ra = (rdeg * Math.PI) / 180;
  const rail = (w, u) => new THREE.Vector2(rx + w * Math.cos(ra) + u * Math.sin(ra), rz - w * Math.sin(ra) + u * Math.cos(ra));
  const rect = (w0, w1, u0, u1, P = THREE.Shape) => new P([rail(w0, u0), rail(w1, u0), rail(w1, u1), rail(w0, u1)]);
  const [lw0, lw1, lu0, lu1] = c.lug;
  const lug = rect(lw0, lw1, lu0, lu1);
  // 2.2: the slide plate stands in (y, u), sw0..sw1 in w: a (y, u) shape extruded along w, then mapped like the rest.
  const [sw0, sw1, su0, su1, sh] = c.slide;
  const yu = (y0, y1, u0, u1, P = THREE.Shape) => new P([[y0, u0], [y1, u0], [y1, u1], [y0, u1]].map(([y, u]) => new THREE.Vector2(y, u)));
  const slide = yu(-sh / 2, sh / 2, su0, su1);
  for (const [y, u, dy, du] of c.strap_slots) slide.holes.push(yu(y, y + dy, u + du, u, THREE.Path));

  // Extrude a finger-frame (x, z) shape `depth` thick, centred in y, and place it on side s (the left is the mirror).
  const place = (shp, depth, s, mat) => {
    const g = new THREE.ExtrudeGeometry(shp, { depth, bevelEnabled: false, curveSegments: 24 });
    const p = g.attributes.position, a = (s * c.angle * Math.PI) / 180;
    for (let i = 0; i < p.count; i++) {
      const x = s * p.getX(i), z = p.getY(i), y = p.getZ(i) - depth / 2;   // shape y is CAD z, the extrusion is CAD y
      p.setXYZ(i, s * c.pivot + x * Math.cos(a) + z * Math.sin(a), y, -x * Math.sin(a) + z * Math.cos(a));
    }
    g.computeVertexNormals();
    return new THREE.Mesh(g, mat);
  };
  const placeSlide = (s) => {
    const g = new THREE.ExtrudeGeometry(slide, { depth: sw1 - sw0, bevelEnabled: false });
    const p = g.attributes.position, a = (s * c.angle * Math.PI) / 180;
    for (let i = 0; i < p.count; i++) {
      const v = rail(sw0 + p.getZ(i), p.getY(i)), x = s * v.x, z = v.y, y = p.getX(i);
      p.setXYZ(i, s * c.pivot + x * Math.cos(a) + z * Math.sin(a), y, -x * Math.sin(a) + z * Math.cos(a));
    }
    g.computeVertexNormals();
    return new THREE.Mesh(g, black);   // black is set below, before placeSlide runs
  };
  const yellow = material('#efb83b'), black = material('#26272b');
  const finger = (s) => {
    const group = new THREE.Group();
    group.add(place(shape, c.plate, s, yellow), place(lug, c.plate, s, yellow));
    return group;
  };
  return [
    { name: 'Left finger', object: finger(-1), explode: [-30, 0, 0] },
    { name: 'Right finger', object: finger(1), explode: [30, 0, 0] },
    { name: 'Left strap slide', object: placeSlide(-1), explode: [-60, 0, -20] },
    { name: 'Right strap slide', object: placeSlide(1), explode: [60, 0, -20] },
  ];
}
