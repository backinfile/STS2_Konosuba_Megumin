import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as spine from '@esotericsoftware/spine-core';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../idle-v2');
const raw=JSON.parse(fs.readFileSync(path.join(root,'export/megumin-idle.json'),'utf8'));
const meta=JSON.parse(fs.readFileSync(path.join(root,'export/manifest.json'),'utf8'));
const bind=JSON.parse(fs.readFileSync(path.join(root,'bind-check.json'),'utf8'));
const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(root,'export/megumin-idle.atlas'),'utf8'));
for(const p of atlas.pages)p.setTexture(new spine.FakeTexture({width:p.width,height:p.height}));
const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw);
const meshRaw=raw.skins[0].attachments.reference_mesh['idle-reference'];
function frame(t,name='idle_loop'){
 const sk=new spine.Skeleton(data);
 data.findAnimation(name).apply(sk,0,t,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);
 sk.updateWorldTransform(spine.Physics.update);
 const slot=sk.findSlot('reference_mesh'),mesh=slot.attachment;
 assert(mesh instanceof spine.MeshAttachment && mesh.bones,'Must be an actual weighted Spine mesh');
 const v=new Float32Array(mesh.worldVerticesLength);mesh.computeWorldVertices(slot,0,v.length,v,0,2);
 return v;
}
const rest=frame(0),end=frame(4);
let maxBindError=0,maxSeamError=0,maxFixedDrift=0,maxMotion=0,minAreaRatio=Infinity,maxAreaRatio=0;
function area(v,a,b,c){return (v[b*2]-v[a*2])*(v[c*2+1]-v[a*2+1])-(v[b*2+1]-v[a*2+1])*(v[c*2]-v[a*2]);}
for(let i=0;i<rest.length;i++){
 maxBindError=Math.max(maxBindError,Math.abs(rest[i]-bind.expected_world[i]));
 maxSeamError=Math.max(maxSeamError,Math.abs(rest[i]-end[i]));
}
assert(maxBindError<.0001,'Rest pose no longer aligns with source texture');
assert(maxSeamError<.0001,'Loop endpoints differ');
// Check the rendered positions around independently chosen visible landmarks.
const probes={staffTip:[95,246],orb:[182,492],grip:[309,882],staffBase:[415,1320],rightToe:[540,1333],leftToe:[706,1329]};
const tri=meshRaw.triangles,uv=meshRaw.uvs;
const src=[];for(let i=0;i<uv.length;i+=2)src.push(uv[i]*meta.source_size[0],uv[i+1]*meta.source_size[1]);
function locate([px,py]){
 for(let i=0;i<tri.length;i+=3){const [a,b,c]=tri.slice(i,i+3),den=area(src,a,b,c);
   const ax=src[a*2],ay=src[a*2+1],bx=src[b*2],by=src[b*2+1],cx=src[c*2],cy=src[c*2+1];
   const wb=((px-ax)*(cy-ay)-(py-ay)*(cx-ax))/den;
   const wc=((bx-ax)*(py-ay)-(by-ay)*(px-ax))/den,wa=1-wb-wc;
   if(Math.min(wa,wb,wc)>-1e-8)return {ids:[a,b,c],weights:[wa,wb,wc]};
 }throw Error('Landmark outside mesh');
}
function sample(v,p){let x=0,y=0;for(let i=0;i<3;i++){x+=v[p.ids[i]*2]*p.weights[i];y+=v[p.ids[i]*2+1]*p.weights[i]}return [x,y]}
const located=Object.fromEntries(Object.entries(probes).map(([k,p])=>[k,locate(p)]));
const probeDrift=Object.fromEntries(Object.keys(probes).map(k=>[k,0]));
for(let n=0;n<=240;n++){
 const v=frame(n/60);assert([...v].every(Number.isFinite));
 for(let i=0;i<v.length;i+=2)maxMotion=Math.max(maxMotion,Math.hypot(v[i]-rest[i],v[i+1]-rest[i+1]));
 for(const i of bind.fixed_vertex_indices)maxFixedDrift=Math.max(maxFixedDrift,Math.hypot(v[i*2]-rest[i*2],v[i*2+1]-rest[i*2+1]));
 for(const [name,p] of Object.entries(located)){const a=sample(rest,p),b=sample(v,p);probeDrift[name]=Math.max(probeDrift[name],Math.hypot(a[0]-b[0],a[1]-b[1]));}
 for(let i=0;i<tri.length;i+=3){const [a,b,c]=tri.slice(i,i+3),ratio=area(v,a,b,c)/area(rest,a,b,c);minAreaRatio=Math.min(minAreaRatio,ratio);maxAreaRatio=Math.max(maxAreaRatio,ratio);assert(ratio>.7&&ratio<1.3,'Folded or badly stretched triangle');}
}
assert(maxFixedDrift<.0001,'Anchored mesh vertices drift');
assert(Object.values(probeDrift).every(v=>v<.0001),'Staff, grip or toes drift');
assert(maxMotion>.2&&maxMotion<1.2,'Idle must move subtly at 320px character height');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
assert.equal(hash(path.join(root,'export/idle-reference.png')),meta.texture_sha256);
assert.equal(hash(path.join(root,'images/idle-reference.png')),meta.texture_sha256);
assert.equal(hash(path.resolve(root,'../../megumin-concepts-20261009/quartet/idle-02-right-hand.png')),meta.texture_sha256);
const result={passed:true,runtime:'@esotericsoftware/spine-core 4.2.95',samples:241,
 textureByteIdentical:true,bones:data.bones.length,vertices:rest.length/2,triangles:tri.length/3,
 maxRestErrorAt320px:maxBindError,maxLoopSeamAt320px:maxSeamError,maxAnchorDriftAt320px:maxFixedDrift,
 maxMotionAt320px:maxMotion,landmarkDriftAt320px:probeDrift,minTriangleAreaRatio:minAreaRatio,maxTriangleAreaRatio:maxAreaRatio};
fs.writeFileSync(path.join(root,'export/validation.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify(result,null,2));
