import json
import re
from html import escape
from pathlib import Path
from design_status import with_design_notice

root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'docs/惠惠核心机制候选.json').read_text(encoding='utf-8'))

native_terms = {
    '格挡': '格挡抵消受到的伤害。',
    '爆裂魔法': '本方案的爆裂攻击牌。',
    '保留': '保留的牌不会在回合结束时被弃掉。',
    '消耗': '在战斗结束前移除。',
    '消耗牌堆': '存放本场战斗被消耗的牌。',
    '虚无': '如果这张牌在这个回合结束时留在你的手牌中，则将其消耗。',
    '不能被打出': '不能被打出的牌无法被打出。',
    '虚弱': '攻击造成的伤害减少25%。每层持续1个回合。',
    '易伤': '受到的攻击伤害增加50%。层数表示持续回合数。',
}


def card_text(text, terms):
    pattern = re.compile('|'.join(re.escape(term) for term in sorted(terms, key=len, reverse=True)))
    pieces = []
    end = 0
    for match in pattern.finditer(text):
        pieces.append(escape(text[end:match.start()]))
        term = match.group()
        pieces.append(f'<abbr title="{escape(terms[term], quote=True)}">{escape(term)}</abbr>')
        end = match.end()
    pieces.append(escape(text[end:]))
    return ''.join(pieces).replace('\n', '<br>')


def card_properties(card, terms):
    return ''.join(f'<abbr title="{escape(terms[key], quote=True)}">{escape(key)}</abbr>。' for key in card['keywords'])


def resource_cost_markup(card):
    if not card.get('resource_cost'):
        return ''
    resource = card['resource_cost']
    label = f'{resource["amount"]}{resource["term"]}'
    hint = f'需要并消耗{resource["amount"]}点{resource["term"]}。'
    return f'<span class="resource-cost" title="{escape(hint, quote=True)}">{escape(label)}</span>'


def card_cost_markup(card):
    cost = escape(card['cost']) + '费'
    if card.get('upgraded_cost') is not None:
        cost += f'<small class="deck-type">升级后{escape(card["upgraded_cost"])}费</small>'
    return cost


def resolve_starter_card(entry, scheme):
    if 'sample_card' in entry:
        return next(card for card in scheme['cards'] if card['name'] == entry['sample_card'])
    return entry


page = ['''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>惠惠 · 核心机制候选</title>
<style>
:root{--bg:#f5f1e8;--surface:#fffdf8;--border:#d9d1c1;--text:#2d2923;--text-dim:#645e54;--accent:#a43d28;--gold:#886022}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:17px/1.85 'Microsoft YaHei','PingFang SC',sans-serif}
main{max-width:1100px;margin:auto;padding:40px 28px 56px}h1{font-size:32px;line-height:1.4;margin:0 0 10px}h2{font-size:26px;line-height:1.45;margin:0 0 16px}h3{font-size:18px;margin:0 0 12px}p{margin:0 0 16px;overflow-wrap:break-word}
.intro,.note,footer{font-size:14px;color:var(--text-dim)}nav{display:flex;flex-wrap:wrap;gap:20px;margin:22px 0}nav a{color:var(--accent);text-underline-offset:4px}
section{border-top:1px solid var(--border);padding:34px 0;scroll-margin-top:20px}.number{color:var(--accent)}.definition{border-left:2px solid var(--border);padding:0 0 0 16px;margin:14px 0;font-size:15px}.definition strong{color:var(--gold)}.kind{font-size:12px;color:var(--text-dim);margin-left:8px}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:20px}.card{display:flex;flex-direction:column;min-width:0;background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:19px}.card-top{display:flex;gap:12px;align-items:center;flex-wrap:wrap}.energy{display:inline-grid;place-items:center;width:34px;height:34px;border-radius:50%;background:var(--accent);color:white;font-weight:700;flex-shrink:0}.resource-cost{font-size:13px;color:var(--gold);border:1px solid var(--border);padding:2px 7px;border-radius:4px}.card h4{font-size:18px;margin:0}.meta{font-size:12px;color:var(--text-dim);margin:9px 0 16px}.card p{font-size:16px;margin:0 0 14px;line-height:1.85}.properties{margin-top:auto;border-top:1px solid var(--border);padding-top:10px;min-height:38px;font-size:14px;color:var(--gold)}abbr{color:var(--gold);font-weight:600;text-decoration:none;cursor:help}footer{border-top:1px solid var(--border);padding-top:18px}a:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.starter-layout{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2.5fr);gap:24px;margin:26px 0}.starter-relic,.starter-deck{min-width:0}.starter-relic{border-left:3px solid var(--accent);padding-left:16px}.starter-relic h4{font-size:19px;color:var(--gold);margin:0 0 10px}.starter-relic p{font-size:15px}.deck-total{font-size:14px;font-weight:400;color:var(--text-dim);margin-left:8px}.deck-table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.8}.deck-table th{text-align:left;color:var(--text-dim);font-weight:400;border-bottom:1px solid var(--border);padding:0 8px 8px}.deck-table td{border-bottom:1px solid var(--border);padding:10px 8px;vertical-align:top;overflow-wrap:break-word}.deck-table th:first-child,.deck-table td:first-child{padding-left:0;width:23%}.deck-table th:last-child,.deck-table td:last-child{padding-right:0}.deck-count,.deck-cost{width:1%;white-space:nowrap}.deck-card-name{font-weight:600}.deck-type{display:block;font-size:12px;color:var(--text-dim)}.deck-properties{color:var(--gold)}.deck-table .resource-cost{display:block;font-size:12px;margin-top:4px;padding:0 4px}.starter-note{margin-top:12px}
.generated-note{font-size:14px;padding:10px 14px;background:#ece6d9;margin:16px 0;color:var(--text-dim)}.generated-note strong{color:var(--text)}.basis{margin:18px 0;font-size:14px;color:var(--text-dim)}.basis summary{cursor:pointer;color:var(--accent);width:fit-content}.basis ul{padding-left:22px}.basis li{padding:7px 0;overflow-wrap:break-word}.basis a,footer a{color:var(--accent);text-underline-offset:3px}.adaptation{display:block;margin-top:4px}.evidence{font-size:12px;color:var(--gold)}summary:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.core{padding:20px 0 26px}.core h2{font-size:21px}.core-flow{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:22px 0;padding:16px 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}.core-flow b{display:block;font-size:16px;color:var(--accent)}.core-flow span{display:block;font-size:14px;color:var(--text-dim)}.research-row{margin:16px 0}.research-row p{margin:5px 0}.core .definition{margin:16px 0}
.timing-table{margin:18px 0}.timing-table caption{text-align:left;color:var(--text-dim);font-size:13px;padding-bottom:8px}.timing-table th:first-child,.timing-table td:first-child{width:14%}
.recommendation{border-left:3px solid var(--accent);padding:12px 18px;background:#ece6d9;margin:22px 0}.recommendation h3{margin-bottom:8px}.recommendation p:last-child{margin:0}.table-scroll{overflow-x:auto;margin:22px 0}.comparison-table{min-width:630px}.comparison-table caption{text-align:left;font-size:14px;color:var(--text-dim);padding-bottom:10px}.comparison-table th:first-child,.comparison-table td:first-child{width:15%}.comparison-table td{width:28%}.comparison-table a{color:var(--accent)}.play-examples li{padding:8px 0}.play-examples strong{color:var(--text)}.play-examples .result{display:block;color:var(--gold)}nav{position:sticky;top:0;z-index:10;background:var(--bg);padding:12px 0;border-bottom:1px solid var(--border);flex-wrap:nowrap;overflow-x:auto}nav a{flex-shrink:0;white-space:nowrap}section{scroll-margin-top:76px}
@media(max-width:900px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}.starter-layout{grid-template-columns:1fr;gap:16px}}@media(max-width:600px){main{padding:26px 18px}.cards{grid-template-columns:1fr}h1{font-size:26px}h2{font-size:23px}nav{gap:12px;font-size:14px}.deck-table{font-size:13px}.deck-table td,.deck-table th{padding-left:5px;padding-right:5px}}@media print{body{background:white}nav{display:none}.card,.starter-relic,tr{break-inside:avoid}}
@media(max-width:600px){.core-flow{grid-template-columns:1fr;gap:12px}.recommendation{padding:12px 14px}.comparison-table{font-size:13px}}@media print{.table-scroll{overflow:visible}.comparison-table{min-width:0}}
.declaration-demo{display:flex;align-items:center;flex-wrap:wrap;gap:24px;margin:20px 0;padding:22px 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}.declaration-demo [hidden]{display:none}.declaration-token{width:112px;height:112px;border:3px solid var(--accent);border-radius:50%;display:flex;align-items:center;justify-content:center;flex-direction:column;background:var(--surface);flex-shrink:0}.declaration-token strong{font-size:30px;line-height:1.4}.declaration-token span{font-size:12px;color:var(--text-dim)}.declaration-controls{flex:1;min-width:230px}.declaration-controls button{font:inherit;font-size:14px;padding:7px 12px;margin:0 8px 8px 0;border:1px solid var(--border);border-radius:4px;background:var(--surface);color:var(--text);cursor:pointer}.declaration-controls button:focus-visible{outline:3px solid var(--accent);outline-offset:3px}.declaration-controls button:disabled{opacity:.5;cursor:default}.declaration-empty{font-size:14px;color:var(--text-dim);max-width:112px}.declaration-status{font-size:15px;min-height:2em}.declaration-reference{max-width:440px}@media print{.declaration-controls button{display:none}}
</style></head><body><main>''']
page[0] = page[0].replace('<title>惠惠 · 核心机制候选</title>', f'<title>{escape(data["title"])}</title>')
page.append(f'<header><h1>{escape(data["title"])}</h1><p class="intro">{escape(data["intro"])}</p></header>')
if data.get('other_systems_exploration'):
    other = data['other_systems_exploration']
    page.append(f'<p class="generated-note"><a href="{escape(other["page"], quote=True)}">{escape(other["title"])}</a>：{escape(other["summary"])}</p>')
