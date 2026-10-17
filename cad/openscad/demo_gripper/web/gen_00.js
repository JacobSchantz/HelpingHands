// gen_00 · slim two pairs — the VISION. Two interchangeable rigid jaw pairs
// on one hub: A, broad and flat-faced (yellow), shown on the hub; B, the
// tapered crow beak (teal), shown parked 140 mm to the right as the swap pair.
// Slim: 10 mm behind each gripping face, the digit pad straight on the back.

export default function build(THREE, { material, box, profile, rod }) {
  const yellow = material('#efb739');
  const teal = material('#36b2b0');
  const dark = material('#454e60');
  const light = material('#bdc6d4');

  const broad = (side, dx) => profile(side < 0
    ? [[dx - 20, -16], [dx - 1, -16], [dx - 1, 72], [dx - 10, 72], [dx - 20, 40]]
    : [[dx + 1, -16], [dx + 22, -16], [dx + 22, 40], [dx + 10, 72], [dx + 1, 72]], -5, side < 0 ? 16 : 22, yellow);
  const beak = (side, dx) => profile(side < 0
    ? [[dx - 20, -16], [dx - 1, -16], [dx - 1, 84], [dx - 6, 84], [dx - 20, 30]]
    : [[dx + 1, -16], [dx + 22, -16], [dx + 22, 30], [dx + 6, 84], [dx + 1, 84]], -5, side < 0 ? 16 : 22, teal);

  const hub = new THREE.Group();
  hub.add(box([-21, -10.4, -26], [27.5, 10.4, 15.5], dark),
          rod([-6, 0, 0], 2.2, 24, 'y', light), rod([12, 0, 0], 2.2, 24, 'y', light));
  const cradle = new THREE.Group();
  cradle.add(box([-21, -134, -47], [27.5, -76, -30], dark), box([-21, -90, -30], [27.5, -76, 11], dark));

  return [
    { name: 'A · left', object: broad(-1, 0), explode: [-38, 0, 22] },
    { name: 'A · right', object: broad(1, 0), explode: [38, 0, 22] },
    { name: 'B · left', object: beak(-1, 140), explode: [-24, 0, 22] },
    { name: 'B · right', object: beak(1, 140), explode: [24, 0, 22] },
    { name: 'Hub', object: hub, explode: [0, 0, -35] },
    { name: 'Pivot insert', object: box([-2, -12.8, -27], [26, -5.5, 14], light), explode: [0, -25, 0] },
    { name: 'SO-101 cradle', object: cradle, explode: [0, -50, -45] },
  ];
}
