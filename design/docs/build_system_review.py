"""Render the qualitative system review. Does not alter gameplay or run models."""
from pathlib import Path
from html import escape
import json
import re
from megumin_system_analysis import load as load_audit, render_full, AUDIT_CSS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
d = json.loads((HERE / '体系复盘与补充建议.json').read_text(encoding='utf-8'))
if d.get('superseded_by'):
    print('旧体系复盘已归档；当前统一体系表请运行 build_system_tables.py。')
    raise SystemExit(0)

evidence = json.loads((HERE / '体系复盘源码依据.json').read_text(encoding='utf-8'))
prior = json.loads((HERE / '体系复盘既有研究依据.json').read_text(encoding='utf-8'))
audit, audit_cards, audit_fingerprint = load_audit()
full_audit = render_full(audit, audit_cards, audit_fingerprint)
study_map = {x['id']: x for x in prior['files']}
e = escape
source_map = {x['id']: x for x in evidence['files']}
aliases = {
    'DarkEmbracePower': '黑暗之拥：消耗抽牌',
    'FeelNoPainPower': '无惧疼痛：消耗格挡',
    'BarricadePower': '壁垒：保留格挡',
    'CorruptionPower': '腐化：技能减费与消耗',
    'PoisonPower': '中毒结算',
    'EnvenomPower': '涂毒：攻击连接中毒',
    'LightningOrb': '闪电球',
    'DarkOrb': '黑暗球',
    'HauntPower': '纠缠：灵魂连接伤害',
    'DevourLifePower': '吞噬生命：灵魂连接召唤',
    'DoomPower': '灾厄判定',
    'KarenStageIsWaitingPower': '舞台正在等待着：取空回能',
    'KarenStarlight02Power': 'Starlight第二幕：重放与耗尽',
}


def ul(items):
    return '<ul>' + ''.join('<li>' + e(x) + '</li>' for x in items) + '</ul>'


def refs(ids):
    assert all(key in source_map for key in ids)
    return ' · '.join('<a href="#source-' + e(key) + '">' +
                      e(aliases.get(key, source_map[key]['title'])) + '</a>' for key in ids)


def table(headers, rows, css=''):
    return '<div class="table-scroll ' + css + '"><table><thead><tr>' + ''.join(
        '<th scope="col">' + e(x) + '</th>' for x in headers
    ) + '</tr></thead><tbody>' + ''.join(
        '<tr><th scope="row">' + row[0] + '</th>' + ''.join('<td>' + x + '</td>' for x in row[1:]) + '</tr>'
        for row in rows
    ) + '</tbody></table></div>'


inventory = table(['内容与层次', '当前设计', '复盘判断'], [
    ['<a href="' + e(x['href']) + '">' + e(x['name']) + '</a><small>' + e(x['layer']) + ' · ' + e(x['state']) + '</small>',
     e(x['current']), e(x['assessment'])] for x in d['inventory']
])
def study_refs(ids):
    assert all(key in study_map for key in ids)
    return ' · '.join('<a href="#research-' + e(key) + '">' + e(study_map[key]['title']) + '</a>' for key in ids)

comparison_rows = []
for x in d['comparison']:
    citations = '<details class="compact"><summary>代表卡牌关系与源码</summary><p>' + e(x['shared']) + '</p><p>' + e(x['outputs']) + '</p><p>' + e(x['decision']) + '</p><p>' + refs(x['sources']) + '</p></details>'
    comparison_rows.append([
        e(x['name']) + '<small>' + e(x['structure_basis']) + '</small>',
        ul(x['major_systems']), ul(x['minor_systems']),
        '<p>' + e(x['lesson']) + '</p><p>' + study_refs(x['study_refs']) + '</p>' + citations
    ])
