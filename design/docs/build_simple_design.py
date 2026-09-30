import json
from pathlib import Path
from html import escape

root = Path(__file__).resolve().parents[1]
source = json.loads((root / 'docs/惠惠爆裂三阶段卡表.json').read_text(encoding='utf-8-sig'))
specs = [
 dict(id='time', name='等得越久，爆裂越强', old='定时咏唱', tag='时间型',
      pitch='决定现在炸，还是再撑一回合，换一发更强的爆裂。',
      phases=['花 2 能量进入预备，蓄力等级为 1。', '下一回合开始升 1 级，最高 3 级。预备中，每个敌人每轮的首次攻击总伤害减少 2。', '1 / 2 / 3 级分别造成 26 / 34 / 42 点群体伤害，随后失去预备减伤。'],
      routes=[
       ('快速爆裂', '用牌加速升级，少挨敌人的攻击。', [4,6,9], ['最直接的加速。','加速时顺便补牌。','用不要的手牌换加速。'], '进入预备 → 打出两张加速牌 → 当回合达到 3 级 → 释放 42 点群伤。', '省等待时间，但会花掉能量和手牌。'),
       ('防守蓄力', '靠防御和抽牌撑住，让爆裂自己升级。', [1,5,8], ['挡住眼前的攻击。','同时照顾下一回合。','等待升级也能补充手牌。'], '1 级时防御 → 下回合自然到 2 级并抽牌 → 再撑一轮，3 级释放。', '更省加速牌，但要承受敌人行动。'),
       ('单发重击', '把增伤和目标集中到这一发，争取解决强敌。', [7,12,10], ['满级后进一步增伤。','放弃群攻，集中打一个敌人。','没有打死时，给下一回合留保护。'], '达到 3 级 → 此刻正好 → 单点爆破 → 对一个敌人造成 (42 + 12) × 2 = 108 点伤害。', '伤害集中，但准备牌多；必须另外拿升级和防御牌。')]),
 dict(id='mana', name='投入越多，爆裂越强', old='投入蓄爆', tag='资源型',
      pitch='把能量和手牌投入这一发；投入爆裂的资源，就不能拿去做别的事。',
      phases=['花 2 能量进入预备，本次投入从 0 开始。', '每花 1 能量注能，投入 +1，通常上限 6。每轮首张技能额外给 3 格挡；回合末有剩余能量时，自动花 1 点注能。', '造成 22 + 6 × 投入的群体伤害。投入 3 是 40 点；投入 6 是 58 点。释放后清空投入。'],
      routes=[
       ('省能积攒', '先用少量牌保护自己，把剩余能量留给爆裂。', [1,3,5], ['投入起来后，防御更划算。','找下一张需要的牌。','提前覆盖下回合的防御。'], '进入预备 → 留 1 能量自动注能 → 下回合先防御，再把剩余能量注入爆裂。', '节约手牌，但慢；剩余能量也是真实成本。'),
       ('消耗换火力', '消耗不需要的手牌，尽快堆高投入。', [4,6,11], ['花 1 能量换 2 投入。','拿一张手牌当燃料。','一次处理整手牌，再补新牌。'], '专心注能得到 2 投入 → 拿这个当燃料再得 2 → 现在就能释放 46 点群伤。', '启动快，但被消耗的牌本场不能再抽到。'),
       ('高投入爆发', '先存到一定投入，再获得抽牌、防护和更高上限。', [7,10,12], ['达到 3 投入后，能一次抽 3 张。','达到 4 投入后，为释放加伤。','允许这一发继续存到 9。'], '存到 4 投入 → 不留遗憾 → 本回合释放，造成 22 + 24 + 14 = 60 点群伤。', '强牌有门槛；提高上限本身不会送你投入。')]),
 dict(id='choice', name='每一发，选择两种帮助', old='术式装填', tag='组合型',
      pitch='增伤、防御、抽牌只能选两种。选择会同时改变预备阶段和释放结果。',
      phases=['花 2 能量进入预备，获得两个空位。', '用牌或花 1 能量装入“破 / 护 / 导”。不能重复；装满后可替换。下表说明三者的效果。', '基础是 24 点群伤，再结算选中的两种效果。释放后，两个位置都清空。'],
      routes=[
       ('进攻抽牌：破 + 导', '要爆裂伤害，也要更多手牌继续操作。', [4,6,10], ['装入增伤效果。','装入抽牌效果。','把手牌留给后续回合。'], '先装破，再装导 → 预备中攻击与技能分别受益 → 释放 36 点群伤，再抽 2 张。', '没有护的减伤和格挡，需要通用防御牌。'),
       ('攻守兼顾：破 + 护', '保证爆裂伤害，同时保护预备与释放之后。', [4,5,8], ['补伤害并装入破。','获得格挡并装入护。','两种都齐时，提前安排下一回合格挡。'], '装破与护 → 双重确认 → 释放 36 点群伤，获得 12 格挡，下回合再得 9 格挡。', '没有导的抽牌，需要另外补充过牌。'),
       ('防守运转：护 + 导', '用较低的爆裂伤害，换安全和持续找牌。', [5,6,12], ['提供预备时的保护。','让预备和释放都能补牌。','把释放时的格挡推迟到下回合。'], '装护与导 → 护式转交 → 释放 24 点群伤并抽 2 张，下回合获得 12 格挡。', '牺牲破的 12 点增伤，适合更需要生存的战斗。')])
]

