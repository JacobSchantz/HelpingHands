import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {clone} from 'three/addons/utils/SkeletonUtils.js';

// Average human hand (voice-bf770cd7): a reference hand to lay beside or over the gripper, with fingers that bend. The mesh is the
// WebXR Input Profiles generic hand (MIT, reference/human_hand/SOURCE.txt): a skinned hand on the 25 WebXR joints, every joint a
// child of one Armature, -Z along each bone and +Y out of the back of the hand. It is scaled uniformly so wrist crease to middle
// fingertip is the ANSUR II mean hand length, and posed so the fingers point +Z (the gripper's fingers) and the palm faces -X.
export const SIZES = [
  {id:'adult', label:'Average adult · 187 mm', length:187.2},
  {id:'man', label:'Average man · 193 mm', length:193.3},
  {id:'woman', label:'Average woman · 181 mm', length:181.1},
];
export const FINGERS = ['thumb', 'index', 'middle', 'ring', 'pinky'];
// Each finger's chain from its first bending joint to its tip, and the bend (degrees) of those first three joints at full curl,
// a loose fist: knuckle, middle joint, end joint (the thumb: base, knuckle, end).
const CHAINS = {thumb: ['thumb-metacarpal', 'thumb-phalanx-proximal', 'thumb-phalanx-distal', 'thumb-tip']};
for (const finger of FINGERS.slice(1)) CHAINS[finger] = ['proximal', 'intermediate', 'distal'].map(bone => finger + '-finger-phalanx-' + bone).concat(finger + '-finger-tip');
const CURL = {thumb:[30, 40, 65], index:[80, 100, 70], middle:[85, 100, 70], ring:[88, 100, 70], pinky:[90, 100, 70]};

const loader = new GLTFLoader(), sources = {};
// One load per side; each view gets its own clone (its own skeleton to bend).
function source(side) {
  return sources[side] ||= loader.loadAsync('reference/human_hand/' + side + '.glb').then(gltf => {
    const scene = gltf.scene, mesh = scene.getObjectByProperty('type', 'SkinnedMesh'), bone = name => scene.getObjectByName(name);
    scene.updateMatrixWorld(true);
    const wrist = bone('wrist').position.clone(), tip = bone('middle-finger-tip').position.clone();
    const distal = tip.clone().sub(wrist).normalize();
    const dorsal = new THREE.Vector3(0, 1, 0).applyQuaternion(bone('middle-finger-phalanx-proximal').quaternion);
    dorsal.addScaledVector(distal, -dorsal.dot(distal)).normalize();
    // Hand length as ANSUR measures it: wrist to the farthest skin along the fingers.
    const position = mesh.geometry.attributes.position, vertex = new THREE.Vector3();
    let reach = 0;
    for (let i = 0; i < position.count; i++) reach = Math.max(reach, vertex.fromBufferAttribute(position, i).sub(wrist).dot(distal));
    // Model frame (dorsal, distal, side) onto CAD (+X, +Z, -Y): fingers along +Z, back of the hand +X, palm -X.
    const from = new THREE.Matrix4().makeBasis(dorsal, distal, new THREE.Vector3().crossVectors(dorsal, distal));
    const to = new THREE.Matrix4().makeBasis(new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 0, 1), new THREE.Vector3(0, -1, 0));
    const turn = new THREE.Quaternion().setFromRotationMatrix(to.multiply(from.transpose()));
    return {scene, wrist, reach, turn};
  });
}

// A hand for one view: root sits at the wrist crease in CAD millimetres; pose() bends it.
export async function makeHand(side) {
  const {scene, wrist, reach, turn} = await source(side);
  const copy = clone(scene), inner = new THREE.Group(), root = new THREE.Group();
  copy.position.copy(wrist).negate(); inner.add(copy); inner.quaternion.copy(turn); root.add(inner);
  const material = new THREE.MeshStandardMaterial({color:'#d9a98c', roughness:.7, metalness:0, transparent:true});
  const bones = {}, rest = {};
  copy.traverse(node => {
    if (node.isSkinnedMesh) { node.material = material; node.frustumCulled = false; }
    if (node.isBone) { bones[node.name] = node; rest[node.name] = new THREE.Matrix4().compose(node.position, node.quaternion, node.scale); }
  });
  root.userData = {side, reach, inner, bones, rest, material};
  return root;
}
export function sizeHand(root, length) { root.userData.inner.scale.setScalar(length / root.userData.reach); }

