import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import * as spine from '@esotericsoftware/spine-core';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const raw=JSON.parse(fs.readFileSync(path.join(root,'export/megumin.json'),'utf8'));
const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(root,'export/megumin.atlas'),'utf8'));
// Tests need atlas geometry but no GPU or image decoder.
for(const page of atlas.pages) page.setTexture(new spine.FakeTexture({width:page.width,height:page.height}));
const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw);
function frame(name,t){
  const sk=new spine.Skeleton(data);
  const a=data.findAnimation(name);
  a.apply(sk,0,t,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);
  sk.updateWorldTransform(spine.Physics.update);
  return sk;
}
let samples=0,maxGripError=0;
for(const a of data.animations){
  assert(a.duration>0,`${a.name} has no duration`);
  for(let i=0;i<=Math.ceil(a.duration*60);i++){
    const sk=frame(a.name,Math.min(i/60,a.duration));samples++;
    for(const b of sk.bones) for(const prop of ['a','b','c','d','worldX','worldY']) assert(Number.isFinite(b[prop]),`${a.name}/${b.data.name}/${prop}`);
    for(const slot of sk.slots){
      const attachment=slot.attachment;
      if(attachment instanceof spine.MeshAttachment){
        const vertices=new Float32Array(attachment.worldVerticesLength);
        attachment.computeWorldVertices(slot,0,vertices.length,vertices,0,2);
        assert([...vertices].every(Number.isFinite),`${a.name} invalid mesh`);
        assert([...attachment.regionUVs].every(v=>v>=0&&v<=1),`${a.name} mesh UV outside image`);
      }
    }
    if(sk.findSlot('fore_r').attachment){
      const f=sk.findBone('fore_r'), g=sk.findBone('grip_r');
      const error=Math.hypot(f.worldX+f.a*f.data.length-g.worldX,f.worldY+f.c*f.data.length-g.worldY);
      maxGripError=Math.max(maxGripError,error);
      assert(error<.25,`${a.name} right grip drift: ${error}`);
    }
  }
}
const loops=['idle_loop','chant_loop','explosion_hold','relaxed_loop'];
for(const name of loops){
  const a=frame(name,0),b=frame(name,data.findAnimation(name).duration);
  for(let i=0;i<a.bones.length;i++) for(const p of ['a','b','c','d','worldX','worldY']) assert(Math.abs(a.bones[i][p]-b.bones[i][p])<.001,`${name}/${a.bones[i].data.name} loop seam`);
}
// Feet and primary staff grip remain anchored throughout idle breathing.
for(const t of [.3,.9,1.5,2.1,2.7]){
  const a=frame('idle_loop',0),b=frame('idle_loop',t);
  for(const name of ['leg_l','leg_r','staff']) for(const p of ['worldX','worldY']) assert.equal(a.findBone(name)[p],b.findBone(name)[p]);
}
for(const name of ['chant_loop','explosion_hold']) for(const t of [0,.2,.5]){
  const sk=frame(name,t),staff=sk.findBone('staff'),target=sk.findBone('grip_l'),f=sk.findBone('fore_l');
  const x=staff.worldX+staff.b*55,y=staff.worldY+staff.d*55;
  assert(Math.hypot(x-target.worldX,y-target.worldY)<.001,`${name} support grip target`);
  assert(Math.hypot(f.worldX+f.a*f.data.length-x,f.worldY+f.c*f.data.length-y)<.25,`${name} left grip drift`);
}
for(const name of ['dead','dead_from_down']){
  const sk=frame(name,data.findAnimation(name).duration);
  assert.equal(sk.findSlot('down').attachment.name,'defeat');
  assert.equal(sk.findSlot('head').attachment,null);
}
const events=[];data.findAnimation('explosion_release').apply(new spine.Skeleton(data),-1,.6,false,events,1,spine.MixBlend.setup,spine.MixDirection.mixIn);
assert.equal(events.filter(e=>e.data.name==='release').length,1);
const result={runtime:'@esotericsoftware/spine-core 4.2.95',animations:data.animations.length,bones:data.bones.length,samples,maxRightGripError:maxGripError,loopsChecked:loops,passed:true};
fs.writeFileSync(path.join(root,'export/validation.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify(result,null,2));
