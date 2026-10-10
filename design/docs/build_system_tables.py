"""One comparable system table per character, grounded in the local research docs."""
from pathlib import Path
from hashlib import sha256
from html import escape as esc
from collections import Counter
import json
import re

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
RESEARCH = Path('D:/Github/STS2_Card_Reserch/docs')
STEM = '原版五职业与华恋及惠惠体系表'
SOURCES = []


def source(path, purpose):
    content = path.read_text(encoding='utf-8')
    SOURCES.append({'path': str(path), 'sha256': sha256(path.read_bytes()).hexdigest(), 'purpose': purpose})
    return content


def md_rows(text):
    return [[cell.strip() for cell in line.strip().strip('|').split('|')]
            for line in text.splitlines() if line.startswith('|') and not re.match(r'^\|\s*:?-', line)]


def section(text, heading):
    start = text.index(heading) + len(heading)
    rest = text[start:]
    return rest.split('\n## ', 1)[0]


def normalize_row(name, scale, position, ports, count, trigger=None, reward=None, note='', members=None):
    return {'name': name, 'scale': scale, 'position': position, 'ports': ports, 'count': count,
            'trigger': trigger, 'reward': reward, 'note': note, 'members': members or []}


positions = {
    'ironclad': ['易伤状态驱动的输出与抽牌', '消耗事件驱动的资源转换主轴', '生命作为成本与触发资源',
                 '格挡的取得、保留与兑现', '低费攻击、复制与连打插件', '力量放大多段攻击的输出副轴', '打击名称标签副轴'],
    'silent': ['持续中毒与额外毒结算', '小刀生成、强化与使用', '弃牌触发奇巧与资源收益',
               '大量出牌／抽牌的奖励层', '虚弱减伤与攻击增幅副轴', '以技能密度支撑复制和弃牌收益'],
    'defect': ['球种、槽位、集中、被动与激发的主体系', '把状态牌副作用转成资源',
               '低费攻击复用与回收', '能力生成、复制与出牌奖励层'],
    'necrobinder': ['召唤与奥斯提生命／攻击主轴', '灾厄阈值与负面状态收益',
                    '以灵魂衍生牌连接抽牌与召唤', '虚无标签驱动的一次性牌与持续收益', '高费、死亡与终结节奏副轴'],
    'regent': ['星的获取、支付与读取', '铸造持续强化君王之剑', '生成事件与生成牌收益',
               '安排牌堆顶并自动打出', '技能密度与多牌出牌奖励层'],
}

characters = []
for key, name, total in [('ironclad', '铁甲战士', 87), ('silent', '静默猎手', 88),
                         ('defect', '故障机器人', 88), ('necrobinder', '亡灵契约师', 88),
                         ('regent', '储君', 88)]:
    path = RESEARCH / 'mods' / (key + '_card_analysis_zh.md')
    text = source(path, name + '：体系规模、端口、数量、触发收益与五类定位')
    raw = md_rows(section(text, '## 2. 体系分布摘要'))
    assert raw[0] == ['体系', '判定', '卡牌数', '引导', '基础', '核心', '突破', '中坚', '触发牌', '收益牌', '端口覆盖', '结论']
    assert len(raw) - 1 == len(positions[key])
    rows = []
    for index, cells in enumerate(raw[1:]):
        assert len(cells) == 12
        count = int(cells[2]); classes = [int(x) for x in cells[3:8]]
        assert sum(classes) == count, (key, cells)
        coverage = cells[10].split('；')[0]
        ports = ['覆盖' if p in coverage else '缺失／外接' for p in ['输出', '防御', '运转']]
        item = normalize_row(cells[0], cells[1], positions[key][index], ports, count,
                             int(cells[8]), int(cells[9]), cells[11])
        item['classes'] = classes
        rows.append(item)
    characters.append({'id': key, 'name': name, 'kind': 'STS2原版 · 既有研究统计', 'total': total,
                       'pool_note': f'原文职业卡池为{total}种牌，含基础牌；体系之间允许重复归属。',
                       'path': str(path), 'rows': rows,
                       'notes': ['大／小体系、卡数和端口均沿用原文。触发数和收益数含交集，不能相加当体系总数。'],
                       'member_notes': []})

