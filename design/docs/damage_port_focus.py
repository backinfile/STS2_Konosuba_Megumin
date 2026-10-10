"""Current editorial model: damage responsibilities, not every damage payoff."""
import html
import json

FOCUS = []


def axis(char, name, kind, scope, native, investment, curve, decisions, limits, cards, sources=''):
    FOCUS.append(dict(char=char, name=name, kind=kind, scope=scope, native=native,
                      investment=investment, curve=curve, decisions=decisions,
                      limits=limits, cards=cards.split(), sources=sources.split()))


axis('铁甲战士','力量攻击','属性成长','本场',
     '力量直接提高攻击伤害；叠力量、增加攻击段数、提供高效攻击共同组成伤害端。它不是另一套防守或抽牌机制偶尔附带的一张伤害牌。',
     '燃烧一次提高基线；恶魔形态提供逐回合力量；撕裂把失血动作接入力量端。攻击牌负责把力量按段兑现。'.replace('\u200b',''),
     '力量总量 × 可打出的有效攻击段数。一次增益带来稳定增幅，持续叠力量才构成长战斗成长；多段攻击放大每点力量的价值。',
     '先花费用叠力量，还是先杀掉危险目标；本回合多段集中爆发，还是继续投资后续回合。',
     '成长期需要独立防守；攻击次数不足时，已有力量无法及时兑现。失血是可选输入，不把整个自伤机制都算进伤害主轴。',
     'Inflame DemonForm Rupture Whirlwind TearAsunder','RupturePower')
axis('静默猎手','中毒','持续伤害','目标',
     '中毒状态本身就负责伤害，施毒、持续补毒、加速结算围绕同一个杀敌目标工作；不需要额外装上一张“把毒变伤害”的转换卡才开始扣血。',
     '致命毒药直接铺层；毒雾提供后续输入；涂毒把攻击接入施毒端；触媒增加每次敌方回合开始的触发次数。',
     '单次上毒会随减层而衰减。持续补毒可以维持或抬高每轮产出；触媒主要提前兑现已有层数，而非直接把总伤害翻倍。',
     '把毒集中在长命目标，还是分配给多个敌人；继续补层，还是用即时攻击先解决威胁。',
     '伤害要等到结算点，过量叠在将死目标上会浪费；需要防守或即时伤害覆盖等待期。毒性爆发只是内部的额外兑现分支，不是本体系成立的前提。',
     'DeadlyPoison NoxiousFumes Envenom Accelerant Outbreak','PoisonPower')
axis('静默猎手','小刀攻势','攻击数量','本回合／本场',
     '小刀是专门的零费攻击载体。制造小刀、提高每刀伤害、让刀保留或变群攻，都是直接建设伤害端。',
     '刀刃之舞提供当前数量，无尽刀刃提供每回合供给；精准提高单刀伤害，幻影之刃与刀扇改变兑现方式。',
     '总输出主要由小刀数量、每刀质量和可打出的次数决定。可稳定续航，也可在一回合堆出大量攻击；并不天然每回合数值递增。',
     '优先增加数量还是质量；现在打完，还是保留到增益窗口；补充单体集火还是群攻能力。',
     '生成占据手牌空间，也增加打牌次数；需要抽牌、能量和防守支持，但这些支持系统不因此变成小刀伤害体系本体。',
     'BladeDance InfiniteBlades Accuracy PhantomBlades FanOfKnives Finisher')
axis('故障机器人','闪电输出','持续伤害','本场',
     '闪电球的被动与激发都直接造成伤害；生成、集中、球位与重复触发围绕场上的伤害装置组织。',
     '先铺球，再提高集中、球位或触发频率；特斯拉线圈集中触发被动，电流相生按历史生成量补球，雷霆强化激发。',
     '固定球数、集中和频率时，每轮产出基本稳定；继续提升这三个维度才形成成长。激发可把持续收益提前换成当下伤害。',
     '留住球持续触发，还是快速轮换激发；扩大球阵，还是优先提高每次触发质量；如何减少随机落点带来的浪费。',
     '通常需要铺场，随机伤害不总能及时解决指定目标；防守球与伤害球还争用球位。集中是跨球种增益，本节只分析它在闪电端的作用。',
     'Defragment Capacitor Loop TeslaCoil Thunder Voltaic','LightningOrb ThunderPower')
axis('故障机器人','黑暗蓄积','储伤爆发','球存续期',
     '黑暗球积累的是待释放的伤害，生成、加速被动、保护球序与多重激发都围绕这一攻击载体。',
     '生成黑暗球，持续触发被动增加储伤，再用合适的激发次数兑现；漆黑与循环加快积累，多重释放放大一次兑现。',
     '蓄积阶段可以不造成任何伤害，但未来的一击越来越大。它是成长性爆发，不是毒或闪电那样的持续扣血。',
     '何时停止蓄积；是否值得等下一轮；怎样安排球序，避免被迫提前激发；怎样处理最低生命目标选择。',
     '等待期需要其他伤害解决小怪，并需要防守；过度蓄积可能溢出，提前激发又会失去继续成长的载体。',
     'Darkness Loop MultiCast','DarkOrb')