if data.get('reference_study'):
    study = data['reference_study']
    page.append(f'<aside class="recommendation"><h3><a href="{escape(study["page"], quote=True)}">{escape(study["title"])}</a></h3><p class="note">{escape(study["summary"])}</p></aside>')
if data.get('hanging_declarations'):
    page.append('<p class="generated-note"><strong>历史宣言：</strong>本页保留按格挡次数完成的旧稿。最新已改为连续3张技能触发，回合结束进度归零，<a href="惠惠当前设计总览.html#declaration">查看当前规则</a>。旧稿为悬挂任务、完成回2能量后弃牌。<a href="#hanging-declaration">查看1费7格挡参考牌与0/3演示</a>。首张限制与回合末判定不再沿用。</p>')
elif data.get('independent_systems'):
    page.append('<p class="generated-note"><strong>当前设计原则：</strong>两个体系可以独立闭环。积蓄与爆裂是一个体系；另列无需爆裂的宣言候选。<a href="#independent-systems">查看体系关系与新样例</a></p>')
elif data.get('battle_builds'):
    page.append('<p class="generated-note"><strong>当前新提案：</strong>保留吟唱连打，新增爆裂专精与魔力透支。积蓄是共用准备工具；牌区驻留和脱力转化已退出优先方向。<a href="#battle-builds">查看具体卡牌与战斗计划</a></p>')
elif data.get('archetype_reassessment'):
    page.append('<p class="generated-note"><strong>流派判定已修正：</strong>原连打、回流、高费压缩合并为同一积蓄运转体系。新方向仅为候选。<a href="#archetypes">查看修正与新探索</a></p>')