comparison = table(['角色与分类依据', '大体系／主轴', '小体系／副轴或连接层', '修正与对惠惠的启发'], comparison_rows, 'comparison')
correction_blocks = ''.join('<article class="review-finding"><h3>' + e(x['problem']) + '</h3><p><b>上一版：</b>' + e(x['before']) + '</p><p><b>本次修正：</b>' + e(x['after']) + '</p><p>' + study_refs(x['sources']) + '</p></article>' for x in d['analysis_corrections'])
port_table = table(['当前定位与核心', '来源与触发', '已有端口', '需要补齐'], [
    [e(x['name']) + '<small>' + e(x['level']) + '</small><p>' + e(x['core']) + '</p>',
     e(x['trigger']), '<p><b>输出：</b>' + e(x['output']) + '</p><p><b>防御：</b>' + e(x['defense']) + '</p><p><b>运转：</b>' + e(x['engine']) + '</p>', e(x['gap'])]
    for x in d['megumin_systems']
])
research_entries = ''.join('<details class="source-entry" id="research-' + e(x['id']) + '"><summary>' + e(x['title']) + '</summary><p>' + e(x['use']) + '</p><p><a href="' + e(x['href']) + '">打开原文</a> · 原文起始行 ' + str(x['line']) + '</p><p class="source-path">' + e(x['path']) + '</p><p class="muted">SHA256：' + e(x['sha256']) + '</p><pre>' + e(x['excerpt']) + '</pre></details>' for x in prior['files'])
findings = ''.join(
    '<article class="review-finding" id="finding-' + e(x['id']) + '"><span class="badge">' + e(x['priority']) +
    '</span><h3>' + e(x['title']) + '</h3><p>' + e(x['observation']) + '</p><p class="proposal"><b>建议：</b>' +
    e(x['proposal']) + '</p><p class="muted">' + e(x['reason']) + '</p>' +
    ('<details class="compact"><summary>参考关系</summary><p>' + refs(x['sources']) + '</p></details>' if x['sources'] else '') +
    '</article>' for x in d['findings']
)
routes = ''.join(
    '<article class="route"><span class="eyebrow">' + e(x['status']) + '</span><h3>' + e(x['name']) + '</h3>' +
    '<dl><dt>想要的牌</dt><dd>' + e(x['wants']) + '</dd><dt>怎样行动</dt><dd>' + e(x['action']) +
    '</dd><dt>专属投入</dt><dd>' + e(x['investment']) + '</dd><dt>尚缺什么</dt><dd>' + e(x['missing']) + '</dd></dl></article>'
    for x in d['routes']
)
card_review = table(['卡牌', '处理建议', '原因'], [
    [e(x['name']), '<span class="badge draft">' + e(x['action']) + '</span>', e(x['detail'])] for x in d['card_review']
])
rules = table(['规则', '现状', '建议与边界'], [[e(x['topic']), e(x['current']), e(x['proposal'])] for x in d['rule_questions']])
not_now = table(['方向', '当前建议', '理由'], [[e(x['name']), e(x['decision']), e(x['reason'])] for x in d['not_now']])
sources = ''.join(
    '<details class="source-entry" id="source-' + e(x['id']) + '"><summary>' +
    e(aliases.get(x['id'], x['title'])) + ' <span class="muted">' + e(x['id']) + '</span></summary>' +
    '<p class="source-path">' + e(x['path']) + '</p><p class="muted">SHA256：' + e(x['sha256']) + '</p>' +
    ('<p>' + e(x['description']).replace('\n', '<br>') + '</p>' if x['description'] else '') +
    '<pre><code>' + e(x['excerpt']) + '</code></pre></details>' for x in evidence['files']
)
web_sources = ''.join('<li><a href="' + e(x['url']) + '">' + e(x['title']) + '</a>：' + e(x['use']) + '</li>' for x in evidence['web_sources'])
base = (ROOT / '惠惠当前设计总览.html').read_text(encoding='utf-8')
style = re.search(r'<style>(.*?)</style>', base, re.S).group(1)
style += AUDIT_CSS
style += '''
.review-finding{border-top:1px solid var(--border);padding:25px 0}.review-finding h3{margin-top:14px;font-family:var(--serif);font-size:25px}.proposal{border-left:3px solid var(--green);padding:12px 17px;background:#eef1e8}.summary-strip{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;margin:28px 0}.summary-strip>div{border-top:2px solid var(--red);padding-top:13px}.summary-strip b{font:21px var(--serif);display:block}.summary-strip p{font-size:13px;color:var(--text-dim);margin-top:8px}.review-scope{font-size:13px;color:var(--text-dim)}.comparison table{min-width:1000px}.comparison tbody th{width:10%}.comparison td:nth-child(2){width:25%}.comparison td:nth-child(3){width:34%}.comparison td:nth-child(4){width:31%}.compact{font-size:12px;padding:10px 0}.compact[open]>summary{margin-bottom:10px}.compact p{font-size:12px;line-height:2}.route{padding:25px;border:1px solid var(--border);background:var(--surface)}.route h3{font:29px var(--serif);margin-top:12px}dt{font-size:12px;color:var(--red);font-weight:700;margin-top:15px}dd{margin:5px 0 17px;font-size:14px}.source-entry{scroll-margin-top:40px;border-top:1px solid var(--border)}.source-entry>summary{font-size:14px}.source-path{font-size:12px;overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.65 var(--mono);background:#efe9df;padding:17px;max-height:480px;overflow:auto}.return-link{font-size:13px}.review-next li{padding:8px 0;font-size:16px}.review-keyline{font-size:19px;line-height:1.8;color:var(--red)}
@media(max-width:700px){.summary-strip{grid-template-columns:1fr;gap:10px}.route{padding:20px}.review-finding h3{font-size:22px}}
'''
page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>惠惠体系复盘 · 原版五职业与Karen</title><style>@@STYLE@@</style></head><body><div class="wrap"><nav class="toc" aria-label="体系复盘章节"><strong>MEGUMIN / REVIEW</strong><a href="#megumin-audit">惠惠逐项分析</a><a href="#audit-explosion">爆裂逐卡定位</a><a href="#audit-declaration">宣言逐卡定位</a><a href="#audit-bonus">增伤小体系</a><a href="#audit-support">共享燃料与配套</a><a href="#basis">文档与纠正依据</a><a href="#inventory">当前全部内容</a><a href="#ports">惠惠体系完整性</a><a href="#comparison">原版五职业与Karen</a><a href="#findings">需要补充什么</a><a href="#routes">两套体系怎样连接</a><a href="#cards">现有卡牌怎么处理</a><a href="#rules">先明确宣言规则</a><a href="#not-now">暂不新增的体系</a><a href="#next">写卡顺序</a><a href="#sources">来源与范围</a><a href="惠惠当前设计总览.html">返回当前总览</a></nav><main class="main"><header><span class="eyebrow">SYSTEM REVIEW · 2026.10.09</span><h1>从共同核心，<br><em>看体系是否完整。</em></h1><p class="lead">@@VERDICT@@</p><p>@@SUMMARY@@</p><div class="summary-strip"><div><b>爆裂：主体系候选</b><p>爆裂狂提供入口，吟唱记录技能，回合末统一兑现。</p></div><div><b>增伤：爆裂内的小配套</b><p>卡面直接写下一次伤害提高多少；不再设威力关键词。</p></div><div><b>宣言：主体系候选</b><p>围绕悬挂与完成，连接运转、防守和爆裂输出。</p></div></div><p class="review-scope">@@BOUNDARY@@</p><p class="review-scope">@@SCOPE@@</p></header>
@@FULL_AUDIT@@
<section id="basis"><span class="eyebrow">00 / RESTORED RESEARCH</span><h2 class="section-title">先纠正体系与伤害路线的混用</h2><p>已找回五职业的逐职业体系分析、体系判定流程，以及Karen的设计文档。上文已将分析模板实际用于惠惠；下面保留此前找回的原研究分类与纠错依据。</p>@@ANALYSIS_CORRECTIONS@@<p><a href="#prior-research">查看12份原文与摘录 →</a></p></section>
<section id="inventory"><span class="eyebrow">01 / CURRENT DESIGN</span><h2 class="section-title">按共同核心整理当前体系与其他内容</h2><p>爆裂与宣言分别作为主体系候选，增伤是用户指定的小配套；长篇咏唱是组合构筑，联机卡和局外成长另列。主体系候选表示值得按完整体系继续设计，不表示当前卡池已成熟。</p>@@INVENTORY@@<details><summary>这次如何判断体系是否成立</summary>@@PRINCIPLES@@</details></section>
<section id="ports"><span class="eyebrow">PORTS AND CARD ROLES</span><h2 class="section-title">分别检查爆裂、宣言与增伤小配套</h2><p>来源与收益是否成对，输出、防御、运转由哪些牌承接，再看缺少引导、基础、核心、突破还是中坚牌。共享一个伤害出口不妨碍两个体系成立。</p>@@PORTS@@</section>
<section id="comparison"><span class="eyebrow">02 / SIX REFERENCES</span><h2 class="section-title">六职业按原研究的大／小体系重新对照</h2><p>五职业列出原分析文档中的完整体系分组；Karen采用自身设计文档的双主轴与副轴分类。这些是既有研究结论，非官方分类或最新版本重计，不能把数量直接当作惠惠的配额。</p>@@COMPARISON@@<div class="notice"><p><b>统一口径：</b>先看共同核心、稳定触发与收益、多个端口和牌间需求。输出主轴只是其中一个观察角度；运转体系能成为大体系，同一大体系内也能存在不同构筑方向。</p></div></section>
<section id="findings"><span class="eyebrow">03 / GAPS AND CHANGES</span><h2 class="section-title">按体系缺口补牌，再决定是否新增主轴</h2><p class="review-scope">以下补充建议尚未采用；现有卡面已同步取消威力关键词的决定。</p>@@FINDINGS@@</section>
<section id="routes"><span class="eyebrow">04 / BUILD DIRECTIONS</span><h2 class="section-title">爆裂与宣言各有经营对象，可以共同构筑</h2><div class="two">@@ROUTES@@</div><div class="notice"><p>@@DECISION_EXAMPLE@@</p></div><p class="review-keyline">这里比较两个主体系候选的经营重点；具体卡组可以同时使用它们。增伤继续作为爆裂内的小配套。</p></section>
<section id="cards"><span class="eyebrow">05 / CARD RESPONSIBILITIES</span><h2 class="section-title">哪些保留，哪些值得重新写</h2><p>去掉宣言的即时效果后，要同步检查配套的用途，而不只是删掉卡面第一行。</p>@@CARD_REVIEW@@<p><a href="惠惠当前设计总览.html#declaration-cards">查看当前宣言与配套</a> · <a href="惠惠长篇咏唱流派设计.html#cards">查看6张长篇咏唱候选</a></p></section>
<section id="rules"><span class="eyebrow">06 / DECLARATION RULES</span><h2 class="section-title">多张宣言如何推进，需要先决定</h2><p>“全部各自计数”偏向并行准备；“只推进最早一张”偏向队列管理。它们会改变抓牌价值和行动顺序，不能等到做数值时才补。</p>@@RULES@@<p class="muted">这里只提出规则选择；不把建议写成用户已确认，也不从能量球的外观自动继承槽位、激发或顶出。</p></section>
<section id="not-now"><span class="eyebrow">07 / SCOPE CONTROL</span><h2 class="section-title">这些方向现在不必一起重开</h2>@@NOT_NOW@@</section>
<section id="next"><span class="eyebrow">08 / NEXT CARDS</span><h2 class="section-title">接下来按这个顺序写卡</h2><ol class="review-next">@@NEXT@@</ol><p class="return-link"><a href="惠惠当前设计总览.html">回到已给规则与当前卡面 →</a></p></section>
<section id="sources"><span class="eyebrow">09 / EVIDENCE</span><h2 class="section-title">来源与核对范围</h2><div id="prior-research"><h3>找回的体系分析原文</h3><p>@@PRIOR_SCOPE@@</p>@@PRIOR_RESEARCH@@<p><a href="docs/体系复盘既有研究依据.json">既有研究摘录与路径快照</a></p></div><h3>此前已核对的代表卡牌源码</h3><p>@@SCOPE@@</p><p>@@METHOD@@</p><p>本次保留42个本地源码文件的内容、路径和SHA256，下面摘录关键逻辑。与既有证据重叠的文件摘要均一致；新补来源独立保存。</p><ul>@@WEB_SOURCES@@</ul><details><summary>避免把旧版本或简写带入分析</summary>@@CORRECTIONS@@</details>@@SOURCES@@<p><a href="docs/体系复盘源码依据.json">完整本地来源快照</a> · <a href="docs/体系复盘与补充建议.json">结构化分析与建议</a></p></section><footer>机制复盘与文档整理；未实装新卡或改动游戏源码，未进行实战或数值模型。<a href="惠惠当前设计总览.html">当前总览</a></footer></main></div></body></html>'''
values = {
    'FULL_AUDIT': full_audit, 'STYLE': style, 'VERDICT': e(d['verdict']), 'SUMMARY': e(d['summary']),
    'ANALYSIS_CORRECTIONS': correction_blocks, 'PORTS': port_table,
    'PRIOR_SCOPE': e(prior['scope']), 'PRIOR_RESEARCH': research_entries,
    'BOUNDARY': e(d['boundary']), 'SCOPE': e(evidence['scope']), 'METHOD': e(evidence['method']),
    'INVENTORY': inventory, 'PRINCIPLES': ul(d['principles']), 'COMPARISON': comparison,
    'FINDINGS': findings, 'ROUTES': routes, 'DECISION_EXAMPLE': e(d['decision_example']),
    'CARD_REVIEW': card_review, 'RULES': rules, 'NOT_NOW': not_now,
    'NEXT': ''.join('<li>' + e(x) + '</li>' for x in d['next_steps']),
    'WEB_SOURCES': web_sources, 'CORRECTIONS': ul(d['corrections']), 'SOURCES': sources,
}
for key, value in values.items():
    page = page.replace('@@' + key + '@@', value)
assert '@@' not in page
out = ROOT / '惠惠体系复盘与六职业对照.html'
out.write_text(page, encoding='utf-8')
portable = page
for href in re.findall(r'href="([^"]+)"', page):
    if not href.startswith(('#', 'http:', 'https:', 'file:')):
        filename, sep, fragment = href.partition('#')
        portable = portable.replace('href="' + href + '"', 'href="' + (ROOT / filename).resolve().as_uri() + sep + fragment + '"')
target = Path.home() / '.agent/diagrams'
target.mkdir(exist_ok=True, parents=True)
(target / 'megumin-system-review.html').write_text(portable, encoding='utf-8')
print(json.dumps({'inventory': len(d['inventory']), 'comparisons': len(d['comparison']), 'findings': len(d['findings']), 'source_files': len(evidence['files']), 'output': str(out)}, ensure_ascii=False))
