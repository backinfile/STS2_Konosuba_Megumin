// Choose a single attachment switch per directed pose pair, never oscillating
// between images. Runtime deformation is measured on both candidate drawings.
import fs from 'node:fs';import path from 'node:path';
import {root,meta,data,frame,folds} from './v7_runtime.mjs';
const pairs={};
for(const [name,plan] of Object.entries(meta.clips)){
 if(name.startsWith('_bind/'))continue;
 for(const f of plan.frames){if(f.from_pose===f.to_pose||f.blend<.01||f.blend>.99)continue;
  const vals=[];
  for(const pose of [f.from_pose,f.to_pose]){const sk=frame(name,f.time);
   for(const s of sk.slots){if(s.data.name==='staff'||s.data.name==='body_under')continue;if(!s.attachment)continue;s.setAttachment(data.defaultSkin.getAttachment(s.data.index,pose+'/'+s.data.name));}
   vals.push(folds(sk).foldedArea);
  }
  (pairs[f.from_pose+' > '+f.to_pose]??=[]).push({u:f.blend,vals});
 }
}
const thresholds={},report=[];
for(const [pair,samples] of Object.entries(pairs)){
 const cost=q=>Math.max(...samples.map(s=>s.vals[s.u<q?0:1]));
 let q=.5,best=cost(q),before=best;
 for(let candidate=.2;candidate<=.8;candidate+=.01){const c=cost(candidate);if(c<best-.01){best=c;q=+candidate.toFixed(2);}}
 thresholds[pair]=q;report.push({pair,before,after:best,threshold:q});
}
fs.writeFileSync(path.join(root,'attachment-switches.json'),JSON.stringify({thresholds,report},null,2));
console.log(JSON.stringify(report,null,2));
