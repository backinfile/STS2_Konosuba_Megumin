const $=id=>document.getElementById(id);
const labels={idle_loop:['待机','保留原图站姿，轻呼吸；眨眼只替换眼部。'],cast_short:['普通施放','左手短手势，结束返回待机。'],chant_enter:['进入吟唱','右手主握，左手搭杖，过渡到朝右上方。'],chant_loop:['吟唱保持','双手握点固定；等待游戏的释放事件。'],chant_cancel:['取消吟唱','放下法杖并收回左手。'],chant_ack:['吟唱中出牌','短暂点头回应，继续保持双手持杖。'],attack_short:['普通出招','抬杖短送，杖头全程可见，结束返回待机。'],explosion_release:['爆裂释放','收蓄后向右推出；只触发一次 release 事件。'],explosion_hold:['爆裂保持','等待多段伤害结算，不按每段伤害重复身体动作。'],explosion_exit:['爆裂卸力','结束持杖用力，转入脱力。'],hit:['站立受击','冲击回缩、咬牙，帽发稍后跟随。'],hit_chant:['吟唱中受击','受击后回到双手吟唱姿势。'],relaxed_fall:['脱力倒下','腿软后坐倒，再向后躺下；同一套骨架连续过渡。'],relaxed_loop:['脱力保持','仰躺微呼吸，不自动视为死亡。'],get_up:['起身','左掌撑地，收腿承重，再握杖、起身恢复原姿。'],dead:['死亡','侧倒后保持最后一帧。'],dead_from_down:['倒地后死亡','由已有倒地姿态进入死亡，不先站起来。'],hit_down:['倒地受击','保持倒地，仅短促位移。']};
labels.setup_pose=['静态原姿','清理后的原图分层与关节绑定检查。'];
const looping=new Set(['idle_loop','chant_loop','explosion_hold','relaxed_loop']);
let data,skeleton,state,renderer,current='idle_loop',mode='idle',queue=[],stepElapsed=0,stepLimit=Infinity,paused=false,speed=1,last=performance.now(),pulseCount=0,flash=0,demoHold=false;
const canvas=$('canvas'),gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:true,antialias:true,preserveDrawingBuffer:true});
function log(text){const item=document.createElement('div');item.textContent=text;$('events').prepend(item);while($('events').children.length>12)$('events').lastChild.remove();}
function phaseFor(name){return name.startsWith('dead')?'dead':name.startsWith('chant')&&name!=='chant_cancel'||name==='hit_chant'?'chant':name.startsWith('explosion')?'release':name.startsWith('relaxed')||name==='hit_down'?'down':'idle';}
function play(name,loop=looping.has(name),limit=null){
  current=name;stepElapsed=0;stepLimit=limit??(loop?Infinity:data.findAnimation(name).duration);
  // Reset discrete inspection/queue clips; authored adjacent endpoints match.
  skeleton.setToSetupPose();state.clearTracks();state.setAnimation(0,name,loop);state.apply(skeleton);skeleton.updateWorldTransform(spine.Physics.update);
  $('clip').value=name;$('description').textContent=labels[name][1];$('state').textContent=`${labels[name][0]} / ${name}`;log(name);paused=false;$('pause').textContent='暂停';
}
function run(steps){queue=[...steps];next();}
function next(){if(!queue.length)return;const s=queue.shift();mode=s.mode??phaseFor(s.name);demoHold=!!s.pulses;if(demoHold){pulseCount=0;$('pulse').textContent=''}play(s.name,s.loop??looping.has(s.name),s.limit);}
function base(){return mode==='chant'?'chant_loop':mode==='down'?'relaxed_loop':mode==='dead'?'dead':'idle_loop';}
function pulse(){if(mode!=='release')return;pulseCount++;flash=.22;$('pulse').textContent=`伤害脉冲 ${String(pulseCount).padStart(2,'0')} · 身体未重播`;log(`damage pulse ${pulseCount}`);}
function command(action){
  if(mode==='dead'&&action!=='reset')return;
  queue=[];demoHold=false;
  if(action==='reset'){mode='idle';pulseCount=0;$('pulse').textContent='';play('idle_loop');}
  if(action==='cast'){const b=base();run([{name:mode==='chant'?'chant_ack':'cast_short',mode},{name:b,mode}]);}
  if(action==='chant'&&mode==='idle'){run([{name:'chant_enter',mode:'chant'},{name:'chant_loop',mode:'chant'}]);}
  if(action==='hit'){const b=base();run([{name:mode==='chant'?'hit_chant':mode==='down'?'hit_down':'hit',mode},{name:b,mode}]);}
  if(action==='release'&&(mode==='idle'||mode==='chant')){pulseCount=0;$('pulse').textContent='';run([...(mode==='idle'?[{name:'chant_enter',mode:'chant'}]:[]),{name:'explosion_release',mode:'release'},{name:'explosion_hold',mode:'release'}]);}
  if(action==='pulse')pulse();
  if(action==='finish'&&mode==='release')run([{name:'explosion_exit',mode:'release'},{name:'relaxed_fall',mode:'down'},{name:'relaxed_loop',mode:'down'}]);
  if(action==='recover'&&mode==='down')run([{name:'get_up',mode:'down'},{name:'idle_loop',mode:'idle'}]);
  if(action==='dead')run([{name:mode==='down'?'dead_from_down':'dead',mode:'dead'}]);
}
function demo(){pulseCount=0;$('pulse').textContent='';run([
 {name:'idle_loop',limit:.6},{name:'cast_short'},{name:'chant_enter'},
 {name:'chant_loop',limit:1.5},{name:'chant_ack'},{name:'chant_loop',limit:.65},{name:'hit_chant'},{name:'chant_loop',limit:.8},
 {name:'explosion_release'},{name:'explosion_hold',limit:1.15,pulses:true},{name:'explosion_exit'},
 {name:'relaxed_fall'},{name:'relaxed_loop',limit:1.3},{name:'get_up'},{name:'idle_loop'}]);}
