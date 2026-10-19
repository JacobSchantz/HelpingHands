// Independent Three.js geometry from the same measurements/pose as jake_hand.scad.
// Convex hulls of ellipsoids follow the CAD construction; mesh tessellation differs.
// Thicknesses retain the CAD's explicitly unmeasured estimates.
import { ConvexGeometry } from '../../../compare/vendor/geometries/ConvexGeometry.js';

export default async function build(THREE, { material }) {
  const response = await fetch(new URL('../jake_hand.scad', import.meta.url) + `?t=${Date.now()}`);
  if (!response.ok) throw new Error('Cannot read hand measurements');
  const h = {};
  for (const m of (await response.text()).matchAll(/^hand_(\w+)\s*=\s*([^;]+);/gm)) {
    try { h[m[1]] = JSON.parse(m[2]); } catch { /* no evaluated code */ }
  }
  const skin = material('#e2b49a', { roughness: .8 });
  const root = new THREE.Group();
  const rad = THREE.MathUtils.degToRad;
  function blob(w, t, l, center = [0, 0, 0]) {
    const points = [];
    for (let j = 0; j <= 14; j++) {
      const latitude = Math.PI * j / 14;
      for (let i = 0; i < 28; i++) {
        const longitude = 2 * Math.PI * i / 28;
        points.push(new THREE.Vector3(center[0] + w/2 * Math.sin(latitude) * Math.cos(longitude),
          center[1] + l/2 * Math.sin(latitude) * Math.sin(longitude), center[2] + t/2 * Math.cos(latitude)));
      }
    }
    return points;
  }
  function hull(parent, points) { parent.add(new THREE.Mesh(new ConvexGeometry(points), skin)); }
  function segment(parent, length, w0, t0, w1, t1) {
    hull(parent, [...blob(w0,t0,Math.min(w0,t0)), ...blob(w1,t1,Math.min(w1,t1),[0,length,0])]);
  }
  function group(parent, position, rx = 0, rz = 0) {
    const g = new THREE.Group(); g.position.set(...position);
    g.rotation.x = rad(rx); g.rotation.z = rad(rz); parent.add(g); return g;
  }
  const bases = []; let edge = h.palm_width / 2;
  for (let i = 0; i < 4; i++) {
    bases.push([edge - h.finger_base_w[i]/2, h.palm_length-h.knuckle_drop[i], h.finger_base_t[i]/2]);
    edge -= h.finger_base_w[i];
  }
  const palm = [...blob(h.wrist_width,h.wrist_thick,20,[0,0,h.wrist_thick/2]),
    ...blob(h.heel[2],h.palm_thick,h.heel[2]*1.6,[-h.palm_width/2-h.heel[0]+h.heel[2]/2,h.heel[1],h.palm_thick/2])];
  bases.forEach((b,i) => palm.push(...blob(h.finger_base_w[i],h.palm_thick,h.finger_base_w[i],[b[0],b[1],h.palm_thick/2])));
  hull(root,palm);
  for (let i=0;i<4;i++) {
    const w=Array.from({length:4},(_,k)=>h.finger_base_w[i]+(h.finger_tip_w[i]-h.finger_base_w[i])*k/3);
    const t=Array.from({length:4},(_,k)=>h.finger_base_t[i]+(h.finger_tip_t[i]-h.finger_base_t[i])*k/3);
    const ends=h.phalanx.map(f=>h.finger_len[i]*f); ends[2]-=Math.min(w[3],t[3])/2;
    let parent=group(root,bases[i],0,-h.splay[i]);
    for(let k=0;k<3;k++) {
      const joint=group(parent,[0,0,0],-h.flex[i][k]);
      segment(joint,ends[k],w[k],t[k],w[k+1],t[k+1]);
      parent=group(joint,[0,ends[k],0]);
    }
  }
  const w=h.thumb_w,t=h.thumb_t,ends=[...h.thumb_len]; ends[2]-=Math.min(w[3],t[3])/2;
  let thumb=group(root,[...h.thumb_cmc,t[0]/2],0,-h.thumb_yaw);
  hull(thumb,[...blob(w[0],t[0],w[0]),...blob(w[0],t[0],w[0],[-18,0,0])]);
  for(let k=0;k<3;k++) {
    if(k) thumb=group(thumb,[0,ends[k-1],0],-h.thumb_flex[k-1]);
    segment(thumb,ends[k],w[k],t[k],w[k+1],t[k+1]);
  }
  const forearm=new THREE.Mesh(new THREE.CylinderGeometry(1,1,40,28),skin);
  forearm.scale.set(h.wrist_width/2,1,h.wrist_thick/2);
  forearm.position.set(0,-20,h.wrist_thick/2);root.add(forearm);
  return [{name:'Your hand',object:root,explode:[0,0,0]}];
}