axis('故障机器人','爪击成长','攻击成长','本场',
     '爪击的使用同时完成伤害和本场同名攻击的强化；零费回收围绕这一伤害核心提供重复使用机会。',
     '反复打出爪击，并用万物一心、野性、全息影像增加回收与再打出的次数。',
     '每次使用提高本场现有爪击的伤害；使用次数既贡献本次输出，也加快未来成长。它不必等自然回合推进才变强。',
     '投入多少爪击和回收牌；早期低伤害能否承受；增加同名密度与维持抽牌、防守之间怎样平衡。',
     '基础伤害低，零费仍然消耗抽牌机会。爪击是伤害核心，零费回收是服务它的运转接口；后者还能服务别的攻击。',
     'Claw AllForOne Feral Hologram')
axis('亡灵契约师','奥斯提攻势','攻击连段','本回合／本场',
     '明确限定为奥斯提攻击子体系：有成组的专属攻击、专属增伤、攻击次数奖励和攻击牌密度奖励。不能将整个召唤／替伤机制笼统视为输出。',
     '戳击等牌发起攻击；钙化提高奥斯提每段伤害；重压奖励此前攻击，猛晃读取回合攻击历史，榨取奖励奥斯提攻击牌密度。',
     '以专属增伤和连段频率为主，回合内可增加攻击效率与段数。召唤提高生命不等于普通奥斯提攻击自动增伤。',
     '先打哪些攻击以解锁后续效率；投入多少专属攻击；什么时候补充召唤维持攻击载体，什么时候集中出手。',
     '奥斯提需要存活；成长更多依赖额外增伤与连段，不是“宠物活得越久攻击就自然越大”。出击读生命、亡灵精通转失血另归资源转换旁支。',
     'Poke Calcify Flatten Rattle Squeeze HighFive RightHandHand')
axis('亡灵契约师','灾厄处决','击杀阈值','目标',
     '灾厄状态的用途就是推进敌人的死亡阈值，施加、扩张、提前判定都在建设杀敌端。虽然不是逐次扣血，仍属于原生终结体系。',
     '增加灾厄并配合直接伤害降低目标当前生命；死神形态将攻击接入灾厄端，末日降临可提前执行处决判定。',
     '进展表现为“距离处决还差多少”，不表现为每回合持续掉血。正常在敌方回合末，当灾厄达到当前生命时处决。',
     '继续堆灾厄还是直接削血；分散阈值压力还是先处决一个目标；是否需要立即判定避免敌人先行动。',
     '达到阈值和实际结算并非总在同一时刻。大限已至把灾厄变成普通攻击，是可选兑现器；没有它，灾厄仍然能自己完成杀敌。',
     'BlightStrike ReaperForm EndOfDays TimesUp','DoomPower')
axis('储君','铸剑攻势','攻击成长','本场',
     '铸造直接养大君王之剑这一攻击载体；取回、重放、翻倍、变群攻构成围绕同一伤害核心的配套。',
     '铸造增加剑的伤害；熔炉提供每回合增长，征召上前保证取用，剑圣与征服者放大兑现，追踪之刃扩展目标范围。',
     '本场持续积累的单载体成长。成长量、能打出几次、倍率与目标数共同决定最终输出；不需要每次从零重新准备。',
     '继续铸造还是现在出剑；补取回与降费能力，还是继续堆伤害；选择单体爆发还是覆盖群体。',
     '伤害集中在一个载体上，取用和支付费用必须跟上。招架能把攻击接到防守端，但它不改变铸剑体系主要负责伤害的性质。',
     'SovereignBlade Furnace SummonForth SwordSage Conqueror SeekingEdge Parry')
axis('Karen','临时力量攻势','窗口爆发','本回合／本场',
     '临时力量直接增强攻击；供给力量、延长保留时间和多段兑现都围绕伤害窗口组织。约定取牌只是其中一种力量来源与调度接口。',
     '食物提供临时力量，保留机制延长窗口；多段闪耀攻击与回击放大每点力量价值；常规力量牌补充较稳定的基线。',
     '默认是当回合爆发；成功续存并继续补力量时才形成跨回合成长。其特色是管理增长的寿命，不是无条件永久加伤。',
     '何时吃力量、何时打多段；是否值得用资源续存；爆发窗口与高质量攻击能否对齐。',
     '保留中断会失去临时增益，需要供给与调度支持。过去与未来是约定动作通往力量伤害端的连接牌，不把整个约定体系升格为伤害体系。',
     'KarenEatTogether KarenBananaMuffin KarenFinancier KarenShineStrikeBarrage KarenCounter KarenReady KarenPastAndFuture',
     'RetainTmpStrengthPatch')