function draw(){
  const w=canvas.clientWidth,h=canvas.clientHeight,dpr=Math.min(devicePixelRatio||1,2);
  if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);}
  const scale=$('small').checked?1:Math.min((h-94)/340,(w-85)/530);
  const cx=w*.46,ground=h-65;
  gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);
  renderer.camera.position.set((w/2-cx)/scale,(ground-h/2)/scale,0);renderer.camera.setViewport(w/scale,h/scale);renderer.camera.update();
  renderer.begin();
  renderer.line((25-cx)/scale,0,(w-25-cx)/scale,0,$('dark').checked?new spine.Color(.46,.44,.50,1):new spine.Color(.81,.75,.69,1));
  const radius=mode==='down'||mode==='dead'?150:78,shadowX=mode==='down'||mode==='dead'?-50:0,shadow=new spine.Color(.2,.14,.1,.09);
  for(let i=0;i<32;i++){const a=i/32*Math.PI*2,b=(i+1)/32*Math.PI*2;renderer.triangle(true,shadowX,-2,shadowX+Math.cos(a)*radius,Math.sin(a)*9-2,shadowX+Math.cos(b)*radius,Math.sin(b)*9-2,shadow,shadow,shadow);}
  renderer.drawSkeleton(skeleton,false);
  if($('bones').checked){const green=new spine.Color(.1,.6,.55,1),white=new spine.Color(1,1,1,1),red=new spine.Color(.92,.2,.18,1);for(const b of skeleton.bones){renderer.line(b.worldX,b.worldY,b.worldX+b.a*b.data.length,b.worldY+b.c*b.data.length,green);renderer.circle(true,b.worldX,b.worldY,2.4/scale,white,12);}for(const name of ['grip_r','grip_l','foot_r','foot_l']){const b=skeleton.findBone(name);renderer.circle(false,b.worldX,b.worldY,5/scale,red,20);}}
  if(flash>0)renderer.rect(true,-cx/scale,(ground-h)/scale,w/scale,h/scale,new spine.Color(.92,.64,.24,flash*.55));
  renderer.end();
}
function update(now){
 const dt=Math.min((now-last)/1000,.05)*speed;last=now;
 if(!paused){stepElapsed+=dt;state.update(dt);state.apply(skeleton);skeleton.updateWorldTransform(spine.Physics.update);flash=Math.max(0,flash-dt);if(demoHold&&pulseCount<3&&stepElapsed>[.08,.43,.78][pulseCount])pulse();if(stepElapsed>=stepLimit&&queue.length)next();}
 const track=state.getCurrent(0),duration=track.animation.duration,t=track.loop?track.trackTime%duration:Math.min(track.trackTime,duration);
 $('scrub').value=Math.round(t/duration*1000);$('time').textContent=`${t.toFixed(2)} / ${duration.toFixed(2)}`;
 $('pulse').style.display=mode==='release'?'':'none';
 for(const b of document.querySelectorAll('[data-action]')){const a=b.dataset.action;b.disabled=mode==='dead'&&a!=='reset'||['pulse','finish'].includes(a)&&mode!=='release'||a==='recover'&&mode!=='down'||a==='chant'&&mode!=='idle'||['release'].includes(a)&&!['idle','chant'].includes(mode)||['cast'].includes(a)&&!['idle','chant'].includes(mode)||a==='hit'&&mode==='release';}
 draw();requestAnimationFrame(update);
}
try{
 if(!gl)throw new Error('浏览器没有可用的 WebGL 上下文。');
 const assets=new spine.AssetManager(gl,'export/');
 const [raw,atlas]=await Promise.all([fetch('export/megumin.json').then(r=>{if(!r.ok)throw Error(r.status);return r.json()}),assets.loadTextureAtlasAsync('megumin.atlas')]);
 data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw);skeleton=new spine.Skeleton(data);state=new spine.AnimationState(new spine.AnimationStateData(data));renderer=new spine.SceneRenderer(canvas,gl);
 state.addListener({event:(entry,event)=>log(`event: ${event.data.name}`)});
 for(const a of data.animations){const option=document.createElement('option');option.value=a.name;option.textContent=`${labels[a.name][0]} · ${a.name}`;$('clip').append(option);}
 $('clip').addEventListener('change',()=>{queue=[];demoHold=false;mode=phaseFor($('clip').value);play($('clip').value);});
 $('pause').addEventListener('click',()=>{paused=!paused;$('pause').textContent=paused?'播放':'暂停';});
 $('speed').addEventListener('change',()=>speed=+$('speed').value);
 $('dark').addEventListener('change',()=>$('stage').classList.toggle('dark',$('dark').checked));
 $('scrub').addEventListener('input',()=>{queue=[];demoHold=false;paused=true;$('pause').textContent='播放';skeleton.setToSetupPose();state.clearTracks();const e=state.setAnimation(0,current,false);e.trackTime=data.findAnimation(current).duration*+$('scrub').value/1000;state.apply(skeleton);skeleton.updateWorldTransform(spine.Physics.update);stepElapsed=e.trackTime;});
 document.querySelectorAll('[data-action]').forEach(b=>b.addEventListener('click',()=>command(b.dataset.action)));$('demo').addEventListener('click',demo);
 play('idle_loop');requestAnimationFrame(update);
}catch(error){$('error').style.display='block';$('error').textContent='无法载入 Spine 资源。请从本地 HTTP 预览地址打开。\n'+error.stack;console.error(error);}
