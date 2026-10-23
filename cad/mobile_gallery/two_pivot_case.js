// Shared CAD/hand-fit contract for voice-550038ca and voice-3f6ae8e1.
// Reuse the existing complete WebXR hand and outside-contact solver.
import * as THREE from 'three';
import {makeHand,sizeHand,gripHand,fingerContacts} from './human_hand.js';
export const CASE={id:'two-finger-gripper-v322-generalist-two-pivot-support',base:21,gripper:25,exported:15,min:0,max:30,pivot:15.675,pinion:[15.675,0,-28.215],ratio:1.25,band:[-3,3],station:50,length:187.2,radius:8};
export async function makeCase(meshes,{side='right',length=CASE.length,station=CASE.station,curlOpen=.2,curlClosed=.8}={}) {
 const hand=await makeHand(side);sizeHand(hand,length);
 function solve(angle){
  for(const m of meshes){
   const name=m.userData.name;let p,sign;
   if(/^Right/.test(name)){p=[CASE.pivot,0,0];sign=1;}
   if(/^Left/.test(name)){p=[-CASE.pivot,0,0];sign=-1;}
   if(/^(Pinion|Stock aluminum)/.test(name)){p=CASE.pinion;sign=-CASE.ratio;}
   if(p){m.rotation.y=THREE.MathUtils.degToRad((angle-CASE.exported)*sign);const c=new THREE.Vector3(...p);m.position.copy(c).sub(c.clone().applyEuler(m.rotation));}
   m.updateMatrixWorld(true);
  }
  const contacts=fingerContacts(meshes,side,station);
  if(!contacts)throw Error('Missing outside finger contacts');
  const solids=meshes.map(m=>new THREE.Box3().setFromObject(m));
  gripHand(hand,...contacts,solids,{indexOnly:true,lockWrist:true,radius:CASE.radius,freeCurl:curlClosed+(curlOpen-curlClosed)*(angle-CASE.min)/(CASE.max-CASE.min)});
  hand.updateMatrixWorld(true);hand.traverse(n=>{if(n.isSkinnedMesh)n.skeleton.update();});
  return {angle,...hand.userData.fit,wrist:hand.userData.grip.slice(0,6),contacts:contacts.map(c=>({point:c.point.toArray(),normal:c.normal.toArray()}))};
 }
 return {hand,meshes,solve};
}
