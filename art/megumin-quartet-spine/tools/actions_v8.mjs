import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const env={...process.env,MEGUMIN_ACTIONS:'actions-v8'};
function run(command,...args){const r=spawnSync(command,args,{cwd:root,env,stdio:'inherit'});if(r.error)throw r.error;if(r.status)process.exit(r.status);}
const build=process.argv.includes('--build');
if(build)run('py','-X','utf8','tools/build_actions_v8.py');
run('py','-X','utf8','tools/validate_moire.py');
run('py','-X','utf8','tools/measure_alpha_triangles.py');
run('node','tools/validate_actions_v7.mjs');
run('node','tools/audit_v7_continuity.mjs','--output=actions-v8/verification/continuity.json');
if(build)run('py','-X','utf8','tools/package_actions_v8.py');