source(RESEARCH / '体系分析流程.md', '体系核心、三个端口和大／小体系判定方法')
source(RESEARCH / '卡牌分析流程.md', '统计与五类单卡定位口径')
source(RESEARCH / 'mods' / 'sts2_five_classes_card_analysis_summary_zh.md', '五职业卡池总数与体系结构复核')
source(RESEARCH / 'mods' / 'sts2_character_cards_zh.md', '原版抽牌、能量恢复与本局跨战斗成长的卡面依据')
for filename in ['Orbs/PlasmaOrb.cs', 'Powers/SubroutinePower.cs', 'Cards/Soul.cs']:
    source(Path('D:/Github/spire-codex/extraction/raw/src/Core/Models') / filename,
           '补充核对等离子回能、子程序回能或灵魂抽牌，避免静态文本遗漏')

karen_path = RESEARCH / 'mods' / 'karen_mod_character_cards_zh.md'
karen_text = source(karen_path, '华恋Mod：86张主卡池与27张衍生／选项牌的静态提取表')
raw = md_rows(section(karen_text, '## 主卡池'))
assert raw[0] == ['稀有度', '类型', '费用', '名称', '效果', '升级后', '机制备注']
karen_cards = [dict(zip(['rarity', 'type', 'cost', 'name', 'text', 'upgrade', 'notes'], row)) for row in raw[1:]]
assert len(karen_cards) == 86 and len({c['name'] for c in karen_cards}) == 86


def select(predicate):
    return [c['name'] for c in karen_cards if predicate(c)]


promise = select(lambda c: '约定牌堆' in c['text'] + c['upgrade'] or c['name'] in ['东京塔下', '门票'])
shine = select(lambda c: '闪耀' in c['text'] + c['upgrade'] or re.search(r'闪耀 \d+', c['notes']))
strength = select(lambda c: c['name'] in ['Banana松饼', '一起吃饭吧', '观察情况', 'Banana午餐', 'Banana费南雪',
                                         '约定的那天', '棒球', 'Banana什锦', '过去与未来'])
movement = select(lambda c: c['name'] in ['旋转', '下一个舞台', '招架', '添麻烦了'])
relics = select(lambda c: '禁用' in c['text'])
assert [len(x) for x in [promise, shine, strength, movement, relics]] == [41, 31, 9, 4, 2]
kr = [
    normalize_row('约定牌堆', '大体系／主轴', '存入、取回、清空与专属牌区管理',
                  ['牌数转伤害、自动打出', '入库格挡、生成防御牌', '抽取、取空回能、检索'], len(promise), note='41张直接关系牌；升级后才出现约定效果的唤醒也计入。', members=promise),
    normalize_row('闪耀', '大体系／主轴', '闪耀牌、闪耀耗尽与奖励',
                  ['闪耀攻击、耗尽成长、重放', '闪耀防御牌、总闪耀转格挡', '闪耀牌抽牌／回能及出牌奖励'], len(shine), note='31张含闪耀属性或明确读取／处理闪耀的牌。', members=shine),
    normalize_row('临时力量与保留', '副轴', '获取临时力量并延长可用时间',
                  ['力量强化攻击', '保留牌附带格挡／格挡保留', '保留、补牌；连接约定取回'], len(strength), note='9张直接来源、三明治生成或力量保留牌；不把所有多段攻击都算进来。', members=strength),
    normalize_row('移牌收益', '连接层', '牌区移动或手牌增减触发',
                  ['旋转成长', '添麻烦了、招架', '下一个舞台抽牌'], len(movement), note='仅计4张专属收益牌；触发来源借用约定等体系，未在本行重复加总。', members=movement),
    normalize_row('禁用遗物', '运转副轴', '牺牲遗物功能换当回合资源',
                  ['无直接收益', '无直接收益', '摘星回能、星罪抽牌'], len(relics), note='2张直接禁用遗物的牌；产遗物牌属于外部来源，不一并扩张计数。', members=relics),
]
characters.append({'id': 'karen', 'name': '爱城华恋', 'kind': 'Mod资料 · 本次按明确成员重新计数', 'total': 86,
    'pool_note': '主卡池86种；另有27张Token／选项／诅咒等衍生牌，不计入本表的体系成员数。', 'path': str(karen_path),
    'rows': kr, 'notes': [
        '原文只有卡牌表，没有现成的体系汇总。本表的主轴／副轴定位与端口是本次根据卡面归纳，成员数可由下面清单复核。',
        '计数看基础或升级效果，以及闪耀数值属性；不按牌名联想。约定额外计入生成约定之塔的东京塔下、门票。',
        '移牌行只数专属收益牌，其他行数明确相关成员，故这些数字不能作为与原版体系规模一比一的平衡配额。',
        '触发／收益和五类定位没有在原文中统计，本次不伪造精确拆分。“—”表示未统计，不表示0。'],
    'member_notes': [{'title': row['name'] + f'：{row["count"]}张', 'text': '、'.join(row['members'])} for row in kr]})

