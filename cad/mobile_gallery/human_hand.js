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

// curls: {thumb, index, ...} each 0 (straight) to 1 (fist). Each bending joint turns everything past it about its own X axis.
const step = new THREE.Matrix4(), spin = new THREE.Matrix4(), posed = new THREE.Matrix4(), axis = new THREE.Vector3(), pivot = new THREE.Vector3(), quat = new THREE.Quaternion(), scale = new THREE.Vector3();
export function poseHand(root, curls) {
  const {bones, rest} = root.userData;
  for (const finger of FINGERS) {
    const chain = new THREE.Matrix4(), amount = Math.max(0, Math.min(1, curls[finger] || 0));
    CHAINS[finger].forEach((name, i) => {
      if (i < 3) {
        rest[name].decompose(pivot, quat, scale); axis.set(1, 0, 0).applyQuaternion(quat);
        spin.makeRotationAxis(axis, -THREE.MathUtils.degToRad(CURL[finger][i] * amount));
        step.makeTranslation(pivot.x, pivot.y, pivot.z).multiply(spin).multiply(new THREE.Matrix4().makeTranslation(-pivot.x, -pivot.y, -pivot.z));
        chain.multiply(step);
      }
      posed.multiplyMatrices(chain, rest[name]).decompose(bones[name].position, bones[name].quaternion, bones[name].scale);
    });
  }
}
