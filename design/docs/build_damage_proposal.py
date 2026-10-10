"""Render the separate, unapproved damage-archetype proposal; never edit the fixed core."""
from pathlib import Path
from html import escape
import hashlib
import json
from design_status import with_design_notice

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / '惠惠伤害体系候选.json').read_text(encoding='utf-8'))
CORE = HERE / '惠惠核心机制候选.json'


def esc(value):
    return escape(str(value), quote=True)


def render():
    d = DATA
    cards = ''.join(f'''<article class="spell" id="card-{c['id']}">
      <div class="spell-meta"><span>{esc(c['type'])} · {esc(c['rarity'])}</span><b>{c['cost']}费</b></div>
      <h3>{esc(c['name'])}</h3><span class="role">{esc(c['role'])}</span>
      <p class="card-text">{esc(c['text'])}</p><p>{esc(c['reason'])}</p>
      <p class="muted">取舍：{esc(c['tradeoff'])}</p>
      <small>{'首轮验证牌' if c['prototype'] else '第二轮扩展牌；不依赖它启动'}</small></article>'''
      for c in d['cards'])
    refs = ''.join(f'<tr><th scope="row">{esc(r["reference"])}</th><td>{esc(r["learn"])}</td><td>{esc(r["adapt"])}</td></tr>' for r in d['references'])
    steps = ''.join(f'<tr><th scope="row">{esc(s["play"])}</th><td>{s["energy"]}</td><td>{s["N"]}</td><td>{s["P"]}</td><td>{esc(s["result"])}</td></tr>' for s in d['opening']['steps'])
    turns = ''.join(f'''<article class="turn"><div class="turn-head"><b>回合 {t['turn']}</b><strong>{t['damage']}<small> 群伤</small></strong></div>
      <p><b>指定手牌：</b>{esc(t['hand'])}</p><p>{esc(t['play'])}</p>
      <p class="equation">{t['N']} 出牌 + {t['P_at_damage']} 威力 + {t['B']} 本次加伤 = {t['damage']}</p>
      <p>{esc(t['other'])}</p><p class="muted">结算后威力：{t['P_after']}（战斗继续时）。</p></article>''' for t in d['three_turns']['turns'])
    checks = ''.join(f'<li>{esc(x)}</li>' for x in d['acceptance'])
    actual_hash = hashlib.sha256(CORE.read_bytes()).hexdigest()
    source_note = ('已核对：原核心文件内容未改。' if actual_hash == d['fixed_core_sha256'] else '原核心文件在本候选建立后发生变化，需重新检查兼容性。')
    template = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>惠惠伤害体系候选 · 爆裂强化</title>