current_path = HERE / '当前设计总览.json'
d = json.loads(source(current_path, '惠惠：当前核心、体系职责与版本状态'))
if d.get('ruleset') == 'explosion_power_v1':
    labels = [
        ['主输出', '技能体系外接', '蓄积与结算'],
        ['接爆裂来源', '主防御', '基础抽牌'],
        ['少量联动', '外接', '抽牌与能量恢复'],
        ['取决于所存卡牌', '取决于所存卡牌', '延后自动出牌（消耗能量）'],
        ['尚未设计', '尚未设计', '尚未设计'],
    ]
    mr = []
    for system, ports in zip(d['systems'], labels):
        row = normalize_row(system['name'], system['scale'], system['role'], ports, None,
                            note=system['status'] + '；' + system['size_suggestion'])
        row['count_display'] = '不适用' if system['id'] == 'skill_points' else '待统计'
        mr.append(row)
    characters.append({'id': 'megumin', 'name': '惠惠', 'kind': '爆裂Power版 · 规模与样例待验证', 'total': None,
        'pool_note': '核心已更新；旧卡数不作为新版统计。样例牌不等于已定卡池。',
        'path': str(current_path), 'rows': mr,
        'notes': ['爆裂规则由用户指定；其余规模、样例牌与细则为建议。'], 'member_notes': []})