parts = ['''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>惠惠核心设计 · 简明版</title><style>
:root{--bg:#f5f1e8;--surface:#fffdf8;--border:#d9d1c1;--text:#2d2923;--text-dim:#645e54;--red:#a43d28;--green:#416453;--blue:#385e77}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:75px}body{margin:0;background:var(--bg);color:var(--text);font:17px/1.7 'Microsoft YaHei','PingFang SC',sans-serif}main{max-width:1120px;margin:auto;padding:48px 28px}h1,h2,h3,p{margin:0 0 16px}h1{font:700 clamp(30px,5vw,54px)/1.25 'Microsoft YaHei',sans-serif;letter-spacing:-1px}h2{font-size:30px;line-height:1.4}h3{font-size:23px}a{color:var(--red);text-underline-offset:4px}nav{position:sticky;top:0;background:var(--surface);border-bottom:1px solid var(--border);z-index:2;display:flex;justify-content:center;gap:24px;padding:12px 18px;flex-wrap:wrap}nav a{font-size:15px;text-decoration:none;font-weight:bold}section{margin:48px 0 64px}.eyebrow{color:var(--red);font-size:13px;letter-spacing:2px;font-weight:bold}.lead{font-size:20px;max-width:820px}.note{color:var(--text-dim);font-size:14px}.compare{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin:28px 0}.compare a{display:block;color:var(--text);text-decoration:none;border-top:4px solid var(--red);padding:16px 0}.compare strong{font-size:20px;display:block}.compare span{color:var(--text-dim);font-size:15px}.common{border-left:4px solid var(--green);padding:18px 24px;background:var(--surface)}.common p:last-child{margin:0}.phase{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin:24px 0}.phase div{border-top:1px solid var(--border);padding-top:12px}.phase b{color:var(--red);display:block;margin-bottom:6px}.phase p{font-size:15px}.route{border-top:1px solid var(--border);padding-top:28px;margin-top:30px}.routehead{display:flex;gap:18px;align-items:baseline;flex-wrap:wrap}.routehead h3{margin-bottom:6px}.routehead span{font-size:14px;color:var(--text-dim)}.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:18px 0}.card{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:20px;min-width:0}.meta{font-size:12px;color:var(--text-dim)}.card h4{font-size:18px;margin:8px 0 12px}.card p{font-size:16px}.purpose{border-top:1px dashed var(--border);padding-top:12px;color:var(--green);font-size:14px!important;margin:0}.example{padding:14px 18px;background:#e9eee7;font-size:15px}.cost{color:var(--text-dim);font-size:14px;margin-top:10px}.tablewrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:15px}th,td{padding:12px;text-align:left;border-bottom:1px solid var(--border);min-width:115px}th{background:#eae4d8}details{margin-top:20px}summary{cursor:pointer;font-weight:bold}footer{border-top:1px solid var(--border);padding-top:20px;color:var(--text-dim);font-size:14px}a:focus-visible,summary:focus-visible{outline:3px solid var(--blue);outline-offset:4px}p,td{overflow-wrap:break-word}@media(max-width:760px){main{padding:30px 18px}.compare,.phase,.cards{grid-template-columns:1fr}.compare{gap:0}.phase{gap:0}.card{padding:16px}nav{gap:14px}h2{font-size:26px}.routehead{gap:2px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{nav{position:static}.card{break-inside:avoid}body{background:white}main{max-width:none}}
</style></head><body><nav aria-label="方案导航"><a href="#time">① 等回合</a><a href="#mana">② 投资源</a><a href="#choice">③ 选效果</a><a href="#recommend">我的推荐</a></nav><main>
<header><p class="eyebrow">MEGUMIN / 2026.09.30 / 简明设计稿</p><h1>三种爆裂玩法，<br>每种三条构筑路线。</h1><p class="lead">先看核心怎么玩，再看该拿哪些牌。三套是<strong>备选方案，选一套做核心</strong>；同一套里的三条路线可以混搭。</p><p class="note">这是上一版的简明重述。删去审查表、统计和实现细节，保留玩法、取舍与样例牌。所有数值均为未实测的草案。</p></header>
<div class="compare"><a href="#time"><strong>① 用时间换威力</strong><span>现在炸，还是等更强？</span></a><a href="#mana"><strong>② 用资源换威力</strong><span>现在防御，还是多投一点？</span></a><a href="#choice"><strong>③ 三种效果选两种</strong><span>这一发要伤害、保护，还是手牌？</span></a></div>
<aside class="common"><p><strong>三套共用的基本流程</strong><br>正常出牌 → 花 2 能量进入预备 → 继续出牌、强化这一发 → 0 能量释放爆裂。</p><p>预备最多跨过两次敌人行动，之后自动释放。释放后，下个玩家回合少 1 能量且不能预备；该回合结束后恢复。场上余波在下回合开始造成一次 3 点群伤，然后消失。</p><p class="note">爆裂是主要输出；余波只是留下的影响。每个例子都可跨回合完成，默认每回合 3 能量。伤害示例未计算敌人格挡等修正，也未计入固定余波。</p></aside>
''']