core = data.get('fixed_core')
core_terms = {rule['term']: rule['text'] for rule in core['rules']} if core else {}
grade_labels = {'A': '官方日文正文', 'B': '非官方译文定位', 'C': '简介／二手索引'}
if core:
    page.append(f'<div class="core" aria-labelledby="fixed-core-title"><h2 id="fixed-core-title">{escape(core.get("heading", "当前试用核心"))}</h2><div class="core-flow" aria-label="核心循环">')
    for step in core['flow']:
        page.append(f'<div><b>{escape(step["title"])}</b><span>{escape(step["text"])}</span></div>')
    page.append('</div>')
    for rule in core['rules']:
        page.append(f'<p class="definition"><strong>{escape(rule["term"])}</strong><span class="kind">{escape(rule["kind"])}</span><br>{escape(rule["text"])}</p>')
    page.append(f'<p class="note">{escape(core["trigger_text"])}</p>')
    if core.get('scope_note'):
        page.append(f'<details class="basis"><summary>上一版内容的记录与本轮范围</summary><p>{escape(core["scope_note"])}</p></details>')
    if core.get('recommendation'):
        recommendation = core['recommendation']
        page.append(f'<aside class="recommendation"><h3>{escape(recommendation["title"])}</h3><p>{escape(recommendation["text"])}</p><p class="note">{escape(recommendation["secondary"])}</p></aside>')
    if core.get('comparison'):
        comparison = core['comparison']
        page.append('<div class="table-scroll"><table class="deck-table comparison-table">')
        page.append(f'<caption>{escape(comparison["caption"])}</caption><thead><tr>')
        for column in comparison['columns']:
            page.append(f'<th scope="col">{escape(column)}</th>')
        page.append('</tr></thead><tbody>')
        for row in comparison['rows']:
            page.append(f'<tr><td><a href="#{escape(row["id"], quote=True)}">{escape(row["name"])}</a></td><td>{escape(row["decision"])}</td><td>{escape(row["benefit"])}</td><td>{escape(row["risk"])}</td></tr>')
        page.append('</tbody></table></div>')
    if core.get('example_turns'):
        page.append(f'<table class="deck-table timing-table" aria-labelledby="timing-caption"><caption id="timing-caption">{escape(core.get("timeline_caption", "前4回合：含固定遗物，不含咏唱加成"))}</caption><thead><tr><th scope="col">回合</th><th scope="col">{escape(core.get("timeline_middle_label", "状态与咏唱"))}</th><th scope="col">回合结束</th></tr></thead><tbody>')
        for turn in core['example_turns']:
            page.append(f'<tr><td>{escape(turn["turn"])}</td><td>{escape(turn["state"])}</td><td>{escape(turn["ending"])}</td></tr>')
        page.append('</tbody></table>')
    if core.get('acquisition'):
        acquisition = core['acquisition']
        page.append(f'<p class="definition"><strong>获取建议</strong><br>{escape(acquisition["recommendation"])}</p>')
        page.append('<details class="basis"><summary>三种获取方式的取舍</summary>')
        page.append(f'<p>{escape(acquisition["reason"])}</p><ul>')
        for option in acquisition['options']:
            page.append(f'<li><strong>{escape(option["name"])}</strong>：{escape(option["method"])}<span class="adaptation">{escape(option["assessment"])}</span></li>')
        page.append('</ul></details>')
    if core.get('research'):
        page.append('<details class="basis"><summary>原作依据与命名核查</summary>')
    for research in core.get('research', []):
        reference = research.get('local_reference') or data['original_reference']['page'] + '#' + research['entry']
        reference_label = research.get('reference_label', '资料索引')
        page.append(f'<div class="research-row"><strong>{escape(research["label"])}</strong><p>{escape(research["result"])}</p><p>设计建议：{escape(research["recommendation"])}</p><a href="{escape(research["source_url"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(research["source_title"])}</a><span class="evidence"> · {escape(grade_labels[research["grade"]])}</span> · <a href="{escape(reference, quote=True)}">{escape(reference_label)}</a></div>')
    if core.get('research'):
        page.append('</details>')
    page.append(f'<details class="basis"><summary>{escape(core.get("notes_label", "计数与结算边界（本轮建议）"))}</summary><ul>')
    for note in core['notes']:
        page.append(f'<li>{escape(note)}</li>')
    page.append('</ul></details>')
    if core.get('alternative_trigger'):
        alternative = core['alternative_trigger']
        page.append(f'<details class="basis"><summary>{escape(alternative["title"])}</summary><p>{escape(alternative["text"])}</p></details>')
    if core.get('entry_comparison'):
        comparison = core['entry_comparison']
        page.append(f'<details class="basis" id="entry-options"><summary>{escape(comparison["title"])}</summary><p>{escape(comparison["intro"])}</p>')
        for option in comparison['options']:
            page.append(f'<div class="research-row"><strong>{escape(option["name"])}</strong><p>{escape(option["rule"])}</p><p>示例：{escape(option["example"])}</p><p>{escape(option["benefit"])} {escape(option["tradeoff"])}</p></div>')
        page.append(f'<p>{escape(comparison["recommendation"])}</p></details>')
    page.append('</div>')
nav_labels = {'queued': '咏唱暂存', 'sequence': '技能连打', 'exhaust': '消耗强化'}
page.append('<nav aria-label="核心方案">')
if data.get('hanging_declarations'):
    page.append('<a href="#hanging-declaration">宣言参考牌</a><a href="#hanging-examples">费用与进度</a><a href="#hanging-review">强度与待定规则</a>')
elif data.get('independent_systems'):
    page.append('<a href="#independent-systems">体系可以独立</a><a href="#declaration-system">宣言候选</a><a href="#declaration-example">独立运转算例</a>')
elif data.get('battle_builds'):
    page.append('<a href="#battle-builds">新体验提案</a>')
    for route in data['battle_builds']['routes']:
        page.append(f'<a href="#{escape(route["id"], quote=True)}">{escape(route["name"])}</a>')
    page.append('<a href="#build-choices">抓牌与回合选择</a>')
elif data.get('archetype_reassessment'):
    page.append('<a href="#archetypes">流派重新判定</a>')
    for direction in data['archetype_reassessment']['directions']:
        page.append(f'<a href="#{escape(direction["id"], quote=True)}">{escape(direction["name"])}</a>')
elif data.get('archetype_exploration'):
    page.append('<a href="#archetypes">流派总览</a>')
    for route in data['archetype_exploration']['routes']:
        page.append(f'<a href="#{escape(route["id"], quote=True)}">{escape(route["name"])}</a>')
if data.get('power_candidates'):
    page.append('<a href="#story-powers">剧情Power候选</a>')
for index, scheme in enumerate(data['schemes'], 1):
    label = scheme.get('nav_label', nav_labels.get(scheme['id'], scheme['title']))
    page.append(f'<a href="#{scheme["id"]}">{index:02d} {escape(label)}</a>')
page.append('</nav>')