else:
    cards = [{'name': '爆裂魔法', 'type': '技能', 'text': d['core']['explosion_text'], 'cost': d['core']['explosion_cost'], 'generated': True},
             {**d['confirmed_cards'][0], 'type': '技能', 'generated': False},
             {**d['token_cards'][0], 'generated': True}]
    cards += [{**c, 'generated': False} for c in d['skill_archetype']['cards'] + d['declaration']['cards'] + d['multiplayer_cards']]
    assert len(cards) == 19 and len({c['name'] for c in cards}) == 19
    explosion_names = ['爆裂魔法', '咒文续接', '爆裂咒文', '咒文展开', '稳住声线', '烂熟于心', '禁忌的咒文', '越说越起劲', '人人都是爆裂狂']
    skill_names = [c['name'] for c in cards if c['type'] == '技能']
    defense_names = [c['name'] for c in cards if c['type'] == '技能' and '格挡' in c['text']]
    decl_names = [c['name'] for c in d['declaration']['cards']]
    assert len(skill_names) == 16 and len(defense_names) == 2 and len(decl_names) == 9 <= d['declaration']['card_count_limit']
    assert set(explosion_names) | set(skill_names) | set(decl_names) == {c['name'] for c in cards}
    storage = d['storage_system']
    assert storage['keyword'] == '选择一张手牌加入魔力积蓄，开始吟唱时，将所有魔力积蓄放回手牌。'
    mr = [
        normalize_row('爆裂体系', '主要大体系', '包含吟唱、爆裂结算及下一次爆裂增伤',
                      ['主要职责：技能数＋增伤兑现群伤', '借技能牌体系支撑', '吟唱条件资源与存取候选支持'], 9,
                      note='9张直接关联设计，含2张生成牌；爆裂狂是Buff，不计卡数。增伤并入本行，不再单列主体系。', members=explosion_names),
        normalize_row('技能牌体系', '第二大体系', '防御骨架；技能事件连接输出与运转',
                      ['＋爆裂体系＝输出', '主要职责；目前仅2张明确格挡牌', '＋宣言体系＝抽牌／能量等运转'], 16,
                      note='16种按当前建议类型归类的技能，含生成牌与宣言交集；不是16张防御牌。', members=skill_names),
        normalize_row('红魔族宣言', '小体系；10张以内', '连续3张技能后的资源奖励',
                      ['通过咒文与持续增伤连接爆裂', '绝不退场为交叉防御牌', '主要职责：抽牌、能量，兼有减费／生成／复制／回收'], 9,
                      note='当前6张宣言本体＋3张配套，共9张，整体不超过10张。不是第二大体系。', members=decl_names),
        normalize_row('魔力积蓄', '待评估的运转体系', '存入手牌，开始吟唱时全部取回',
                      ['间接准备爆裂所需技能', '没有已设计的防御牌', '主要职责：手牌存取与时机调度'], 0,
                      note='新关键词下具体卡牌尚未确认；旧压缩魔力、回流一击待重审，不计当前成员。'),
        normalize_row('技能点', '全局成长资源', '少量点数，用于额外获取卡牌',
                      ['尚未设计', '尚未设计', '尚未设计'], None,
                      note='类似金币的全局点数，获取较少；额外卡牌的获取方式待设计。'),
    ]
    characters.append({'id': 'megumin', 'name': '惠惠', 'kind': '当前设计草稿 · 按用户指定结构', 'total': 19,
        'pool_note': '当前19种具体卡面：16种技能（部分类型为建议）、2种能力、1种类型未定。含2张生成牌；初始牌组与完整奖励池尚未设计。',
        'path': str(current_path), 'rows': mr, 'notes': [
            '体系定位：爆裂大体系＋技能牌大体系＋10张以内宣言小体系；技能点为全局点数，提供额外卡牌获取；魔力积蓄待评估。',
            '这里统计“当前已写内容”，不是成熟职业的成品卡池配额。爆裂9、技能16、宣言9之间有交集，去重后仍为19张。',
            '爆裂按直接提及或服务爆裂／吟唱及咒文的关联卡计数；技能按卡牌类型计数；宣言按现有本体与配套清单计数。三行的成员边界明确列在下方，不能拿宽口径的16技能与原版专属体系直接比较大小。',
            '目前实际格挡牌为稳住声线、绝不退场；后者还要完成宣言。防御是技能牌体系的既定职责，现有防御牌数量则说明这一部分还需补齐。',
            '触发／收益数暂不沿用上轮错误体系划分的数字；多宣言推进与部分牌型未定，不把潜在触发牌数冒充稳定可用数。'],
        'member_notes': [{'title': row['name'] + f'：{row["count"]}张', 'text': '、'.join(row['members'])} for row in mr if row['members']] +
            [{'title': '魔力积蓄关键词（用户原文）', 'text': storage['keyword']},
             {'title': '魔力积蓄的评估边界', 'text': '它负责存取手牌，宣言负责抽牌和能量。优先评估存入代价、取回时手牌上限、与烂熟于心的起唱触发顺序。旧版“积蓄时生成爆裂”不沿用，也不自动赋予免费打出。'},
             {'title': '技能点', 'text': '类似金币的少量全局点数；额外获取卡牌的方式待设计。'}]})

