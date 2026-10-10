"""Build a local video index and zip from verified native recordings."""
from pathlib import Path
import html,json,zipfile,os
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'art/megumin-quartet-spine'/os.environ.get('MEGUMIN_ACTIONS','actions-v9')
OUT=ART/'verification/recordings'
VERSION=ART.name.split('-')[-1]
NAMES={'full-sequence':'完整动作链：吟唱 → 释放 → 脱力 → 起身','normal-combat':'正常战斗：出牌、受击、胜利与奖励',
       'idle_loop':'待机','chant_enter':'进入吟唱','chant_loop':'持续吟唱','chant_cancel':'取消吟唱','chant_ack':'吟唱确认',
       'explosion_release':'爆裂释放','explosion_hold':'释放保持','explosion_exit':'释放后卸力','relaxed_fall':'脱力趴地',
       'relaxed_loop':'趴地休息','get_up':'撑地起身','hit':'站立受击','hit_chant':'吟唱受击','hit_down':'倒地受击',
       'dead':'站立死亡','dead_from_down':'倒地死亡','dead_loop':'死亡保持','attack_short':'普通攻击','cast_short':'普通施放'}
report=json.loads((OUT/'verification.json').read_text())
assert report['passed'] and len(report['videos'])==len(NAMES)
rows=[]
for name,label in NAMES.items():
    path=OUT/(name+'.mp4');assert path.is_file()
    meta=json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    rows.append({'file':path.name,'label':label,'seconds':round(meta['capture']['video_duration_seconds'],2),
                 'capture_fps':round(meta['capture']['capture_fps'],2),'repeated_frames':meta['capture']['frames_repeated']})
buttons=''.join(f'<button data-file="{r["file"]}" data-label="{html.escape(r["label"])}">{html.escape(r["label"])}<span>{r["seconds"]:.2f} 秒</span></button>' for r in rows)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>惠惠 v8 · 游戏内原速录像</title>
<style>*{box-sizing:border-box}body{margin:0;background:#eeeae3;color:#2b2926;font:16px/1.6 system-ui,sans-serif}main{max-width:1320px;margin:32px auto;padding:0 24px}h1{font-size:28px;margin-bottom:8px}p{max-width:1000px;color:#61594f}video{width:100%;aspect-ratio:16/9;background:#191b17;display:block}h2{font-size:19px;margin:20px 0 10px}nav{display:grid;grid-template-columns:repeat(auto-fit,minmax(275px,1fr));gap:1px;background:#ccc4b9;border:1px solid #ccc4b9}button{border:0;background:#f8f5f0;color:inherit;padding:14px 16px;text-align:left;cursor:pointer;font:inherit}button:hover,button[aria-current=true]{background:#e7d5c6}button span{display:block;font-size:13px;color:#796f61}a{color:#8f3429}.meta{font-size:14px}footer{margin:28px 0;color:#756b5f;font-size:14px}</style>
<main><h1>惠惠 v8 · 游戏内原速录像</h1><p>游戏视口实时录制，1280 × 720，30 fps 编码，1 倍速，无声。共 19 个单项动作、1 段完整动作链、1 场正常战斗。</p>
<p class="meta">单项动作与完整动作链通过测试接口触发，保留前后姿势；正常战斗由实际出牌和回合流程触发。正式爆裂玩法尚未接入。</p>
<video id="video" controls preload="metadata" src="full-sequence.mp4" poster="poster.jpg"></video><h2 id="title">完整动作链：吟唱 → 释放 → 脱力 → 起身</h2>
<p><a id="download" href="full-sequence.mp4" download>下载当前录像</a>　·　<a href="megumin-v8-native-recordings.zip" download>下载全部录像</a></p><nav>__BUTTONS__</nav>
<footer>录像未改变动画速度，未逐帧摆拍或插帧。采集帧率、重复帧数量、动作时间线与核对结果保存在同目录 JSON 中。</footer></main>
<script>const v=document.querySelector('#video');for(const b of document.querySelectorAll('button'))b.onclick=()=>{for(const other of document.querySelectorAll('button'))other.removeAttribute('aria-current');b.setAttribute('aria-current','true');v.src=b.dataset.file;v.removeAttribute('poster');document.querySelector('#title').textContent=b.dataset.label;document.querySelector('#download').href=b.dataset.file;v.play();v.scrollIntoView({behavior:'smooth',block:'start'});};</script></html>'''
page=page.replace('__BUTTONS__',buttons).replace('v8',VERSION)
if (OUT/'comparison.html').exists():page=page.replace('<nav>','<p><a href="comparison.html">查看 v8 / v9 原速并排对照与轨迹图</a></p><nav>')
(OUT/'index.html').write_text(page,encoding='utf-8')
(OUT/'catalog.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
readme=['# 惠惠 v8 游戏内原速录像','','打开 `index.html` 逐项查看。全部为游戏原生画面的实时录像，1 倍速、1280×720、30 FPS 编码，无声。',
        '动作展示由测试接口触发；`normal-combat.mp4` 使用实际出牌与回合操作，没有在战斗中手动调用动画。正式爆裂玩法仍未接入。','',
        '| 录像 | 时长 | 实测采集 FPS |','|---|---:|---:|']
readme += [f'| [{r["label"]}]({r["file"]}) | {r["seconds"]:.2f} 秒 | {r["capture_fps"]:.2f} |' for r in rows]
(OUT/'README.md').write_text(('\n'.join(readme)+'\n').replace('v8',VERSION),encoding='utf-8')
archive=OUT/f'megumin-{VERSION}-native-recordings.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.iterdir()):
        if p.suffix in ('.mp4','.json','.html','.md','.jpg','.png'):z.write(p,p.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('Packaged',len(rows),'videos:',archive,archive.stat().st_size,'bytes')
