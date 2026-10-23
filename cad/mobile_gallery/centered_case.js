// Shared CAD/hand-fit contract for voice-550038ca and voice-3f6ae8e1.
// Reuse the existing complete WebXR hand and outside-contact solver.
import * as THREE from 'three';
import {makeHand,sizeHand,gripHand,fingerContacts} from './human_hand.js';
export const CASE={id:'two-finger-gripper-v323-generalist-centered-drive',base:22,gripper:26,exported:15,min:0,max:30,pivot:9.8,pinion:[0,0,-21.3811131611],ratio:0.7142857142857143,band:[-3,3],station:50,length:187.2,radius:8};
export async function makeCase(meshes,{side='right',length=CASE.length,station=CASE.station,curlOpen=.2,curlClosed=.8}={}) {
 // Select actual working-band triangles for the inherited contact raycaster.
 // Integral upper gears must not move the contact ray above the human finger band.
 // These probes never enter the scene or replace physical solids in collision checks.
 const probes=meshes.filter(m=>/^(Left|Right) finger/.test(m.userData.name)).map(source=>{
  const geom=source.geometry.index?source.geometry.toNonIndexed():source.geometry;
  const pos=geom.attributes.position,vertices=[];
  for(let i=0;i<pos.count;i+=3){
   if([0,1,2].every(j=>pos.getY(i+j)>=CASE.band[0]-.0001&&pos.getY(i+j)<=CASE.band[1]+.0001))
    for(let j=0;j<3;j++)vertices.push(pos.getX(i+j),pos.getY(i+j),pos.getZ(i+j));
  }
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geometry.computeVertexNormals();
  const mesh=new THREE.Mesh(geometry,source.material);mesh.userData.name=source.userData.name;return {source,mesh};
 });
 const hand=await makeHand(side);sizeHand(hand,length);
 function solve(angle){
  for(const m of meshes){
   const name=m.userData.name;let p,sign;
   if(/^Right/.test(name)){p=[CASE.pivot,0,0];sign=1;}
   if(/^Left/.test(name)){p=[-CASE.pivot,0,0];sign=-1;}
   if(/^(Pinion|Stock aluminum|Plate screws|Center screw)/.test(name)){p=CASE.pinion;sign=-CASE.ratio;}
   if(p){m.rotation.y=THREE.MathUtils.degToRad((angle-CASE.exported)*sign);const c=new THREE.Vector3(...p);m.position.copy(c).sub(c.clone().applyEuler(m.rotation));}
   m.updateMatrixWorld(true);
  }
  for(const {source,mesh} of probes){mesh.position.copy(source.position);mesh.quaternion.copy(source.quaternion);mesh.updateMatrixWorld(true);}
  const contacts=fingerContacts(probes.map(p=>p.mesh),side,station);
  if(!contacts)throw Error('Missing outside finger contacts');
  const solids=meshes.map(m=>new THREE.Box3().setFromObject(m));
  gripHand(hand,...contacts,solids,{indexOnly:true,lockWrist:true,radius:CASE.radius,freeCurl:curlClosed+(curlOpen-curlClosed)*(angle-CASE.min)/(CASE.max-CASE.min)});
  hand.updateMatrixWorld(true);hand.traverse(n=>{if(n.isSkinnedMesh)n.skeleton.update();});
  return {angle,...hand.userData.fit,wrist:hand.userData.grip.slice(0,6),contacts:contacts.map(c=>({point:c.point.toArray(),normal:c.normal.toArray()}))};
 }
 return {hand,meshes,solve};
}