# Subdivide only where the referenced effects identify a concrete resource.
# A generic engine port is intentional when the source does not support a split.
engine_profiles = {
    'ironclad': [
        ['抽牌：凶恶，给予易伤时抽牌'],
        ['抽牌：黑暗之拥、战鼓', '能量恢复：战鼓被消耗时回能', '运转端口：腐化减费等支持'],
        ['抽牌：祭品', '能量恢复：放血、祭品'],
        ['抽牌：耸肩无视'],
        ['抽牌：剑柄打击', '运转端口：复制与连打'],
        ['运转端口：沿用原文覆盖判断，具体抽牌／回能未单独拆分'],
        ['抽牌：剑柄打击', '运转端口：打击牌自动打出'],
    ],
    'silent': [
        ['运转端口：缺失／外接'],
        ['运转端口：小刀生成、保留与重放'],
        ['抽牌：杂技、早有准备、本能反应', '能量恢复：战术大师', '运转端口：弃牌触发奇巧'],
        ['运转端口：覆盖，出牌／抽牌连动'],
        ['运转端口：缺失／外接'],
        ['抽牌：逃脱计划', '运转端口：技能复制与奇巧联动'],
    ],
    'defect': [
        ['抽牌：冷静头脑、编译冲击', '能量恢复：等离子球的被动与激发', '运转端口：球种、槽位与激发调度'],
        ['抽牌：超频、迭代', '能量恢复：内核加速', '运转端口：处理状态牌副作用'],
        ['抽牌：刮削、超越光速', '运转端口：低费牌回收'],
        ['抽牌：机器学习', '能量恢复：子程序，打出能力牌时回能', '运转端口：能力牌生成与复制'],
    ],
    'necrobinder': [
        ['抽牌：取回', '能量恢复：唤起（下回合）'],
        ['抽牌：鞭打', '运转端口：负面状态连动'],
        ['抽牌：灵魂衍生牌', '运转端口：生成灵魂与召唤联动'],
        ['抽牌：书页风暴', '运转端口：虚无牌生成与减费'],
        ['运转端口：高费牌回收与死亡降费'],
    ],
    'regent': [
        ['抽牌：辉光、大爆炸', '能量恢复：星位序列、大爆炸', '运转端口：星的获取与支付（独立于能量）'],
        ['抽牌：战利品、大爆炸', '能量恢复：淬炼刀刃（下回合）、大爆炸'],
        ['运转端口：生成牌及其使用奖励'],
        ['抽牌：光子切割、微光', '运转端口：牌堆顶调度与自动打出'],
        ['运转端口：技能与多牌连打的资源支持'],
    ],
    'karen': [
        ['抽牌：命运与本能等，从约定牌堆抽取', '能量恢复：命运与本能、舞台正在等待着', '运转端口：存入、取回与检索'],
        ['抽牌：Starlight第一幕、投下燃料', '能量恢复：迈向那个舞台、投下燃料', '运转端口：闪耀牌重放'],
        ['抽牌：Banana松饼', '运转端口：手牌／能量保留与约定取回'],
        ['抽牌：下一个舞台'],
        ['抽牌：星罪', '能量恢复：摘星'],
    ],
    'megumin': [
        ['抽牌：咒文续接、烂熟于心', '能量恢复：咒文续接'],
        ['抽牌：删繁就简、咒文备忘；接宣言补牌', '能量恢复：咒文续接；接宣言的吾名惠惠！', '运转端口：技能减费、生成与保留'],
        ['抽牌：红魔族第一的天才', '能量恢复：吾名惠惠！', '运转端口：技能减费、生成、复制与回收'],
        ['运转端口：手牌存入与起唱时取回；具体卡牌待设计'],
        [],
    ],
}
if d.get('ruleset') == 'explosion_power_v1':
    engine_profiles['megumin'] = [
        ['运转端口：蓄积与结算配套待设计'],
        ['抽牌：基础运转；引爆回合优先提前防护'],
        ['抽牌：准备回合', '能量恢复：准备回合'],
        ['运转端口：下回合开始自动打出所存手牌，消耗能量'],
        [],
    ]
growth_notes = {
    'ironclad': '跨战斗成长：狂宴提高最大生命。',
    'silent': '战后收益：狩猎增加卡牌奖励。',
    'defect': '跨战斗成长：遗传算法提高自身格挡。',
    'necrobinder': '跨战斗成长：巨镰提高自身伤害；禁忌魔典提供战后删牌。',
    'regent': '战后收益：王国资产提供金币。铸造仅在战斗内成长。',
    'karen': '跨战斗成长：我们犯下的罪过；遗物收益：嫉妒、激情等。',
    'megumin': '全局成长：少量技能点提供额外卡牌获取，方式待设计。',
}
for char in characters:
    profiles = engine_profiles[char['id']]
    assert len(profiles) == len(char['rows'])
    for row, profile in zip(char['rows'], profiles):
        row['engine_detail'] = profile
    char['growth_note'] = growth_notes[char['id']]
    char['notes'].append(char['growth_note'])
kr[1]['outside_growth'] = '本局跨战斗成长：我们犯下的罪过；遗物收益：嫉妒、激情等'
mr[-1]['outside_growth'] = '全局成长：额外获取卡牌'

