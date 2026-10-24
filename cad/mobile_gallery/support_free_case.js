// Same hand/contact solver; only the version and measured drive axes differ.
import {makeCase as solveCase} from './contact_case.js';
export const CASE={id:'two-finger-gripper-v327-generalist-support-free',base:26,gripper:30,exported:15,min:0,max:30,pivot:15,pinion:[0,0,-10.656453443805773],ratio:18/28,band:[-3,3],station:50,length:187.2,radius:8};
export const makeCase=(meshes,options={})=>solveCase(meshes,{...options,design:CASE});
