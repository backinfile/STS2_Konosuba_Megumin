"""Visual audit: actual exported Spine frames and local official references.

This writes an observation page only. It never changes source art or animations.
"""
from pathlib import Path
import base64,json,html
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'actions-v3'
groups=[
 ('cast','普通施放', 'cast_short', [0,.12,.28,.52]),
 ('chant','进入吟唱', 'chant_enter', [.18,.35,.57,.7]),
 ('attack','普通攻击', 'attack_short', [0,.15,.28,.50]),
 ('explosion','爆裂释放', 'explosion_release', [0,.28,.4,.6]),
 ('hit','站立受击', 'hit', [0,.07,.15,.4]),
 ('fall','脱力倒地', 'relaxed_fall', [0,.38,.75,1.05]),
 ('rise','起身恢复', 'get_up', [0,.56,.85,1.3]),
 ('death','死亡', 'dead', [0,.47,.8,1.1]),
 ('secondary','衍生动作', None, [('chant_cancel',.12),('chant_ack',.25),('hit_chant',.1),('hit_down',.15)]),
 ('compare','脱力与死亡对比',None,[('relaxed_loop',0),('dead',1.1),('dead_from_down',.35),('relaxed_loop',1.5)])
]
bundle={'skeleton':json.loads((OUT/'export/megumin.json').read_text(encoding='utf-8')),
        'atlas':(OUT/'export/megumin.atlas').read_text(encoding='utf-8'),
        'pages':{f.name:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode('ascii') for f in (OUT/'export').glob('*.png')}}
audit=json.loads((OUT/'action-audit-findings.json').read_text(encoding='utf-8'))
refroot=ROOT.parent/'isekai-quartet-references-20261009'
catalog=json.loads((refroot/'catalog.json').read_text(encoding='utf-8'))
refs={a['id']:a for a in catalog['items'] if a['id'] in ['A02','A05','A07']}
bundle['references']={k:'data:image/jpeg;base64,'+base64.b64encode((refroot/v['file']).read_bytes()).decode('ascii') for k,v in refs.items()}
panels=[]
for id,title,clip,times in groups:
    cells=[]
    for i,entry in enumerate(times):
        name,t=(clip,entry) if clip else entry
        cells.append(f'<figure><button class="frame" data-clip="{name}" data-time="{t}" aria-label="放大 {name} {t:.2f} 秒"><img alt="{name} {t:.2f} 秒运行时画面"></button><figcaption>{name} · {t:.2f}s</figcaption></figure>')
    finding=audit['groups'][id]
    reference=''
    if finding.get('reference'):
        ref=refs[finding['reference']]
        reference=f'<details class="reference"><summary>查看依据：{ref["id"]} {ref["title"]}</summary><img data-reference="{ref["id"]}" alt="{ref["title"]}"><p>{ref["limitation"]} 此处比较姿态结构，不把剧照取景当作游戏机位。<a href="{ref["source_page"]}" target="_blank" rel="noreferrer">官方出处</a></p></details>'
    analysis=f'<div class="analysis"><p><b>看到的问题</b>{finding["observed"]}</p><p><b>根因</b>{finding["cause"]}</p><p><b>修正方向</b>{finding["change"]}</p>{reference}</div>'
    panels.append(f'<section id="{id}"><h2>{title}<small>{finding["verdict"]}</small></h2><div class="frames">'+''.join(cells)+'</div>'+analysis+'</section>')
