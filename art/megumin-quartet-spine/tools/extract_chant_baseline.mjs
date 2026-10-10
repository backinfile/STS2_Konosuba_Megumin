// Read-only baseline sampling for the chant-entry design document.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as spine from '@esotericsoftware/spine-core';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const dir=path.join(root,'chant-enter-plan');fs.mkdirSync(dir,{recursive:true});
const raw=JSON.parse(fs.readFileSync(path.join(root,'actions-v5/export/megumin.json'),'utf8'));
const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(root,'actions-v5/export/megumin.atlas'),'utf8'));
for(const p of atlas.pages)p.setTexture(new spine.FakeTexture({width:p.width,height:p.height}));
const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw);
const anim=data.findAnimation('chant_enter'),frames=[];
for(let f=0;f<=63;f++){
 const sk=new spine.Skeleton(data);anim.apply(sk,0,f/60,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);sk.updateWorldTransform(spine.Physics.update);
 frames.push({f,t:f/60,bones:Object.fromEntries(sk.bones.map(b=>[b.data.name,{x:b.worldX,y:b.worldY,angle:Math.atan2(b.c,b.a)*180/Math.PI,length:b.data.length}])),slots:Object.fromEntries(sk.slots.map(s=>[s.data.name,{alpha:s.color.a,attachment:s.getAttachment()?.name}]))});
}
fs.writeFileSync(path.join(dir,'baseline-v5.json'),JSON.stringify({duration:anim.duration,fps:60,frames},null,2));
console.log(JSON.stringify({firstSideFrame:frames.find(x=>x.slots.side_head.alpha>.5).f,frames:[0,12,21,30,37,46,47,54,63].map(f=>({f,grip:frames[f].bones.grip_r,side:frames[f].slots.side_head.alpha})),initialBones:frames[0].bones},null,2));
