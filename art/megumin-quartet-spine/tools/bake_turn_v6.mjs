// Continuous 2.5D turn of the original UV art, preserving hand/eye identity.
// Apply after the ground-contact bake; existing weighted deforms are retained.
import fs from 'node:fs';import path from 'node:path';import{fileURLToPath}from'node:url';import * as spine from '@esotericsoftware/spine-core';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../actions-v6');
const raw=JSON.parse(fs.readFileSync(path.join(root,'export/megumin.json'),'utf8')),poses=JSON.parse(fs.readFileSync(path.join(root,'authoring-poses.json'),'utf8'));
const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(root,'export/megumin.atlas'),'utf8'));for(const p of atlas.pages)p.setTexture(new spine.FakeTexture({width:p.width,height:p.height}));
const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw);
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
let count=0;
for(const anim of data.animations){
 if(!poses[anim.name]?.some(p=>p.turn||p.headturn))continue;
 const tracks={};
 for(let n=0;n<=Math.ceil(anim.duration*60);n++){
  const t=Math.min(n/60,anim.duration),p=poses[anim.name][Math.min(n,poses[anim.name].length-1)];
  const sk=new spine.Skeleton(data);anim.apply(sk,0,t,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);sk.updateWorldTransform(spine.Physics.update);
  for(const name of ['head','head_repair','eye','body','body_repair','torso_fill','costume_under']){
   const slot=sk.findSlot(name),mesh=slot.attachment;if(!(mesh instanceof spine.MeshAttachment))continue;
   const key=name+'/'+mesh.name,xy=new Float32Array(mesh.worldVerticesLength);mesh.computeWorldVertices(slot,0,xy.length,xy,0,2);
   const head=['head','head_repair','eye'].includes(name),anchor=sk.findBone(head?'head':'torso'),turn=(head?p.headturn:p.turn)*(1-p.prone);
   const deform=[],bs=mesh.bones;let bi=0,di=0;const det=anchor.a*anchor.d-anchor.b*anchor.c;
   for(let i=0;i<xy.length;i+=2){
    const dx=xy[i]-anchor.worldX,dy=xy[i+1]-anchor.worldY,lx=(anchor.d*dx-anchor.b*dy)/det,ly=(-anchor.c*dx+anchor.a*dy)/det;
    let change;
    if(head){const face=smooth((ly+38)/26)*(1-smooth((ly-58)/42));change=(-.28*lx+10)*face*turn;}
    else{const top=smooth((ly+2)/90);change=(-.28*lx+7*top)*turn;}
    const wx=anchor.a*change,wy=anchor.c*change,nBones=bs[bi++];
    for(let j=0;j<nBones;j++){
     const b=sk.bones[bs[bi++]],bd=b.a*b.d-b.b*b.c;
     deform.push(+((slot.deform[di++]??0)+(b.d*wx-b.b*wy)/bd).toFixed(6),+((slot.deform[di++]??0)+(-b.c*wx+b.a*wy)/bd).toFixed(6));
    }
   }
   let begin=0,end=deform.length;while(begin<end&&deform[begin]===0)begin++;while(end>begin&&deform[end-1]===0)end--;
   (tracks[key]??=[]).push(end===begin?{time:+t.toFixed(7)}:{time:+t.toFixed(7),offset:begin,vertices:deform.slice(begin,end)});
  }
 }
 const target=(raw.animations[anim.name].attachments??={}).default??={};
 for(const [key,keys]of Object.entries(tracks)){const[s,a]=key.split('/');(target[s]??={})[a]={deform:keys};count++;}
}
for(const name of ['megumin.json','megumin.spine-json'])fs.writeFileSync(path.join(root,'export',name),JSON.stringify(raw));
fs.writeFileSync(path.join(root,'export/turn-bake.json'),JSON.stringify({timelines:count,method:'Continuous weighted-mesh projection; original UVs, no whole-head swaps or horizontal mirroring.'},null,2));
console.log({turnTimelines:count});