if data.get('hanging_declarations'):
    hanging = data['hanging_declarations']
    card = hanging['card']
    terms = {**native_terms, **core_terms, '红魔族宣言': card['keyword']}
    page.append(f'<section id="hanging-declaration"><p class="generated-note"><strong>历史条件：</strong>下方获得格挡的规则和演示已停用。<a href="惠惠当前设计总览.html#declaration">当前宣言为连续3张技能触发，回合结束进度归零 →</a></p><h2>{escape(hanging["title"])}</h2><p class="note">{escape(hanging["status"])}</p><p>{escape(hanging["summary"])}</p><p>{escape(hanging["independence"])}</p>')
    page.append(f'<article class="card declaration-reference"><div class="card-top"><span class="energy">{escape(card["cost"])}</span><h4>{escape(card["name"])}</h4></div><div class="meta">{escape(card["rarity"])} · {escape(card["type"])}</div><p>{card_text(card["text"], terms)}</p><div class="properties">完成宣言：获得2能量，本牌进入弃牌堆。</div></article><p class="note">{escape(card["note"])}</p>')
    page.append('''<div class="declaration-demo" aria-label="单张宣言进度演示"><div id="declaration-token" class="declaration-token"><strong id="declaration-progress">0/3</strong><span>获得格挡</span></div><div id="declaration-empty" class="declaration-empty" hidden>悬挂位置已空<br>本牌进入弃牌堆</div><div class="declaration-controls"><p id="declaration-status" class="declaration-status" role="status" aria-live="polite">已获得本牌的7格挡，现在从0/3开始悬挂。</p><button type="button" id="declaration-advance">模拟获得一次格挡</button><button type="button" id="declaration-reset">重看悬挂过程</button><p class="note">仅演示单张任务；每次点击代表后续一次有效格挡，来源与费用另计。展示一个位置不代表容量上限为1。</p></div></div>''')
    page.append('''<script>(()=>{const counter=document.getElementById('declaration-progress'),token=document.getElementById('declaration-token'),empty=document.getElementById('declaration-empty'),status=document.getElementById('declaration-status'),advance=document.getElementById('declaration-advance'),reset=document.getElementById('declaration-reset');let progress=0;advance.addEventListener('click',()=>{if(progress>=3)return;progress++;counter.textContent=progress+'/3';if(progress===3){token.hidden=true;empty.hidden=false;advance.disabled=true;status.textContent='达到3/3：获得2能量；本牌移入弃牌堆，任务结束。'}else{status.textContent='后续已获得'+progress+'次格挡，进度'+progress+'/3；尚未回能。'}});reset.addEventListener('click',()=>{progress=0;counter.textContent='0/3';token.hidden=false;empty.hidden=true;advance.disabled=false;status.textContent='已获得本牌的7格挡，现在从0/3开始悬挂。';});})();</script>''')
    page.append('<ol class="play-examples">')
    for step in hanging['flow']:
        page.append(f'<li><strong>{escape(step["label"])}</strong>：{escape(step["detail"])}</li>')
    page.append('</ol><details class="basis"><summary>用户已指定的内容与计数口径</summary><h3>用户已指定</h3><ul>')
    for point in hanging['confirmed']:
        page.append(f'<li>{escape(point)}</li>')
    page.append('</ul><h3>用于推演的口径与未定边界</h3><ul>')
    for point in hanging['trial_rules']:
        page.append(f'<li>{escape(point)}</li>')
    page.append('</ul></details></section><section id="hanging-examples"><h2>1费的投入，怎样换来后续能量</h2>')
    for example in hanging['examples']:
        page.append(f'<p class="definition"><strong>{escape(example["title"])}</strong><br>{escape(example["text"])}</p>')
    page.append('</section><section id="hanging-review"><h2>强度取决于获得格挡的频率</h2><ul>')
    for point in hanging['assessment']:
        page.append(f'<li>{escape(point)}</li>')
    page.append('</ul><h3>还未定下的规则</h3>')
    for decision in hanging['open_decisions']:
        page.append(f'<p class="definition"><strong>{escape(decision["name"])}</strong><span class="kind">{escape(decision["status"])}</span><br>{escape(decision["detail"])}</p>')
    page.append(f'<details class="basis"><summary>本地事件语义核对</summary><p>{escape(hanging["source_note"])}</p></details></section>')

if data.get('independent_systems'):
    if data.get('hanging_declarations'):
        page.append('<details class="basis"><summary>前稿对照：回合挑战与气势（已被悬挂任务参考牌修正）</summary>')
    independent = data['independent_systems']
    terms = {**native_terms, **core_terms, '宣言': independent['rules'][0]['text'], '气势': independent['rules'][2]['text']}
    page.append(f'<section id="independent-systems"><h2>{escape(independent["title"])}</h2><p>{escape(independent["principle"])}</p><p>{escape(independent["correction"])}</p><aside class="recommendation"><p>{escape(independent["criterion"])}</p></aside></section>')
    page.append(f'<section id="declaration-system"><h2>{escape(independent["name"])}</h2><p class="note">{escape(independent["status"])}</p><p>{escape(independent["experience"])}</p>')
    for rule in independent['rules']:
        page.append(f'<p class="definition"><strong>{escape(rule["name"])}</strong><br>{escape(rule["text"])}</p>')
    page.append('<div class="cards">')
    for card in independent['cards']:
        page.append(f'<article class="card independent-card" id="independent-{escape(card["id"], quote=True)}"><div class="card-top"><span class="energy">{escape(card["cost"])}</span><h4>{escape(card["name"])}</h4></div><div class="meta">{escape(card["type"])} · 机制样例</div><p>{card_text(card["text"], terms)}</p><details class="basis"><summary>用途与边界</summary><p>{escape(card["note"])}</p></details></article>')
    page.append('</div></section>')
    example = independent['example']
    page.append(f'<section id="declaration-example"><h2>拿掉爆裂后，怎样完成两个回合</h2><p class="note">{escape(example["setup"])}</p><ol class="play-examples">')
    for step in example['steps']:
        page.append(f'<li>{escape(step)}</li>')
    page.append(f'</ol><p class="definition"><strong>可选桥接</strong><br>{escape(independent["bridge"])}</p><details class="basis"><summary>还需要验证什么</summary><ul>')
    for risk in independent['risks']:
        page.append(f'<li>{escape(risk)}</li>')
    lore = independent['lore']
    reference = data['original_reference']['page'] + '#' + lore['entry']
    page.append(f'</ul></details><p class="note">{escape(lore["text"])} <a href="{escape(reference, quote=True)}">本地资料定位</a></p></section>')
    if data.get('hanging_declarations'):
        page.append('</details>')

