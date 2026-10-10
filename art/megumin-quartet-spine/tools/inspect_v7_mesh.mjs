import assert from 'node:assert/strict';
import {frame,folds} from './v7_runtime.mjs';
const report=[];
for(const [name,t,max] of [['chant_enter',.45,15],['relaxed_fall',.82,20],['get_up',1.58,5]]){
 const result={name,t,...folds(frame(name,t))};report.push(result);
 if(process.argv.includes('--assert'))assert(result.foldedArea<max,`${name}@${t}: folded mesh area ${result.foldedArea} >= ${max}`);
}
console.log(JSON.stringify(report,null,2));
