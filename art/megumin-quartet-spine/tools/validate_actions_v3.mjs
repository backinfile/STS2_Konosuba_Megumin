import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import * as spine from '@esotericsoftware/spine-core';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../actions-v3');
const raw=JSON.parse(fs.readFileSync(path.join(root,'export/megumin.json'),'utf8'));
const geometry=JSON.parse(fs.readFileSync(path.join(root,'geometry.json'),'utf8'));
const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(root,'export/megumin.atlas'),'utf8'));
for(const page of atlas.pages) page.setTexture(new spine.FakeTexture({width:page.width,height:page.height}));
const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw);
const frame=(name,t)=>{
  const sk=new spine.Skeleton(data);
  data.findAnimation(name).apply(sk,0,t,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);
  sk.updateWorldTransform(spine.Physics.update);
  return sk;
};
function vertices(slot){
  const mesh=slot.attachment,xy=new Float32Array(mesh.worldVerticesLength);
  mesh.computeWorldVertices(slot,0,xy.length,xy,0,2);
  return xy;
}
function compare(a,b){
  let max=0;
  for(let i=0;i<a.slots.length;i++){
    const sa=a.slots[i],sb=b.slots[i];
    assert.equal(sa.attachment?.name,sb.attachment?.name,`attachment seam: ${sa.data.name}`);
    if(!sa.attachment) continue;
    const av=vertices(sa),bv=vertices(sb);
    assert.equal(av.length,bv.length);
    for(let j=0;j<av.length;j++) max=Math.max(max,Math.abs(av[j]-bv[j]));
  }
  return max;
}
let samples=0,maxIKError=0,maxStretch=0,stretchAt={},minClothY=Infinity;
for(const anim of data.animations){
  for(let i=0;i<=Math.ceil(anim.duration*120);i++){
    const t=Math.min(i/120,anim.duration),sk=frame(anim.name,t);samples++;
    for(const b of sk.bones){
      for(const p of ['a','b','c','d','worldX','worldY']) assert(Number.isFinite(b[p]),`${anim.name}/${b.data.name}/${p}`);
      if(/^(upper|fore|thigh|shin)_/.test(b.data.name)){
        const stretch=Math.hypot(b.a,b.c);
        if(stretch>maxStretch){maxStretch=stretch;stretchAt={clip:anim.name,time:t,bone:b.data.name};}
      }
    }
    for(const [end,target] of [['fore_r','grip_r'],['fore_l','grip_l'],['shin_r','foot_r'],['shin_l','foot_l']]){
      const b=sk.findBone(end),g=sk.findBone(target);
      const error=Math.hypot(b.worldX+b.a*b.data.length-g.worldX,b.worldY+b.c*b.data.length-g.worldY);
      maxIKError=Math.max(maxIKError,error);
      assert(error<.1,`${anim.name}@${t} ${end} misses target by ${error}`);
    }
    for(const slot of sk.slots){
      if(!(slot.attachment instanceof spine.MeshAttachment)) continue;
      const xy=vertices(slot);
      assert(xy.every(Number.isFinite),`${anim.name}/${slot.data.name} invalid geometry`);
      assert(slot.attachment.regionUVs.every(v=>v>=0&&v<=1),`${slot.data.name} invalid UV`);
      if(['body','body_repair','costume_under'].includes(slot.data.name)){
        for(let j=1;j<xy.length;j+=2) minClothY=Math.min(minClothY,xy[j]);
      }
    }
  }
}
// Check the source-aligned setup only on unchanged visible regions. New hidden
// underpainting is deliberately excluded; source fidelity and motion are distinct.
const setup=frame('setup_pose',0);let maxSourceMappingError=0;
for(const name of ['body','head','staff','arm_r','arm_l','leg_r','leg_l','hand_r','hand_open']){
  const slot=setup.slots.find(s=>s.attachment?.name===name),xy=vertices(slot),expected=geometry[name].expected_world;
  for(let i=0;i<xy.length;i++) maxSourceMappingError=Math.max(maxSourceMappingError,Math.abs(xy[i]-expected[i]));
}
assert(maxSourceMappingError<.002,`source map drift ${maxSourceMappingError}`);
const loops=['idle_loop','chant_loop','explosion_hold','relaxed_loop'],loopSeams={};
for(const name of loops){
  loopSeams[name]=compare(frame(name,0),frame(name,data.findAnimation(name).duration));
  assert(loopSeams[name]<.002,`${name} loop seam ${loopSeams[name]}`);
}
const transitions=[['cast_short','idle_loop'],['chant_enter','chant_loop'],['chant_cancel','idle_loop'],['chant_ack','chant_loop'],['attack_short','idle_loop'],['hit','idle_loop'],['hit_chant','chant_loop'],['explosion_release','explosion_hold'],['explosion_exit','relaxed_fall'],['relaxed_fall','relaxed_loop'],['relaxed_loop','get_up'],['get_up','idle_loop'],['dead_from_down','dead'],['hit_down','relaxed_loop']];
const transitionSeams={};
for(const [from,to] of transitions){
  const toTime=to==='dead'?data.findAnimation('dead').duration:0;
  const error=compare(frame(from,data.findAnimation(from).duration),frame(to,toTime));
  transitionSeams[`${from} -> ${to}`]=error;
  assert(error<.002,`${from} -> ${to} seam ${error}`);
}
let idleAnchorDrift=0;
const initial=frame('idle_loop',0);
for(let i=0;i<=240;i++){
  const sk=frame('idle_loop',i/60);
  for(const name of ['staff','grip_r','foot_r','foot_l']){
    const a=initial.findBone(name),b=sk.findBone(name);
    idleAnchorDrift=Math.max(idleAnchorDrift,Math.hypot(a.worldX-b.worldX,a.worldY-b.worldY));
  }
}
assert(idleAnchorDrift<.0001);
let supportError=0;
for(const name of ['chant_loop','chant_ack','explosion_release','explosion_hold']){
  for(let i=0;i<=60;i++){
    const sk=frame(name,i/60*data.findAnimation(name).duration),s=sk.findBone('staff'),g=sk.findBone('grip_l');
    const x=-42*320/1320,y=122*320/1320;
    supportError=Math.max(supportError,Math.hypot(s.worldX+s.a*x+s.b*y-g.worldX,s.worldY+s.c*x+s.d*y-g.worldY));
  }
}
assert(supportError<.08,`support hand target drift ${supportError}`);
assert(minClothY>-.03,`cloth below floor: ${minClothY}`);
// Stretch is only a small IK allowance, not a substitute for reachable poses.
assert(maxStretch<1.03,`limb stretches too far: ${maxStretch} at ${JSON.stringify(stretchAt)}`);
const eventCounts={};
for(const [name,event] of [['explosion_release','release'],['attack_short','impact']]){
  const events=[],a=data.findAnimation(name);
  a.apply(new spine.Skeleton(data),-1,a.duration,false,events,1,spine.MixBlend.setup,spine.MixDirection.mixIn);
  eventCounts[event]=events.filter(e=>e.data.name===event).length;
  assert.equal(eventCounts[event],1);
}
for(const name of ['dead','dead_from_down']){
  const d=data.findAnimation(name).duration;
  assert(compare(frame(name,d),frame(name,d+5))<.002,`${name} does not hold`);
}
const result={runtime:'@esotericsoftware/spine-core 4.2.95',animations:data.animations.length,actionClips:data.animations.length-1,bones:data.bones.length,samples,maxIKError,maxStretch,stretchAt,maxSourceMappingError,minClothY,idleAnchorDrift,supportError,loopSeams,transitionSeams,eventCounts,passed:true};
fs.writeFileSync(path.join(root,'export/validation.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify(result,null,2));
