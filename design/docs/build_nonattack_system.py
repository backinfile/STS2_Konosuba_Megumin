"""Render the proposed non-attack damage-card system; no gameplay changes."""
from pathlib import Path
from html import escape
import json
import re
from design_status import with_design_notice

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
d = json.loads((HERE/'非攻击伤害体系草案.json').read_text(encoding='utf-8'))
evidence = json.loads((HERE/'非攻击伤害战士参考.json').read_text(encoding='utf-8'))
refs = {x['id']: x for x in evidence['files']}
e = escape
def ul(items):
    return '<ul>'+''.join('<li>'+e(x)+'</li>' for x in items)+'</ul>'

# Share the existing report's visual language; the generated file embeds all CSS.
base = (ROOT/'惠惠当前设计总览.html').read_text(encoding='utf-8')
style = re.search(r'<style>(.*?)</style>', base, re.S).group(1)
style += '''
.proposal-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px 32px}.proposal-card{min-width:0;padding:24px 0;border-top:2px solid var(--red)}.proposal-card h3{font:27px var(--serif);margin:10px 0 18px}.proposal-card .card-text{font-size:16px}.proposal-card p{font-size:14px}.proposal-card .meta{font:12px var(--mono);color:var(--red)}.proposal-card .role{color:var(--green);font-size:12px}.proposal-card details{font-size:12px}.proposal-card details p{font-size:12px}.proposal-card details a{margin-right:10px}.rules li{max-width:950px}.calc table{min-width:560px}.calc td strong{font:20px var(--mono);color:var(--red)}.source-files{overflow-wrap:anywhere}.source-files pre{overflow:auto;max-height:280px;font-size:11px;background:var(--surface);padding:15px}.demo-table{min-width:780px}.demo-table th{width:auto}.source-table th{width:19%}.source-table td:nth-child(2){width:37%}.controls .toggle{display:flex;align-items:center;gap:10px}#system-count,#system-might{max-width:300px}.summary-line{font-size:17px;color:var(--red)}@media(max-width:700px){.proposal-grid{grid-template-columns:1fr}}
'''
card_blocks = []
for c in d['cards']:
    sources = ' '.join(f'<a href="#ref-{rid}">{e(refs[rid].get("title",rid))}</a>' for rid in c['ref_ids'])
    card_blocks.append(f'''<article class="proposal-card" id="card-{e(c['id'])}"><div class="meta">{c['cost']}费 · {e(c['rarity'])} · {e(c['type'])}</div><h3>{e(c['name'])}</h3><p class="role">{e(c['role'])}</p><p class="card-text"><b>{e(c['text'])}</b></p><p class="muted">升级：{e(c['upgrade'])}</p><p>{e(c['why'])}</p><details><summary>参考、边界与题材</summary><p>{e(c['reference'])}</p><p>{e(c['boundary'])}</p><p class="muted">{e(c['theme'])}</p><p>{sources}</p></details></article>''')
