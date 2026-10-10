import fs from 'node:fs';
import path from 'node:path';
import {root,raw,meta,data,frame,vertices,cross} from './v7_runtime.mjs';

// Curved, offset paths need new per-part swap times. Choose only within the
// original pose interval, minimizing mesh inversion with a small timing bias.
// This does not create artwork or certify silhouettes; native review follows.
function area(slot){
 const a=slot.attachment;if(!a)return 0;
 const xy=vertices(slot);let sum=0;
 for(let i=0;i<a.triangles.length;i+=3){
  const [ia,ib,ic]=a.triangles.slice(i,i+3),uv=cross(a.regionUVs,ia,ib,ic),v=cross(xy,ia,ib,ic);
  if(uv*v>1e-9)sum+=Math.abs(v)/2;
 }
 return sum;
}
const changes=[];
for(const [clip,plan] of Object.entries(meta.clips)){
 if(clip.startsWith('_bind/'))continue;
 for(const sn of ['body','cape','leg_l','leg_r','arm_l','arm_r','hand_l']){
  const originalKeys=raw.animations[clip].slots[sn].attachment;
  const keys=originalKeys.filter((key,i)=>i===0||key.name!==originalKeys[i-1].name);
  raw.animations[clip].slots[sn].attachment=keys;
  for(let k=1;k<keys.length;k++){
   const before=keys[k-1].name,after=keys[k].name,original=keys[k].time;
   if(!before||!after||before===after)continue;
   const interval=plan.schedule.findIndex(([t],i)=>i&&t>=original-1e-5);
   if(interval<1)continue;
   const start=plan.schedule[interval-1][0],end=plan.schedule[interval][0];
   const samples=[];
   for(let tick=Math.ceil(start*60);tick<=Math.floor(end*60);tick++){
    const t=tick/60,sk=frame(clip,t),slot=sk.findSlot(sn);
    slot.setAttachment(data.defaultSkin.getAttachment(slot.data.index,before));const a=area(slot);
    slot.setAttachment(data.defaultSkin.getAttachment(slot.data.index,after));const b=area(slot);
    samples.push({t,a,b});
   }
   const score=cut=>{
    const values=samples.map(s=>s.t<cut?s.a:s.b);
    return Math.max(...values)+values.reduce((a,b)=>a+b,0)/values.length*.2+Math.abs(cut-original)*2;
   };
   let chosen=original,best=score(original);
   for(const {t} of samples){
    if(t<=start+.1*(end-start)||t>=end-.1*(end-start))continue;
    const cost=score(t);if(cost<best){best=cost;chosen=t;}
   }
   if(Math.abs(chosen-original)>1e-4){
    keys[k].time=+chosen.toFixed(5);
    changes.push({clip,slot:sn,before,after,original,chosen:keys[k].time,beforeCost:score(original),afterCost:best});
   }
  }
  // Visibility/draw-order events can add redundant attachment reset keys.
  // Their times are kept ordered; only actual drawing changes were optimized.
  keys.sort((a,b)=>a.time-b.time);
 }
}
fs.writeFileSync(path.join(root,'export/megumin.json'),JSON.stringify(raw));
fs.writeFileSync(path.join(root,'verification/attachment-timing.json'),JSON.stringify({method:'Per-slot inversion cost over the new continuous world paths, constrained to the source pose interval.',changes},null,2));
console.log(`Adjusted ${changes.length} local part switches.`);