short_notes = {
    'ironclad': ['易伤兼顾增伤与抽牌。', '消耗换资源，配套完整。', '失去生命换输出与资源。',
                '保留格挡，再转为伤害。', '低费攻击与复制配套。', '多段放大力量收益。', '按“打击”名称联动。'],
    'silent': ['持续伤害，运转外接。', '生成、强化、保留小刀。', '弃牌换资源，主体系。',
               '奖励多次出牌与抽牌。', '来源多，专属收益少。', '服务弃牌与连打。'],
    'defect': ['职业主体系，配套完整。', '把状态牌副作用转为收益。', '低费循环，防御外接。', '依赖能力牌密度。'],
    'necrobinder': ['召唤、攻击、死亡联动。', '灾厄斩杀与负面状态收益。', '衔接抽牌与召唤。',
                   '一次性牌换持续收益。', '高费终结与死亡奖励。'],
    'regent': ['星为独立资源。', '强化君王之剑。', '来源多，收益集中。', '调度牌堆顶，提高稳定性。', '依赖星、生成牌或低费牌。'],
    'karen': ['含升级后生效与生成约定牌。', '含闪耀属性与相关收益牌。', '临时力量来源与保留配套。',
              '仅计专属收益牌。', '仅计禁用遗物牌。'],
    'megumin': ['含2张生成牌；爆裂狂Buff不计数。', '16张技能中，明确格挡牌仅2张。',
                '6张本体＋3张配套；上限10张。', '关键词已定，卡牌待设计。', '点数类似金币，获取较少；获牌方式待设计。'],
}
short_positions = {
    'ironclad': ['易伤联动', '消耗换资源', '生命换收益', '格挡积累与转伤', '低费攻击与复制', '力量放大多段', '打击名称联动'],
    'silent': ['持续中毒', '小刀生成与强化', '弃牌与奇巧', '出牌／抽牌奖励', '虚弱减伤与增伤', '技能密度联动'],
    'defect': ['球种、槽位与激发', '状态牌转资源', '低费牌复用', '能力牌联动'],
    'necrobinder': ['奥斯提召唤与攻击', '灾厄与负面状态', '灵魂衍生牌', '虚无牌联动', '高费与死亡联动'],
    'regent': ['星的获取与支付', '铸造强化剑', '生成牌奖励', '牌堆顶与自动打出', '技能与多牌奖励'],
    'karen': ['约定牌堆存取', '闪耀与耗尽收益', '临时力量与保留', '移牌触发', '遗物换资源'],
    'megumin': ['吟唱、爆裂与增伤', '防御与技能联动', '连续3张技能触发', '存牌与起唱取回', '局外成长'],
}
if d.get('ruleset') == 'explosion_power_v1':
    short_notes['megumin'] = ['20–26张为规划建议；新卡待设计。', '18–24张建议；补跨回合防守。',
                              '6–9张建议；上限10张。', '关键词已定；规模与能量不足处理待定。', '点数少量获取；获牌方式待设计。']
    short_positions['megumin'] = ['积累爆裂，停手引爆', '即时与跨回合防守', '准备回合运转', '延后自动出牌', '额外获取卡牌']
for char in characters:
    assert len(char['rows']) == len(short_notes[char['id']]) == len(short_positions[char['id']])
    for row, note, position in zip(char['rows'], short_notes[char['id']], short_positions[char['id']]):
        row['short_note'] = note
        row['short_position'] = position
    char['display_notes'] = [char['growth_note']]
characters[-2]['display_notes'] = ['按主卡池卡面归纳；移牌体系仅计收益牌。']
characters[-1]['display_notes'] = ['当前草稿；技能牌类型部分暂定，各体系有交集。']
mr[0]['short_ports'] = '主输出／抽牌／能量恢复；防御外接'
mr[1]['short_ports'] = '主防御；接爆裂输出；接宣言抽牌、能量恢复'
mr[2]['short_ports'] = '主运转：抽牌、能量恢复；兼输出、防御'
mr[3]['short_ports'] = '运转端口：存入手牌，起唱取回'
kr[1]['outside_growth'] = '跨战斗成长／遗物收益'
characters[-2]['display_notes'].append(characters[-2]['growth_note'])
if d.get('ruleset') == 'explosion_power_v1':
    characters[-1]['display_notes'] = ['旧卡不计作新版卡池；规模建议见结构说明。']
    mr[0]['short_ports'] = '主输出；防御、运转通过联动补足'
    mr[1]['short_ports'] = '主防御／抽牌；部分牌提供爆裂'
    mr[2]['short_ports'] = '抽牌／能量恢复（准备回合）'
    mr[3]['short_ports'] = '运转端口：下回合自动打出（消耗能量）'


