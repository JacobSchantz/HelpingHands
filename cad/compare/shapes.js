// Helpers every concept scene gets as build()'s second argument, so a concept
// file imports nothing (one module to fetch, easy to retry). CAD frame: mm, Z up.
export function material(THREE, color, extra = {}) {
  return new THREE.MeshPhysicalMaterial({ color, roughness: 0.45, clearcoat: 0.3, side: THREE.DoubleSide, ...extra });
}

// A box from its min and max corner.
export function box(THREE, min, max, mat) {
  const size = max.map((v, i) => v - min[i]);
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), mat);
  mesh.geometry.translate(...min.map((v, i) => v + size[i] / 2));
  return mesh;
}

// A profile drawn in the XZ plane (front view), extruded along +Y from y0.
export function profile(THREE, points, y0, depth, mat, bevel = 0.8) {
  const shape = new THREE.Shape(points.map(([x, z]) => new THREE.Vector2(x, z)));
  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: depth - 2 * bevel, bevelEnabled: bevel > 0, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 2,
  });
  geometry.translate(0, 0, bevel);
  geometry.rotateX(Math.PI / 2);   // shape y -> world z, extrusion z -> world -y
  geometry.translate(0, y0 + depth, 0);
  return new THREE.Mesh(geometry, mat);
}

// A cylinder along an axis ('x' | 'y' | 'z') centred at c.
export function rod(THREE, c, radius, length, axis, mat) {
  const geometry = new THREE.CylinderGeometry(radius, radius, length, 32);
  if (axis === 'x') geometry.rotateZ(Math.PI / 2);
  if (axis === 'z') geometry.rotateX(Math.PI / 2);
  geometry.translate(...c);
  return new THREE.Mesh(geometry, mat);
}
