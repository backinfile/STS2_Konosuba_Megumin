import fs from 'node:fs';import path from 'node:path';import{fileURLToPath}from'node:url';import * as spine from '@esotericsoftware/spine-core';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../actions-v4'),raw=JSON.parse(fs.readFileSync(path.join(root,'export/megumin.json'),'utf8')),geometry=JSON.parse(fs.readFileSync(path.join(root,'geometry.json'),'utf8'));
const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(root,'export/megumin.atlas'),'utf8'));for(const p of atlas.pages)p.setTexture(new spine.FakeTexture({width:p.width,height:p.height}));
const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw),report={};
for(const a of data.animations){let stretch=1,at={},low=0,lowAt={},ik=0;for(let n=0;n<=120;n++){
 const t=n/120*a.duration,sk=new spine.Skeleton(data);a.apply(sk,0,t,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);sk.updateWorldTransform(spine.Physics.update);
 for(const b of sk.bones){if(/^(upper|fore|thigh|shin)_/.test(b.data.name)){let v=Math.hypot(b.a,b.c);if(v>stretch){stretch=v;at={t,b:b.data.name}}}}
 for(const[end,target]of[['fore_r','grip_r'],['fore_l','grip_l'],['shin_r','foot_r'],['shin_l','foot_l']]){const b=sk.findBone(end),g=sk.findBone(target);ik=Math.max(ik,Math.hypot(b.worldX+b.a*b.data.length-g.worldX,b.worldY+b.c*b.data.length-g.worldY))}
 for(const s of sk.slots){if(!s.attachment||s.color.a<.9)continue;const m=s.attachment,xy=new Float32Array(m.worldVerticesLength);m.computeWorldVertices(s,0,xy.length,xy,0,2);for(const i of geometry[m.name]?.visible_vertices??[]){if(xy[i*2+1]<low){low=xy[i*2+1];lowAt={t,s:s.data.name}}}}
 }report[a.name]={stretch,at,low,lowAt,ik}}
fs.writeFileSync(path.join(root,'measurements.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