for data, spec in zip(source, specs):
    parts.append(f'<section id="{spec["id"]}"><p class="eyebrow">{spec["tag"]} / 原方案：{spec["old"]}</p><h2>{spec["name"]}</h2><p class="lead">{spec["pitch"]}</p><div class="phase">')
    for title, content in zip(['开始前 → 开始预备','预备中','释放时'], spec['phases']):
        parts.append(f'<div><b>{title}</b><p>{content}</p></div>')
    parts.append('</div>')
    if spec['id']=='time':
        parts.append('<p class="note">原稿的“咏唱等级”在本页写成“蓄力等级”，只是便于阅读的数值标签；“咏唱”留给下方的延后触发关键字。</p>')
    if spec['id']=='choice':
        parts.append('<div class="tablewrap"><table><caption>破、护、导是设计占位名，并非原作术语。</caption><thead><tr><th>选择</th><th>预备时已经生效</th><th>释放时获得</th></tr></thead><tbody><tr><td>破：增伤</td><td>每轮首张普通攻击额外造成 3 伤害（每目标首段）</td><td>爆裂伤害 +12</td></tr><tr><td>护：防御</td><td>每个敌人每轮首次攻击总伤害减少 2</td><td>12 点格挡</td></tr><tr><td>导：抽牌</td><td>每轮首张技能结算后抽 1 张牌</td><td>抽 2 张牌</td></tr></tbody></table></div><p class="note">首次完整挡住敌人的一次攻击时，本轮可自动装入护：需有空位且尚未装护。装入效果不追溯刚打出的牌，替换也不刷新本轮次数。</p>')
    for i,(name,desc,indices,uses,example,cost) in enumerate(spec['routes'],1):
        parts.append(f'<article class="route"><div class="routehead"><h3>{i}. {name}</h3><span>本核心中的一种构筑体系</span></div><p>{desc}</p><div class="cards">')
        for index,use in zip(indices,uses):
            card=data['cards'][index-1]
            effect=card['effect'].replace('咏唱','蓄力等级')
            parts.append(f'<div class="card"><div class="meta">{card["cost"]} 能量 · {card["type"]}</div><h4>{escape(card["name"])}</h4><p>{escape(effect)}</p><p class="purpose">作用：{use}</p></div>')
        parts.append(f'</div><div class="example"><strong>怎么玩：</strong>{example}</div><p class="cost"><strong>取舍：</strong>{cost}</p></article>')
    parts.append('</section>')