# Offensive groups are real damage structures, but do not silently gain the scope of a whole mechanic.
GROUPS = [
    dict(char='铁甲战士',name='易伤攻击辅助',
         why='易伤本身就是攻击增幅状态，属于伤害端辅助；但它不是与力量同样自给的独立主轴。',
         feature='重在维持倍率与爆发窗口。普通层数主要延长持续时间；欺凌、熔融之拳才额外开发层数价值。',
         cards='Cruelty Bully MoltenFist'),
    dict(char='铁甲战士',name='打击攻击群',
         why='打击牌本来就是攻击；完美打击与地狱狂徒奖励这个攻击家族的密度和抽取。',
         feature='偏构筑密度与攻击频率，不是自然逐回合成长。专属配套规模较小，列为攻击子群。',
         cards='PerfectedStrike Hellraiser'),
    dict(char='故障机器人',name='玻璃伤害球',
         why='玻璃被动和激发都直接造成群伤，是原生伤害子系统；当前配套规模较小。',
         feature='无集中时被动 4→3→2→1→0，属于会衰减的持续输出。重点在补充与提前激发，而非一直留场养大。',
         cards='Glasswork',sources='GlassOrb'),
    dict(char='储君',name='星费攻击群',
         why='星星整体是资源机制；这里只计星界脉冲、七星等直接使用星费攻击的子群，以及新月长矛的攻击配套。',
         feature='把储备资源投入当下攻击，偏资源预算与爆发效率。新月长矛奖励星费牌密度；不能由此将所有星星牌都算成输出体系。',
         cards='AstralPulse SevenStars CrescentSpear'),
    dict(char='Karen',name='闪耀攻击与重放',
         why='限定为闪耀攻击牌与攻击重放构成的进攻子群；闪耀整体还承担防守、运转和本局经济。',
         feature='用高质量攻击和第二幕重放换即时爆发，代价是闪耀寿命；需考虑后续供给。第二幕也能重放非攻击牌，所以不是整个闪耀机制天然只负责伤害。',
         cards='KarenShineStrikeBarrage KarenDebut KarenStarlight02Card',sources='KarenStarlight02Power'),
    dict(char='Karen',name='续演攻势',
         why='续演本身是纯攻击素材，再生产专门不断供给这种素材；可以识别为小型输出套件，不能因此把整个约定牌堆算成输出。',
         feature='固定低费攻击的数量型续航，可叠力量。供给不缺仍需足够取牌能力；“无限续演”不自动等于无限出手。',
         cards='KarenStageReproduce KarenContinue',sources='PromisePileManager'),
]

CONVERSIONS = [
    ('铁甲战士：格挡','防守／格挡保留','BodySlam Juggernaut','防守体系通过少数牌把当前格挡或获得格挡事件变成伤害。实际构筑可以靠它杀敌，但本轮不将格挡整体归为原生伤害体系。'),
    ('铁甲战士：自伤与消耗','生命支付／牌组管理／运转','Inferno TearAsunder FiendFire AshenStrike PactsEnd','能接入力量端或其他伤害出口；自伤和消耗也服务资源、压缩与防守。不能把整个机制按伤害用途概括。'),
    ('静默猎手：抽弃与出牌','过牌／能量／行动效率','MementoMori Speedster Murder SerpentForm Strangle Ricochet Haze','奇巧是免费打出的触发方式，可承载攻击、毒、抽牌或能量；铭记死亡等是对运转动作的伤害奖励，不据此把抽弃整体列为伤害主轴。'),
    ('故障机器人：冰霜','防守','Hailstorm','冰霜仍以格挡为主；冰雹风暴是从这一防守结构接出的伤害支路。'),
    ('故障机器人：状态与能力','代价处理／能力运转','Smokestack FlakCannon Storm CreativeAi Subroutine','烟囱、散射炮是状态牌的伤害出口；雷暴将能力牌运转接入闪电端。状态、能力标签本身不是独立的原生伤害对象。'),
    ('亡灵契约师：灵魂、虚无、宠物生命','抽牌／牌组时限／防守资源','Haunt SoulStorm PullFromBelow BansheesCry Unleash NecroMastery','灵魂本身负责抽牌；纠缠将其转伤害。虚无使用历史、宠物生命也能通过专用牌兑现，但不和灾厄、奥斯提攻击群混列。'),
    ('储君：星星事件与生成牌','资源／产牌','BlackHole Radiate Arsenal Supermassive PillarOfCreation','黑洞、辐射兑现星星事件或点数；武器库把产牌接入力量端，超质量体兑现生成历史。它们是资源机制与伤害端的连接。'.replace('\u200b','')),
    ('Karen：约定调度','存牌／取牌／出牌调度','KarenBackToBackCard KarenGeer KarenPastAndFuture KarenLastWord','背靠背读库存，过去与未来接入力量，最后的台词提供条件终结。命运的齿轮打出什么，就服务什么端口。'.replace('\u200b','')),
    ('Karen：闪耀寿命与奖励','卡牌寿命／本局经济','KarenCarryingGuilt KarenStarlight03Card','我们犯下的罪过把不同闪耀牌耗尽记录转成伤害；不据此称整个闪耀经济为成长伤害体系。'),
]