if data.get('battle_builds'):
    if data.get('independent_systems'):
        page.append('<details class="basis"><summary>上一轮爆裂配套讨论：专精与透支</summary><p>这些卡牌仍可作为素材，不再据此声称已有三个独立体系。</p>')
    builds = data['battle_builds']
    terms = {**native_terms, **core_terms, '专精': builds['rules'][0]['text'], '透支': builds['rules'][1]['text'], '魔力债务': builds['rules'][1]['text']}
    page.append(f'<section id="battle-builds"><h2>{escape(builds["title"])}</h2><p class="note">{escape(builds["status"])}</p><p>{escape(builds["thesis"])}</p><p class="note">{escape(builds["scope"])}</p>')
    page.append('<div class="table-scroll"><table class="deck-table comparison-table"><caption>比较整场战斗的计划</caption><thead><tr><th scope="col">路线</th><th scope="col">体验</th><th scope="col">经营的资源</th><th scope="col">付出的代价</th></tr></thead><tbody>')
    for route in builds['routes']:
        page.append(f'<tr><td><a href="#{escape(route["id"], quote=True)}">{escape(route["name"])}</a></td><td>{escape(route["experience"])}</td><td>{escape(route["resource"])}</td><td>{escape(route["cost"])}</td></tr>')
    page.append('</tbody></table></div><h3>仅由新卡牌引入的规则</h3>')
    for rule in builds['rules']:
        page.append(f'<p class="definition"><strong>{escape(rule["name"])}</strong><br>{escape(rule["text"])}</p>')
    page.append('</section>')
    for route in builds['routes']:
        page.append(f'<section id="{escape(route["id"], quote=True)}"><h2>{escape(route["name"])}</h2><p class="note">{escape(route["status"])}</p><p>{escape(route["experience"])}</p><p class="definition"><strong>战斗计划</strong><br>{escape(route["plan"])}</p><p><strong>抓牌偏好：</strong>{escape(route["picks"])}</p><p>{escape(route["difference"])}</p><div class="cards">')
        for card in route['cards']:
            page.append(f'<article class="card battle-card" id="proposal-{escape(card["id"], quote=True)}"><div class="card-top"><span class="energy">{escape(card["cost"])}</span><h4>{escape(card["name"])}</h4></div><div class="meta">{escape(card["type"])} · {escape(card["rarity"])}建议 · {escape(card["role"])}</div><p>{card_text(card["text"], terms)}</p><details class="basis"><summary>用途与规则</summary><p>{escape(card["note"])}</p></details></article>')
        page.append('</div>')
        example = route['example']
        page.append(f'<aside class="recommendation"><h3>3能量算例 · 计入准备成本</h3><p class="note">{escape(example["setup"])}</p><ol class="play-examples">')
        for step in example['steps']:
            page.append(f'<li>{escape(step)}</li>')
        page.append(f'</ol><p><strong>{escape(example["result"])}</strong></p></aside><p><strong>取舍：</strong>{escape(route["cost"])}</p><details class="basis"><summary>原作主题与新增规则的区别</summary><ul>')
        for lore in route['lore']:
            reference = data['original_reference']['page'] + '#' + lore['entry']
            page.append(f'<li>{escape(lore["text"])} <a href="{escape(reference, quote=True)}">本地资料</a></li>')
        page.append('</ul></details></section>')
    page.append('<section id="build-choices"><h2>同一张牌，为什么会作不同选择</h2><div class="table-scroll"><table class="deck-table comparison-table"><thead><tr><th scope="col">局面</th><th scope="col">吟唱连打</th><th scope="col">爆裂专精</th><th scope="col">魔力透支</th></tr></thead><tbody>')
    for choice in builds['choices']:
        page.append('<tr>' + ''.join(f'<td>{escape(choice[key])}</td>' for key in ('situation', 'chant', 'mastery', 'debt')) + '</tr>')
    page.append(f'</tbody></table></div><p>{escape(builds["hybrids"])}</p><aside class="recommendation"><h3>哪些问题还需要验证</h3><ul>')
    for point in builds['review']:
        page.append(f'<li>{escape(point)}</li>')
    page.append('</ul></aside></section>')
    if data.get('independent_systems'):
        page.append('</details>')

if data.get('archetype_reassessment'):
    if data.get('battle_builds'):
        page.append('<details class="basis"><summary>已退出优先方向：驻留成长与脱力转化</summary><p>以下仅保留讨论过程；当前建议以上方战斗计划提案为准。</p>')
    assessment = data['archetype_reassessment']
    terms = {**native_terms, **core_terms}
    page.append(f'<section id="archetypes" aria-labelledby="archetypes-title"><h2 id="archetypes-title">{escape(assessment["title"])}</h2><p class="note">{escape(assessment["feedback"])}</p><p>{escape(assessment["diagnosis"])}</p><aside class="recommendation"><p>{escape(assessment["recommendation"])}</p></aside>')
    page.append('<div class="table-scroll"><table class="deck-table comparison-table"><caption>用资源投入和回合决策比较，不按增伤能力分组</caption><thead><tr><th scope="col">方向</th><th scope="col">核心资源或代价</th><th scope="col">行动选择</th></tr></thead><tbody>')
    for direction in assessment['directions']:
        page.append(f'<tr><td><a href="#{escape(direction["id"], quote=True)}">{escape(direction["name"])}</a></td><td>{escape(direction["resource"])}</td><td>{escape(direction["decision"])}</td></tr>')
    page.append('</tbody></table></div><details class="basis"><summary>新候选怎样才算成立</summary><ul>')
    for criterion in assessment['tests']:
        page.append(f'<li>{escape(criterion)}</li>')
    page.append('</ul></details></section>')
    for direction in assessment['directions']:
        page.append(f'<section id="{escape(direction["id"], quote=True)}" aria-labelledby="title-{escape(direction["id"], quote=True)}"><h2 id="title-{escape(direction["id"], quote=True)}">{escape(direction["name"])}</h2><p class="note">{escape(direction["status"])}</p><p class="definition"><strong>资源循环</strong><br>{escape(direction["loop"])}</p><p><strong>抓牌变化：</strong>{escape(direction["picks"])}</p><p><strong>区分是否成立：</strong>{escape(direction["contrast"])}</p>')
        if direction['seeds']:
            page.append('<h3>用于推演的机制种子 · 费用与数值均待验证</h3><div class="cards">')
            for seed in direction['seeds']:
                page.append(f'<article class="card direction-seed"><div class="card-top"><span class="energy">{escape(seed["cost"])}</span><h4>{escape(seed["name"])}</h4></div><div class="meta">{escape(seed["type"])}</div><p>{card_text(seed["text"], terms)}</p><details class="basis"><summary>建议口径</summary><p>{escape(seed["note"])}</p></details></article>')
            page.append('</div>')
        page.append(f'<p class="note">与现有核心的连接：{escape(direction["bridge"])}</p><aside class="recommendation"><h3>尚未解决</h3><p>{escape(direction["gap"])}</p></aside>')
        if direction['lore']:
            page.append('<details class="basis"><summary>原作意象与改编界线</summary><ul>')
            for lore in direction['lore']:
                reference = data['original_reference']['page'] + '#' + lore['entry']
                page.append(f'<li>{escape(lore["text"])} <a href="{escape(reference, quote=True)}">本地资料定位</a></li>')
            page.append('</ul></details>')
        page.append('</section>')
    page.append(f'<aside class="recommendation"><h3>下一轮验证重点</h3><p>{escape(assessment["next"])}</p><p class="note">{escape(assessment["scope"])}</p></aside>')
    if data.get('battle_builds'):
        page.append('</details>')

