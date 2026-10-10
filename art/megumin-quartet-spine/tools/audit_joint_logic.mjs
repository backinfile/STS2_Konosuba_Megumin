// Reproduce impossible folds / branch pops in the exported Spine data.
import fs from 'node:fs';import path from 'node:path';import{fileURLToPath}from'node:url';import * as spine from '@esotericsoftware/spine-core';
const version=process.argv[2]??'actions-v4',root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..',version);
const raw=JSON.parse(fs.readFileSync(path.join(root,'export/megumin.json'),'utf8')),atlas=new spine.TextureAtlas(fs.readFileSync(path.join(root,'export/megumin.atlas'),'utf8'));
for(const p of atlas.pages)p.setTexture(new spine.FakeTexture({width:p.width,height:p.height}));
const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw),wrap=a=>(a+540)%360-180,angle=b=>Math.atan2(b.c,b.a)*180/Math.PI;
const pairs=[['elbow_r','upper_r','fore_r'],['elbow_l','upper_l','fore_l'],['knee_r','thigh_r','shin_r'],['knee_l','thigh_l','shin_l']];
const report={version,samples:0,thresholds:{maxFoldDegrees:150,maxJointStepAt240Hz:3,branchFlipFoldDegrees:10},clips:{},violations:[]};
for(const a of data.animations){let previous=null,peakFold={value:0},peakStep={value:0},flips=[],joints={};
 for(let i=0;i<=Math.ceil(a.duration*240);i++){
  const t=Math.min(i/240,a.duration),sk=new spine.Skeleton(data);report.samples++;a.apply(sk,0,t,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);sk.updateWorldTransform(spine.Physics.update);
  const snapshot={};for(const[name,upper,lower]of pairs){const u=sk.findBone(upper),l=sk.findBone(lower),fold=wrap(angle(l)-angle(u));snapshot[name]={x:l.worldX,y:l.worldY,fold};
   const j=joints[name]??={maxFold:0,maxStep:0};j.maxFold=Math.max(j.maxFold,Math.abs(fold));
   if(Math.abs(fold)>peakFold.value)peakFold={value:Math.abs(fold),joint:name,time:t};
   if(previous){const p=previous[name],step=Math.hypot(p.x-l.worldX,p.y-l.worldY);j.maxStep=Math.max(j.maxStep,step);if(step>peakStep.value)peakStep={value:step,joint:name,time:t};
    if(fold*p.fold<0&&Math.min(Math.abs(fold),Math.abs(p.fold))>10)flips.push({joint:name,time:t,from:p.fold,to:fold,step});
   }
  }previous=snapshot;
 }
 report.clips[a.name]={peakFold,peakStep,flips,joints};
 if(peakFold.value>150.1||peakStep.value>3||flips.length)report.violations.push({clip:a.name,peakFold,peakStep,flips});
}
fs.writeFileSync(path.join(root,'joint-audit.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({version,violations:report.violations},null,2));
if(process.argv.includes('--strict')&&report.violations.length)process.exitCode=1;
