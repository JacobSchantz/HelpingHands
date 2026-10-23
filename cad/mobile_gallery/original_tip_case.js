// Same hand/contact solver; only the version and measured drive axes differ.
import {makeCase as solveCase} from './contact_case.js';
export const CASE={id:'two-finger-gripper-v325-generalist-original-tip-closure',base:24,gripper:28,exported:15,min:0,max:30,pivot:15,pinion:[0,0,-32.7261363439],ratio:30/42,band:[-3,3],station:50,length:187.2,radius:8};
export const makeCase=(meshes,options={})=>solveCase(meshes,{...options,design:CASE});
