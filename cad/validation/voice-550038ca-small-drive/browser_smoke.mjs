import {spawn} from 'node:child_process';import fs from 'node:fs';
const out=new URL('.',import.meta.url).pathname;const chrome=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',['--headless=new','--no-first-run','--no-default-browser-check','--remote-debugging-port=9336','--user-data-dir=/tmp/voice-550038ca-chrome','about:blank'],{stdio:'ignore'});
let ws;const errors=[],pending=new Map();let serial=0;
const delay=ms=>new Promise(r=>setTimeout(r,ms));
try{
 let tabs;for(let i=0;i<100;i++){try{tabs=await(await fetch('http://127.0.0.1:9336/json')).json();break;}catch{await delay(200);}}
 ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 ws.onmessage=e=>{const x=JSON.parse(e.data);if(x.id){const p=pending.get(x.id);pending.delete(x.id);if(x.error)p.reject(x.error);else p.resolve(x.result);}if(x.method==='Runtime.exceptionThrown')errors.push(x.params);};
 const call=(method,params={})=>new Promise((resolve,reject)=>{let id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>(await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true})).result.value;
 await call('Runtime.enable');await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1600,height:1200,deviceScaleFactor:1,mobile:false});await call('Page.navigate',{url:'http://127.0.0.1:8768/small_drive_acceptance.html?angle=0'});
 let ready=false;for(let i=0;i<120;i++){if(await evaluate('!!window.ready')){ready=true;break;}await delay(250);}if(!ready)throw Error('Acceptance page did not become ready');
 const samples=[];for(let a=0;a<=30;a+=2.5)samples.push(await evaluate(`window.pause();window.setAngle(${a});window.fit`));
 await evaluate('window.setAngle(0)');await delay(300);let shot=await call('Page.captureScreenshot',{format:'png'});fs.writeFileSync(out+'whole-hand-0.png',Buffer.from(shot.data,'base64'));
 await evaluate('window.setAngle(30)');await delay(300);shot=await call('Page.captureScreenshot',{format:'png'});fs.writeFileSync(out+'whole-hand-30.png',Buffer.from(shot.data,'base64'));
 const copy=await evaluate(`(async()=>{let copied;Object.defineProperty(navigator,'clipboard',{value:{writeText:async t=>{copied=t}},configurable:true});document.querySelector('#copy').click();await Promise.resolve();return JSON.parse(copied).case.id;})()`);
 const report={errors,samples,copied_design_id:copy};fs.writeFileSync(out+'browser-smoke.json',JSON.stringify(report,null,2)+'\n');if(errors.length||copy!=='two-finger-gripper-v326-generalist-small-drive')throw Error('Browser or Copy report failed');console.log('PASS browser:13 poses, no exceptions, correct Copy report design');
}finally{if(ws)ws.close();chrome.kill();}