mapping = ''.join(f'<tr><th scope="row">{e(refs[c["ref_ids"][0]]["title"])}</th><td>{e(refs[c["ref_ids"][0]]["verified"])}</td><td><a href="#card-{e(c["id"])}">{e(c["name"])}</a><small>{e(c["reference"])}</small></td></tr>' for c in d['cards'])
damage_cards = [c for c in d['cards'] if 'base_damage' in c]
damage_rows = ''.join(f'<tr><th scope="row">{e(c["name"])}</th><td>{e(c["target"])}</td><td><strong id="d-{e(c["id"])}">{c["base_damage"]*c["hits"]}</strong></td><td><span id="f-{e(c["id"])}">({c["base_damage"]}+0)×{c["hits"]}</span></td></tr>' for c in damage_cards)
steps = ''.join(f'<tr><th scope="row">{e(x["action"])}</th><td>{x["energy"]}</td><td>{x["might"]}</td><td>{x["plays"]}</td><td>{x["block"]}</td><td>{e(x["damage"])}<small>{e(x["detail"])}</small></td></tr>' for x in d['example']['steps'])
other_examples = ''.join(f'<article class="record"><h3>{e(x["title"])}</h3><p>{e(x["text"])}</p></article>' for x in d['other_examples'])
sources = ''.join(f'<details id="ref-{e(x["id"])}"><summary>{e(x.get("title",x["id"]))} · {e(x["id"])}</summary><p><a href="{e(Path(x["path"]).as_uri(),quote=True)}">{e(x["path"])}</a></p><p class="muted">SHA256：{e(x["sha256"])}</p><pre>{e(x["excerpts"])}</pre></details>' for x in evidence['files'])
page = r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>惠惠 · 技能输出与配套候选</title><style>@@STYLE@@</style></head><body><div class="wrap"><nav class="toc" aria-label="设计章节"><strong>MEGUMIN / DAMAGE</strong><a href="#structure">体系定位</a><a href="#reference">战士参考</a><a href="#cards">8张候选牌</a><a href="#calculator">威力与连打试算</a><a href="#example">独立回合算例</a><a href="#limits">取舍与待验证</a><a href="#sources">源码依据</a><a href="惠惠当前设计总览.html#history">返回全部体系</a></nav><main class="main">
<header><span class="eyebrow">PROPOSED CARD SYSTEM · 2026.10.09</span><h1>用技能输出，<br><em>用技能串起配套。</em></h1><p class="lead">@@CONCLUSION@@</p><div class="notice"><p><b>@@STATUS@@。</b>卡名与题材是工作稿；本轮参考的是战士攻击牌之间的关系。</p><p>@@CURRENT@@</p></div></header>
<section id="structure"><span class="eyebrow">01 / ROLE AND RULES</span><h2>威力负责成长，输出牌负责打起来</h2><div class="two"><div class="definition"><h3>威力体系 ≈ 力量体系</h3><p>决定每段伤害增加多少。常驻和临时来源仍单独设计。</p></div><div class="definition"><h3>技能输出与配套 ≈ 攻击牌配套</h3><p>决定选哪些输出牌、怎样连续打出，以及如何取得续牌、格挡和减费回报。</p></div></div>@@LOOP@@<div class="notice"><p><b>关键建议：按牌计连打，按段吃威力。</b>一张双段牌享受两次威力加值，但只触发一次出牌配套。技能配套也包含防御与爆裂咒文，不要求造成伤害。</p></div><details class="large-details"><summary>伤害来源、技能类型与计数规则</summary><div class="rules">@@RULES@@</div></details></section>
<section id="reference"><span class="eyebrow">02 / IRONCLAD REFERENCES</span><h2>借鉴触发与收益的关系</h2><p class="muted">@@REFERENCE_SCOPE@@</p><div class="table-scroll"><table class="source-table"><thead><tr><th>战士原牌</th><th>本地核对的效果</th><th>借到惠惠这边</th></tr></thead><tbody>@@MAPPING@@</tbody></table></div></section>
<section id="cards"><span class="eyebrow">03 / PROPOSED CARDS</span><h2>6张输出牌，2张配套牌</h2><p class="muted">3普通、4罕见、1稀有；7技能、1能力。伤害卡面直接写“造成X点伤害”，由技能牌承担输出。输出牌有基础伤害，威力为0时也能发挥作用。</p><div class="proposal-grid">@@CARDS@@</div></section>
<section id="calculator"><span class="eyebrow">04 / TWO DIFFERENT PAYOFFS</span><h2>威力与出牌次数，分别影响什么</h2><div class="calc"><div class="controls"><div><label for="system-might">当前总威力 <b id="system-might-value">0</b></label><input type="range" id="system-might" min="0" max="6" value="0"></div><div><label for="system-count">本回合已打出技能牌 <b id="system-count-value">0</b></label><input type="range" id="system-count" min="0" max="8" value="0"></div><label class="toggle"><input type="checkbox" id="system-upgrade">查看升级效果</label></div><p class="muted">总威力需由明确效果取得，不从出牌数自动生成。这里比较单卡；试爆生成的Token尚未打出，不能计入本牌伤害。</p><div class="table-scroll"><table><thead><tr><th>牌</th><th>伤害范围</th><th>原始伤害</th><th>计算</th></tr></thead><tbody>@@DAMAGE_ROWS@@</tbody></table></div><p class="summary-line">一气呵成当前耗能：<b id="finisher-cost">3</b>　·　硝烟掩护每张后续技能：<b id="cover-block">3</b>格挡</p><p class="muted">群伤按每个敌人计算，未计算格挡、减伤与过量伤害。勾选升级不把能力或配套视为已打出；格挡显示单次触发值，不追溯早于硝烟掩护的出牌。</p></div></section>
<section id="example"><span class="eyebrow">05 / A TURN WITHOUT EXPLOSION</span><h2>@@EXAMPLE_TITLE@@</h2><p>@@EXAMPLE_SETUP@@</p><div class="table-scroll"><table class="demo-table"><thead><tr><th>依次打出</th><th>剩余能量</th><th>临时威力</th><th>技能牌数</th><th>累计格挡</th><th>本步伤害与操作</th></tr></thead><tbody>@@STEPS@@</tbody></table></div><p class="summary-line">@@RESULT@@</p><p class="muted">@@EXAMPLE_LIMITS@@</p><div class="two">@@OTHER_EXAMPLES@@</div></section>
<section id="limits"><span class="eyebrow">06 / TRADEOFFS AND VALIDATION</span><h2>成立的理由与仍需付出的代价</h2>@@TRADEOFFS@@<h3>下一步要检验的内容</h3>@@CHECKS@@<p class="muted">完成的是本地源码核对、纸面资源账和页面试算；没有游戏实装或实战平衡结果。上一轮11张威力牌仍保留为待重做历史稿。</p></section>
<section id="sources"><span class="eyebrow">07 / LOCAL EVIDENCE</span><h2>可回查的源码与资料</h2><p>8张原版参照卡、狂怒与好勇斗狠的能力实现，以及铁甲战士卡池归属均已读取。中文名与文本取自同一快照的本地化文件。</p><div class="source-files">@@SOURCES@@</div><p><a href="素晴爆裂魔法原作资料索引.html#p-y1-mushroom">爆炸蘑菇与连锁反应题材</a> · <a href="docs/非攻击伤害战士参考.json">来源快照与本地化摘要</a></p></section><footer><a href="惠惠当前设计总览.html#history">返回按体系整理的当前总览</a> · <a href="docs/非攻击伤害体系草案.json">本候选结构化数据</a><br>@@STATUS@@。</footer>
</main></div><script>
(()=>{const cards=@@CALC_DATA@@;const $=id=>document.getElementById(id);function render(){const w=+$('system-might').value,n=+$('system-count').value,up=$('system-upgrade').checked;$('system-might-value').textContent=w;$('system-count-value').textContent=n;cards.forEach(c=>{const b=up?c.upgraded_damage:c.base_damage;$('d-'+c.id).textContent=(b+w)*c.hits;$('f-'+c.id).textContent=`(${b}+${w})×${c.hits}`;});$('finisher-cost').textContent=Math.max(0,3-n);$('cover-block').textContent=up?4:3;}['system-might','system-count','system-upgrade'].forEach(id=>$(id).addEventListener('input',render));render();})();
</script></body></html>'''
values = {
    'STYLE':style,'CONCLUSION':e(d['conclusion']),'STATUS':e(d['status']),'CURRENT':e(d['current_rules']),
    'LOOP':ul(d['core_loop']),'RULES':ul(d['scope_rules']),'REFERENCE_SCOPE':e(d['reference_scope']),
    'MAPPING':mapping,'CARDS':''.join(card_blocks),'DAMAGE_ROWS':damage_rows,
    'EXAMPLE_TITLE':e(d['example']['title']),'EXAMPLE_SETUP':e(d['example']['setup']),
    'STEPS':steps,'RESULT':e(d['example']['result']),'EXAMPLE_LIMITS':e(d['example']['limits']),
    'OTHER_EXAMPLES':other_examples,'TRADEOFFS':ul(d['tradeoffs']),'CHECKS':ul(d['next_checks']),
    'SOURCES':sources,'CALC_DATA':json.dumps([{k:c[k] for k in ['id','base_damage','upgraded_damage','hits']} for c in damage_cards],ensure_ascii=False)
}
for k,v in values.items():
    page=page.replace('@@'+k+'@@',v)
assert '@@' not in page
if d.get('review_status') == 'retired':
    page = with_design_notice(page, 'nonattack-retired')
    page = page.replace('<title>惠惠 · 技能输出与配套候选</title>', '<title>已停止探索 · 非攻击伤害流历史草案</title>')
    page = page.replace('PROPOSED CARD SYSTEM', 'RETIRED CARD PROPOSAL')
    page = page.replace('用技能输出，<br><em>用技能串起配套。</em>', '非攻击伤害流，<br><em>已停止探索。</em>')
    page = page.replace(e(d['conclusion']), e(d['retirement']['reason']))
    page = page.replace(e(d['current_rules']), e(d['retirement']['current_rule']))
    page = page.replace('8张候选牌', '8张历史草案')
    page = page.replace('6张输出牌，2张配套牌', '已停止：6张输出牌，2张配套牌')
    page = page.replace('<div class="meta">', '<div class="meta">历史草案 · 已停止探索 · ')
    page = page.replace('威力与出牌次数，分别影响什么', '旧规则试算：不适用当前威力')
    page = page.replace('不使用爆裂魔法的3能量回合', '历史算例：旧规则下的3能量回合')
    page = page.replace('下一步要检验的内容', '当时的验证计划（已停止）')
    page = page.replace('<div class="calc"><div class="controls">', '<div class="notice"><p>'+e(d['retirement']['historical_examples'])+'</p></div><div class="calc"><div class="controls">')
(ROOT/'惠惠非攻击伤害体系设计.html').write_text(page,encoding='utf-8')
portable=page
for href in re.findall(r'href="([^"]+)"',page):
    if not href.startswith(('#','http:','https:','file:')):
        filename,sep,fragment=href.partition('#')
        portable=portable.replace(f'href="{href}"',f'href="{(ROOT/filename).resolve().as_uri()}{sep}{fragment}"')
target=Path.home()/'.agent'/'diagrams'
target.mkdir(exist_ok=True,parents=True)
(target/'megumin-nonattack-card-system.html').write_text(portable,encoding='utf-8')
print(json.dumps({'proposed_cards':len(d['cards']),'output_cards':len(damage_cards),'reference_files':len(refs)}))
