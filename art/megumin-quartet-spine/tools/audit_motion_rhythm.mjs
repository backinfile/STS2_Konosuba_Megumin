import fs from 'node:fs';
import path from 'node:path';
import {root,meta,frame} from './v7_runtime.mjs';

// These are passing poses in the authored action, not contact/reversal holds.
// Read final runtime transforms so the audit includes hierarchy and baking.
const cases = [
  ['chant_enter','E01','hand_r'],
  ['chant_enter','turn-upright','hand_r'],
  ['get_up','lower','chest'],
  ['get_up','brace','chest'],
  ['get_up','kneel-rise','chest'],
];
function velocity(clip,bone,time,dt){
  const lo=Math.max(0,time-dt/2),hi=Math.min(meta.clips[clip].duration,time+dt/2);
  const a=frame(clip,lo).findBone(bone);
  const b=frame(clip,hi).findBone(bone);
  return Math.hypot(b.worldX-a.worldX,b.worldY-a.worldY)/(hi-lo);
}
const checks=cases.map(([clip,pose,bone])=>{
  const s=meta.clips[clip].schedule,i=s.findIndex(([,p])=>p===pose);
  if(i<1||i>=s.length-1)throw new Error(`Missing passing pose: ${clip}/${pose}`);
  const t=s[i][0],lo=s[i-1][0],hi=s[i+1][0];
  const peak=Math.max(...Array.from({length:100},(_,j)=>velocity(clip,bone,lo+(j+.5)/100*(hi-lo),1/600)));
  const speed=velocity(clip,bone,t,1/60),ratio=speed/Math.max(1e-8,peak);
  return {clip,pose,bone,time:t,speed,nearbyPeakSpeed:peak,ratio,minimumRatio:.20,passed:ratio>=.20};
});
const traces={};
for(const [clip,bone] of [['chant_enter','hand_r'],['get_up','chest']]){
 const duration=meta.clips[clip].duration;
 traces[clip]=Array.from({length:Math.floor(duration*120)+1},(_,i)=>{
  const t=i/120,b=frame(clip,t).findBone(bone);
  return {time:t,x:b.worldX,y:b.worldY,speed:velocity(clip,bone,t,1/60)};
 });
}
const report={runtime:'Spine Core 4.2.95',scope:'Regression for unintentional stop-go at declared passing poses; visual review remains required.',checks,traces,passed:checks.every(c=>c.passed)};
const destination=process.argv.find(v=>v.startsWith('--output='))?.slice(9)||path.join(root,'verification/motion-rhythm.json');
fs.mkdirSync(path.dirname(destination),{recursive:true});
fs.writeFileSync(destination,JSON.stringify(report,null,2));
console.log(JSON.stringify({...report,traces:undefined},null,2));
if(!report.passed)process.exitCode=1;
