"""Render the skill-chain proposal and verify its explicit paper resource ledger."""
from pathlib import Path
from html import escape
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
d = json.loads((HERE/'长篇咏唱流派草案.json').read_text(encoding='utf-8'))
evidence = json.loads((HERE/'长篇咏唱原版与Karen参考.json').read_text(encoding='utf-8'))
cards = {c['id']: c for c in d['cards']}
e = escape

def ul(items):
    return '<ul>'+''.join('<li>'+e(s)+'</li>' for s in items)+'</ul>'

def simulate(explosion_cost):
    """Only the specified hand, draw order and action sequence; no game simulation."""
    hand = list(d['example']['starting_hand'])
    draw_pile = list(d['example']['draw_pile'])
    energy, k, bonus, block, discount, token_serial = 3, 0, 0, 0, 0, 0
    max_hand, chanting, stopped = len(hand), False, None
    rows = []
    lookup = {'unfold_a':'unfold','unfold_b':'unfold','steady_a':'steady','steady_b':'steady'}
    def card_info(ident):
        if ident == 'explosion': return '爆裂魔法', explosion_cost
        if ident == 'continuation': return '咒文续接', 0
        if ident == 'defend': return '防御', 1
        if ident.startswith('token_'): return '爆裂咒文', 0
        c = cards[lookup.get(ident,ident)]
        return c['name'], c['cost']
    for ident in d['example']['actions'] + ['defend']:
        assert ident in hand, (ident,hand)
        name, base_cost = card_info(ident)
        paid = max(0,base_cost-discount)
        if paid > energy:
            stopped = f'剩{energy}能量，不能支付{name}的{paid}费。'
            break
        discount = 0
        energy -= paid
        hand.remove(ident)
        if chanting:
            k += 1
        detail = ''
        tokens, draws = 0, 0
        if ident == 'explosion':
            chanting = True
            detail = '开始吟唱；本牌不计K，结算后进入消耗牌堆。'
        elif ident == 'continuation':
            energy += 1
            draws = 2
            detail = '回1能量，抽稳住声线与防御；本牌消耗。'
        elif ident == 'breath':
            discount = cards['breath']['values']['next_skill_discount']
            detail = '下一张技能减费1；本牌消耗。'
        elif ident.startswith('unfold_'):
            tokens = cards['unfold']['values']['tokens']
            detail = f'生成{tokens}张咒文；生成本身不计K。'
        elif ident.startswith('steady_'):
            block += cards['steady']['values']['block']
            tokens = cards['steady']['values']['tokens']
            detail = '获得6格挡并生成1张咒文。'
        elif ident.startswith('token_'):
            bonus += 2
            detail = '下一次爆裂魔法造成的伤害提高2点；作为技能也计1次K，随后消耗。'
        elif ident == 'trim':
            target = d['example']['consume_target']
            assert target in hand
            hand.remove(target)
            draws = cards['trim']['values']['draw']
            detail = '消耗打击，抽第二张展开与稳住声线；本牌也消耗。'
        elif ident == 'defend':
            block += 5
            detail = '只有爆裂0费的比较中还有能量打出这张普通防御。'
        for _ in range(tokens):
            token_serial += 1
            hand.append(f'token_{token_serial}')
        for _ in range(draws):
            assert draw_pile, 'The ledger never assumes additional draws or a reshuffle.'
            hand.append(draw_pile.pop(0))
        max_hand = max(max_hand,len(hand))
        rows.append({'action':name,'paid':paid,'energy':energy,'hand':len(hand),'skills':k,'bonus':bonus,'block':block,'detail':detail})
    return {'explosion_cost':explosion_cost,'skills':k,'bonus':bonus,'damage':k+bonus,'block':block,'energy':energy,'max_hand':max_hand,'remaining_hand':hand,'stopped':stopped,'steps':rows,'post_resolution_bonus':0}

