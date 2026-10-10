import fs from 'node:fs';import path from 'node:path';import{fileURLToPath}from'node:url';import * as spine from '@esotericsoftware/spine-core';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../actions-v3');
const raw=JSON.parse(fs.readFileSync(path.join(root,'export/megumin.json'),'utf8'));
const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(root,'export/megumin.atlas'),'utf8'));
for(const p of atlas.pages)p.setTexture(new spine.FakeTexture({width:p.width,height:p.height}));
const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw);
let result={};
for(const a of data.animations){let max={};for(let n=0;n<=60;n++){
 const t=n/60*a.duration,sk=new spine.Skeleton(data);a.apply(sk,0,t,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);sk.updateWorldTransform(spine.Physics.update);
 for(const [end,target]of[['fore_r','grip_r'],['fore_l','grip_l'],['shin_r','foot_r'],['shin_l','foot_l']]){
  const b=sk.findBone(end),g=sk.findBone(target),err=Math.hypot(b.worldX+b.a*b.data.length-g.worldX,b.worldY+b.c*b.data.length-g.worldY);
  if(!max[end]||err>max[end].error)max[end]={error:+err.toFixed(3),time:+t.toFixed(3)};
 }
}result[a.name]=max}
fs.writeFileSync(path.join(root,'ik-audit.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify(Object.fromEntries(Object.entries(result).filter(([k,v])=>Object.values(v).some(x=>x.error>.1))),null,2));