if data.get('archetype_exploration'):
    exploration = data['archetype_exploration']
    terms = {**native_terms, **core_terms}
    exploration_id = 'component-materials' if data.get('archetype_reassessment') else 'archetypes'
    if data.get('archetype_reassessment'):
        page.append('<details class="basis"><summary>上轮九张配件素材（流派划分已撤回）</summary>')
    page.append(f'<section id="{exploration_id}" aria-labelledby="{exploration_id}-title"><h2 id="{exploration_id}-title">{escape(exploration["title"])}</h2><p class="note">{escape(exploration["status"])}</p>')
    page.append(f'<aside class="recommendation"><h3>配件归类</h3><p>{escape(exploration["recommendation"])}</p></aside><p>{escape(exploration["finding"])}</p><p class="note">{escape(exploration["method"])}</p>')
    page.append('<div class="table-scroll"><table class="deck-table comparison-table"><caption>配件作用与归类</caption><thead><tr><th scope="col">分组</th><th scope="col">使用目的</th><th scope="col">收益来自什么</th><th scope="col">当前判断</th></tr></thead><tbody>')
    for route in exploration['routes']:
        page.append(f'<tr><td><a href="#{escape(route["id"], quote=True)}">{escape(route["name"])}</a></td><td>{escape(route["decision"])}</td><td>{escape(route["trigger"])}</td><td>{escape(route["position"])}</td></tr>')
    page.append('</tbody></table></div><details class="basis"><summary>现有六张牌分别支持什么</summary><div class="table-scroll"><table class="deck-table comparison-table"><thead><tr><th scope="col">牌</th><th scope="col">角色</th><th scope="col">判定原因</th></tr></thead><tbody>')
    for role in exploration['current_roles']:
        page.append(f'<tr><td>{escape(role["name"])}</td><td>{escape(role["role"])}</td><td>{escape(role["reason"])}</td></tr>')
    page.append('</tbody></table></div></details></section>')
    for route in exploration['routes']:
        page.append(f'<section id="{escape(route["id"], quote=True)}" aria-labelledby="title-{escape(route["id"], quote=True)}"><h2 id="title-{escape(route["id"], quote=True)}">{escape(route["name"])}</h2><p class="note">{escape(route["position"])}</p><p><strong>{escape(route["decision"])}</strong></p>')
        page.append(f'<p class="definition"><strong>核心循环</strong><br>{escape(route["loop"])}</p><p><strong>抓牌理由：</strong>{escape(route["picks"])}</p><p class="note">{escape(route["ports"])}</p>')
        page.append('<h3>三张候选配件 · 数值待测试</h3><div class="cards">')
        for card in route['cards']:
            page.append(f'<article class="card archetype-card" id="candidate-{escape(card["id"], quote=True)}"><div class="card-top"><span class="energy" aria-label="{escape(card["cost"], quote=True)}费建议">{escape(card["cost"])}</span><h4>{escape(card["name"])}</h4></div><div class="meta">{escape(card["type"])} · {escape(card["rarity"])}建议 · {escape(card["role"])}</div><p>{card_text(card["text"], terms)}</p><details class="basis"><summary>定位与规则备注</summary><p>{escape(card["note"])}</p></details></article>')
        page.append('</div>')
        example = route['example']
        page.append(f'<aside class="recommendation"><h3>独立算例 · 已计入准备成本</h3><p class="note">{escape(example["setup"])}</p><p>{escape(example["result"])}</p></aside><p><strong>路线取舍：</strong>{escape(route["tradeoff"])}</p><details class="basis"><summary>风险与原作意象</summary><p>{escape(route["risk"])}</p><ul>')
        for lore in route['lore']:
            reference = data['original_reference']['page'] + '#' + lore['entry']
            page.append(f'<li>{escape(lore["text"])} <a href="{escape(reference, quote=True)}">本地原作定位</a></li>')
        page.append('</ul><p>以上原作定位来自本地译文整理；规则与数值为Mod改编。</p></details></section>')
    page.append('<section id="archetype-review" aria-labelledby="archetype-review-title"><h2 id="archetype-review-title">配件关系与记录</h2>')
    for connection in exploration['connections']:
        page.append(f'<p>{escape(connection)}</p>')
    page.append('<h3>先测试什么</h3><ol class="note">')
    for step in exploration['next_steps']:
        page.append(f'<li>{escape(step)}</li>')
    page.append('</ol>')
    for key, label in [('not_archetypes', '暂不独立成流派的效果'), ('boundaries', '候选规则边界')]:
        page.append(f'<details class="basis"><summary>{label}</summary><ul>')
        for note in exploration[key]:
            page.append(f'<li>{escape(note)}</li>')
        page.append('</ul></details>')
    page.append('<details class="basis"><summary>本轮审阅记录 · 同一助手按不同角度检查</summary><ul>')
    for finding in exploration['review']:
        page.append(f'<li><strong>{escape(finding["perspective"])}</strong>：{escape(finding["result"])}</li>')
    page.append('</ul></details><details class="basis"><summary>阅读依据与用途</summary><ul>')
    for source in exploration['sources']:
        page.append(f'<li><a href="{escape(source["href"], quote=True)}">{escape(source["title"])}</a>：{escape(source["use"])}</li>')
    page.append('</ul></details></section>')
    if data.get('archetype_reassessment'):
        page.append('</details>')

if data.get('power_candidates'):
    power_bundle = data['power_candidates']
    terms = {**native_terms, **core_terms}
    page.append(f'<section id="story-powers" aria-labelledby="story-powers-title"><h2 id="story-powers-title">{escape(power_bundle["title"])}<span class="deck-total">{len(power_bundle["items"])} 个</span></h2><p>{escape(power_bundle["intro"])}</p>')
    page.append(f'<p class="generated-note">{escape(power_bundle["recommendation"])}</p><div class="cards">')
    for power in power_bundle['items']:
        source = power['source']
        reference = data['original_reference']['page'] + '#' + source['entry']
        page.append(f'<article class="card story-power" id="power-{escape(power["id"], quote=True)}"><div class="card-top"><span class="energy" aria-label="{escape(power["cost"], quote=True)}费草案">{escape(power["cost"])}</span><h4>{escape(power["name"])}</h4></div><div class="meta">能力牌候选 · {escape(power["role"])} · {escape(power["priority"])}</div><p>{card_text(power["text"], terms)}</p><p class="note">{escape(power["purpose"])}</p>')
        page.append(f'<details class="basis"><summary>剧情出处与触发细则</summary><p><strong>{escape(source["title"])}</strong>：{escape(source["story"])}</p><p><a href="{escape(source["url"], quote=True)}" target="_blank" rel="noopener noreferrer">来源译文</a> · <a href="{escape(reference, quote=True)}">本地索引</a><span class="evidence"> · {escape(grade_labels[source["grade"]])}</span></p><p>改编：{escape(power["adaptation"])}</p><p>持续：{escape(power["duration"])}。叠加：{escape(power["stacking"])}。</p><p>{escape(power["boundary"])}</p><p>例：{escape(power["example"])}</p></details></article>')
    page.append('</div><details class="basis"><summary>Power通用边界与组合复核</summary><ul>')
    for note in power_bundle['notes']:
        page.append(f'<li>{escape(note)}</li>')
    page.append('</ul></details></section>')