SMALL = [
    ('暴走／痛殴','本张 · 本场','使用后增伤／吞掉攻击牌养大自身；属于攻击核心，配套体量不等于力量主轴。','Rampage Thrash'),
    ('吊杀','同名 · 同一敌人','对该敌人的后续同名攻击倍增，目标死亡后不能把倍率带给新目标。','Hang'),
    ('巨镰','本张 · 本局','反复使用积累跨战斗伤害，依赖尽早取得并多次出手。','TheScythe'),
    ('王者之拳','本张 · 本场','被抽到时养大本张攻击，仍然需要循环供给。','KinglyPunch'),
    ('旋转','本张 · 本场','自身移动时增伤；是可装在约定引擎上的成长攻击核心，不是约定调度整体的属性。','KarenSpin'),
    ('永无结束的命运舞台','本张 · 升级来源决定期限','多次升级养大攻击；要区分永久升级与战斗内升级。','KarenContinue02'),
    ('续写','同名耗尽记录 · 本局','同名攻击留下的耗尽记录扩大后续重放规模，适合作为小型攻击构筑研究；不将其泛化为整个闪耀体系。','KarenRewrite'),
    ('轰击','本张 · 本场','消耗后可每回合自动再打，是固定持续伤害单卡；有持续输出不等于形成独立完整体系。','Bombardment'),
]

OVERVIEW = [
    ('铁甲战士','力量攻击','易伤攻击辅助；打击攻击群','格挡、自伤、消耗的伤害转换'),
    ('静默猎手','中毒；小刀攻势','其他条件攻击作为补充','抽弃／出牌事件的伤害奖励'),
    ('故障机器人','闪电；黑暗；爪击','玻璃伤害球','冰霜转伤、状态转伤、能力运转'),
    ('亡灵契约师','奥斯提攻势；灾厄','吊杀、巨镰等单卡核心','灵魂／虚无／宠物生命转伤'),
    ('储君','铸剑攻势','星费攻击群','星星事件、生成牌转伤'),
    ('Karen','临时力量攻势','闪耀攻击子群；续演攻势','约定库存与调度、闪耀经济转伤'),
]


def evidence_names():
    names = set()
    for r in FOCUS:
        names.update(r['cards']+r['sources'])
    for r in GROUPS:
        names.update((r['cards']+' '+r.get('sources','')).split())
    for r in CONVERSIONS:
        names.update(r[2].split())
    for r in SMALL:
        names.update(r[3].split())
    return names