// curls: {thumb, index, ...} each 0 (straight) to 1 (fist). turns: extra turns {joint: [x, y, z] degrees} about a joint's own axes
// (negative x bends toward the palm), for poses the curls cannot make, like the thumb swinging across to hold the gripper.
// Each bending joint turns everything past it about its own rest axes.
const step = new THREE.Matrix4(), spin = new THREE.Matrix4(), axis = new THREE.Vector3(), pivot = new THREE.Vector3(), quat = new THREE.Quaternion(), scale = new THREE.Vector3();
const delta = new THREE.Quaternion(), euler = new THREE.Euler(), deg = THREE.MathUtils.degToRad;
// A finger's posed joint matrices in Armature space, by joint name.
function chainPose(root, finger, curl, turns) {
  const {rest} = root.userData, chain = new THREE.Matrix4(), out = {}, amount = Math.max(0, Math.min(1, curl || 0));
  CHAINS[finger].forEach((name, i) => {
    if (i < 3) {
      const turn = turns[name] || [0, 0, 0];
      rest[name].decompose(pivot, quat, scale);
      euler.set(deg(turn[0] - CURL[finger][i] * amount), deg(turn[1]), deg(turn[2]));
      delta.setFromEuler(euler); spin.makeRotationFromQuaternion(quat.clone().multiply(delta).multiply(quat.invert()));
      step.makeTranslation(pivot.x, pivot.y, pivot.z).multiply(spin).multiply(new THREE.Matrix4().makeTranslation(-pivot.x, -pivot.y, -pivot.z));
      chain.multiply(step);
    }
    out[name] = new THREE.Matrix4().multiplyMatrices(chain, rest[name]);
  });
  return out;
}
export function poseHand(root, curls, turns = {}) {
  const {bones} = root.userData;
  for (const finger of FINGERS) for (const [name, matrix] of Object.entries(chainPose(root, finger, curls[finger], turns)))
    matrix.decompose(bones[name].position, bones[name].quaternion, bones[name].scale);
}

// Solve thumb/index contact with opposing outer finger faces. The legacy
// two-finger handle mode remains available to callers without indexOnly.
// Generic joint limits and local coordinate descent provide screening, not fit certification.
const THUMB = CHAINS.thumb, RING = {ring:[85, 100, 65], pinky:[90, 100, 65]};
// Unknowns: x, y, z (mm), turn about x, y, z (degrees, on the seed), index knuckle and middle joints, middle the same, thumb base
// x, y, z, thumb knuckle and end; each with its limits and the relaxed value it is pulled toward.
const LIMITS = [[-1e4, 1e4], [-1e4, 1e4], [-1e4, 1e4], [-90, 90], [-90, 90], [-90, 90],
  [-95, 0], [-80, 0], [-95, 0], [-80, 0], [-60, 40], [-70, 70], [-70, 70], [-60, 15], [-70, 15]];