parts.append('''<section id="keyword"><h2>“咏唱”放在哪里？</h2><p>它是可以加入上述任一方案的<strong>卡牌关键字</strong>，不是第四套核心。</p><aside class="common"><p><strong>咏唱：获得 6 点格挡。</strong><br>已经在预备中：立刻获得。<br>还没进入预备：记下这份效果，下次进入预备时获得一次。</p></aside><p class="note">同一效果只触发一次；多份效果按登记顺序触发，战斗结束清空。这里展示的是新增关键字用法，上面 27 个样例牌展示位沿用原卡表效果，没有偷偷改成延后触发。</p><p>可以用达克妮丝的形象承载格挡、和真的形象承载抽牌、阿库娅的形象承载恢复。队友帮助惠惠准备和善后，主要输出仍交给爆裂。</p></section>
<section id="recommend"><h2>我推荐先做①，再考虑②。</h2><p class="lead"><strong>①最容易看懂，也最容易表现惠惠“准备一发大爆裂”的感觉。</strong>快速爆裂、防守蓄力、单发重击，三条路线的区别能直接从出牌方式看出来。</p><p>如果你更喜欢每回合精打细算能量与手牌，选②。③更擅长临场组合，但要同时记住三种预备效果和三种释放效果，理解负担最大，而且占位名还需要重新包装。</p><p class="note">这是设计判断，不是测试结论。三条路线目前是构筑草案，还不能算三套已经验证可独立通关的牌组。</p>
<details><summary>少量共同读牌规则</summary><ul><li>“消耗”：这张牌本场战斗不再进入正常抽牌循环；“保留”：回合结束仍留在手中。</li><li>只有准备效果的牌，需要先进入预备。兼有格挡、攻击、抽牌的牌，预备外仍可使用其普通部分。</li><li>本次增伤、投入、装入效果在释放后清空；普通能力牌按其文本持续生效。</li><li>“每轮”指你的回合开始到下个回合开始前。等级、投入和术式等只属于各自方案，不能混装。</li><li>自动释放发生在跨过两次敌人行动后的玩家回合开始；先处理该方案自然升级，再释放，之后正常刷新能量与抽牌。脱力与余波在释放后的下个玩家回合生效。</li><li>同名的单次爆裂修饰默认不叠加，文中连招均使用不同修饰。</li></ul></details></section>
<footer>依据：<a href="惠惠爆裂三阶段设计.html">原完整设计</a> · <a href="参考资料/原作名词与命名素材.md">原作名词资料</a><br>样例牌效果来自现有卡表；牌名多为临时设计名，不代表原作技能名称。规则与数值均为 Mod 原创草案。<br>3 个备选核心 · 9 条构筑路线 · 每条 3 张样例牌（不同路线可共用同一张牌）。</footer></main></body></html>''')

output = root / '惠惠核心设计简明版.html'
output.write_text('\n'.join(parts), encoding='utf-8')
print(output)
