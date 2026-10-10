import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import * as spine from '@esotericsoftware/spine-core';
const root=path.resolve(import.meta.dirname,'..');
const game='D:/Github/spire-codex/extraction/raw/animations/characters';
const out=path.join(root,'actions-v7/research');
fs.mkdirSync(out,{recursive:true});
const report={source:game,scope:'Local extracted base-game character data; not Watcher mod. Inspected read-only.',characters:[]};
for(const name of ['ironclad','silent','necrobinder','regent','defect']){
 const dir=path.join(game,name),file=path.join(dir,name+'.skel');
 const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(dir,name+'.atlas'),'utf8'));
 const data=new spine.SkeletonBinary(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(fs.readFileSync(file));
 const slots=new Map();
 for(const skin of data.skins)for(const entry of skin.getAttachments()){
  const slot=data.slots[entry.slotIndex].name;
  if(!slots.has(slot))slots.set(slot,[]);
  const a=entry.attachment;
  slots.get(slot).push({skin:skin.name,name:entry.name,path:a.path,type:a.constructor.name,vertices:a.worldVerticesLength??0,weighted:!!a.bones});
 }
 const anims=data.animations.map(a=>({name:a.name,duration:a.duration,timelineTypes:a.timelines.reduce((n,t)=>(n[t.constructor.name]=(n[t.constructor.name]??0)+1,n),{}),attachmentKeys:a.timelines.filter(t=>t instanceof spine.AttachmentTimeline).map(t=>({slot:data.slots[t.slotIndex].name,keys:[...t.frames].map((time,i)=>({time,attachment:t.attachmentNames[i]}))})),drawOrder:a.timelines.filter(t=>t instanceof spine.DrawOrderTimeline).map(t=>({times:[...t.frames],orders:t.drawOrders}))}));
 const entry={name,version:data.version,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),bones:data.bones.length,slots:data.slots.length,ik:data.ikConstraints.length,skins:data.skins.map(s=>s.name),multiAttachmentSlots:[...slots.entries()].filter(([n,v])=>v.length>1).map(([name,attachments])=>({name,attachments})),animations:anims};
 report.characters.push(entry);
 console.log(JSON.stringify({name,version:entry.version,bones:entry.bones,slots:entry.slots,multiSlots:entry.multiAttachmentSlots.length,clips:anims.map(a=>({name:a.name,duration:a.duration,swaps:a.attachmentKeys.reduce((n,t)=>n+t.keys.length,0),types:a.timelineTypes}))}));
}
fs.writeFileSync(path.join(out,'sts2-character-attachment-audit.json'),JSON.stringify(report,null,2));