ledgers = [simulate(cost) for cost in [3,2,1,0]]
main = ledgers[2]
assert [main[k] for k in ['skills','bonus','damage','block','energy','max_hand']] == [13,12,25,12,0,6]
assert [ledgers[0][k] for k in ['skills','bonus','damage','block']] == [8,6,14,6]
assert all(x['max_hand']<=6 and x['energy']>=0 for x in ledgers)
(HERE/'长篇咏唱资源账.json').write_text(json.dumps({'scope':'纸面指定序列，不是游戏实测；全部未升级。','cases':ledgers},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

base = (ROOT/'惠惠当前设计总览.html').read_text(encoding='utf-8')
style = re.search(r'<style>(.*?)</style>',base,re.S).group(1)
style += '''
.new-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px 34px}.draft-card{min-width:0;border-top:2px solid var(--red);padding-top:22px;scroll-margin-top:25px}.draft-card .meta{font:12px var(--mono);color:var(--red)}.draft-card h3{font:27px var(--serif);margin:12px 0}.draft-card .text{font-size:17px}.draft-card .role{color:var(--green);font-size:13px}.draft-card details,.draft-card details p{font-size:13px}.numbers{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;margin:24px 0}.numbers>div{border-top:1px solid var(--border);padding-top:16px;min-width:0}.numbers strong{display:block;font:36px var(--mono);color:var(--red)}.numbers span{font-size:13px;color:var(--text-dim)}.ledger{min-width:880px}.ledger th,.ledger td{padding-right:14px}.ledger th{width:auto}.ledger td:last-child{min-width:280px}.fee-table{min-width:660px}.source-files{overflow-wrap:anywhere}.source-files details{margin-bottom:15px}.source-files code{font-size:11px}.inline-rule{border-left:3px solid var(--green);padding:12px 18px;margin:16px 0}.source-files p{margin-bottom:10px}@media(max-width:750px){.new-cards{grid-template-columns:1fr}.numbers{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''
card_blocks=''.join(f'''<article class="draft-card" id="card-{e(c['id'])}"><span class="meta">{c['cost']}费 · {e(c['type'])} · {e(c['rarity'])} · 助手候选</span><h3>{e(c['name'])}</h3><p class="role">{e(c['role'])}</p><p class="text"><b>{e(c['text'])}</b></p><p class="muted">升级：{e(c['upgrade'])}</p><p>{e(c['why'])}</p><details><summary>代价与参考关系</summary><p>{e(c['tradeoff'])}</p><p class="muted">{e(c['reference'])}</p></details></article>''' for c in d['cards'])
steps=''.join(f'''<tr><th scope="row">{i}. {e(x['action'])}</th><td>{x['paid']}</td><td>{x['energy']}</td><td>{x['hand']}</td><td>{x['skills']}</td><td>{x['bonus']}</td><td>{x['block']}</td><td>{e(x['detail'])}</td></tr>''' for i,x in enumerate(main['steps'],1))
comparison=''.join(f'''<tr><th scope="row">{x['explosion_cost']}费爆裂</th><td>{x['skills']}</td><td>{x['bonus']}</td><td>{x['damage']}</td><td>{x['block']}</td><td>{x['energy']}</td></tr>''' for x in ledgers)
source_rows=''.join(f'''<details><summary>{e(s['title'])} · {e(s['id'])}</summary><p>{e(s['verified'])}</p><p><a href="{e(Path(s['path']).as_uri())}">{e(s['path'])}</a></p><code>SHA256 {e(s['sha256'])}</code></details>''' for s in evidence['files'])
page=r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>惠惠 · 长篇咏唱与联机爆裂</title><style>@@STYLE@@</style></head><body><div class="wrap"><nav class="toc" aria-label="设计章节"><strong>MEGUMIN / LONG CHANT</strong><a href="#core">用户核心规则</a><a href="#coop">人人都是爆裂狂</a><a href="#engine">怎样连续打技能</a><a href="#cards">6张配套候选</a><a href="#ledger">逐步资源账</a><a href="#limits">代价与验证</a><a href="#sources">原版与Karen参考</a><a href="惠惠当前设计总览.html#explosion">返回总览</a></nav><main class="main"><header><span class="eyebrow">EXPLOSION ARCHETYPE · 2026.10.09</span><h1>长篇咏唱，<br><em>把整段准备变成爆裂。</em></h1><p class="lead">@@THESIS@@</p><div class="notice"><p><b>@@STATUS@@。</b></p><p>这是爆裂体系内的技能连打构筑；已停止的独立非攻击伤害流及其8张牌不恢复。</p></div></header>
<section id="core"><span class="eyebrow">01 / USER RULES</span><h2>爆裂狂提供入口，保留创造等待窗口</h2><div class="definition"><h3>玩家Buff：爆裂狂</h3><p>@@BUFF@@</p></div><article class="spell"><span class="cost">3费 · 保留 · 消耗 · 用户指定</span><h3>爆裂魔法</h3><p>@@EXPLOSION@@</p></article><div class="two"><div class="definition"><h3>吟唱（姿态）</h3><p>@@CHANT@@</p></div><div class="definition"><h3>爆裂增伤配套（无关键词）</h3><p>卡面直接描述：@@BONUS@@</p><p class="muted">爆裂咒文：@@TOKEN@@</p></div></div><p>@@WAITING@@</p><div class="inline-rule"><b>默认规则：</b>吟唱期间不能再次打出爆裂。爆裂本身不计K；卡面与姿态说明指向同一次回合末伤害。</div><details><summary>已给规则与本稿推演边界</summary>@@CONFIRMED@@@@WORKING@@</details><p class="muted">@@OLD_STORAGE@@</p></section>
<section id="coop"><span class="eyebrow">02 / CO-OP CARD</span><h2>人人都是爆裂狂</h2><article class="spell"><span class="cost">2费 → 升级1费 · 用户指定</span><p>@@COOP_TEXT@@</p><small>牌种与稀有度未定；不擅自附加消耗。</small></article><p>@@COOP_SCOPE@@</p><p>@@COOP_EXAMPLE@@</p><div class="calc"><div class="controls"><div><label for="cost-global">本场全局减费 D <b id="cost-global-value">0</b></label><input id="cost-global" type="range" min="0" max="3" value="0"></div><div><label for="cost-held">这张爆裂累计减费 A <b id="cost-held-value">0</b></label><input id="cost-held" type="range" min="0" max="3" value="0"></div></div><div class="calc-result" aria-live="polite"><strong id="current-cost">3</strong><div><p id="cost-formula">max(0, 3－0－0)＝3费</p><small>新生成的另一张爆裂不继承旧牌的A，只继承本场D；下一战D重置。</small></div></div></div><details><summary>重复获得、范围与未定项</summary>@@COOP_NOTES@@</details></section>
<section id="engine"><span class="eyebrow">03 / THE ENGINE</span><h2>一串技能，需要手牌、能量和防守同时成立</h2>@@ROLES@@<article class="definition"><h3>继续使用：咒文续接 · 0费技能</h3><p><b>@@CONTINUATION@@</b></p><p class="muted">用户此前指定，名称暂定；稀有度与升级未定。进入吟唱后可以在0能量时打出，计1次K，提供1能量并抽2。</p></article><p>每张爆裂咒文在吟唱中打出时，按建议的技能类型贡献1次K与2点额外增伤，总计增加3点群伤。生成咒文不直接计数，消耗而未打出的咒文也没有这份收益。</p></section>
<aside class="notice"><p>@@DECLARATION_SYNERGY@@</p><a href="惠惠当前设计总览.html#declaration-cards">查看当前宣言与配套 →</a></aside><section id="cards"><span class="eyebrow">04 / SIX CANDIDATES</span><h2>6张新牌，各自解决一个瓶颈</h2><p class="muted">2普通、3罕见、1稀有；5技能、1能力。名称、数值、稀有度与升级都是候选，不是已采用卡池。</p><div class="new-cards">@@CARDS@@</div></section>
<section id="ledger"><span class="eyebrow">05 / PAPER RESOURCE LEDGER</span><h2>指定一手牌，逐张核算能否打出来</h2><p>@@EXAMPLE_SETUP@@</p><div class="numbers"><div><strong>13</strong><span>吟唱期间技能牌数</span></div><div><strong>12</strong><span>6张咒文提供的额外增伤</span></div><div><strong>25</strong><span>每个敌人的原始伤害</span></div><div><strong>12</strong><span>本回合格挡</span></div></div><div class="table-scroll"><table class="ledger"><thead><tr><th>依次打出</th><th>实付</th><th>剩余能量</th><th>手牌数</th><th>K</th><th>增伤B</th><th>格挡</th><th>本步效果</th></tr></thead><tbody>@@STEPS@@</tbody></table></div><p class="result-note">回合末结束吟唱，造成13＋12＝25点群伤，再清空本次计数与已用增伤。手中还有1张未打出的防御；它不贡献K。全程最多6张手牌。</p><p class="muted">@@EXAMPLE_LIMITS@@</p><h3>同一组可用牌，爆裂费用改变多少空间</h3><div class="table-scroll"><table class="fee-table"><thead><tr><th>爆裂耗能</th><th>技能数K</th><th>额外增伤B</th><th>群伤</th><th>格挡</th><th>剩余能量</th></tr></thead><tbody>@@COMPARISON@@</tbody></table></div><p class="muted">受控比较只改变爆裂费用；遇到下一张付费牌无法支付就停止，不自动寻找其他牌。0费组还能打出最后的防御；等待只保留爆裂，不会凭空保存这整手配套。</p><h3>等待时也要付出防守成本</h3><p>@@PREPARATION@@</p></section>
<section id="limits"><span class="eyebrow">06 / TRADEOFFS</span><h2>候选成立的条件与代价</h2>@@TRADEOFFS@@<h3>下一步验证</h3>@@CHECKS@@<p class="muted">验证范围是卡牌源码核对、指定序列的费用与手牌账、页面交互；没有游戏实装、实战胜率或稳定抽序结论。</p></section>
<section id="sources"><span class="eyebrow">07 / PRIMARY SOURCE REFERENCES</span><h2>借卡牌之间的关系，保留可回查的来源</h2><p>@@SOURCE_SCOPE@@</p><div class="source-files">@@SOURCES@@</div><p><a href="docs/长篇咏唱原版与Karen参考.json">完整源码快照与校验摘要</a> · <a href="docs/长篇咏唱资源账.json">4组费用对应的逐步资源账</a></p></section><footer><a href="惠惠当前设计总览.html#explosion">当前设计总览</a> · <a href="docs/长篇咏唱流派草案.json">本流派结构化草案</a><br>@@STATUS@@。</footer></main></div><script>(()=>{const $=id=>document.getElementById(id);const ids=['cost-global','cost-held'];function update(){const [d,a]=ids.map(id=>+$(id).value);ids.forEach((id,i)=>$(id+'-value').textContent=[d,a][i]);const cost=Math.max(0,3-d-a);$('current-cost').textContent=cost;$('cost-formula').textContent=`max(0, 3－${d}－${a})＝${cost}费`;}ids.forEach(id=>$(id).addEventListener('input',update));update();})();</script></body></html>'''
c=d['core']; co=d['multiplayer']
values={'STYLE':style,'DECLARATION_SYNERGY':e(d['declaration_synergy']),'THESIS':e(d['thesis']),'STATUS':e(d['status']),'BUFF':e(c['buff_text']),'EXPLOSION':e(c['explosion_text']),'CHANT':e(c['chant_text']),'BONUS':e(c['next_explosion_bonus_text']),'TOKEN':e(c['token_text']),'WAITING':e(c['waiting']),'CONFIRMED':ul(c['confirmed']),'WORKING':ul(c['working_rules']),'OLD_STORAGE':e(c['old_storage']),'COOP_TEXT':e(co['text']),'COOP_SCOPE':e(co['scope']),'COOP_EXAMPLE':e(co['example']),'COOP_NOTES':ul(co['notes']),'ROLES':ul(d['roles']),'CONTINUATION':e(d['existing_card']['text']),'CARDS':card_blocks,'EXAMPLE_SETUP':e(d['example']['setup']),'EXAMPLE_LIMITS':e(d['example']['limits']),'STEPS':steps,'COMPARISON':comparison,'PREPARATION':e(d['preparation_example']),'TRADEOFFS':ul(d['tradeoffs']),'CHECKS':ul(d['next_checks']),'SOURCE_SCOPE':e(evidence['scope']),'SOURCES':source_rows}
for k,v in values.items(): page=page.replace('@@'+k+'@@',v)
assert '@@' not in page
(ROOT/'惠惠长篇咏唱流派设计.html').write_text(page,encoding='utf-8')
portable=page
for href in re.findall(r'href="([^"]+)"',page):
    if not href.startswith(('#','http:','https:','file:')):
        filename,sep,fragment=href.partition('#')
        portable=portable.replace(f'href="{href}"',f'href="{(ROOT/filename).resolve().as_uri()}{sep}{fragment}"')
target=Path.home()/'.agent/diagrams'; target.mkdir(exist_ok=True,parents=True)
(target/'megumin-long-chant.html').write_text(portable,encoding='utf-8')
print(json.dumps({'candidate_cards':len(cards),'source_files':len(evidence['files']),'ledgers':[{k:x[k] for k in ['explosion_cost','skills','bonus','damage','block','energy','max_hand']} for x in ledgers]},ensure_ascii=False))
