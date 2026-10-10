// Read-only measurements supporting the visual audit, not a quality pass/fail.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as spine from '@esotericsoftware/spine-core';
const dir=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../actions-v3');
const raw=JSON.parse(fs.readFileSync(path.join(dir,'export/megumin.json'),'utf8'));
const atlas=new spine.TextureAtlas(fs.readFileSync(path.join(dir,'export/megumin.atlas'),'utf8'));
for(const p of atlas.pages)p.setTexture(new spine.FakeTexture({width:p.width,height:p.height}));
const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw);
function frame(name,t){const sk=new spine.Skeleton(data);data.findAnimation(name).apply(sk,0,t,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);sk.updateWorldTransform(spine.Physics.update);return sk;}
function bone(sk,name){const b=sk.findBone(name);return {x:b.worldX,y:b.worldY,rotation:Math.atan2(b.c,b.a)*180/Math.PI};}
const up=frame('get_up',.65),stand=frame('setup_pose',0),sit=frame('relaxed_fall',.38),release=frame('explosion_release',.4),chant=frame('chant_loop',0),down=frame('relaxed_loop',0),dead=frame('dead',1.1);
const endA=bone(chant,'grip_r'),endB=bone(chant,'grip_l');
const report={
  coordinate_unit:'world pixels; nominal character height 320 px',
  get_up_065_left_grip_height:bone(up,'grip_l').y,
  sitting_feet_horizontal_offsets:{right:bone(sit,'foot_r').x-bone(stand,'foot_r').x,left:bone(sit,'foot_l').x-bone(stand,'foot_l').x},
  chant_grip_separation:Math.hypot(endA.x-endB.x,endA.y-endB.y),
  explosion_release_head_world_angle:bone(release,'head').rotation,
  down_pelvis_world_angle:bone(down,'pelvis').rotation,
  dead_pelvis_world_angle:bone(dead,'pelvis').rotation,
  down_and_dead_use_same_expression:down.findSlot('eye').attachment.name===dead.findSlot('eye').attachment.name,
  fixed_draw_order:raw.slots.map(s=>s.name),
  clips_with_draw_order_tracks:Object.entries(raw.animations).filter(([n,a])=>a.drawOrder||a.draworder).map(([n])=>n),
  hat_hair_separate_bones:raw.bones.filter(b=>/hat|hair/.test(b.name)).map(b=>b.name),
  clip_hand_angle_max_adjacent_step:Object.fromEntries(Object.entries(raw.animations).map(([n,a])=>{const k=a.bones.hand_l.rotate;return [n,Math.max(...k.slice(1).map((v,i)=>Math.abs(v.value-k[i].value)))]})),
  floor_bake:JSON.parse(fs.readFileSync(path.join(dir,'export/floor-bake.json'),'utf8')),
  note:'These explain observed artifacts. Low numerical error does not establish a good pose.'
};
fs.writeFileSync(path.join(dir,'action-audit-measurements.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
