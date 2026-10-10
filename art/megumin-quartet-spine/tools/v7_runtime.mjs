import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as spine from '@esotericsoftware/spine-core';
export {spine};
export const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..',process.env.MEGUMIN_ACTIONS||'actions-v7');
export const raw=JSON.parse(fs.readFileSync(path.join(root,'export/megumin.json'),'utf8'));
export const meta=JSON.parse(fs.readFileSync(path.join(root,'authoring.json'),'utf8'));
const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(root,'export/megumin.atlas'),'utf8'));
for(const p of atlas.pages)p.setTexture(new spine.FakeTexture({width:p.width,height:p.height}));
export const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw);
export function frame(name,t){const sk=new spine.Skeleton(data);data.findAnimation(name).apply(sk,0,t,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);sk.updateWorldTransform(spine.Physics.update);return sk;}
export function vertices(slot){const a=slot.attachment,xy=new Float32Array(a.worldVerticesLength);a.computeWorldVertices(slot,0,xy.length,xy,0,2);return xy;}
export const cross=(xy,a,b,c)=>(xy[b*2]-xy[a*2])*(xy[c*2+1]-xy[a*2+1])-(xy[b*2+1]-xy[a*2+1])*(xy[c*2]-xy[a*2]);
export function folds(sk){let total=0;const slots=[];for(const s of sk.slots){const a=s.attachment;if(!(a instanceof spine.MeshAttachment))continue;const xy=vertices(s);let area=0,count=0;for(let i=0;i<a.triangles.length;i+=3){const ia=a.triangles[i],ib=a.triangles[i+1],ic=a.triangles[i+2],u=cross(a.regionUVs,ia,ib,ic),v=cross(xy,ia,ib,ic);if(u*v>1e-9){area+=Math.abs(v)/2;count++;}}total+=area;if(area>.1)slots.push({slot:s.data.name,area:+area.toFixed(2),triangles:count});}return {foldedArea:+total.toFixed(2),slots};}