def render_report(data, out):
    e = html.escape
    evidence = data['evidence']
    def links(names):
        if isinstance(names,str): names = names.split()
        return '、'.join(f'<a href="#e-{e(n)}">{e(evidence[n]["title"])}</a>' for n in names)
    summary = ''.join(f'<tr><th>{e(c)}</th><td><b>{e(a)}</b></td><td>{e(b)}</td><td>{e(d)}</td></tr>' for c,a,b,d in OVERVIEW)
    sections=[]
    for i,(char,*_) in enumerate(OVERVIEW):
        articles=[]
        for r in FOCUS:
            if r['char']!=char:continue
            search=' '.join([r['name'],r['native'],r['curve']]+[evidence[n]['title'] for n in r['cards']])
            articles.append(f'''<article class="axis" data-char="{e(char)}" data-kind="{e(r['kind'])}" data-search="{e(search)}">
<div class="axis-top"><h3>{e(r['name'])}</h3><span>{e(r['kind'])} · {e(r['scope'])}</span></div>
<p class="native"><b>为什么属于伤害体系</b><br>{e(r['native'])}</p>
<h4>建设的是什么</h4><p>{e(r['investment'])}</p>
<h4>伤害曲线</h4><p>{e(r['curve'])}</p>
<div class="pair"><div><h4>主要决策</h4><p>{e(r['decisions'])}</p></div><div><h4>代价与边界</h4><p>{e(r['limits'])}</p></div></div>
<p class="refs"><b>代表牌</b>　{links(r['cards'])}</p>
{f'<details><summary>额外机制依据</summary><p>{links(r["sources"])}</p></details>' if r['sources'] else ''}</article>''')
        groups=[r for r in GROUPS if r['char']==char]
        group_html=''.join(f'<div class="subgroup"><h4>{e(r["name"])} <span>攻击子群／小型套件</span></h4><p>{e(r["why"])}</p><p>{e(r["feature"])}</p><p class="refs">{links(r["cards"])}</p></div>' for r in groups)
        sections.append(f'<section class="char-section" id="class-{i}" data-char="{e(char)}"><div class="section-title"><span>0{i+1}</span><h2>{e(char)}</h2></div><div class="axes">{"".join(articles)}</div>{f"<details class='group-list'><summary>同角色的原生攻击子群与小型输出套件</summary>{group_html}</details>" if groups else ""}</section>')
    conversion=''.join(f'<tr><th>{e(a)}</th><td>{e(b)}</td><td>{links(c)}</td><td>{e(d)}</td></tr>' for a,b,c,d in CONVERSIONS)
    small=''.join(f'<tr><th>{links(d)}</th><td>{e(b)}</td><td>{e(c)}</td></tr>' for a,b,c,d in SMALL)
    sources=''.join(f'<details class="evidence" id="e-{e(n)}"><summary>{e(v["title"])} <code>{e(n)}</code></summary><p class="path">{e(v["path"])}</p><p class="path">SHA-256 {e(v["sha256"])}</p><p class="raw">{e(v["description"])}</p><pre>{e(v["excerpts"])}</pre></details>' for n,v in evidence.items())
    nav=''.join(f'<a href="#class-{i}">{e(c[0])}</a>' for i,c in enumerate(OVERVIEW))
    opts=''.join(f'<option>{e(c[0])}</option>' for c in OVERVIEW)
    kinds=''.join(f'<option>{e(x)}</option>' for x in dict.fromkeys(r['kind'] for r in FOCUS))
    text=TEMPLATE
    for key,val in dict(CSS=CSS,SUMMARY=summary,SECTIONS=''.join(sections),CONVERSIONS=conversion,SMALL=small,SOURCES=sources,NAV=nav,CLASS_OPTIONS=opts,KIND_OPTIONS=kinds,COUNT=str(len(FOCUS)),SOURCECOUNT=str(len(evidence))).items():
        text=text.replace('@@'+key+'@@',val)
    assert '@@' not in text
    out.write_text(text,encoding='utf-8')
    print(json.dumps(dict(output=str(out),damage_axes=len(FOCUS),attack_groups=len(GROUPS),conversion_groups=len(CONVERSIONS),single_card_examples=len(SMALL),sources=len(evidence)),ensure_ascii=False))