<style>
:root{--bg:#f7f1e6;--surface:#fffcf6;--border:#d7c7af;--text:#302820;--text-dim:#716454;--red:#96372c;--gold:#986419;--sage:#476752;--dark:#362822}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--text);font-family:"Microsoft YaHei UI","PingFang SC",sans-serif;line-height:1.8;font-size:16px}a{color:var(--red);text-underline-offset:4px}button,input,select{font:inherit}button,select{cursor:pointer}button:focus-visible,input:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid var(--gold);outline-offset:4px}.wrap{max-width:1410px;margin:auto;padding:32px 38px 70px;display:grid;grid-template-columns:155px minmax(0,1fr);gap:42px}.toc{position:sticky;top:25px;align-self:start}.toc strong{display:block;font-size:12px;letter-spacing:.1em;margin-bottom:14px;color:var(--text-dim)}.toc a{display:block;padding:9px 0;border-bottom:1px solid var(--border);text-decoration:none;font-size:14px}.toc .back{margin-top:30px;font-size:12px}.main{min-width:0}header{padding:17px 0 36px;border-bottom:3px solid var(--dark)}.eyebrow{font-family:Consolas,monospace;letter-spacing:.14em;color:var(--red);font-size:12px}h1,h2,h3{font-family:"Noto Serif SC","Source Han Serif SC",SimSun,serif;line-height:1.35}h1{font-size:clamp(35px,4.4vw,58px);margin:20px 0}h1 em{color:var(--red);font-style:normal}h2{font-size:29px;margin:0 0 18px}h3{font-size:23px;margin:7px 0 10px}p{margin:10px 0}.lead{font-size:19px;max-width:850px}.status{display:inline-block;font-size:12px;border:1px solid var(--red);color:var(--red);padding:3px 9px;margin-top:14px}.section{padding:38px 0;scroll-margin-top:25px;border-bottom:1px solid var(--border)}.section-label{font-family:Consolas,monospace;font-size:12px;color:var(--gold);letter-spacing:.08em;display:block;margin-bottom:8px}.muted,small{color:var(--text-dim)}.callout{border-left:4px solid var(--red);background:#eee4d4;padding:17px 22px;margin:20px 0}.callout p{margin:0}.formula{background:var(--dark);color:#fff6e6;padding:27px 30px;margin:23px 0}.formula strong{font:clamp(29px,4vw,44px)/1.4 Consolas,monospace}.formula p{color:#e4d3ba}.two{display:grid;grid-template-columns:1fr 1fr;gap:27px}.two>*{min-width:0}.point{padding:17px 0;border-top:2px solid var(--border)}.point h3{font-size:20px}.table-wrap{overflow-x:auto;border:1px solid var(--border);margin:20px 0}table{border-collapse:collapse;width:100%;font-size:14px;background:var(--surface)}th,td{text-align:left;padding:15px 16px;border-bottom:1px solid var(--border);vertical-align:top;overflow-wrap:break-word}thead{background:#ece2d2}th{font-weight:600}table caption{text-align:left;padding:12px 16px;background:#f0e6d5;color:var(--text-dim);font-size:13px}.references th{width:22%}.cards{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:25px}.spell{min-width:0;background:var(--surface);border:1px solid var(--border);padding:22px 25px;border-top:4px solid var(--red)}.spell:last-child{grid-column:1/-1}.spell-meta{display:flex;justify-content:space-between;gap:16px;font-size:12px;color:var(--text-dim)}.spell-meta b{font:24px/1.4 Consolas,monospace;color:var(--red)}.role{font-size:12px;color:var(--gold)}.card-text{padding:15px 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border);font-weight:600}.spell p{font-size:14px}.spell small{font-size:12px}.controls{display:grid;grid-template-columns:1fr 1fr;gap:23px}label{display:block;font-size:14px}input[type=range]{display:block;width:100%;accent-color:var(--red);margin-top:12px}select{width:100%;padding:10px;background:var(--surface);border:1px solid var(--border);border-radius:0;color:var(--text)}.number{font-family:Consolas,monospace;color:var(--red);font-weight:bold}output{display:block}.calc{padding:26px;background:var(--surface);border:1px solid var(--border)}.result{margin-top:22px;display:grid;grid-template-columns:1.4fr 1fr;gap:20px;background:#ece3d4;padding:18px 22px}.result strong{display:block;font:38px/1.5 Consolas,monospace;color:var(--red)}.result span{font-size:13px;color:var(--text-dim)}.checkbox{margin-top:20px;display:flex;gap:9px;align-items:baseline}.checkbox input{accent-color:var(--red)}.turn{padding:18px 0 24px;border-bottom:1px dashed var(--border)}.turn-head{display:flex;align-items:center;justify-content:space-between;gap:20px}.turn-head>b{color:var(--red)}.turn-head strong{font:32px/1.4 Consolas,monospace;color:var(--red)}.turn-head small{font:13px/1.4 "Microsoft YaHei UI",sans-serif}.turn p{font-size:14px}.equation{font-family:Consolas,"Microsoft YaHei UI",monospace;background:#eee4d4;padding:9px 14px}details{border:1px solid var(--border);padding:16px 20px;margin-top:22px;background:var(--surface)}summary{cursor:pointer;font-weight:600}li{margin:10px 0}ul,ol{padding-left:23px}footer{padding:25px 0;font-size:12px;color:var(--text-dim)}.source-links{display:flex;flex-wrap:wrap;gap:10px 24px}button{padding:6px 14px;border:1px solid var(--border);background:transparent;color:var(--text);margin-top:13px}.narrow{max-width:820px}
@media(max-width:1000px){.wrap{grid-template-columns:1fr;gap:12px;padding:0 24px 45px}.toc{z-index:2;top:0;display:flex;gap:20px;overflow:auto;white-space:nowrap;background:var(--bg);padding:10px 0;border-bottom:1px solid var(--border)}.toc strong,.toc .back{display:none}.toc a{border:0;padding:3px 0;font-size:12px}.section{scroll-margin-top:64px}}
@media(max-width:640px){.wrap{padding:0 18px 35px}.two,.cards,.controls,.result{grid-template-columns:1fr}.cards .spell:last-child{grid-column:auto}h1{font-size:37px}h2{font-size:25px}.lead{font-size:17px}.formula{padding:20px}.spell{padding:20px}.calc{padding:18px}.table-wrap table{min-width:640px}.result{gap:5px}.section{padding:29px 0}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
</style></head><body><div class="wrap">
<nav class="toc" aria-label="章节"><strong>MEGUMIN / DESIGN 01</strong><a href="#proposal">推荐方向</a><a href="#rules">伤害规则</a><a href="#cards">五张配套牌</a><a href="#calculator">伤害试算</a><a href="#turns">实际出牌</a><a href="#review">取舍与验证</a><a class="back" href="原版五职业与Karen伤害体系分析.html">← 六职业伤害参考</a></nav>
<main class="main"><header><span class="eyebrow">DAMAGE ARCHETYPE · 2026.10.09</span><h1>每一次爆裂，<br><em>都有值得投资的威力。</em></h1><p class="lead">@@RECOMMENDATION@@</p><span class="status">纸面候选 · 未采纳 · 数值用于比较，不代表平衡结论</span></header>
<section class="section" id="proposal"><span class="section-label">01 / OFFENSIVE RESPONSIBILITY</span><h2>首选：爆裂强化</h2><div class="narrow"><p>现有爆裂已经有一个清晰的伤害载体，但原始收益只有“吟唱后每打1张牌，爆裂加1伤”。增加抽牌、能量和积蓄会让它更顺，却仍然只是在扩大出牌数量。可以给它补上一组直接提高爆裂伤害的牌。</p><p><b>核心投资 → 爆裂威力增加 → 后续爆裂更强。</b>即使积蓄、抽牌和出牌次数都不变，拿到这组牌仍然能改善杀敌。这正是它承担伤害职责的理由。</p></div>
<div class="two"><div class="point"><h3>角色体验</h3><p>反复使用同一个招牌攻击，为它投资，再决定何时把后劲集中到最后一发。对应惠惠的练习、专精与孤注一掷；战斗内数值规则是原创Mod设计。</p></div><div class="point"><h3>构筑结构</h3><p>普通牌给直接强化和当次爆发；能力牌给长战斗成长；少量高阶牌负责放大与收尾。成长轴无需依赖稀有牌才成立。</p></div></div>
<div class="table-wrap"><table class="references"><caption>从已经核对的伤害主轴中借结构</caption><thead><tr><th>参考</th><th>借鉴的特点</th><th>惠惠这里的处理</th></tr></thead><tbody>@@REFS@@</tbody></table></div>
<p class="muted">这是现有爆裂主轴的成长分支。它与大量低费牌追求高出牌数的玩法可以混搭；在实测前，不把它宣布为已经独立、成熟的新流派。</p></section>
<section class="section" id="rules"><span class="section-label">02 / ONE SHARED OFFENSIVE STAT</span><h2>一个本场共享的数值：爆裂威力</h2><p>@@MECHANIC@@</p><div class="formula"><strong>D = N + P + B</strong><p>N：本次吟唱出牌数　P：结算时的爆裂威力　B：仅限本次的额外伤害</p></div><div class="two"><div><h3>怎么保留</h3><p>P跨回合存在，普通爆裂结算不扣除；战斗结束清零。它属于角色本场的爆裂修正，之后新生成的爆裂同样受益。</p><p>这不是局外技能点，不用于学技能或改成长树。已记录的“技能点在局外”定位继续成立。</p></div><div><h3>怎么结算</h3><p>在现有回合末时点，读取当前N/P/B，打出一次群体伤害。清掉本次吟唱与B，再处理“爆裂结算后获得威力”。</p><p>爆裂研习带来的+3从下一次爆裂开始受益；本次的伤害不会反过来生成更多威力。</p></div></div>
<div class="callout"><p><b>为什么先用相加？</b>当前吟唱已奖励多出牌。如果改成N×(1+P)，抽牌、减费与成长会相互放大。先试N+P，可以清楚观察“多打牌”和“投入威力”各自的收益。代价是P过大可能掩盖N，这要作为首要实测问题。</p></div>
<details><summary>边界与原规则的衔接</summary><ul><li>没有新修正时，仍是D=N，没有擅自给爆裂添加常驻基础伤害。</li><li>N=0但P&gt;0时，本候选会让爆裂造成P伤；这需要用户采纳本候选后才成为规则。</li><li>吟唱期间仍不能再打出爆裂；积蓄返回手牌而非自动打出。威力没有改变存牌、返手或费用。</li><li>存牌、抽牌、格挡和宣言完成都不自动增加P。只有明确的威力牌生效，保证该主轴的投入与收益可辨认。</li><li>本页全为原始伤害。P只加一次，再对整次伤害应用游戏修正；正常可被格挡。力量与最终牌种的接入尚未定。</li><li>当次增伤牌本身若在吟唱中打出，也正常使N加1；算例已计算这一点。</li></ul></details></section>
<section class="section" id="cards"><span class="section-label">03 / A SMALL, COMPLETE OFFENSIVE PACKAGE</span><h2>先用五张牌把选择做出来</h2><p>所有名称、费用、稀有度和数值均为候选。本轮先保留基础版，不扩写升级版本；前三张足够验证主轴，后两张用于后续扩展。</p><div class="cards">@@CARDS@@</div>
<div class="callout"><p><b>最小验证包：</b>威力强化、全力咏唱、爆裂研习，加上现有积蓄入口和爆裂。先看基础投资、短战斗爆发与长战斗成长能否形成实际选择。</p></div></section>
<section class="section" id="calculator"><span class="section-label">04 / DAMAGE, NOT A FULL COMBAT SIMULATOR</span><h2>固定出牌数，看伤害投资改变什么</h2><p>试算只改变伤害修正，不模拟抽牌和费用。N包含本次吟唱中实际打出的所有牌；选用下方模式时不会自动再加一次计数。每个敌人分别承受结果，未计算格挡、易伤或过量伤害。</p><div class="calc"><div class="controls"><label for="count">吟唱出牌数 N：<span class="number" id="count-value">4</span><input id="count" type="range" min="0" max="12" value="4"></label><label for="power">处理本次模式前的威力 P：<span class="number" id="power-value">8</span><input id="power" type="range" min="0" max="30" value="8"></label><label for="mode">本次模式<select id="mode"><option value="normal">保留威力，正常爆裂</option><option value="burst">全力咏唱：本次B +10</option><option value="spend">倾尽魔力：清空P，本次B +2P</option></select></label><label class="checkbox" for="study"><input id="study" type="checkbox">已有一份爆裂研习（结算后P +3）</label></div><div class="result" aria-live="polite"><output id="damage"><span>本次对每个敌人的原始伤害</span><strong>12</strong></output><output id="remaining"><span>若战斗继续，结算后保有的威力</span><strong>8</strong></output></div><p id="calculation" class="equation">4 + 8 + 0 = 12</p><button type="button" id="reset">重置试算</button></div>
<details><summary>1费持续强化与1费当次爆发：什么时候回本？</summary><p>只比较两张牌各自增加的伤害，固定后续N与可释放次数，忽略其它伤害和击杀时点。两张牌在吟唱中打出时都额外贡献同样的1个N，因此这项不影响差值。</p><div class="table-wrap"><table><thead><tr><th>从现在起实际结算爆裂</th><th>威力强化：每次+4</th><th>全力咏唱：只本次+10</th></tr></thead><tbody><tr><th>1次</th><td>累计+4</td><td>累计+10</td></tr><tr><th>2次</th><td>累计+8</td><td>累计+10</td></tr><tr><th>3次</th><td>累计+12</td><td>累计+10</td></tr><tr><th>4次</th><td>累计+16</td><td>累计+10</td></tr></tbody></table></div><p>这些数值给出了“第三次才超过”的纸面分界。实际选择还受提前击杀、当前敌人数、防御压力与抽到牌的时间影响。</p></details></section>
<section class="section" id="turns"><span class="section-label">05 / PLAY SEQUENCES</span><h2>能接进现有牌，也能读清代价</h2><h3>与压缩、续接的单回合配合</h3><p>@@OPENING_SETUP@@</p><div class="table-wrap"><table><thead><tr><th>打牌 / 结算</th><th>剩余能量</th><th>N</th><th>P</th><th>结果</th></tr></thead><tbody>@@STEPS@@</tbody></table></div><p>这回合合计<b>18直接单体伤害、10群伤、5格挡</b>；威力的后续收益仍在。@@OPENING_NOTE@@</p>
<details><summary>三回合完整账目：先投资，最后决定是否倾尽</summary><p>@@TURN_SETUP@@</p>@@TURNS@@<div class="callout"><p>@@TURN_DECISION@@</p></div><p class="muted">第一回合没有防御，是实在的启动代价。这组给定抽牌只用于检验规则与能量账，不代表稳定抽序或可接受的承伤。</p></details></section>
<section class="section" id="review"><span class="section-label">06 / THE DECISION TO TEST</span><h2>它应该带来的三种选择</h2><div class="narrow"><ol><li><b>现在杀，还是以后更强。</b>全力咏唱和威力强化用同样费用，交换不同时间分布的伤害。</li><li><b>这回合投资，还是先保命。</b>研习与翻倍都占能量，牌组需要防御帮助渡过启动回合。</li><li><b>保留成长，还是为击杀清空。</b>倾尽魔力应当在预计能结束战斗时有价值，误判则失去后劲。</li></ol><p>这条路线的持续性来自多回合重复爆裂，成长性来自P提高。它没有新增敌人身上的持续伤害状态；也不要求把防御、弃牌或牌区移动都兑换成伤害。</p><p>局外技能点、单张稀有的爆裂鉴赏、悬挂宣言分别保留现有定位。这里先只决定爆裂的伤害如何投资和兑现。</p></div>
<details><summary>首轮验证标准与主要风险</summary><ul>@@CHECKS@@</ul><p><b>最需要承认的风险：</b>P过大以后，0费爆裂可能变成每回合固定领取群伤，玩家不再重视吟唱次序。优先压低P的投放速度、检查N在不同战斗阶段的贡献；不要先用新的进度条或复杂阈值来遮掩问题。若调低P仍不能形成有趣选择，就说明这条成长分支尚不值得扩成卡池。</p></details>
<p class="muted">当前完成的是可讨论的纸面设计与出牌核算，尚未实装或做实战平衡测试。@@SOURCE_NOTE@@</p><div class="source-links"><a href="惠惠核心设计简明版.html">当前已记录核心</a><a href="原版五职业与Karen伤害体系分析.html">原版与Karen的伤害参考</a><a href="惠惠其他体系探索.html">人物特点与原作出处</a><a href="docs/惠惠伤害体系候选.json">本候选结构化数据</a></div></section>
<footer>原创Mod机制候选 · 原作题材依据见人物特点报告 · 数据与页面单独保存，便于采纳、修改或放弃。</footer></main></div>
<script>
(()=>{const $=id=>document.getElementById(id);function update(){const n=Number($('count').value),p=Number($('power').value),mode=$('mode').value;const usedP=mode==='spend'?0:p,b=mode==='spend'?2*p:mode==='burst'?10:0,after=usedP+($('study').checked?3:0);$('count-value').textContent=n;$('power-value').textContent=p;$('damage').querySelector('strong').textContent=n+usedP+b;$('remaining').querySelector('strong').textContent=after;$('calculation').textContent=`${n} 出牌 + ${usedP} 威力 + ${b} 本次加伤 = ${n+usedP+b}`;}for(const id of ['count','power','mode','study'])$(id).addEventListener('input',update);$('reset').addEventListener('click',()=>{$('count').value=4;$('power').value=8;$('mode').value='normal';$('study').checked=false;update();});update();})();
</script></body></html>'''
    replacements = {
        'RECOMMENDATION': esc(d['recommendation']), 'REFS': refs, 'CARDS': cards,
        'MECHANIC': esc(d['mechanic']['description']), 'OPENING_SETUP': esc(d['opening']['setup']),
        'STEPS': steps, 'OPENING_NOTE': esc(d['opening']['note']),
        'TURN_SETUP': esc(d['three_turns']['setup']), 'TURNS': turns,
        'TURN_DECISION': esc(d['three_turns']['decision']), 'CHECKS': checks, 'SOURCE_NOTE': source_note,
    }
    for key, value in replacements.items():
        template = template.replace('@@' + key + '@@', value)
    if '@@' in template:
        raise ValueError('Unresolved template marker')
    output = HERE.parent / '惠惠伤害体系候选.html'
    output.write_text(with_design_notice(template, 'old-damage'), encoding='utf-8')
    print(f'Rendered {output}; fixed core unchanged: {actual_hash == d["fixed_core_sha256"]}')


if __name__ == '__main__':
    render()
