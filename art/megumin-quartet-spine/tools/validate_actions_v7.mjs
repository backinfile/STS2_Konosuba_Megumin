import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {spine,root,raw,meta,data,frame,vertices,folds} from './v7_runtime.mjs';
function compare(a,b){let max=0;assert.deepEqual(a.drawOrder.map(s=>s.data.name),b.drawOrder.map(s=>s.data.name));for(let i=0;i<a.slots.length;i++){const sa=a.slots[i],sb=b.slots[i];assert.equal(sa.attachment?.name,sb.attachment?.name);if(!sa.attachment)continue;const av=vertices(sa),bv=vertices(sb);for(let j=0;j<av.length;j++)max=Math.max(max,Math.abs(av[j]-bv[j]));}return max;}
let samples=0,gripError=0,staffLengthDrift=0,referenceMappingError=0;const foldPeaks={},baseStaff=vertices(frame('chant_enter',0).findSlot('staff'));
for(const a of data.animations){
 const plan=meta.clips[a.name];assert(plan,`missing plan ${a.name}`);
 for(const s of raw.slots)assert.equal(raw.animations[a.name].slots[s.name].attachment[0].time,0,`missing reset ${a.name}/${s.name}`);
 for(let i=0;i<=Math.ceil(a.duration*120);i++){
  const t=Math.min(i/120,a.duration),sk=frame(a.name,t);samples++;
  for(const b of sk.bones)for(const key of ['a','b','c','d','worldX','worldY'])assert(Number.isFinite(b[key]),`${a.name}/${b.data.name}/${key}`);
  const hand=sk.findBone('hand_r'),staff=sk.findBone('staff');gripError=Math.max(gripError,Math.hypot(hand.worldX-staff.worldX,hand.worldY-staff.worldY));
  assert.equal(sk.findSlot('staff').attachment.name,'rigid_staff');
  const sv=vertices(sk.findSlot('staff'));
  for(let j=2;j<sv.length;j+=2)staffLengthDrift=Math.max(staffLengthDrift,Math.abs(Math.hypot(sv[j]-sv[0],sv[j+1]-sv[1])-Math.hypot(baseStaff[j]-baseStaff[0],baseStaff[j+1]-baseStaff[1])));
  for(const s of sk.slots)if(s.attachment){assert(s.attachment instanceof spine.MeshAttachment);assert(vertices(s).every(Number.isFinite));}
  if(!a.name.startsWith('_bind/')){const f=folds(sk);if(!foldPeaks[a.name]||f.foldedArea>foldPeaks[a.name].foldedArea)foldPeaks[a.name]={time:t,...f};}
 }
}
for(const [name,peak] of Object.entries(foldPeaks))assert(peak.foldedArea<250,`${name}@${peak.time}: major mesh fold ${peak.foldedArea}`);
assert(gripError<.001);assert(staffLengthDrift<.002);
for(const [name,p] of Object.entries(meta.poses)){
 const sk=frame('_bind/'+name,0);
 for(const s of sk.slots){const a=s.attachment;if(!a||a.path!==name)continue;const xy=vertices(s),w=a.region.originalWidth,h=a.region.originalHeight;
  const transform=s.data.name==='hand_r'?meta.hand_transforms?.[name]:null;
  for(let i=0;i<xy.length;i+=2){let x=(a.regionUVs[i]*w-p.origin[0])*p.scale,y=(p.origin[1]-a.regionUVs[i+1]*h)*p.scale;if(transform){x=x*transform.scale+transform.translation[0];y=y*transform.scale+transform.translation[1];}referenceMappingError=Math.max(referenceMappingError,Math.abs(x-xy[i]),Math.abs(y-xy[i+1]));}
 }
}
assert(referenceMappingError<.01,`binding drift ${referenceMappingError}`);
const loops={},seams={};for(const [name,p] of Object.entries(meta.clips))if(p.loop){loops[name]=compare(frame(name,0),frame(name,p.duration));assert(loops[name]<.002);}
const transitions=[['idle_loop','chant_enter'],['chant_enter','chant_loop'],['chant_ack','chant_loop'],['chant_cancel','idle_loop'],['explosion_release','explosion_hold'],['explosion_hold','explosion_exit'],['explosion_exit','relaxed_fall'],['relaxed_fall','relaxed_loop'],['relaxed_loop','get_up'],['get_up','idle_loop'],['hit','idle_loop'],['hit_chant','chant_loop'],['hit_down','relaxed_loop'],['dead','dead_loop'],['dead_from_down','dead_loop'],['attack_short','idle_loop'],['cast_short','idle_loop']];
for(const [a,b] of transitions){seams[`${a} -> ${b}`]=compare(frame(a,meta.clips[a].duration),frame(b,0));assert(seams[`${a} -> ${b}`]<.002,`${a} -> ${b}: ${seams[`${a} -> ${b}`]}`);}
const events={};for(const [name,key] of [['explosion_release','release'],['attack_short','impact']]){const ev=[],a=data.findAnimation(name);a.apply(new spine.Skeleton(data),-1,a.duration,false,ev,1,spine.MixBlend.setup,spine.MixDirection.mixIn);events[key]=ev.filter(e=>e.data.name===key).length;assert.equal(events[key],1);}
for(const name of ['dead','dead_from_down'])assert(compare(frame(name,meta.clips[name].duration),frame(name,99))<.002);
// Regression guards for the observed folding frames, not an art-quality score.
const regression={};for(const [name,t,max] of [['chant_enter',.45,15],['relaxed_fall',.82,20],['get_up',1.58,5]]){regression[name]=folds(frame(name,t)).foldedArea;assert(regression[name]<max,`${name} folded mesh regression`);}
const report={runtime:'Spine Core 4.2.95',samples,bones:data.bones.length,slots:data.slots.length,gameplayClips:data.animations.filter(a=>!a.name.startsWith('_bind/')).length,bindPoses:Object.keys(meta.poses).length,gripError,staffLengthDrift,referenceMappingError,loops,seams,events,regression,foldPeaks,passed:true,scope:'Offline Spine Core checks; game verification is recorded separately in verification/native-lab.json',notVerified:['Spine Editor import'],note:'Fold peaks include transparent triangles; numbers do not certify animation quality or floor contact.'};
fs.writeFileSync(path.join(root,'export/validation.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({...report,foldPeaks:Object.fromEntries(Object.entries(foldPeaks).map(([k,v])=>[k,{time:v.time,foldedArea:v.foldedArea}]))},null,2));

