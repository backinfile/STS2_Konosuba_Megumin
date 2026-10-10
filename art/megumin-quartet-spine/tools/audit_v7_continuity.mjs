// Repro for visible part-size jumps. Measures geometry at +/- 0.1 ms around
// attachment switches, so ordinary animation speed cannot explain a failure.
import fs from 'node:fs';
import path from 'node:path';
import {root, raw, data, meta, frame, vertices, cross} from './v7_runtime.mjs';
const alphaPath=path.join(root,'verification/alpha-triangles.json');
const alpha=fs.existsSync(alphaPath)?JSON.parse(fs.readFileSync(alphaPath,'utf8')):null;

function shape(sk, slotName) {
  const s=sk.findSlot(slotName), a=s.attachment;
  if(!a)return null;
  const xy=vertices(s);let area=0,cx=0,cy=0;
  for(let i=0;i<a.triangles.length;i+=3){
    const [p,q,r]=a.triangles.slice(i,i+3), sample=alpha?.[a.name]?.[i/3]||[1,1/3,1/3,1/3], w=Math.abs(cross(xy,p,q,r))/2*sample[0];
    area+=w;cx+=w*(xy[2*p]*sample[1]+xy[2*q]*sample[2]+xy[2*r]*sample[3]);cy+=w*(xy[2*p+1]*sample[1]+xy[2*q+1]*sample[2]+xy[2*r+1]*sample[3]);
  }
  return {attachment:a.name,area,cx:cx/area,cy:cy/area};
}
const switches=[], deformations=[], teleports=[];
for(const clip of data.animations){
  if(clip.name.startsWith('_bind/'))continue;
  for(const slot of ['head','hand_r','leg_l','leg_r','body']){
    for(const key of raw.animations[clip.name].slots[slot].attachment){
      if(!key.time)continue;
      const a=shape(frame(clip.name,key.time-.0001),slot),b=shape(frame(clip.name,key.time+.0001),slot);
      if(!a||!b||a.attachment===b.attachment)continue;
      switches.push({clip:clip.name,slot,time:key.time,from:a.attachment,to:b.attachment,
        areaJump:Math.abs(b.area/a.area-1),centroidJump:Math.hypot(b.cx-a.cx,b.cy-a.cy)});
    }
  }
  let previous;
  for(let i=0;i<=Math.ceil(clip.duration*60);i++){
    const t=Math.min(i/60,clip.duration),sk=frame(clip.name,t),s=shape(sk,'head');
    const bind=shape(frame('_bind/'+s.attachment.split('/')[0],0),'head');
    deformations.push({clip:clip.name,time:t,headAreaRatio:s.area/bind.area});
    if(previous){
      const b=sk.findBone('hand_l'),p=previous.findBone('hand_l');
      const distance=Math.hypot(b.worldX-p.worldX,b.worldY-p.worldY);
      if(distance>20)teleports.push({clip:clip.name,time:t,bone:'hand_l',distance});
    }
    previous=sk;
  }
}
const failures=switches.filter(s=>(s.slot==='head'&&(s.areaJump>.06||s.centroidJump>4))||
  (s.slot==='hand_r'&&(s.areaJump>.01||s.centroidJump>1)));
const headStretch=deformations.filter(s=>Math.abs(s.headAreaRatio-1)>.05);
const report={passed:failures.length===0&&headStretch.length===0&&teleports.length===0,limits:{headSwitchAreaJump:.06,headSwitchCentroid:4,headWithinPoseAreaDrift:.05},switches,
  maxima:Object.fromEntries(['head','hand_r','leg_l','leg_r','body'].map(slot=>{const rows=switches.filter(s=>s.slot===slot);return[slot,{areaJump:Math.max(...rows.map(s=>s.areaJump)),centroidJump:Math.max(...rows.map(s=>s.centroidJump))}]})),
  failingSwitches:failures.sort((a,b)=>b.areaJump-a.areaJump),headStretch:headStretch.sort((a,b)=>Math.abs(b.headAreaRatio-1)-Math.abs(a.headAreaRatio-1)).slice(0,20),teleports,
  switchCount:switches.length,measurement:alpha?'Alpha-weighted triangle area and centroid':'Geometry including transparent padding',note:'Perspective and occlusion change body/leg visible area. Head and gripping hand size, within-pose deformation and arm teleports are the hard regression guards; visual replay must still check drawing changes.'};
const output=process.argv.find(a=>a.startsWith('--output='))?.slice(9);
if(output)fs.writeFileSync(path.resolve(output),JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,failingSwitches:failures.length,headStretchSamples:headStretch.length,worstSwitches:report.failingSwitches.slice(0,6),worstStretch:report.headStretch.slice(0,3),teleports:teleports.slice(0,4)},null,2));
if(!report.passed)process.exitCode=1;
