from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
env={'__file__':str(ROOT/'tools/gallery_actions_v5.py')}
exec((ROOT/'tools/gallery_actions_v5.py').read_text(encoding='utf-8'),env)
groups=[
 ('待机、手势与受击',[('待机','idle_loop',0),('张掌预备','cast_short',.12),('张掌施法','cast_short',.28),('收手','cast_short',.5),('受击起点','hit',.035),('受击冲量','hit',.07),('帽发跟随','hit',.13),('受击回收','hit',.27),('恢复待机','hit',.44)]),
 ('吟唱与中断',[('抬杖','chant_enter',.2),('抬杖经过','chant_enter',.4),('转身送杖','chant_enter',.75),('进入完成','chant_enter',1.05),('侧身单手预备','chant_loop',0),('吟唱回应','chant_ack',.25),('吟唱受击','hit_chant',.07),('受击缓冲','hit_chant',.15),('取消收杖','chant_cancel',.62)]),
 ('普通攻击与爆裂',[('普通预备','attack_short',.2),('普通出招','attack_short',.52),('普通收回','attack_short',.77),('爆裂蓄力','explosion_release',.15),('爆裂收蓄','explosion_release',.3),('爆裂释放','explosion_release',.46),('爆裂保持','explosion_hold',0),('卸力收杖','explosion_exit',.58),('卸力完成','explosion_exit',1.1)]),
 ('脱力与倒地',[('腿软','relaxed_fall',.1),('坐倒前','relaxed_fall',.3),('坐倒','relaxed_fall',.36),('向后倒','relaxed_fall',.55),('松杖','relaxed_fall',.7),('躺下','relaxed_fall',.9),('倒地完成','relaxed_fall',1.2),('倒地保持','relaxed_loop',0),('倒地受击','hit_down',.1)]),
 ('撑地起身',[('倒地起点','get_up',0),('手掌着地','get_up',.46),('掌心保持','get_up',.65),('收腿承重','get_up',.86),('抬手','get_up',1.07),('重新握杖','get_up',1.25),('弯腰承重','get_up',1.55),('站起','get_up',1.85),('恢复原姿','get_up',2.35)]),
 ('死亡保持',[('失力','dead',.35),('坐倒','dead',.63),('侧倒','dead',.85),('蜷腿','dead',1.05),('落定前','dead',1.25),('死亡落定','dead',1.5),('倒地后死亡 1','dead_from_down',.1),('倒地后死亡 2','dead_from_down',.25),('倒地后死亡 3','dead_from_down',.45)])
]
html=env['html'].replace('惠惠 · 九帧动作对照','惠惠 · 54 帧动作复查').replace('同一套美术，九个动作时刻。','54 个时刻，检查动作中间过程。')
html=html.replace('<div class="sheet">','<label for="reviewGroup">动作组 </label><select id="reviewGroup" style="font:inherit;margin:0 0 18px;padding:6px 12px" aria-label="审查动作组">'+''.join(f'<option value="{i}">{name}</option>' for i,(name,_) in enumerate(groups))+'</select><div class="sheet">')
html=html.replace("try{const gl=",'const groups='+json.dumps(groups,ensure_ascii=False,separators=(',',':'))+';\ntry{const gl=')
html=html.replace("draw();addEventListener('resize',draw);","function choose(){p.poses=groups[+document.getElementById('reviewGroup').value][1];document.querySelector('.labels').innerHTML=p.poses.map(([a,b,c])=>`<div class=\"label\">${a}<small>${b} / ${c.toFixed(2)}s</small></div>`).join('');draw()}document.getElementById('reviewGroup').addEventListener('change',choose);choose();addEventListener('resize',draw);")
html=html.replace("renderer.begin();renderer.drawSkeleton", "renderer.begin();renderer.line(-300,0,300,0,new spine.Color(.83,.79,.74,1));renderer.drawSkeleton")
(ROOT/'actions-v5/review-frames.html').write_text(html,encoding='utf-8')
print('Review: 54 real Spine frames / six groups')