for index, scheme in enumerate(data['schemes'], 1):
    terms = {**native_terms, **core_terms, **{rule['term']: rule['text'] for rule in scheme['rules']}}
    for generated in scheme.get('generated_cards', []):
        terms[generated['name']] = f'衍生{generated["type"]}牌。' + ''.join(f'{key}：{native_terms[key]}' for key in generated['keywords'])
    page.append(f'<section id="{scheme["id"]}" aria-labelledby="title-{scheme["id"]}"><h2 id="title-{scheme["id"]}"><span class="number">{index:02d} / </span>{escape(scheme["title"])}</h2><p>{escape(scheme["description"])}</p>')
    for rule in scheme['rules']:
        page.append(f'<p class="definition"><strong>{escape(rule["term"])}</strong><span class="kind">{escape(rule["kind"])}</span><br>{escape(rule["text"])}</p>')
    page.append(f'<p class="note">{escape(scheme["note"])}</p>')
    for generated in scheme.get('generated_cards', []):
        page.append(f'<p class="generated-note"><strong>衍生状态牌 · {escape(generated["name"])}</strong>：{card_text(generated["text"], terms)}{card_properties(generated, terms)}<span>只在当前战斗存在；抽到会占用一个抽牌位。</span></p>')
    if scheme.get('basis'):
        page.append('<details class="basis"><summary>原作依据与改编取舍</summary><ul>')
        for basis in scheme['basis']:
            reference = data['original_reference']['page'] + '#' + basis['entry']
            grade = grade_labels[basis['grade']]
            page.append(f'<li>{escape(basis["text"])} <a href="{escape(basis["source_url"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(basis["source_title"])}</a><span class="evidence"> · {escape(grade)}</span> · <a href="{escape(reference, quote=True)}">资料索引</a><span class="adaptation">改编：{escape(basis["adaptation"])}</span></li>')
        page.append('</ul></details>')
    starter_effect = scheme.get('starter_buff') or scheme.get('starter_relic')
    starter_effect_label = '初始Buff' if scheme.get('starter_buff') else '初始遗物'
    deck = scheme.get('starter_deck')
    if starter_effect or deck:
        page.append('<div class="starter-layout">')
    if starter_effect:
        page.append(f'<aside class="starter-relic" aria-labelledby="starter-effect-{scheme["id"]}"><h3 id="starter-effect-{scheme["id"]}">{starter_effect_label}</h3><h4>{escape(starter_effect["name"])}</h4><p>{card_text(starter_effect["text"], terms)}</p><p class="note">{escape(starter_effect["purpose"])}</p></aside>')
    if deck:
        total = sum(entry['count'] for entry in deck['cards'])
        page.append(f'<div class="starter-deck"><h3 id="deck-{scheme["id"]}">初始牌组<span class="deck-total">{total} 张</span></h3><table class="deck-table" aria-labelledby="deck-{scheme["id"]}"><thead><tr><th scope="col">卡牌</th><th scope="col">数量</th><th scope="col">费用</th><th scope="col">效果</th></tr></thead><tbody>')
        for entry in deck['cards']:
            card = resolve_starter_card(entry, scheme)
            props = card_properties(card, terms)
            properties = f'<br><span class="deck-properties">{props}</span>' if props else ''
            page.append(f'<tr><td><span class="deck-card-name">{escape(card["name"])}</span><small class="deck-type">{escape(card["type"])}</small></td><td class="deck-count">×{entry["count"]}</td><td class="deck-cost">{card_cost_markup(card)}{resource_cost_markup(card)}</td><td>{card_text(card["text"], terms)}{properties}</td></tr>')
        page.append(f'</tbody></table><p class="note starter-note">{escape(deck["note"])}</p></div>')
    if starter_effect or deck:
        page.append('</div>')
    page.append(f'<h3>{escape(scheme.get("cards_label", "样例牌"))}</h3><div class="cards">')
    for card in scheme['cards']:
        meta = card['type'] + (' · ' + card['source'] if card.get('source') else '')
        if card.get('upgraded_cost') is not None:
            meta += f' · 升级后{card["upgraded_cost"]}费'
        props = card_properties(card, terms)
        resource_cost = resource_cost_markup(card)
        page.append(f'<article class="card"><div class="card-top"><span class="energy" aria-label="{card["cost"]}费">{card["cost"]}</span><h4>{escape(card["name"])}</h4>{resource_cost}</div><div class="meta">{escape(meta)}</div><p>{card_text(card["text"], terms)}</p>')
        if card.get('note'):
            page.append(f'<p class="note">{escape(card["note"])}</p>')
        if props:
            page.append(f'<div class="properties">{props}</div>')
        page.append('</article>')
    page.append('</div>')
    if scheme.get('example'):
        example = scheme['example']
        expanded = ' open' if len(data['schemes']) == 1 else ''
        page.append(f'<details class="basis play-examples"{expanded}><summary>出牌与回合选择算例</summary><p>{escape(example["setup"])}</p><ul>')
        for option in example['options']:
            page.append(f'<li><strong>{escape(option["play"])}</strong><span class="result">{escape(option["result"])}</span></li>')
        page.append(f'</ul><p>{escape(example["lesson"])}</p></details>')
    if scheme.get('design_notes'):
        page.append('<details class="basis"><summary>这个方向要检查什么</summary><ul>')
        for note in scheme['design_notes']:
            page.append(f'<li>{escape(note)}</li>')
        page.append('</ul></details>')
    page.append('</section>')