const RELAXED = [0, 0, 0, 0, 0, 0, -70, -20, -70, -25, -10, 0, 0, -10, -10];
const PULL = [0, 0, 0, 0, 0, 0, .01, .02, .01, .02, .02, .02, .02, .02, .02];
const point = matrix => new THREE.Vector3().setFromMatrixPosition(matrix), towards = (matrix, x, y, z) => new THREE.Vector3(x, y, z).transformDirection(matrix);
// fingers, thumb: {point, normal} in world mm, a spot on a finger's outer face and its outward normal; solids: world Box3s the
// hand must stay out of (base, top plate, servo). Places the hand (root) and bends it; returns the worst pad miss in mm.
export function gripHand(root, fingers, thumb, solids, options = {}) {
  const {bones} = root.userData, turns = {};
  const radius = options.radius ?? 8, indexOnly = options.indexOnly ?? false;
  const locked = options.lockWrist && root.userData.grip ? root.userData.grip.slice(0, 6) : null;
  for (const finger in RING) CHAINS[finger].slice(0, 3).forEach((name, i) => { turns[name] = [-RING[finger][i], 0, 0]; });
  root.position.set(0, 0, 0); root.quaternion.identity(); root.updateMatrixWorld(true);
  // Armature space -> the hand's own frame (root space, mm); `unit` turns mm into Armature units.
  const toRoot = bones.wrist.parent.matrixWorld.clone().premultiply(root.matrixWorld.clone().invert()), unit = toRoot.getMaxScaleOnAxis();
  const inRoot = (v, isPoint) => isPoint ? v.applyMatrix4(toRoot) : v.transformDirection(toRoot);
  // A phalanx's pad: `along` its length from this joint to the next, 8 mm to the palm side, with its palm-side normal.
  const pad = (posed, joint, next, along) => {
    const normal = towards(posed[joint], 0, -1, 0);
    return {at: inRoot(point(posed[joint]).lerp(point(posed[next]), along).addScaledVector(normal, radius / unit), true), normal: inRoot(normal)};
  };
  const flex = (chain, knuckle, middle) => { turns[chain[0]] = [knuckle, 0, 0]; turns[chain[1]] = [middle, 0, 0]; turns[chain[2]] = [middle * .7, 0, 0]; };
  // Palm skin over the middle finger's metacarpal, its palm-side normal, and the hand's own axes for the seed.
  const rest = chainPose(root, 'middle', 0, {}), knuckle = rest['middle-finger-phalanx-proximal'];
  const palmNormal = inRoot(towards(knuckle, 0, -1, 0)), palmAt = inRoot(point(knuckle).lerp(point(bones.wrist.matrix), .35).addScaledVector(towards(knuckle, 0, -1, 0), 15 / unit), true);
  const reach = inRoot(point(knuckle).sub(point(bones.wrist.matrix)).normalize());
  // Flesh kept out of the solids: balls on the palm (radius 12 mm) and on every finger joint and mid-phalanx (8 mm).
  const fixed = chainPose(root, 'ring', 0, turns), little = chainPose(root, 'pinky', 0, turns);
  const palmBalls = [point(bones.wrist.matrix), ...['index', 'middle', 'ring', 'pinky'].flatMap(finger => {
    const from = point(bones[finger + '-finger-metacarpal'].matrix), to = point(bones[finger + '-finger-phalanx-proximal'].matrix);
    return [from.clone().lerp(to, .5), to];
  }), ...Object.values(fixed).concat(Object.values(little)).map(point)].map(v => inRoot(v, true));
  const balls = posed => { const joints = Object.values(posed).map(point); return joints.concat(joints.slice(1).map((v, i) => v.clone().lerp(joints[i], .5))).map(v => inRoot(v, true)); };
  const inside = (v, radius) => {
    let worst = 0;
    for (const box of solids) {
      const depth = Math.min(v.x - box.min.x, box.max.x - v.x, v.y - box.min.y, box.max.y - v.y, v.z - box.min.z, box.max.z - v.z) + radius;
      worst = Math.max(worst, depth);
    }
    return worst;
  };
  const near = v => solids.length ? Math.min(...solids.map(box => box.distanceToPoint(v))) : 0;
  // Seed: palm facing the mechanism, fingers reaching across the opposing contacts.
  const basis = (a, b) => { const y = b.clone().addScaledVector(a, -b.dot(a)).normalize(); return new THREE.Matrix4().makeBasis(a, y, new THREE.Vector3().crossVectors(a, y)); };
  const across = fingers.point.clone().sub(thumb.point);
  const seed = locked && root.userData.gripSeed ? root.userData.gripSeed.clone() :
    new THREE.Quaternion().setFromRotationMatrix(basis(new THREE.Vector3(0, -1, 0), across).multiply(basis(palmNormal, reach).transpose()));
  root.userData.gripSeed = seed.clone();
  const placed = new THREE.Quaternion(), turn = new THREE.Quaternion(), position = new THREE.Vector3(), world = v => v.applyQuaternion(placed).add(position);
  const misses = [];
  let penetration = 0;
  const cost = a => {
    turn.setFromEuler(new THREE.Euler(deg(a[3]), deg(a[4]), deg(a[5]))); placed.copy(turn).multiply(seed); position.set(a[0], a[1], a[2]);
    flex(CHAINS.index, a[6], a[7]); flex(CHAINS.middle, a[8], a[9]);
    for (let i = 0; i < 3; i++) turns[THUMB[i]] = i ? [a[i + 12], 0, 0] : [a[10], a[11], a[12]];
    const indexPose = chainPose(root, 'index', 0, turns), middlePose = chainPose(root, 'middle', 0, turns), thumbPose = chainPose(root, 'thumb', 0, turns);
    const index = pad(indexPose, 'index-finger-phalanx-intermediate', 'index-finger-phalanx-distal', .5);
    const middle = pad(middlePose, 'middle-finger-phalanx-intermediate', 'middle-finger-phalanx-distal', .5);
    const tip = pad(thumbPose, 'thumb-phalanx-distal', 'thumb-tip', .5);
    const into = n => n.dot(fingers.normal);
    let c = 0;
    // Index pad on its spot, middle pad on the same face, thumb pad on its spot, each facing its face.
    misses[0] = world(index.at).distanceTo(fingers.point);
    misses[1] = Math.abs(world(middle.at.clone()).sub(fingers.point).dot(fingers.normal));
    c += indexOnly ? 0 : Math.max(0, world(middle.at).distanceTo(fingers.point) - 20) ** 2;   // beside the index, in the same strap
    misses[2] = world(tip.at).distanceTo(thumb.point);
    c += misses[0] ** 2 + (indexOnly ? 0 : misses[1] ** 2) + misses[2] ** 2;
    c += 150 * (1 + into(index.normal.applyQuaternion(placed)) + (indexOnly ? 0 : 1 + into(middle.normal.applyQuaternion(placed)))) + 150 * (1 + tip.normal.applyQuaternion(placed).dot(thumb.normal));
    // Penalize overlap; direct finger contact does not require palm contact on a base.
    penetration = 0;
    for (const [points, r] of [[palmBalls.map(v => v.clone()), 12], [[indexPose, middlePose, thumbPose].flatMap(balls), radius]]) {
      for (const v of points) { const depth = inside(world(v), r); penetration = Math.max(penetration, depth); c += 5 * depth ** 2; }
    }
    if (!indexOnly) c += .3 * Math.max(0, near(world(palmAt.clone())) - 2) ** 2;
    return c + a.reduce((sum, v, i) => sum + PULL[i] * (v - RELAXED[i]) ** 2, 0);
  };
  // Start from the last solution (so Open/Close glides), else the seed with the palm on the base; halve the step until settled.
  let a = root.userData.grip;
  if (!a) {
    a = RELAXED.slice(); cost(a);
    const body = solids.reduce((all, box) => all.union(box), new THREE.Box3().expandByPoint(fingers.point).expandByPoint(thumb.point));
    const at = body.getCenter(new THREE.Vector3()).setY(body.max.y + 15).sub(palmAt.clone().applyQuaternion(placed)); a[0] = at.x; a[1] = at.y; a[2] = at.z;
  }
  a = a.slice();
  if (locked) a.splice(0, 6, ...locked);
  let best = cost(a);
  for (let size = 16; size > .2; size /= 2) for (let again = true, rounds = 0; again && rounds < 40; rounds++) {
    again = false;
    for (let i = locked ? 6 : 0; i < a.length; i++) for (const sign of [1, -1]) {
      const was = a[i]; a[i] = Math.max(LIMITS[i][0], Math.min(LIMITS[i][1], was + sign * size));
      const c = cost(a); if (c < best - 1e-6) { best = c; again = true; } else a[i] = was;
    }
  }
  root.userData.grip = a; cost(a);
  root.quaternion.copy(placed); root.position.copy(position);
  poseHand(root, {}, turns);
  const miss = Math.max(misses[0], misses[2], indexOnly ? 0 : misses[1]);
  root.userData.fit = {miss, penetration, span: fingers.point.distanceTo(thumb.point), wristLocked: !!locked};
  return miss;
}

