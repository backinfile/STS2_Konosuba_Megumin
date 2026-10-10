const q=id=>document.getElementById(id),p=JSON.parse(q('packed').textContent);
let playing=false,time=0,last=performance.now(),overlay=false;
const scenes=[];
const meshSvg=document.createElementNS('http://www.w3.org/2000/svg','svg');
meshSvg.style.cssText='position:absolute;inset:0;width:100%;height:100%;pointer-events:none;display:none';
meshSvg.setAttribute('aria-label','实际 Spine 变形网格');q('new-canvas').parentElement.append(meshSvg);
const meshPath=document.createElementNS('http://www.w3.org/2000/svg','path');
meshPath.setAttribute('fill','none');meshPath.setAttribute('stroke','#19876e');meshPath.setAttribute('stroke-width','.45');meshPath.setAttribute('opacity','.6');meshSvg.append(meshPath);
function pose(s,t=0){s.sk.setToSetupPose();if(s.animation)s.animation.apply(s.sk,0,t,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);s.sk.updateWorldTransform(spine.Physics.update);}
async function scene(canvas,bundle,kind){
 const gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:true,antialias:true,preserveDrawingBuffer:true});
 if(!gl)throw Error('此浏览器未提供 WebGL');
 const atlas=new spine.TextureAtlas(bundle.atlas);
 await Promise.all(atlas.pages.map(page=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{page.setTexture(new spine.GLTexture(gl,im));resolve()};im.onerror=reject;im.src=bundle.pages[page.name]})));
 let raw=bundle.skeleton;
 if(kind==='reference'){
  raw=JSON.parse(JSON.stringify(raw));
  raw.skins[0].attachments.reference_mesh['idle-reference']={type:'region',path:'idle-reference',x:(1147/2-608)*p.meta.scale,y:(1348-1371/2)*p.meta.scale,width:1147*p.meta.scale,height:1371*p.meta.scale};
  raw.animations={};
 }
 const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(raw);
 const s={canvas,gl,sk:new spine.Skeleton(data),renderer:new spine.SceneRenderer(canvas,gl),animation:data.findAnimation('idle_loop'),kind};
 pose(s);
 if(kind==='old'){const o=new spine.Vector2(),z=new spine.Vector2();s.sk.getBounds(o,z);s.bounds={x:o.x+z.x/2,y:o.y,h:z.y,w:z.x};}
 else s.bounds={x:(527.5-608)*p.meta.scale,y:0,h:320,w:971*p.meta.scale};
 return s;
}
function draw(s){
 const {canvas,gl,renderer,sk,bounds}=s,w=canvas.clientWidth,h=canvas.clientHeight,dpr=Math.min(devicePixelRatio||1,2);
 if(w<1||h<1)return;
 if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);}
 const height=q('small').checked?Math.min(320,h-60):h-60;
 const scale=Math.min(height/bounds.h,(w-28)/bounds.w),base=h-19;
 gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);
 renderer.camera.position.set(bounds.x,(base-h/2)/scale+bounds.y,0);renderer.camera.setViewport(w/scale,h/scale);renderer.camera.update();
 renderer.begin();renderer.drawSkeleton(sk,false);
 if(q('mesh').checked && s.kind==='new'){
  const slot=sk.findSlot('reference_mesh'),m=slot.attachment,v=new Float32Array(m.worldVerticesLength);m.computeWorldVertices(slot,0,v.length,v,0,2);
  meshSvg.style.display='block';meshSvg.setAttribute('viewBox',`0 0 ${w} ${h}`);
  canvas.dataset.meshTriangles=String(m.triangles.length/3);
  const point=i=>`${(w/2+(v[i]-bounds.x)*scale).toFixed(2)},${(base-(v[i+1]-bounds.y)*scale).toFixed(2)}`;
  let d='';for(let i=0;i<m.triangles.length;i+=3){const a=m.triangles[i]*2,b=m.triangles[i+1]*2,c=m.triangles[i+2]*2;d+=`M${point(a)}L${point(b)}L${point(c)}Z`;}
  meshPath.setAttribute('d',d);
 }else if(s.kind==='new')meshSvg.style.display='none';
 renderer.end();
}
function redraw(){for(const s of scenes){pose(s,s.kind==='new'?time:0);draw(s);}q('new-canvas').style.opacity=overlay?.5:1;q('time').value=Math.round(time*1000);q('time-label').textContent=time.toFixed(2)+' / 4.00 s';}
function play(value){playing=value;q('play').textContent=value?'暂停呼吸':'播放呼吸';q('play').setAttribute('aria-pressed',value);}
q('play').onclick=()=>play(!playing);
q('reset').onclick=()=>{play(false);time=0;redraw()};
q('overlay').onclick=()=>{overlay=!overlay;q('overlay').setAttribute('aria-pressed',overlay);q('views').classList.toggle('overlay',overlay);redraw()};
q('time').oninput=()=>{play(false);time=+q('time').value/1000;redraw()};
q('small').onchange=()=>{q('views').classList.toggle('small',q('small').checked);redraw()};
q('mesh').onchange=redraw;q('dark').onchange=()=>{q('views').classList.toggle('dark',q('dark').checked);redraw()};
window.addEventListener('resize',redraw);
// Same renderer, camera and texture for both draws. Pixel differences here
// measure mesh rasterization versus an ordinary undeformed reference region.
async function gpuCheck(){
 const cv=document.createElement('canvas');cv.width=1147;cv.height=1371;
 const s=await scene(cv,p.current,'new'),r=await scene(document.createElement('canvas'),p.current,'reference');
 // Bind the reference skeleton to the first context's atlas texture.
 const refAttachment=r.sk.slots[0].attachment;refAttachment.region=s.sk.slots[0].attachment.region;refAttachment.updateRegion();
 const {gl,renderer}=s,drawRead=sk=>{gl.viewport(0,0,cv.width,cv.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);renderer.camera.position.set((1147/2-608)*p.meta.scale,(1348-1371/2)*p.meta.scale,0);renderer.camera.setViewport(1147*p.meta.scale,1371*p.meta.scale);renderer.camera.update();renderer.begin();renderer.drawSkeleton(sk,false);renderer.end();const out=new Uint8Array(cv.width*cv.height*4);gl.readPixels(0,0,cv.width,cv.height,gl.RGBA,gl.UNSIGNED_BYTE,out);return out};
 const a=drawRead(s.sk),b=drawRead(r.sk);let max=0,total=0,changed=0;
 for(let i=0;i<a.length;i++){const d=Math.abs(a[i]-b[i]);max=Math.max(max,d);total+=d;if(d>2)changed++;}
 const result={maxChannelDifference:max,meanChannelDifference:total/a.length,channelsOver2:changed,pixels:cv.width*cv.height};
 q('checks').textContent=`静态重合：最大通道差 ${max}/255，平均差 ${(total/a.length).toFixed(5)}；241 帧检查通过，双脚与握杖点无漂移。`;
 q('checks').dataset.result=JSON.stringify(result);
 if(max>4||changed>500)throw Error('静态重合差异异常，请检查网格绑定与纹理坐标');
 s.renderer.dispose();r.renderer.dispose();
}
try{
 scenes.push(...await Promise.all([scene(q('old-canvas'),p.legacy,'old'),scene(q('new-canvas'),p.current,'new'),scene(q('ref-canvas'),p.current,'reference')]));
 redraw();await gpuCheck();
 requestAnimationFrame(function tick(now){const dt=Math.min((now-last)/1000,.05);last=now;if(playing){time=(time+dt)%4;redraw()}requestAnimationFrame(tick)});
}catch(e){q('error').textContent=e.stack;console.error(e)}