page.append(f'<footer>{escape(data["footer"])}<br><a href="{escape(data["original_reference"]["page"], quote=True)}">原作资料索引（含剧透与证据分级）</a> · <a href="{escape(data["history_page"], quote=True)}">{escape(data.get("history_label", "固定咏唱规则前的五套设计"))}</a></footer></main></body></html>')
(root / '惠惠核心设计简明版.html').write_text(with_design_notice('\n'.join(page), 'legacy-core'), encoding='utf-8')
if data.get('other_systems_exploration'):
    other = data['other_systems_exploration']
    report_head = page[0].replace(f'<title>{escape(data["title"])}</title>', f'<title>{escape(other["title"])}</title>')
    report_head = report_head.replace('</style>', '.brainstorm-seeds{grid-template-columns:repeat(2,minmax(0,1fr))}@media(max-width:600px){.brainstorm-seeds{grid-template-columns:1fr}}</style>')
    report = [report_head, f'<header><h1>{escape(other["title"])}</h1><p>{escape(other["intro"])}</p><p class="note">{escape(other["scope"])}</p></header><nav aria-label="体系候选">']
    report.append('<a href="#recorded-decisions">已记录方向</a><a href="#personal-traits">本人特点与出处</a>')
    for direction in other['directions']:
        report.append(f'<a href="#{escape(direction["id"], quote=True)}">{escape(direction["name"].split("：")[0])}</a>')
    report.append('<a href="#lore-material">其他概念</a><a href="#parked-directions">先前候选</a><a href="惠惠核心设计简明版.html#hanging-declaration">返回当前宣言</a></nav>')
    report.append('<section id="recorded-decisions"><h2>已记录的两个方向</h2>')
    for decision in other['decisions']:
        links = ' · '.join(f'<a href="{escape(ref["href"], quote=True)}">{escape(ref["label"])}</a>' for ref in decision['refs'])
        report.append(f'<article id="{escape(decision["id"], quote=True)}"><h3>{escape(decision["name"])} → {escape(decision["placement"])}</h3><p class="note">{escape(decision["status"])}</p><p>{escape(decision["record"])}</p><details class="basis"><summary>未定事项与题材依据</summary><p>{escape(decision["pending"])}</p>{links}</details></article>')
    report.append('</section><section id="personal-traits"><h2>从本人情节到设计用途</h2>')
    requested = other['requested_source']
    report.append(f'<details class="basis"><summary>本轮来源与萌娘百科访问情况</summary><p>{escape(other["research_note"])}</p><a href="{escape(requested["href"], quote=True)}">{escape(requested["label"])}</a></details>')
    for trait in other['personal_traits']:
        links = ' · '.join(f'<a href="{escape(ref["href"], quote=True)}">{escape(ref["label"])}</a>' for ref in trait['refs'])
        report.append(f'<article id="trait-{escape(trait["id"], quote=True)}"><h3>{escape(trait["name"])}</h3><p><strong>原作情节：</strong>{escape(trait["fact"])}</p><p><strong>设计解读：</strong>{escape(trait["interpretation"])}</p><p><strong>适合做什么：</strong>{escape(trait["use"])}</p><details class="basis"><summary>出处与边界</summary><p>{escape(trait["limit"])}</p>{links}</details></article>')
    report.append(f'</section><aside class="recommendation"><h3>当前建议</h3><p>{escape(other["recommendation"])}</p></aside><div class="table-scroll"><table class="deck-table comparison-table"><caption>两个新候选，尚未选定为正式体系</caption><thead><tr><th scope="col">候选</th><th scope="col">经营的对象</th><th scope="col">核心选择</th><th scope="col">当前成熟度</th></tr></thead><tbody>')
    for direction in other['directions']:
        report.append(f'<tr><td><a href="#{escape(direction["id"], quote=True)}">{escape(direction["name"])}</a></td><td>{escape(direction["core"])}</td><td>{escape(direction["decision"])}</td><td>{escape(direction["maturity"])}</td></tr>')
    report.append('</tbody></table></div>')
    for direction in other['directions']:
        links = ' · '.join(f'<a href="{escape(ref["href"], quote=True)}">{escape(ref["label"])}</a>' for ref in direction['refs'])
        report.append(f'<section id="{escape(direction["id"], quote=True)}"><h2>{escape(direction["name"])}</h2><p class="note">{escape(direction["maturity"])}</p><p><strong>原作素材：</strong>{escape(direction["canon"])}</p><div class="basis">{links}</div><p class="definition"><strong>机制骨架</strong><br>{escape(direction["core"])}</p><p><strong>怎样运转：</strong>{escape(direction["loop"])}</p><p><strong>玩家选择：</strong>{escape(direction["decision"])}</p><p><strong>为什么拿不同的牌：</strong>{escape(direction["picks"])}</p><h3>用于理解机制的样例，尚非完整卡表</h3><div class="cards brainstorm-seeds">')
        for seed in direction['seeds']:
            report.append(f'<article class="card"><div class="card-top"><span class="energy">{escape(seed["cost"])}</span><h4>{escape(seed["name"])}</h4></div><p>{escape(seed["text"]).replace(chr(10), "<br>")}</p><details class="basis"><summary>口径与设计边界</summary><p>{escape(seed["note"])}</p></details></article>')
        report.append(f'</div><p class="note">与当前体系的关系：{escape(direction["independent"])}</p><aside class="recommendation"><h3>还缺什么证明</h3><p>{escape(direction["gap"])}</p></aside><p class="note">{escape(direction["boundary"])}</p></section>')
    report.append('<section id="lore-material"><h2>值得继续挖掘的原作概念</h2><p>以下有具体题材价值，但暂时不强行命名为完整流派。</p><div class="table-scroll"><table class="deck-table comparison-table"><thead><tr><th scope="col">概念</th><th scope="col">本地资料支持的含义</th><th scope="col">值得继续想什么</th></tr></thead><tbody>')
    for concept in other['concepts']:
        links = ' · '.join(f'<a href="{escape(ref["href"], quote=True)}">{escape(ref["label"])}</a>' for ref in concept['refs'])
        report.append(f'<tr><td>{escape(concept["name"])}</td><td>{escape(concept["fact"])}<div class="basis">{links}</div></td><td>{escape(concept["opening"])}</td></tr>')
    report.append('</tbody></table></div></section><section id="parked-directions"><h2>先前候选：保留，但调整优先级</h2>')
    for direction in other['parked_directions']:
        report.append(f'<details class="basis" id="{escape(direction["id"], quote=True)}"><summary>{escape(direction["name"])}</summary><p><strong>当前判断：</strong>{escape(direction["park_reason"])}</p><p><strong>历史机制草案：</strong>{escape(direction["core"])}</p><p>{escape(direction["boundary"])}</p></details>')
    report.append(f'</section><section><h2>比较标准</h2><p>{escape(other["comparison"])}</p><p>{escape(other["next"])}</p></section><footer>{escape(other["date"])} · 机制发散与原作素材整理。<a href="惠惠核心设计简明版.html">返回当前设计</a> · <a href="素晴爆裂魔法原作资料索引.html">本地原作资料索引</a></footer></main></body></html>')
    (root / other['page']).write_text(with_design_notice('\n'.join(report), 'other-research'), encoding='utf-8')
    print(f'Brainstorm report: {len(other["directions"])} tentative mechanisms, {len(other["concepts"])} lore concepts.')
print(f'Generated: {len(data["schemes"])} mechanisms with starter effects and decks, {sum(len(s["cards"]) for s in data["schemes"])} displayed cards.')
if data.get('hanging_declarations'):
    print('Current declaration: one user reference card, interactive 0/3 progress, +2 energy and discard on completion.')
if data.get('power_candidates'):
    print(f'Added: {len(data["power_candidates"]["items"])} story-based Power candidates.')
if data.get('archetype_exploration'):
    routes = data['archetype_exploration']['routes']
    label = 'component groups' if data.get('archetype_reassessment') else 'archetype analyses'
    print(f'Added: {len(routes)} {label}, {sum(len(r["cards"]) for r in routes)} proposed cards.')
if data.get('archetype_reassessment'):
    directions = data['archetype_reassessment']['directions']
    print(f'Reassessment: existing engine plus {len(directions) - 1} unconfirmed directions; {sum(len(d["seeds"]) for d in directions)} mechanism seeds.')