// Raycast the outer finger surface in mesh-local coordinates, so the contact
// station follows the finger through its stroke rather than sliding along a world box.
const faceRay = new THREE.Raycaster();
export function outerFingerSpot(mesh, outward, percent) {
  mesh.updateWorldMatrix(true, false);
  mesh.geometry.computeBoundingBox();
  const box = mesh.geometry.boundingBox;
  const origin = new THREE.Vector3(outward > 0 ? box.max.x + 50 : box.min.x - 50,
    (box.min.y + box.max.y) / 2, box.max.z - (box.max.z - box.min.z) * percent / 100);
  const direction = new THREE.Vector3(-outward, 0, 0).transformDirection(mesh.matrixWorld);
  faceRay.set(origin.applyMatrix4(mesh.matrixWorld), direction);
  const hit = faceRay.intersectObject(mesh, false)[0];
  return hit && {point: hit.point, normal: hit.face.normal.clone().transformDirection(mesh.matrixWorld)};
}

// Handles/cradles never participate in contact selection. Missing fingers stay explicit.
export function fingerContacts(meshes, side, percent) {
  const near = side === 'right' ? 'Right' : 'Left', far = near === 'Right' ? 'Left' : 'Right';
  const find = side => meshes.find(mesh => new RegExp('^' + side + ' finger(?:\\s|$)', 'i').test(mesh.userData.name || ''));
  const a = find(near), b = find(far), out = near === 'Right' ? 1 : -1;
  const index = a && outerFingerSpot(a, out, percent), thumb = b && outerFingerSpot(b, -out, percent);
  return index && thumb ? [index, thumb] : null;
}
