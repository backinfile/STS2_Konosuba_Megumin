// Fold only the lower concealed cape edge onto the separate ground-cape art.
// This is standard Spine weighted-mesh deformation, without texture editing.
import fs from 'node:fs';import path from 'node:path';import{fileURLToPath}from'node:url';import * as spine from '@esotericsoftware/spine-core';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../actions-v4'),raw=JSON.parse(fs.readFileSync(path.join(root,'export/megumin.json'),'utf8'));
for(const anim of Object.values(raw.animations))delete anim.attachments;
const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(root,'export/megumin.atlas'),'utf8'));for(const p of atlas.pages)p.setTexture(new spine.FakeTexture({width:p.width,height:p.height}));
const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw);let timelines=0,maxLift=0;
for(const anim of data.animations){const tracks={},active=new Set();
 for(let n=0;n<=Math.round(anim.duration*60);n++){
  const time=Math.min(n/60,anim.duration),sk=new spine.Skeleton(data);anim.apply(sk,0,time,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);sk.updateWorldTransform(spine.Physics.update);
  for(const slotName of ['body_repair','costume_under','body','torso_fill']){
   const slot=sk.findSlot(slotName),mesh=slot.attachment;if(!mesh)continue;const key=slotName+'/'+mesh.name;
   const world=new Float32Array(mesh.worldVerticesLength);mesh.computeWorldVertices(slot,0,world.length,world,0,2);
   const deform=[],bs=mesh.bones;let bi=0;
   for(let v=0;v<world.length;v+=2){const lift=Math.max(0,.45-world[v+1]);maxLift=Math.max(maxLift,lift);if(lift>.0001)active.add(key);const count=bs[bi++];
    for(let j=0;j<count;j++){const b=sk.bones[bs[bi++]],det=b.a*b.d-b.b*b.c;deform.push(+(-b.b*lift/det).toFixed(6),+(b.a*lift/det).toFixed(6))}}
   let begin=0,end=deform.length;while(begin<end&&deform[begin]===0)begin++;while(end>begin&&deform[end-1]===0)end--;
   (tracks[key]??=[]).push(end===begin?{time:+time.toFixed(7)}:{time:+time.toFixed(7),offset:begin,vertices:deform.slice(begin,end)});
  }
 }
 if(active.size){raw.animations[anim.name].attachments={default:{}};for(const key of active){const[s,a]=key.split('/');(raw.animations[anim.name].attachments.default[s]??={})[a]={deform:tracks[key]};timelines++}}
}
const json=JSON.stringify(raw);for(const f of ['megumin.json','megumin.spine-json'])fs.writeFileSync(path.join(root,'export',f),json);
fs.writeFileSync(path.join(root,'export/floor-bake.json'),JSON.stringify({timelines,maxConcealedCapeLift:maxLift,groundCape:'Separate fully drawn flat cape, opaque attachment swap; upper edge folds beneath it.'},null,2));console.log({timelines,maxLift});