def port_summary(row):
    if row.get('short_ports'):
        text = row['short_ports']
    else:
        labels = []
        for label, value in zip(['输出', '防御'], row['ports'][:2]):
            if value not in ['无直接收益', '尚未设计']:
                labels.append(label + ('外接' if value == '缺失／外接' else ''))
        for detail in row['engine_detail']:
            label = detail.split('：', 1)[0]
            labels.append('运转外接' if detail == '运转端口：缺失／外接' else label)
        text = '／'.join(dict.fromkeys(labels))
    if row.get('outside_growth'):
        text += ('\n' if text else '') + row['outside_growth']
    return text

intro = [
    '原版五职业（研究快照）＋华恋Mod＋惠惠草稿，共7张表。',
    '卡数、触发与收益数均有交集；“—”表示未统计。跨战斗成长指本局内保留的成长。',
    '运转细分抽牌、能量恢复；其他或不明确的写“运转端口”。减费、回手与星不计为回能。',
]
headers = ['体系', '规模与定位', '端口与收益', '卡牌数', '触发／收益', '结构说明']


def row_cells(row, markdown=False):
    role = '—' if row['trigger'] is None else f'{row["trigger"]}／{row["reward"]}'
    count = row.get('count_display', '不适用') if row['count'] is None else str(row['count'])
    position = row['scale'] if row['name'] == '技能点' else row['scale'] + '；' + row['short_position']
    return [row['name'], position, port_summary(row), count, role, row['short_note']]


def md_cell(text):
    return str(text).replace('|', '\\|').replace('\n', '<br>')


def markdown_table(rows):
    lines = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    lines += ['| ' + ' | '.join(md_cell(x) for x in row_cells(row, True)) + ' |' for row in rows]
    return '\n'.join(lines)


def html_table(rows):
    return '<div class="table-scroll"><table><thead><tr>' + ''.join('<th scope="col">' + esc(x) + '</th>' for x in headers) + \
        '</tr></thead><tbody>' + ''.join('<tr><th scope="row">' + esc(row_cells(row)[0]) + '</th>' +
        ''.join('<td>' + esc(x).replace('\n', '<br>') + '</td>' for x in row_cells(row)[1:]) + '</tr>' for row in rows) + '</tbody></table></div>'


md = '# 原版五职业、华恋与惠惠体系表\n\n整理日期：' + d['date'] + '。\n\n'
md += '\n\n'.join(intro) + '\n\n'
html_sections = []
for i, char in enumerate(characters, 1):
    name = char['name']; p = Path(char['path'])
    if char['id'] == 'karen':
        caption = 'Mod资料 · 主卡池86种；27种衍生牌不计入。'
    elif char['id'] == 'megumin':
        caption = '爆裂Power版 · 新版卡数待统计。' if d.get('ruleset') == 'explosion_power_v1' else '设计草稿 · 当前19种卡面，含2种生成牌。'
    else:
        caption = f'原版研究统计 · {char["total"]}种牌，含基础牌。'
    md += f'## {i}. {name}\n\n{caption}\n\n'
    md += '[来源文档](/' + p.as_posix() + ')\n\n' + markdown_table(char['rows']) + '\n\n'
    md += '\n'.join('- ' + note for note in char['display_notes']) + '\n\n'
    if char['member_notes']:
        shown_members = [item for item in char['member_notes'] if item['title'] not in ['魔力积蓄的评估边界', '技能点']]
        md += '<details>\n<summary>成员清单与关键词</summary>\n\n' + '\n\n'.join('**' + item['title'] + '**：' + item['text'] for item in shown_members) + '\n\n</details>\n\n'
    members = ''
    if char['member_notes']:
        members = '<details><summary>成员清单与关键词</summary>' + ''.join(
            '<p><b>' + esc(item['title']) + '：</b>' + esc(item['text']) + '</p>' for item in shown_members) + '</details>'
    html_sections.append('<section id="' + char['id'] + '"><h2>' +
        str(i) + '. ' + esc(name) + '</h2><p>' + esc(caption) + '</p><p><a href="' + p.as_uri() +
        '">来源文档</a></p>' + html_table(char['rows']) + '<ul>' + ''.join('<li>' + esc(n) + '</li>' for n in char['display_notes']) +
        '</ul>' + members + '</section>')