CSS = r'''
:root{--bg:#f4f2eb;--surface:#fffef9;--border:#d8d7cb;--text:#202a27;--text-dim:#59685f;--green:#276955;--orange:#ac4c2c;--blue:#315d79}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:76px}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.8 "Microsoft YaHei UI","Noto Sans SC","Segoe UI",sans-serif}header,main,footer{max-width:1240px;margin:auto;padding:28px 34px}header{padding-top:52px}h1,h2,h3,h4,p{margin-top:0}h1{font:600 clamp(32px,4.1vw,54px)/1.25 "Noto Serif SC",SimSun,serif;max-width:900px;margin-bottom:22px}h1 em{font-style:normal;color:var(--green)}h2{font-size:25px;line-height:1.4;margin-bottom:16px}h3{font-size:21px;line-height:1.4;margin-bottom:8px}h4{font-size:13px;color:var(--text-dim);margin-bottom:5px}.eyebrow{font:12px/1.6 Consolas,monospace;letter-spacing:2px;color:var(--green)}.lead{font-size:19px;max-width:920px}.meta,.muted{font-size:13px;color:var(--text-dim)}a{color:var(--green);text-underline-offset:3px}nav{position:sticky;top:0;z-index:10;border-block:1px solid var(--border);background:#f4f2ebf7}.nav-inner{max-width:1240px;margin:auto;padding:10px 34px;display:flex;gap:19px;overflow:auto;white-space:nowrap}nav a{font-size:13px;text-decoration:none}section{margin-bottom:54px}.statement{background:#e9eee5;border-left:4px solid var(--green);padding:19px 23px;margin-bottom:26px}.statement p:last-child{margin-bottom:0}.distinction{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:22px 0}.distinction>div{border-top:3px solid var(--green);background:var(--surface);padding:20px;min-width:0}.distinction>div:last-child{border-top-color:var(--orange)}.distinction strong{font-size:18px}.distinction p{margin:10px 0 0}.table-wrap{overflow-x:auto;border:1px solid var(--border);background:var(--surface)}table{width:100%;border-collapse:collapse;text-align:left;min-width:760px}caption{text-align:left;font-weight:bold;padding:14px 17px}th,td{padding:14px 17px;border-top:1px solid var(--border);vertical-align:top;font-size:13px}thead{background:#e9eee5}tbody th{min-width:110px}td p{margin:0}.filters{display:grid;grid-template-columns:1fr 1fr 1.7fr;gap:15px;padding:18px;background:var(--surface);border:1px solid var(--border)}label{font-size:12px;color:var(--text-dim);min-width:0}select,input,button{font:inherit}select,input{display:block;width:100%;padding:9px 10px;margin-top:5px;background:var(--surface);border:1px solid var(--border);color:var(--text);border-radius:3px;min-width:0}button{cursor:pointer;padding:5px 12px;color:var(--green);border:1px solid var(--border);border-radius:3px;background:transparent}button:focus-visible,select:focus-visible,input:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid var(--orange);outline-offset:3px}.filter-status{display:flex;gap:18px;align-items:center;margin-top:12px;font-size:13px;color:var(--text-dim)}.section-title{display:flex;gap:20px;align-items:baseline;border-bottom:2px solid var(--text);margin-bottom:18px}.section-title>span{font:38px/1 Consolas,monospace;color:#a9b7a8}.axes{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}.axes:has(>.axis:only-child){grid-template-columns:1fr}.axis{background:var(--surface);padding:23px;border:1px solid var(--border);border-radius:4px;min-width:0}.axis p{font-size:14px}.axis-top>span{font-size:12px;color:var(--orange)}.native{margin-top:17px;background:#edf1e9;padding:13px 15px;border-left:2px solid var(--green)}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}.pair>div{min-width:0}.pair p{font-size:13px}.refs{font-size:12px!important;border-top:1px solid var(--border);padding-top:12px;margin-bottom:0}.axis details{margin-top:12px;font-size:12px}summary{cursor:pointer;color:var(--green)}details[open]>summary{margin-bottom:14px}.group-list{border:1px dashed #aab8a3;padding:16px 20px;margin-top:18px;background:#eeefe7}.subgroup{padding-top:14px;border-top:1px solid var(--border);margin-top:16px}.subgroup h4{color:var(--text);font-size:16px}.subgroup h4 span{font-size:11px;color:var(--text-dim);font-weight:normal;margin-left:10px}.subgroup p{font-size:13px;margin-bottom:10px}.models{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.model{padding:19px 20px;background:var(--surface);border-top:3px solid var(--green);min-width:0}.model h3{font-size:18px}.model p{font-size:14px}.formula{font-family:Consolas,"Microsoft YaHei",monospace;color:var(--blue)}.takeaways>p{border-top:1px solid var(--border);padding:18px 0;margin:0}.evidence{border-top:1px solid var(--border);padding:11px 0;scroll-margin-top:76px}.evidence pre{font:11px/1.6 Consolas,monospace;background:#edf0e8;padding:15px;white-space:pre-wrap;overflow-wrap:anywhere;max-height:480px;overflow:auto}.path,.raw{font-size:11px;overflow-wrap:anywhere;color:var(--text-dim)}code{font-size:11px;color:var(--text-dim);overflow-wrap:anywhere}#source-list{content-visibility:auto;contain-intrinsic-size:auto 900px}footer{border-top:1px solid var(--border);font-size:12px;color:var(--text-dim)}[hidden]{display:none!important}
@media(max-width:850px){header,main,footer{padding-inline:20px}.nav-inner{padding-inline:20px}.axes,.distinction{grid-template-columns:1fr}.filters{grid-template-columns:1fr 1fr}.filters label:last-child{grid-column:1/-1}.models{grid-template-columns:1fr}.lead{font-size:17px}}@media(max-width:440px){.pair,.filters{grid-template-columns:1fr}.axis{padding:18px}.filters label:last-child{grid-column:auto}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{nav,.filters,.filter-status{display:none}.axes{display:block}.axis{break-inside:avoid;margin-bottom:15px}body{background:white}}
'''