runtime=(ROOT/'vendor/spine-webgl-4.2.95.min.js').read_text(encoding='utf-8')
text='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>惠惠 · 动作逐帧审查</title><style>
:root{--bg:#f5f0e7;--surface:#fffcf6;--border:#d7cbbf;--text:#322b28;--text-dim:#786b64;--accent:#a44032;--green:#547061;--amber:#9d7736}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.7 'Microsoft YaHei',sans-serif}main{max-width:1280px;padding:24px;margin:auto}h1{font-size:30px;line-height:1.35;max-width:950px}h2{font-size:21px;margin:0 0 14px}h2 small{display:block;font-size:13px;color:#a44032;font-weight:400;margin-top:5px}section{padding:28px 0;border-top:1px solid #d7cbbf;scroll-margin-top:60px}.frames{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));background:#fffcf6;border:1px solid #d7cbbf}figure{margin:0;min-width:0;border-right:1px solid #d7cbbf}.frame{display:block;width:100%;padding:0;border:0;background:transparent;cursor:zoom-in}.frame img{display:block;width:100%;aspect-ratio:340/365;object-fit:contain}figcaption{font:11px Consolas,monospace;color:#786b64;padding:9px 12px;border-top:1px solid #e3d9d0;overflow-wrap:anywhere}nav{position:sticky;top:0;background:#f5f0e7ee;backdrop-filter:blur(8px);padding:10px 0;display:flex;gap:15px;flex-wrap:wrap;z-index:2;font-size:12px}a{color:#a44032}dialog{width:min(840px,95vw);max-height:96vh;overflow:auto;border:1px solid #bbaa9c;padding:15px;background:#fffcf6}dialog::backdrop{background:#272128bb}dialog canvas{display:block;width:100%;height:auto}dialog header{display:flex;justify-content:space-between}button{font:inherit}#error{color:#a44032;white-space:pre-wrap}.obs{color:#74665e}p{max-width:960px}.analysis{padding:12px 0 0;display:grid;grid-template-columns:1.2fr 1fr 1.2fr;gap:24px}.analysis p{margin:7px 0}.analysis b{display:block;font-size:12px;color:#a44032;margin-bottom:5px}.reference{grid-column:1/-1;background:#eee7dc;padding:12px 16px}.reference img{display:block;width:min(760px,100%);height:auto;margin:14px 0}.reference p{font-size:12px;color:#786b64}summary{cursor:pointer;color:#6f5144}.intro{max-width:970px;font-size:16px}.callout{border-left:3px solid #a44032;padding:3px 16px;margin:18px 0 24px;background:#eee5d9}.topproof{grid-template-columns:repeat(3,minmax(0,1fr));margin-top:20px}.topproof figcaption{font-family:'Microsoft YaHei',sans-serif;font-size:13px;color:#322b28;line-height:1.6}.topproof .frame img{aspect-ratio:340/305;object-fit:contain}.repair{display:grid;grid-template-columns:1fr 1fr;gap:40px}.repair li{margin:10px 0;max-width:550px}footer{padding:20px 0;color:#786b64;font-size:12px;border-top:1px solid #d7cbbf}.technical{padding:15px 0;color:#786b64;font-size:12px} @media(max-width:800px){.analysis{grid-template-columns:1fr;gap:0}.repair{grid-template-columns:1fr;gap:10px}}@media(max-width:600px){.frames{grid-template-columns:repeat(2,minmax(0,1fr))}.topproof{grid-template-columns:1fr}main{padding:16px}h1{font-size:25px}}
</style><main><p style="color:#a44032;font:11px Consolas,monospace;letter-spacing:.15em">MEGUMIN / ACTION AUDIT / 2026.10.09</p><h1>Idle 成立，其他动作的关键姿势还没有成立。</h1><p class="intro">__CONCLUSION__</p><div class="callout"><p><b>保留：</b>用户认可的 idle、人物比例与美术方向；持续吟唱、一次释放、多段伤害保持的状态用途。<br><b>重做：</b>法杖路径与遮挡、手臂与握姿、坐倒/躺倒/起身的视角与支撑。先完成清晰关键姿势，再扩展衍生片段。</p></div><div class="frames topproof"><figure><button class="frame" data-clip="attack_short" data-time=".28" aria-label="放大主要问题：攻击"><img alt="命中帧的杖头消失在头帽后面"></button><figcaption><b>攻击 · 0.28s</b><br>命中帧杖头被遮没，杖尖从帽上冒出。</figcaption></figure><figure><button class="frame" data-clip="chant_loop" data-time="0" aria-label="放大主要问题：吟唱"><img alt="吟唱双手挤在腰前"></button><figcaption><b>吟唱 · 保持帧</b><br>双手挤在腰前；肩胸、脸和脚位仍像待机。</figcaption></figure><figure><button class="frame" data-clip="get_up" data-time=".65" aria-label="放大主要问题：起身"><img alt="坐姿折腿且左手悬空"></button><figcaption><b>起身 · 0.65s</b><br>腿部折叠，左手握点距地约 74px，未形成支撑。</figcaption></figure></div><nav>__NAV__<a href="#repair">返工顺序</a></nav><p class="obs">下方 40 个时刻从当前 Spine 导出数据直接渲染，采用统一镜头；点击任一帧可等比放大。没有生成“更好的示意图”替代现有结果。</p><div id="error"></div>__PANELS__<section id="repair"><h2>返工顺序与验收</h2><div class="repair"><div><h3>先姿势，后过渡</h3><ol>__ORDER__</ol></div><div><h3>验收看画面</h3><ul>__ACCEPT__</ul></div></div><details class="technical"><summary>查看实现层的证据与限制</summary><p>staff 在 head 之前绘制，因此法杖始终位于头部后方；所有动作都没有 draw-order 时间线；帽、发没有独立骨骼。起身中段直接复用 SIT。披风接地对低于 y=0.45 的顶点作向上位移，最大约 31.77px；它只证明未穿地，不能证明布料自然铺开。脱力/死亡分别使用 77°/82° 骨盆旋转、同一表情附件。</p><p>源文件：tools/build_actions_v3.py（分件与关键姿势）、tools/bake_floor_v3.mjs（接地变形）、actions-v3/preview.js（播放队列）。测量值来自当前导出数据，角色名义高度为 320px。手的握点不等于掌缘，但约 74px 的高度足以排除这里存在撑地。</p><p>此前 2,756 个采样检查验证了有限坐标、握点和片段端点等数值条件，没有验证剪影、解剖、表情、受力或动态前后遮挡。因此不应把检查通过写成视觉完成。</p></details></section><footer>本轮仅分析并制作证据页；未修改角色图片或导出的动画。官方剧照提供姿态参考，不提供中间帧和动作时长。纹理清理与 mipmap 保留为独立事项，不将采样问题与关节变形混为一谈。</footer></main><dialog id="zoom"><header><b id="zoom-title"></b><button id="close">关闭</button></header><canvas id="zoom-canvas" aria-label="放大动作帧"></canvas></dialog><script id="packed" type="application/json">__DATA__</script><script>__RUNTIME__</script><script type="module">
const p=JSON.parse(document.getElementById('packed').textContent),cv=document.createElement('canvas');cv.width=680;cv.height=730;
try{
const gl=cv.getContext('webgl',{alpha:true,premultipliedAlpha:true,antialias:true,preserveDrawingBuffer:true}),atlas=new spine.TextureAtlas(p.atlas);
await Promise.all(atlas.pages.map(page=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{page.setTexture(new spine.GLTexture(gl,im));resolve()};im.onerror=reject;im.src=p.pages[page.name]})));
const data=new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(p.skeleton),renderer=new spine.SceneRenderer(cv,gl);
function draw(name,t,large=false,overview=false){
cv.width=large?1000:680;cv.height=large?800:overview?610:730;const sk=new spine.Skeleton(data);data.findAnimation(name).apply(sk,0,t,false,[],1,spine.MixBlend.setup,spine.MixDirection.mixIn);sk.updateWorldTransform(spine.Physics.update);
gl.viewport(0,0,cv.width,cv.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);
const vw=overview?420:500,vh=vw*cv.height/cv.width;renderer.camera.setViewport(vw,vh);renderer.camera.position.set(-28,vh/2-24,0);renderer.camera.update();renderer.begin();renderer.line(-300,0,300,0,new spine.Color(.82,.76,.70,1));renderer.drawSkeleton(sk,false);renderer.end();return cv.toDataURL('image/png');}
for(const b of document.querySelectorAll('.frame')){const name=b.dataset.clip,t=+b.dataset.time;b.querySelector('img').src=draw(name,t,false,!!b.closest('.topproof'));b.addEventListener('click',()=>{const im=new Image();im.onload=()=>{const c=document.getElementById('zoom-canvas');c.width=im.width;c.height=im.height;const ctx=c.getContext('2d');ctx.clearRect(0,0,c.width,c.height);ctx.drawImage(im,0,0);};im.src=draw(name,t,true);document.getElementById('zoom-title').textContent=name+' · '+t.toFixed(2)+'s';document.getElementById('zoom').showModal()});}
document.getElementById('close').onclick=()=>document.getElementById('zoom').close();
for(const im of document.querySelectorAll('[data-reference]'))im.src=p.references[im.dataset.reference];
}catch(e){document.getElementById('error').textContent=e.stack;console.error(e)}
</script></html>'''
text=text.replace('__CONCLUSION__',audit['conclusion']).replace('__ORDER__',''.join(f'<li>{a}</li>' for a in audit['review_order'])).replace('__ACCEPT__',''.join(f'<li>{a}</li>' for a in audit['acceptance'])).replace('__NAV__',''.join(f'<a href="#{id}">{title}</a>' for id,title,_,_ in groups)).replace('__PANELS__',''.join(panels)).replace('__DATA__',json.dumps(bundle,separators=(',',':')).replace('</','<\\/')).replace('__RUNTIME__',runtime)
(OUT/'action-audit.html').write_text(text,encoding='utf-8')
copy=Path.home()/'.agent/diagrams/megumin-actions-v3-audit.html'
copy.parent.mkdir(parents=True,exist_ok=True)
copy.write_text(text,encoding='utf-8')
print('Wrote action-audit.html')