md += '[完整数据、端口例子与五类统计](docs/职业体系表数据.json)\n'

css = '''
:root{--bg:#f7f3ec;--ink:#302b26;--muted:#726a61;--line:#d9d0c4;--accent:#96352e}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.8 'Segoe UI','Microsoft YaHei',sans-serif}
.wrap{max-width:1550px;margin:auto;padding:34px 42px 70px}header{padding:20px 0 30px;border-bottom:2px solid var(--ink)}h1{font:42px/1.35 'Palatino Linotype',SimSun,serif;margin:12px 0 22px}h2{font:30px/1.4 'Palatino Linotype',SimSun,serif;margin:8px 0 18px}
p{margin:0 0 15px}a{color:var(--accent);text-underline-offset:4px}.eyebrow{color:var(--accent);font-size:12px;letter-spacing:.6px}nav{position:sticky;top:0;background:var(--bg);display:flex;flex-wrap:wrap;gap:12px 24px;padding:13px 0;border-bottom:1px solid var(--line);z-index:2}nav a{font-size:13px;text-decoration:none}
section{padding:37px 0;border-bottom:1px solid var(--line);scroll-margin-top:85px}.table-scroll{overflow:auto;margin:23px 0}table{border-collapse:collapse;width:100%;min-width:1050px;table-layout:fixed;font-size:13px;line-height:1.85}th,td{border-bottom:1px solid var(--line);padding:14px 15px 14px 0;text-align:left;vertical-align:top;overflow-wrap:anywhere}thead{color:var(--accent)}th:nth-child(1){width:10%}th:nth-child(2){width:18%}th:nth-child(3){width:34%}th:nth-child(4){width:6%}th:nth-child(5){width:8%}th:nth-child(6){width:24%}tbody tr:hover{background:#eee5d8}li{margin-bottom:9px}details{padding:17px 21px;border-left:3px solid var(--line);background:#f0e9df;font-size:13px}summary{color:var(--accent);font-weight:bold;cursor:pointer}details[open]>summary{margin-bottom:16px}.note{color:var(--muted);font-size:13px}.scope{max-width:1120px}footer{font-size:13px;color:var(--muted);padding-top:25px}
@media(max-width:700px){.wrap{padding:20px 18px 45px}h1{font-size:31px}h2{font-size:25px}nav{flex-wrap:nowrap;overflow:auto;white-space:nowrap}section{scroll-margin-top:65px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{nav{position:static}body{background:white}.wrap{padding:0;max-width:none}table{min-width:0;font-size:9px}section{break-before:page}header+nav+section{break-before:auto}}
'''
html = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>原版五职业、华恋与惠惠体系表</title><style>' + css + '</style></head><body><div class="wrap"><header><p class="eyebrow">' + d['date'].replace('-', '.') + '</p><h1>原版五职业、华恋与惠惠体系表</h1><div class="scope">' + ''.join('<p>' + esc(x) + '</p>' for x in intro) + '</div><p><a href="' + STEM + '.md">Markdown版本</a> · <a href="惠惠当前设计总览.html">惠惠当前设计总览</a></p></header><nav aria-label="职业体系表">' + ''.join('<a href="#' + c['id'] + '">' + esc(c['name']) + '</a>' for c in characters) + '</nav>' + ''.join(html_sections) + '<footer><a href="docs/职业体系表数据.json">完整数据、端口例子与五类统计</a></footer></div></body></html>'

(OUT / (STEM + '.md')).write_text(md, encoding='utf-8')
(OUT / (STEM + '.html')).write_text(html, encoding='utf-8')
(HERE / '职业体系表数据.json').write_text(json.dumps({'date': d['date'], 'scope': intro,
    'characters': characters, 'sources': SOURCES}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'tables': len(characters), 'rows': {c['name']: len(c['rows']) for c in characters},
                  'karen_members': {r['name']: r['count'] for r in kr},
                  'megumin_members': {r['name']: r['count'] for r in mr}, 'output': str(OUT / (STEM + '.html'))}, ensure_ascii=False))
