// gen_01 · fin-ray TPU fingers — the VISION, not the print. The look we are
// after (Generalist / UMI): two long soft fin-ray fingers that curve in and
// meet at a point well above the hub, on stiff PETG roots, one shared hub and
// the SO-101 cradle underneath. render_compare holds this against the STLs.

export default function build(THREE, { material, box, profile, rod }) {
  const tpu = material('#f0a43a', { roughness: 0.7, clearcoat: 0 });
  const petg = material('#3f6fb5');
  const dark = material('#454e60');
  const light = material('#bdc6d4');

  // A fin-ray finger: a curved outer wall, a straight gripping face, and
  // slanted ribs between them. side = -1 left, +1 right; the tip leans in.
  function finger(side) {
    const outer = [], inner = [];
    for (let i = 0; i <= 12; i++) {
      const t = i / 12, z = 50 + t * 66;
      outer.push([side * (14 - 13 * Math.pow(t, 1.3) + 3 * Math.sin(Math.PI * t)), z]);
      inner.push([side * (2.5 - 2.0 * t), z]);
    }
    const shell = profile([...inner, ...outer.reverse()], -5, 16, tpu);
    const group = new THREE.Group();
    group.add(shell);
    return group;
  }

  const root = (side) => profile(side < 0
    ? [[-21, -16], [-1, -16], [-2, 52], [-15, 52]]
    : [[1, -16], [22, -16], [15, 52], [2, 52]], -5, 22, petg);

  const hub = box([-21, -10.4, -26], [27.5, 10.4, 15.5], dark);
  const pins = [rod([-6, 0, 0], 2.2, 24, 'y', light), rod([12, 0, 0], 2.2, 24, 'y', light)];
  const insert = box([-2, -12.8, -27], [26, -5.5, 14], light);
  const cradle = new THREE.Group();
  cradle.add(box([-21, -134, -47], [27.5, -76, -30], dark), box([-21, -90, -30], [27.5, -76, 11], dark));

  return [
    { name: 'Left fin-ray finger', object: finger(-1), explode: [-42, 0, 60] },
    { name: 'Right fin-ray finger', object: finger(1), explode: [42, 0, 60] },
    { name: 'Left root', object: root(-1), explode: [-34, 0, 20] },
    { name: 'Right root', object: root(1), explode: [34, 0, 20] },
    { name: 'Hub', object: (() => { const g = new THREE.Group(); g.add(hub, ...pins); return g; })(), explode: [0, 0, -35] },
    { name: 'Pivot insert', object: insert, explode: [0, -25, 0] },
    { name: 'SO-101 cradle', object: cradle, explode: [0, -50, -45] },
  ];
}