TEMPLATE = r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>原版五职业与 Karen · 以伤害为主责的体系</title><style>@@CSS@@</style></head><body>
<header id="top"><p class="eyebrow">DAMAGE PORTS / REVISED SCOPE / 2026.10.09</p><h1>哪些体系，<br><em>本来就负责伤害？</em></h1><p class="lead">先判断体系的主要职责，再分析伤害曲线。正文聚焦负责杀敌的体系；其他端口中的伤害转换牌只作为边界对照。</p><p class="meta">本地原版 v0.107.1 · 59260271；Karen 为 2026-10-09 工作区源码，HEAD e5a9115。分类是设计分析，不是官方流派名单或强度排名。配套规模较小的攻击子群与单卡核心另列，不凑成同一级“体系”。</p></header>
<nav aria-label="页内导航"><div class="nav-inner"><a href="#overview">判定与概览</a><a href="#catalog">伤害主轴</a>@@NAV@@<a href="#patterns">伤害特点</a><a href="#boundaries">转换旁注</a><a href="#single">单卡核心</a><a href="#lessons">惠惠启发</a><a href="#sources">依据</a></div></nav>
<main><section id="overview"><div class="statement"><p><b>本轮修正：</b>前稿把“哪里能找到伤害出口”和“哪个体系负责伤害”混在了一起。格挡能配全身撞击、灵魂能配纠缠、约定能配背靠背，都不足以证明这些机制整体属于伤害端。</p><p>本页现在研究的是：<b>以伤害载体、伤害增幅、攻击供给或击杀条件为核心组织起来的体系。</b>这些体系可以借用过牌、能量和防守，但杀敌机制是它自己的中心。</p></div>
<div class="distinction"><div><strong>伤害端体系</strong><p>建设的是力量、毒层、小刀、伤害球、攻击成长或死亡阈值。增加投入，主要是在增加杀敌能力。</p><p>例：灾厄不需要大限已至才能杀人；大限已至只是额外兑现方式。铸剑不需要招架才能成立；招架只是接向防守的配套。</p></div><div><strong>其他端口 → 伤害转换</strong><p>建设的首先是格挡、抽弃、调度或经济，少数牌再将这些资源、动作或记录转成伤害。</p><p>例：没有冰雹风暴，冰霜仍正常负责防守；没有背靠背，约定仍正常负责调度。本轮不把它们当原生伤害主轴。</p></div></div>
<p class="muted"><b>不是按“核心卡有几张”机械判断。</b>单核心伤害构筑也可能成立。判断应看核心状态／载体的用途、配套围绕什么目标组织，以及伤害是否只是从另一功能上接出的奖励。另一个独立问题是：它已经是体系，还是攻击子群／单卡核心。</p>
<div class="table-wrap"><table><caption>六职业：主要伤害职责与边界</caption><thead><tr><th>角色</th><th>重点分析的伤害体系</th><th>原生攻击子群／小型核心</th><th>本轮降为转换旁注</th></tr></thead><tbody>@@SUMMARY@@</tbody></table></div></section>
<section id="catalog"><h2>伤害主轴：建设什么，如何杀敌</h2><p class="muted">重点展开 @@COUNT@@ 条职责较清晰、配套可辨识的伤害主轴。每个角色后的折叠区补充规模较小或来自混合标签的攻击子群；它们不计入下方主轴筛选。</p><div class="filters"><label for="filter-char">角色<select id="filter-char"><option value="">全部角色</option>@@CLASS_OPTIONS@@</select></label><label for="filter-kind">主要伤害特点<select id="filter-kind"><option value="">全部特点</option>@@KIND_OPTIONS@@</select></label><label for="filter-search">搜索主轴或卡名<input id="filter-search" type="search" placeholder="例如：爪击、黑暗、临时力量"></label></div><div class="filter-status"><span id="result-count" role="status" aria-live="polite">显示 @@COUNT@@ 条伤害主轴</span><button id="clear" type="button">清除筛选</button></div><p id="empty" hidden>没有符合条件的伤害主轴。转换案例与单卡核心在后文单列。</p></section>
@@SECTIONS@@
<section id="patterns"><h2>这些体系真正不同的地方</h2><div class="models"><div class="model"><h3>持续产出</h3><p class="formula">毒 · 闪电 · 小刀供给</p><p>毒层决定未来多次结算，闪电球决定场上触发能力，小刀供给决定每轮可用攻击数量。都是续航，但它们保存的东西不同。</p><p><b>持续不等于成长：</b>一次上毒会衰减；固定球阵产出大致稳定；固定每回合产刀也不自动变强。</p></div><div class="model"><h3>越打越强</h3><p class="formula">力量 · 爪击 · 铸剑</p><p>力量强化广泛攻击，爪击强化同名家族，铸剑养一个载体。三者都能成长，但构筑密度、取回方式与兑现瓶颈不同。</p><p><b>成长也不等于等回合：</b>爪击靠使用次数推进，铸剑靠投入推进，恶魔形态才是典型时间驱动。</p></div><div class="model"><h3>集中兑现与终结</h3><p class="formula">黑暗 · 临时力量 · 灾厄</p><p>黑暗存未来伤害，临时力量提供有期限的攻击窗口，灾厄推进死亡阈值。它们可以很强，却不保证准备过程中持续扣血。</p><p><b>主要决策不同：</b>何时释放、何时续存、何时跨过阈值，分别控制这三类体验。</p></div></div></section>
<section id="boundaries"><h2>边界对照：有伤害出口，不等于主责是伤害</h2><p class="muted">这些转换可以成为某套实战构筑的最终胜利手段，甚至很强。这里只按用户要求区分体系的设计职责，不否认它们能组成可玩的构筑。</p><details><summary>展开其他端口的伤害转换案例</summary><div class="table-wrap"><table><caption>转换接口，仅作旁注</caption><thead><tr><th>机制</th><th>主要职责</th><th>相关牌</th><th>为什么不与伤害主轴并列</th></tr></thead><tbody>@@CONVERSIONS@@</tbody></table></div></details></section>
<section id="single"><h2>另一条边界：原生伤害单卡，也不自动等于体系</h2><p>这些牌本来就负责攻击或成长，适合借鉴具体伤害模式。是否发展成完整体系，还要看有没有足够的定向配套与构筑选择。</p><details><summary>展开单卡核心与小型攻击套件</summary><div class="table-wrap"><table><caption>看成长对象与期限，不夸大体系体量</caption><thead><tr><th>核心牌</th><th>成长／持续范围</th><th>设计特点</th></tr></thead><tbody>@@SMALL@@</tbody></table></div></details></section>
<section id="lessons"><h2>回到惠惠：先定义伤害端本体</h2><div class="takeaways"><p><b>积蓄首先是调度端。</b>即使放进去的攻击越来越强，或有牌按积蓄数量造成伤害，也应分别称为“积蓄支持的攻击核心”或“积蓄转伤害”，不能因此把积蓄本身当成第二条伤害体系。</p><p><b>吟唱爆裂是明确的伤害核心。</b>它把吟唱期间的出牌准备兑现为回合末群伤。若要再设计一条原生伤害路线，首先要明确它自己的攻击载体、成长规律与杀敌节奏，再决定如何借用积蓄和宣言。</p><p><b>新增一张成长攻击，是单卡方案；围绕成长攻击组织配套，才是体系方案。</b>可以先做小型核心，但应明确它处在哪个阶段。以上是分类与设计启发，未替用户定下新机制。</p></div></section>
<section id="sources"><h2>规则依据与分析范围</h2><p class="muted">规则沿用已核对的本地原版和 Karen 源码；本轮补查奥斯提攻击群与星费攻击群。保存 @@SOURCECOUNT@@ 个文件的路径、摘要与关键行，含前稿转换案例证据。分类与体系规模判断是设计归纳，未经实战平衡测试。</p><p><a href="docs/伤害体系源码证据.json">结构化源码证据</a> · <a href="惠惠核心设计简明版.html">当前惠惠核心规则</a> · <a href="#top">返回页首</a></p><button id="close-sources" type="button">收起源码条目</button><div id="source-list">@@SOURCES@@</div></section></main>
<footer>2026-10-09 · 以伤害为主责的体系研究 · 职责、伤害曲线与体系规模分开判断。</footer>
<script>
const fields=['char','kind','search'].map(k=>document.getElementById('filter-'+k));const axes=[...document.querySelectorAll('.axis')];
function filter(){const[c,k,q]=fields.map(x=>x.value.trim().toLowerCase());let n=0;axes.forEach(el=>{el.hidden=!!((c&&el.dataset.char.toLowerCase()!==c)||(k&&el.dataset.kind.toLowerCase()!==k)||(q&&!el.dataset.search.toLowerCase().includes(q)));if(!el.hidden)n++;});document.querySelectorAll('.char-section').forEach(s=>{s.hidden=![...s.querySelectorAll('.axis')].some(a=>!a.hidden);});document.getElementById('result-count').textContent=`显示 ${n} / ${axes.length} 条伤害主轴`;document.getElementById('empty').hidden=n>0;}
fields.forEach(el=>el.addEventListener('input',filter));document.getElementById('clear').addEventListener('click',()=>{fields.forEach(el=>el.value='');filter();});
function reveal(){const id=decodeURIComponent(location.hash.slice(1));const target=document.getElementById(id);if(!target)return;if(target.classList.contains('evidence'))target.open=true;if(target.classList.contains('char-section')&&target.hidden){fields.forEach(el=>el.value='');filter();}requestAnimationFrame(()=>target.scrollIntoView());}
window.addEventListener('hashchange',reveal);document.addEventListener('click',ev=>{const a=ev.target.closest('a[href^="#e-"]');if(a){const d=document.getElementById(a.hash.slice(1));if(d)d.open=true;}});document.getElementById('close-sources').addEventListener('click',()=>document.querySelectorAll('.evidence').forEach(el=>el.open=false));reveal();
</script></body></html>'''
