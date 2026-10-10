"""Render the current-card audit using the repository's system-analysis template."""
from collections import Counter
from hashlib import sha256
from html import escape as e
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
CLASSES = ['机制引导牌', '机制基础牌', '机制核心牌', '突破限制牌', '机制中坚牌']
ROLES = ['扳机触发', '扳机收益', '触发+收益', '配套']
GAMEPLAY_KEYS = ['core', 'player_buffs', 'confirmed_cards', 'token_cards',
                 'multiplayer_cards', 'skill_archetype', 'declaration']


def load():
    current = json.loads((HERE / '当前设计总览.json').read_text(encoding='utf-8'))
    audit = json.loads((HERE / '惠惠体系逐项分析.json').read_text(encoding='utf-8'))
    registry = {}

    def add(key, card, source, href, **overrides):
        assert key not in registry
        registry[key] = {**card, 'rarity': card.get('rarity', '未定'),
                         'source': source, 'href': href, **overrides}

    add('explosion', {'name': '爆裂魔法', 'cost': current['core']['explosion_cost'],
                     'type': '技能', 'text': current['core']['explosion_text']},
        '生成牌／技能类型为建议', '惠惠当前设计总览.html#explosion')
    add('continuation', current['confirmed_cards'][0], '用户指定效果／名称暂定',
        '惠惠当前设计总览.html#explosion', type='技能')
    add('token', current['token_cards'][0], 'Token／技能类型为建议',
        '惠惠当前设计总览.html#might-system')
    for card in current['skill_archetype']['cards']:
        add(card['id'], card, '助手候选／稀有度亦为草案',
            '惠惠长篇咏唱流派设计.html#card-' + card['id'])
    for card in current['declaration']['cards']:
        add(card['id'], card, '宣言或配套候选／类型按当前稿',
            '惠惠当前设计总览.html#decl-card-' + card['id'])
    registry['my_name']['rarity'] = current['declaration']['rarity']
    registry['my_name']['source'] = '用户参考效果与罕见稀有度／名称、类型暂定'
    add('everyone', current['multiplayer_cards'][0], '用户指定联机效果／类型稀有度未定',
        '惠惠当前设计总览.html#multiplayer')
    assert len(registry) == 19
    members = set()
    for system in audit['systems']:
        ids = []
        for row in system['cards']:
            assert len(row) == 9 and row[0] in registry
            assert row[1] in CLASSES and row[2] in ROLES
            assert all(row[i] for i in [3, 4, 5, 6, 8])
            ids.append(row[0])
        assert len(ids) == len(set(ids))
        members.update(ids)
        assert len(system['criteria']) == 7
    support = {row[0] for row in audit['generic_support']}
    assert not members & support
    assert members | support == registry.keys(), 'Every current card needs an explicit placement'
    fingerprint = sha256(json.dumps({k: current[k] for k in GAMEPLAY_KEYS},
                                    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
    if 'card_source_sha256' in audit:
        assert fingerprint == audit['card_source_sha256'], 'Card design changed; revise the qualitative audit before rebuilding'
    for source in audit.get('method_sources', []):
        assert sha256((HERE.parent / source['path']).read_bytes()).hexdigest() == source['sha256']
    return audit, registry, fingerprint


def table(headers, rows, css=''):
    return '<div class="table-scroll audit-table ' + css + '"><table><thead><tr>' + ''.join(
        '<th scope="col">' + e(x) + '</th>' for x in headers
    ) + '</tr></thead><tbody>' + ''.join(
        '<tr><th scope="row">' + row[0] + '</th>' + ''.join('<td>' + x + '</td>' for x in row[1:]) + '</tr>'
        for row in rows) + '</tbody></table></div>'


def ul(items):
    return '<ul>' + ''.join('<li>' + e(x) + '</li>' for x in items) + '</ul>'


def counts(system):
    rows = system['cards']
    roles = Counter(row[2] for row in rows)
    return {'total': len(rows), 'trigger': roles['扳机触发'] + roles['触发+收益'],
            'reward': roles['扳机收益'] + roles['触发+收益'], 'both': roles['触发+收益'],
            'support': roles['配套'], 'cross': sum(bool(row[7]) for row in rows),
            'classes': Counter(row[1] for row in rows)}


def distribution(cards, key):
    values = Counter('未定' if c.get(key) is None else str(c[key]) for c in cards)
    order = {'rarity': ['普通', '罕见', '稀有', '未定'],
             'type': ['攻击', '技能', '能力', '未定'],
             'cost': ['0', '1', '2', '3', 'X', '未定']}[key]
    assert set(values) <= set(order)
    return ' · '.join(f'{x}：{values[x]}' for x in order if values[x])


def card_link(card):
    return '<a href="' + e(card['href']) + '">' + e(card['name']) + '</a>'


def render_summary(audit, registry, destination='惠惠体系复盘与六职业对照.html'):
    rows = []
    for system in audit['systems']:
        c = counts(system)
        rows.append([
            '<a href="' + destination + '#audit-' + system['id'] + '">' + e(system['name']) + '</a>',
            e(system['verdict']),
            f'{c["total"]}张直接成员<small>触发{c["trigger"]}／收益{c["reward"]}／兼具{c["both"]}／跨体系{c["cross"]}</small>',
            e(system['missing'])])
    return '<p>' + e(audit['verdict']) + '</p>' + table(
        ['当前体系', '按文档判定', '逐卡统计', '具体缺口'], rows) + (
        '<p class="muted">统计有交集，不能相加；宣言触发数含条件性推进。19张设计含生成牌与候选，'
        '不是定稿奖励池。详表另列3张通用配套，给出五类定位、独立性和风险。</p>'
        '<p><a href="' + destination + '#megumin-audit">查看七项判定、全部逐卡表与计数口径 →</a></p>')


def render_full(audit, registry, fingerprint):
    def name_list(rows):
        return '、'.join(registry[row[0]]['name'] for row in rows) or '无'

    all_cards = list(registry.values())
    overview = table(['范围', '类型', '升级前费用', '稀有度'], [
        ['当前19张设计', e(distribution(all_cards, 'type')), e(distribution(all_cards, 'cost')),
         e(distribution(all_cards, 'rarity'))]])
    by_rarity = []
    for rarity in ['普通', '罕见', '稀有', '未定']:
        selected = [c for c in all_cards if c['rarity'] == rarity]
        by_rarity.append([f'{rarity}（{len(selected)}张）', e(distribution(selected, 'type')),
                          e(distribution(selected, 'cost'))])
    pool = table(['稀有度', '类型分布', '费用分布'], by_rarity)
    index_rows = []
    for key, card in registry.items():
        placements = [s['name'] + '：' + r[1] for s in audit['systems'] for r in s['cards'] if r[0] == key]
        if not placements:
            placements = ['通用配套，未硬归专属体系']
        index_rows.append([card_link(card), e(card['source']),
                           e(str(card['cost']) if card['cost'] is not None else '未定') + '费 · ' +
                           e(card['type']) + ' · ' + e(card['rarity']),
                           e(card['text']), '<br>'.join(e(x) for x in placements)])
    blocks = []
    for system in audit['systems']:
        rows = system['cards']
        c = counts(system)
        listed = [registry[r[0]] for r in rows]
        lists = [
            ('扳机触发牌（含兼具）', name_list([r for r in rows if r[2] in ['扳机触发', '触发+收益']])),
            ('扳机收益牌（含兼具）', name_list([r for r in rows if r[2] in ['扳机收益', '触发+收益']])),
            ('触发＋收益牌', name_list([r for r in rows if r[2] == '触发+收益'])),
            ('跨体系联动牌', name_list([r for r in rows if r[7]])),
            ('仅配套／上游来源', name_list([r for r in rows if r[2] == '配套']))]
        demographics = table(['体系卡数', '类型', '升级前费用', '稀有度'], [[str(c['total']),
            e(distribution(listed, 'type')), e(distribution(listed, 'cost')), e(distribution(listed, 'rarity'))]])
        role_stats = table(['触发（含兼具）', '收益（含兼具）', '触发＋收益', '跨体系（可重叠）', '仅配套'],
                           [[str(c[k]) for k in ['trigger', 'reward', 'both', 'cross', 'support']]])
        class_stats = table(CLASSES, [[str(c['classes'][key]) for key in CLASSES]])
        card_table = table(['名称／分类', '扳机角色与依据', '端口', '选牌／使用定位', '独立性', '依赖或风险'], [
            [card_link(registry[r[0]]) + '<small>' + e(r[1]) + '</small>',
             '<b>' + e(r[2]) + '</b><small>' + e(r[8]) + '</small>' +
             ('<small>跨体系：' + e('；'.join(r[7])) + '</small>' if r[7] else ''),
             e('、'.join(r[3])), e(r[4]), e(r[5]), e(r[6])] for r in rows], 'audit-card-roles')
        blocks.append('<article class="audit-system" id="audit-' + system['id'] + '"><h3>' +
                      e(system['name']) + '</h3><p class="review-keyline">' + e(system['verdict']) + '</p>' +
                      '<p><b>共同核心：</b>' + e(system['core']) + '</p><p><b>扳机定义：</b>' +
                      e(system['trigger']) + '</p>' + table(['文档的七项检查', '结论', '当前牌面依据'],
                      [[e(x) for x in r] for r in system['criteria']]) +
                      '<h4>来源、收益与三个端口</h4><p><b>来源：</b>' + e(system['source']) + '</p>' +
                      ''.join('<p><b>' + e(k) + '：</b>' + e(v) + '</p>' for k, v in system['ports'].items()) +
                      table(['角色', '卡牌名单'], [[e(k), e(v)] for k, v in lists]) +
                      '<h4>数量与分布</h4>' + demographics + role_stats + class_stats +
                      '<h4>逐张定位</h4>' + card_table + '<p><b>缺失或薄弱处：</b>' + e(system['missing']) +
                      '</p><p><b>体系结论：</b>' + e(system['conclusion']) + '</p></article>')
    support = table(['卡牌', '功能', '如何参与', '为何不另立体系'], [
        [card_link(registry[r[0]]), *[e(x) for x in r[1:]]] for r in audit['generic_support']])
    external_skills = [card['name'] for key, card in registry.items() if card['type'] == '技能' and
                       key not in {r[0] for r in audit['systems'][1]['cards']}]
    assert len(external_skills) == 8
    sources = '<p><a href="参考资料/设计方法/体系分析流程.md">体系分析流程</a> · <a href="参考资料/设计方法/卡牌分析流程.md">卡牌分析流程</a> · <a href="docs/惠惠体系逐项分析.json">本次逐项分析数据</a></p>'
    return ('<section id="megumin-audit"><span class="eyebrow">MEGUMIN / FULL TEMPLATE AUDIT</span>' +
        '<h2 class="section-title">把文档的分析方法逐项用到惠惠身上</h2><p>' + e(audit['scope']) + '</p>' +
        sources + '<p>' + e(audit['scale_policy']) + '</p>' + ul(audit['counting']) +
        '<h3>先确认当前卡池的边界</h3>' + overview + pool +
        '<p>16种技能的统计包含建议类型；2种能力不会推进技能连打，联机牌类型未定。12张稀有度未定，' +
        '因此不能用现有分布宣称“普通池已足够”或“核心全在稀有池”。初始牌组未定，也不把打击、防御示例加入分母。</p>' +
        '<details><summary>19张具体卡面的来源与全部归位</summary>' +
        table(['卡牌', '设计状态', '基础属性', '当前卡面', '在各体系中的定位'], index_rows) + '</details>' +
        ''.join(blocks) + '<article class="audit-system" id="audit-support"><h3>共享燃料与通用配套</h3>' +
        '<p>宣言体系外的8种技能候选：' + e('、'.join(external_skills)) +
        '。这些是可用的触发面，不能把全部都当作稳定起步牌；续接需要吟唱，咒文需要生成，爆裂还要支付启动费用。</p>' +
        support + '<p>五类统计中“基础牌为0”指符合独立可抓标准的专属成员为0，并不表示没有能推进机制的技能。' +
        '已有通用技能和生成物必须与未定初始牌组一起检验，不能只凭分类数字再强行补卡。</p></article>' +
        '<h3>把真正的桥接与共享触发分开</h3>' + table(['卡或关系', '各体系中的职责', '判定'],
        [[e(x) for x in row] for row in audit['bridges']]) +
        '<h3>哪些内容不应另算体系</h3>' + table(['方向', '当前归类', '依据'],
        [[e(x) for x in row] for row in audit['not_systems']]) +
        '<h3>由这次分析得出的改牌顺序</h3>' + table(['顺序', '先处理什么', '具体依据'],
        [[e(x) for x in row] for row in audit['priorities']]) +
        '<p class="muted">这是设计结构分析与暂定角色判断；没有更改卡面、确定新规则或运行新的数值模型。' +
        '当前玩法数据核对指纹：' + fingerprint + '</p></section>')


AUDIT_CSS = '''
.audit-system{border-top:2px solid var(--border);padding:30px 0;scroll-margin-top:70px}
.audit-system>h3{font:29px var(--serif);color:var(--red)}
.audit-system h4{font-size:17px;margin:26px 0 10px}
#megumin-audit .muted{overflow-wrap:anywhere}
.audit-table tbody th{width:auto}.audit-card-roles table{min-width:1120px;table-layout:fixed}
.audit-card-roles th:nth-child(1){width:14%}.audit-card-roles th:nth-child(2){width:22%}
.audit-card-roles th:nth-child(3){width:9%}.audit-card-roles th:nth-child(4){width:18%}
.audit-card-roles th:nth-child(5){width:16%}.audit-card-roles th:nth-child(6){width:21%}
'''
