"""Build the offline lore-to-archetype report. No changes to game/design rules.

Run with Python 3. Reuses the complete existing 105-entry research inventory.
All gameplay loops below are proposals, distinct from the cited fictional facts.
"""
from pathlib import Path
from html import escape as esc
from collections import Counter
import json
import re

from build_explosion_reference import SOURCES as OLD_SOURCES, ENTRIES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "素晴原作流派与专有名词分析.html"
INDEX = "素晴爆裂魔法原作资料索引.html"
SOURCES = {k: dict(v) for k, v in OLD_SOURCES.items()}
EXTRA = {
    "anime5": ("动画官方：《爆焰》5·爆裂狂的诞生", "https://konosuba.com/bakuen/story/?mode=story5", "官方动画", "本轮读取；确认标题和技能点抉择，不能据此补写小说数值。"),
    "school": ("动画官方：《爆焰》1·红魔族与学校", "https://konosuba.com/bakuen/story/", "官方动画", "本轮读取；确认紅魔族、紅魔の里、レッドプリズン。"),
    "characters": ("动画官方：第三季角色资料", "https://konosuba.com/3rd/character/", "官方动画", "本轮读取；职业、魔道具店、队内职责及巴尼尔的见通能力。"),
    "bakuenchar": ("动画官方：《爆焰》角色资料", "https://konosuba.com/bakuen/character/", "官方动画", "本轮读取；悠悠的自称ライバル、同学和阿克西斯教团。"),
    "daily": ("动画官方：第一季第4话", "https://konosuba.com/1st/story/?id=04&mode=detail", "官方动画", "日常爆裂练习的官方入口；小说情节以正篇1第3章为主要依据。"),
    "destroyer": ("动画官方：第一季第10话", "https://konosuba.com/1st/story/?id=10&mode=detail", "官方动画", "破结界、双爆裂与要塞的改编梗概入口。"),
    "stealofficial": ("动画官方：第一季声优评论", "https://konosuba.com/1st/special/?mode=report", "官方动画", "既有名词资料确认Steal名称；不是技能数值规则书。"),
    "trpg": ("F.E.A.R.：《素晴TRPG》追加资料", "https://www.fear.co.jp/ksb/dlc/ksb_ex_data.pdf", "官方TRPG", "沿用已有访问记录；正式衍生规则，不能等同小说中的实际习得技能。"),
    "bakuretsudo": ("授权LINE贴图：爆裂道 ～めぐみん～", "https://store.line.me/stickershop/product/10811/ja", "授权周边", "本轮读取；名称可核实于动画授权贴图。未据此断定小说存在同名技能。"),
    "meguminthieves": ("出版社：《续·爆焰》1·吾等乃惠惠盗贼团", "https://www.kadokawa.co.jp/product/321607000363/", "官方小说简介", "确认她自行组建盗贼团及书名用词；没有据此声称她学会了Steal。"),
}
for key, (title, url, kind, note) in EXTRA.items():
    SOURCES[key] = dict(title=title, url=url, kind=kind, note=note)


def links(refs):
    return '<div class="refs">' + ''.join(
        f'<a href="{esc(SOURCES[r]["url"], quote=True)}" target="_blank" rel="noopener noreferrer">{esc(SOURCES[r]["title"])} ↗</a>'
        for r in refs) + '</div>'


def index_links(ids):
    by_id = {e['id']: e for e in ENTRIES}
    return '<div class="refs local-refs">' + ''.join(
        f'<a href="{INDEX}#{key}">{esc(by_id[key]["title"])} →</a>' for key in ids) + '</div>'


# Start with what Megumin herself names or uses, before broader design proposals.
PERSONAL = [
    dict(name="爆裂魔法", original="爆裂魔法／エクスプロージョン", status="习得魔法", fact="她亲自习得并长期专精的核心攻击魔法。平常一发后魔力枯竭、无法行动。", design="核心攻击。蓄势、一击、脱力都围绕这一招展开。", note="不是拥有一整套火球、雷击、传送法术。", refs=["b156", "m13"]),
    dict(name="爆裂威力提升", original="Explosion Damage Increase；爆発系魔法威力上昇（日文据技能索引）", status="强化技能", fact="第一卷她列出这一技能；第五卷和真把预留技能点投入爆裂强化。", design="强化同一招、持续专精：这是单发威力方向最直接的原作技能素材。", note="日文‘爆発系’是类别名，不能据此认定她另外学了爆発魔法。", refs=["m13", "m56", "skills"]),
    dict(name="高速咏唱", original="Fast Chanting／高速詠唱（日文据技能索引）", status="本人提及的技能", fact="第一卷本人谈爆裂相关技能时明确提及。第九卷也确实描写她咏唱很快。", design="缩短准备、抢先施放、衔接操作；可直接借用这个技能名。", note="第五卷揭示她曾预留技能点，不能仅凭早期自述断言具体加点史；快速施法也不自动证明买过这个技能。", refs=["m13", "m56", "m95", "skills"]),
    dict(name="无咏唱爆裂", original="无咏唱施法的剧情描述；不是另一种爆裂魔法", status="实际施法技巧", fact="第九卷与沃尔巴克对决，惠惠说明自己已经能不念长咒控制爆裂，并抢先施放。", design="省去准备、直接兑现、先手一击。比单纯‘速度增加’有更具体的动作。", note="确认的是施法技巧；尚未确认冒险者卡上存在‘无咏唱’同名技能。", refs=["m95", "m171"]),
    dict(name="魔眼束缚", original="Crimson Eye Bind（公开英译中的招名；中文为工作译名）", status="戒指赋予的招式", fact="《寄道》3第一章，惠惠用魔眼让悠悠和其他冒险者不能移动。", design="控制、定身、制造输出窗口。名字和具体动作都可以直接作为命名素材。", note="来自诅咒戒指的临时能力；不是她常规习得的第二种魔法。", refs=["y31"]),
    dict(name="魔眼雷击", original="Crimson Eye Lightning（公开英译中的招名；中文为工作译名）", status="戒指赋予的招式", fact="同篇中从眼睛射出电击命中悠悠，同时灼伤自己的眼睛。", design="有反噬的攻击：伤敌、自伤与争夺爆裂所需的魔力。", note="眼睛真实受伤；魔眼耗掉她的魔力，之后当天爆裂也放不出来。", refs=["y31"]),
    dict(name="隐身卷轴", original="通过折射光线隐身；所读小说译文未给出统一法术专名", status="本人使用的道具", fact="《爆焰》3中，惠惠亲自用悠悠准备的卷轴隐身，远处观察霍斯特战斗。", design="潜伏、等待时机、突袭；适合少量战术牌。", note="隐身来自卷轴，没有改变她的魔法学习路线。", refs=["b34"]),
    dict(name="开膛手Shack的诅咒剑", original="Sword of Shack the Ripper；中文专名未对照授权译本", status="本人使用的道具", fact="第二卷特典中，惠惠用它斩开桌子和笼锁。剑以魔力切断物体，魔力高的人更易使用，却无法伤害生物。", design="斩物、拆障、破坏装备、借来力量后的自信与失算。", note="她没有因此学会剑士职业；面对巨蛙时，这把剑救不了她。", refs=["ss2"]),
    dict(name="最高级魔力矿石", original="マナタイト／Manatite", status="本人使用的补给", fact="最高级品能替代爆裂所需魔力；后期惠惠依靠库存连续施放。", design="消耗外部库存换施放机会。适合昂贵补给与有限连发题材。", note="材料专名很具体；‘连发’是使用结果，不是已确认的同名新技能。", refs=["m165", "m171"]),
]

PERSONAL_NAMES = [
    ("吾名惠惠／红魔族第一天才", "我が名はめぐみん／紅魔族一の天才", "第一次放爆裂时的本人宣言。适合登场、专精、宣言牌名；属于自称。", ["b156"]),
    ("爆裂娘／爆裂狂", "前者为他人绰号的中文工作译法；爆裂狂确认于官方动画标题", "直接指向惠惠本人及其爆裂执念。可以包装能力牌、专精奖励，不能直接推导出狂怒叠层。", ["y31", "anime5"]),
    ("魔眼惠惠", "Demon Eye Megumin（公开英译中的本人自称）", "《寄道》3获得魔眼后自称的恶魔身份。适合戒指、暂时变身与反噬题材。", ["y31"]),
    ("惠惠盗贼团", "我ら、めぐみん盗賊団（小说副标题）", "她憧憬银发盗贼团后自行组建的团队。是她的冒险身份素材，不能据此给她Steal。", ["meguminthieves"]),
]


def personal_html():
    return ''.join(
        f'<tr id="personal-{i}"><th scope="row">{esc(p["name"])}<small>{esc(p["original"])}</small><span class="pill">{esc(p["status"])}</span></th>'
        f'<td><p>{esc(p["fact"])}</p><small>{esc(p["note"])}</small>{links(p["refs"])}</td>'
        f'<td>{esc(p["design"])}</td></tr>'
        for i, p in enumerate(PERSONAL, 1))


def personal_names_html():
    return ''.join(
        f'<tr><th scope="row">{esc(name)}<small>{esc(original)}</small></th><td>{esc(fact)}{links(refs)}</td></tr>'
        for name, original, fact, refs in PERSONAL_NAMES)


# Each direction includes a distinctive loop and the decisions it asks of players.
ROUTES = [
    dict(id="fanatic", name="爆裂狂 · 极致一发", rank="主轴", identity="高", origin="爆裂狂是官方动画标题用词；‘极致一发’是本报告的设计副标题。", summary="把准备资源尽量投入同一发爆裂，追求一次兑现的质量。", fact="惠惠主动放弃实用魔法路线；第5卷和真替她继续强化爆裂，第9卷说明她将升级点数投入威力。", loop=["保存关键牌", "集中减费／强化", "开吟唱兑现", "重新准备"], decision="现在释放足够解决敌人，还是多准备一回合换取更高收益？", proposal="让积蓄中的关键强化牌在释放回合发挥作用；少量能力牌可以强化后续爆裂。单发积累与整场成长须分别写清，原作没有战斗叠层公式。", fit="适配当前核心", current="压缩魔力已经提供存牌后减费。若需要少量高质量牌也能提高群伤，需另有明确的爆裂强化效果；当前群伤公式只数实际出牌数量。", vocab="爆裂狂、技能点、爆裂魔法、魔力凝练", examples="卡名方向：爆裂狂的执念、孤注一发、只为爆裂。均为自拟。", limit="‘爆裂狂’不能自动解释成狂怒值、生命越低越强或无限增长。", refs=["anime5", "b148", "m56", "m9p"], entries=["s-choice", "s-growth", "p-5-choice", "s-learn", "n-megumin"]),
    dict(id="declaration", name="红魔族 · 宣言连奏", rank="主轴", identity="高", origin="红魔族是作品族群名；‘宣言连奏’是设计命名，不是原作技能。", summary="在同一次吟唱里打出更多牌，把惠惠的仪式感做成连续操作。", fact="红魔族追求帅气演说；惠惠首次爆裂前报上姓名。咏唱具有技术作用，中二宣言又有性格与演出作用。", loop=["存低费组合", "爆裂开吟唱", "续接咒文与支援", "回合末爆发"], decision="先用牌解决眼前需求，还是先开吟唱，让后续操作全部计入爆裂？", proposal="利用低费、抽牌和有限回能增加吟唱期间的实际出牌数。宣言与报姓名用于卡名和反馈，不必另设一个宣言资源。", fit="最直接适配", current="咒文续接已是这一方向的清晰入口。压缩后的免费牌与回流一击都能接入现有出牌计数；不增加重复开吟唱规则。", vocab="红魔族、吾名惠惠、咏唱、咒文、爆焰", examples="卡名方向：吾名惠惠、天才的宣言、咒文续接。后两项为自拟；第一项是台词意译。", limit="不是原作每念一句就获得一层威力；不能把动画长咒词当作小说固定必念文本。", refs=["b114", "b156", "m171", "school"], entries=["s-pronunciation", "s-practice", "s-chant", "p-b-first"]),
    dict(id="walk", name="爆裂散步 · 日课循环", rank="主轴", identity="高", origin="‘爆裂散步’按既有资料沿用为日课题材的中文标签；本轮未逐字确认其日文固定称呼。", summary="一发之后还有下一轮：回收、保存、恢复，形成多回合循环。", fact="和真长期陪她练习、背她回去、给爆裂评分；悠悠也帮助填坑和背人。日课是关系与生活习惯的一部分。", loop=["准备本轮", "完成一次爆裂", "善后与回流", "保存下轮组合"], decision="这一轮把牌全部用掉，还是留下下一轮的准备，保持循环不断？", proposal="围绕释放后的返手、存牌、下一回合资源设计收益；战斗内日课成长属于改编，可以只用卡牌效果表达，不新增日课计数器。", fit="适配当前核心", current="回流一击提供重复使用与自行入区的入口；吟唱期间新存入的牌留给下一回合。它与同回合持续出牌的关注点不同。", vocab="爆裂散步、日课、背回家、爆裂鉴赏", examples="卡名方向：今日也要一发、散步归途、明日的爆裂。均为自拟。", limit="每天练习不等于不练就会死；也不等于原作每放一次自动获得固定战斗增伤。", refs=["m13", "m81", "m9p", "dustss", "daily"], entries=["p-1-castle", "p-8-walk", "p-9-style", "p-11-routine", "p-dust-observe", "n-kazuma"]),
    dict(id="manatite", name="魔力矿石 · 储备供能", rank="替代候选", identity="高", origin="マナタイト／Manatite是原作物品名；‘储备供能’为设计描述。", summary="储存外部施法资源，以消耗库存换取更多释放机会。", fact="最高级Manatite能替代爆裂所需魔力，使用后消失，价格极高。第16—17卷的大量库存支持连续轰击。", loop=["取得矿石", "保存库存", "消耗供能", "继续施放"], decision="为这一轮花掉稀缺库存，还是留给之后更困难的回合？", proposal="优先作为稀有道具或补给套件：有限减费、回能、为后续回合准备。若要真正做同回合多次爆裂，则成为另一套核心方案。", fit="同回合连发有冲突", current="用户已确认吟唱期间不能再打爆裂。不能为矿石题材直接解除这条规则；跨回合补给仍能接入当前方案。", vocab="魔力矿石、最高级Manatite、维兹的魔道具店", examples="卡名方向：最高级魔力矿石、昂贵的赠礼、矿石库存。后两项为自拟。", limit="没有依据把多块矿石合并成无限增强的一发；普通矿石也不能默认足以支付爆裂。", refs=["m165", "m171", "m17pub"], entries=["s-gem", "t-manatite", "p-16-gift", "p-17-castle", "p-17-last"]),
    dict(id="raid", name="传送袭击 · 打完撤退", rank="小套件", identity="中", origin="爆裂与Teleport的组合有小说剧情；‘传送袭击／游击爆裂’为本报告命名。", summary="先制造输出窗口，再在爆裂之后转入防御与下一次准备。", fact="第9卷沃尔巴克远距离爆裂后传送离开；和真、惠惠、悠悠以潜伏接近、爆裂打击、悠悠传送撤离反击。", loop=["潜伏接近", "完成爆裂", "撤退／保护", "再度准备"], decision="在敌人攻击前抢先输出，还是先做好释放后的保护？", proposal="将支援牌或延迟收益放在爆裂结束后、下一回合开始时结算；可支持日课循环，但需要少量牌便能表达，无须构建完整空间系统。", fit="须定义结算时点", current="当前爆裂在回合末结算；‘爆裂后立刻抽牌并继续出牌’不能直接兑现，应写成下一回合收益或非出牌收益。", vocab="悠悠的传送、沃尔巴克、潜伏、爆裂魔法", examples="卡名方向：悠悠的传送、打完就跑、故技重施。均为题材化命名。", limit="惠惠未因此学会Teleport；不能把‘爆杀魔人’当她的游击称号。", refs=["m94", "m95", "m155"], entries=["p-9-raids", "p-15-plan", "n-wolbach", "n-yunyun"]),
    dict(id="relay", name="伙伴接力 · 为爆裂创造窗口", rank="小套件", identity="中", origin="人物与协作情节为原作素材；‘伙伴接力’为自拟玩法标签。", summary="让防御、削弱、供魔和控制服务于惠惠的一击。", fact="毁灭者战有破结界、双爆裂及Drain Touch转魔；海德拉与霍斯特战先经多人削弱；达克妮丝保护咏唱。", loop=["防御或削弱", "补充资源", "抓住机会", "爆裂收尾"], decision="这一回合需要哪种支援，才能让爆裂安全而有效地兑现？", proposal="用现有‘吟唱：’条件和积蓄牌承载队友支援。队友题材可以提供不同功能，不必每个人都建一套召唤物系统。", fit="适配，保持主体", current="已在吟唱时触发支援收益，也可存关键支援到释放回合。用抽牌／回能／格挡即可表达，不增加多种人物计数器。", vocab="Drain Touch、悠悠的自称对手、达克妮丝的保护、阿库娅的破结界", examples="卡名方向：可靠的前排、不坦率的援助、交给我吧。均为自拟。", limit="这些不同魔法由队友或道具承担，不代表惠惠放弃专精、学齐所有魔法。", refs=["m25", "m72", "b34", "y13"], entries=["s-once", "s-team", "p-2-destroyer", "p-7-hydra", "p-b-hoost", "p-y1-front", "p-y1-copy"]),
    dict(id="rating", name="爆裂鉴赏 · 漂亮地完成这一发", rank="小套件", identity="高", origin="和真担任鉴赏者、给分的情节明确；中文称号沿用工作译名，并非技能等级名称。", summary="除了大伤害，还追求一发的完成方式与质量。", fact="第5卷有120分评价；第9卷序章评价威力、热风和弹坑形状。它是惠惠与和真之间的私人鉴赏。", loop=["取得鉴赏条件", "安排本轮操作", "释放爆裂", "达成条件获益"], decision="只求及时击杀，还是兼顾这一发的额外条件？", proposal="让少量能力牌在本轮满足指定条件时强化爆裂或准备下轮。条件例如吟唱中做过防御、出牌达到一定数量，均由Mod设计。", fit="可用少量条件牌", current="复用已有吟唱出牌数、积蓄与格挡等信息，不新增一个复杂评分系统。具体条件不能伪装成小说评分表。", vocab="爆裂鉴赏、120分、爆裂即艺术", examples="卡名方向：一百二十分、圆满的弹坑、爆裂即艺术。前两项为情节提炼，第三项为特典篇名译法。", limit="分数不是伤害单位；不能写成‘120分爆裂＝120伤害’的原作公式。", refs=["m56", "m9p", "ss3"], entries=["s-rating", "p-9-style", "p-ss-art"]),
    dict(id="shop", name="维兹的魔道具店 · 道具补足专精", rank="小套件", identity="高", origin="维兹经营魔道具店是官方角色资料；套件名据此提炼。", summary="在仍然只学爆裂的前提下，用消耗道具补齐其他用途。", fact="惠惠得到同学制作的法杖和眼罩；悠悠安排隐身卷轴；最高级矿石又来自维兹、巴尼尔相关的商品交易。", loop=["获得道具", "准备适合的物资", "择机使用", "辅助爆裂"], decision="现在消耗道具解决问题，还是把它作为下一发的准备？", proposal="用有限生成牌、消耗牌和升级装备表达。法杖适合稳定增强，卷轴适合一次性支援，矿石适合供能，不全塞进同一‘魔石’资源。", fit="可接入存牌区", current="道具牌能进入积蓄，免费标记只作用于指定一次打出。生成／购买、消耗／回收的边界要在卡面写明。", vocab="维兹的魔道具店、法杖、卷轴、Manatite", examples="卡名方向：维兹的新品、同学们的礼物、一次性卷轴。均为自拟。", limit="店铺亏损是喜剧设定，不代表任何商品都有随机自伤；眼罩不是已确认的真正封印。", refs=["characters", "b22", "b34", "m165"], entries=["t-staff", "t-eye", "t-scroll", "p-b-gifts"]),
    dict(id="aftercare", name="脱力与善后 · 一发的代价", rank="成本与支援", identity="中", origin="脱力、背回去和补魔为剧情行为；不是原作的统一状态系统。", summary="用明确而可恢复的代价，让一发爆裂有重量。", fact="首次爆裂消耗魔力与体力，之后需要同伴保护；和真有只补少量魔力让她走路的情节。维兹能爆裂后继续行动。", loop=["完成施法", "承担短暂代价", "获得善后支援", "继续行动"], decision="能否承担释放后的空档，是否已留下恢复或防御手段？", proposal="把代价限制在清晰时点，并配置恢复、保护和存牌收益。可以成为角色共通规则或少量牌的主题，通常不需要独立流派。", fit="新成本需另行决定", current="当前方案未确认新脱力惩罚。报告只给题材方向，不加跳过回合、固定扣血或清空积蓄等规则。", vocab="背回家、担架、Drain Touch、魔力耗尽", examples="卡名方向：背我回去、担架上的功臣、还能自己走。均为情节命名。", limit="不是所有爆裂使用者必然倒地；矿石连发后的鼻血也没有固定中毒阈值。", refs=["b156", "m92", "m64", "dust7"], entries=["s-collapse", "s-transfer", "s-wiz", "p-6-capital", "p-dust7", "p-y3-wiz"]),
    dict(id="terrain", name="爆心与地形 · 单牌和遗物素材", rank="单牌／遗物", identity="中", origin="均为剧情现象；‘余波流’尚无持续状态规则的原作依据。", summary="利用爆心、冲击、噪音与破坏后果丰富少量牌。", fact="爆裂会破坏地形、影响地下城；有故意偏移爆心的场景；炸散汉斯后还需冻结与净化。", loop=["选择施放条件", "造成爆裂", "利用破坏后果", "同伴善后"], decision="爆裂的主目标与附带后果是否都能接受？", proposal="少量牌可表达溅射、削弱、对特定敌人的额外效果；不用为了每一条地形描写新建一个常驻地形区。", fit="局部扩充可行", current="当前爆裂为群伤，没有爆心选取规则。定点、地形与持续余波均是新增机制，应当标为候选。", vocab="爆心、弹坑、冲击波、拆屋事故", examples="卡名方向：故意打偏、巨大的弹坑、拆迁魔法。均为自拟。", limit="小说冲击波不等于数回合持续伤害；爆裂也不是仅有火属性的燃烧法术。", refs=["b113", "ss4", "c25", "m45", "m174"], entries=["s-area", "s-miss", "p-ss-kind", "p-c2-nest", "p-4-hans", "p-17-kazuma"]),
    dict(id="ancient", name="古代兵器与连锁爆炸 · 稀有题材", rank="单牌／遗物", identity="高", origin="毁灭者与Coronatite为名词；轨道炮、会爆炸的蘑菇按对应情节理解。", summary="很有记忆点，但多数只是一场战斗或一则短篇。", fact="第5卷轨道炮吸收爆裂后充满能量，由小米扣动扳机；毁灭者有危险核心；短篇蘑菇会被强魔力刺激而连锁爆炸。", loop=["发现特殊条件", "用爆裂触发", "转换或连锁结算", "处理后果"], decision="为了特殊收益改变本次爆裂的用途，是否值得？", proposal="作为稀有牌、遗物或事件更稳：一次能量转换、一次连锁、一次高代价收益。独立兵器流需要明显偏离惠惠的日常施法主体。", fit="不优先扩为主轴", current="只有素材依据，没有为当前方案添加充能条、兵器召唤或蘑菇标记。", vocab="机动要塞毁灭者、Coronatite、轨道炮、小米抢先开火、爆裂侦探", examples="卡名方向：满格充能、小米抢先开火、爆裂侦探。前两项为情节提炼，第三项为篇名题材。", limit="Coronatite不是补魔用的Manatite；小米没有因此学会爆裂；电影追加战不能反写成小说。", refs=["m25", "m55", "y12"], entries=["p-5-sylvia", "t-railgun", "t-coronatite", "p-y1-mushroom", "n-komekko"]),
    dict(id="curse", name="戒指、借贷与封印 · 事件或外部能力", rank="单牌／事件", identity="中", origin="戒指与禁用诅咒出自《寄道》；‘力量被封印’也有另一个玩笑语境。", summary="能承载代价与借用力量，但不适合作为惠惠常规能力。", fact="《寄道》3中借戒指使用魔眼力量会消耗魔力；欠款引发真正禁用爆裂的诅咒。《续·爆焰》2则是和真抽魔后称力量封印。", loop=["借用外部力量", "付出魔力或债务", "暂时获益", "解除代价"], decision="外部收益是否值得牺牲这一发爆裂或承担后续成本？", proposal="稀有事件或带清晰代价的道具即可表达；不默认加入常驻魔眼／封印解除第二形态。", fit="不优先扩为主轴", current="当前积蓄循环不依赖魔眼或封印。本报告不替它增加新的长期诅咒资源。", vocab="恶魔戒指、巴尼尔、借贷、力量封印（语境分开）", examples="卡名方向：借来的魔眼、先付清欠款、力量被封印了。均为情节提炼。", limit="眼罩造型不能证明眼内真实封印；欠款诅咒与抽魔不足必须分开。", refs=["y31", "c25", "b22"], entries=["p-y3-ring", "p-c2-drain", "q-seal-real"]),
]

TERMS = []


def term(key, name, japanese, kind, distinction, use, reason, refs, note=""):
    TERMS.append(dict(id=key, name=name, japanese=japanese, kind=kind,
                      distinction=distinction, use=use, reason=reason, refs=refs, note=note))


# Distinction is an editorial assessment of association, not exclusivity.
term("explosion", "爆裂魔法／Explosion", "爆裂魔法／エクスプロージョン", "原作用词", "高", "核心动作", "词本身并非所有作品独占；与一发脱力、专精和标志性喊声组合，惠惠联想非常强。", ["b156", "characters"])
term("fanatic", "爆裂狂", "爆裂狂", "官方动画", "高", "流派／能力牌", "比‘魔力强化’更直接指向惠惠对同一魔法的执念。", ["anime5", "b148"], "确认于动画第5话标题；不是已核实的同名叠层技能。")
term("crimson", "红魔族", "紅魔族", "原作用词", "高", "身份／流派包装", "高魔力、高智力和中二文化共同构成作品族群特征。", ["school", "b114"])
term("walk", "爆裂散步／每日一发", "日课题材；日文固定短语待对照", "剧情题材", "高", "循环套件／卡名", "练习、陪伴、背回去与城堡投诉形成素晴特有的日常链条。", ["m13", "m81", "daily"], "中文题材标签，不宣称小说有同名正式技能。")
term("rating", "爆裂鉴赏／120分", "Explosion Connoisseur（英译称号）", "剧情题材", "高", "条件牌／循环奖励", "和真给热风、威力、弹坑打分的私人审美，比通用‘熟练度’更有个性。", ["m9p", "m56"], "中文称号为工作译法；分数不是伤害单位。")
term("manatite", "魔力矿石／Manatite", "マナタイト", "原作用词", "高", "补给／消耗品", "保留Manatite专名和昂贵、一次性、最高级品的情境，比‘魔石’更有辨识度。", ["m165", "m17pub"], "中文名称通用感较强，建议附日文或英文；不是全球独占命名声明。")
term("village", "红魔之里", "紅魔の里", "原作用词", "高", "成长事件／遗物", "世界观地点与红魔族天才、中二文化绑定。", ["school"])
term("school", "Red Prison", "レッドプリズン", "官方动画", "高", "学习牌／成长事件", "学校专名很鲜明，能承载课程、积攒技能点和同学赠礼。", ["school", "b22"], "‘红色监狱’仅作直译线索，授权中文译名未统一核对。")
term("chomusuke", "逗之助", "ちょむすけ", "原作用词", "高", "守护／遗物／演出", "角色专名和黑猫形象有很强联想，适合陪伴与保护题材。", ["b155", "m95"], "没有自动给惠惠回魔的常驻宠物机制证据。")
term("axis", "阿克西斯教团", "アクシズ教団", "官方动画", "高", "外援／事件", "宗教组织专名与布教喜剧鲜明；适合阿库娅、塞西莉相关支援。", ["bakuenchar", "b24"], "不因此把惠惠改成祭司或以信仰作为常驻魔力来源。")
term("shop", "维兹的魔道具店", "ウィズの魔道具店（描述）", "原作题材", "高", "道具套件／遗物", "加上店主，通用魔道具就变成赤字店铺、巴尼尔与物资交易的作品情境。", ["characters", "m165"], "是带人物限定的描述，未确认这串字作为商店正式注册名称。")
term("destroyer", "机动要塞毁灭者", "機動要塞デストロイヤー", "原作用词", "高", "稀有牌／遗物／事件", "古代暴走兵器与双爆裂协作战，事件辨识度很强。", ["m25", "destroyer"])
term("coronatite", "Coronatite／毁灭者核心", "コロナタイト", "原作用词", "高", "高代价遗物／事件", "危险动力核心专名，适合危机或外部兵器题材。", ["m25"], "不是Manatite，不能因为中文都称魔石便当同一种补魔品。")
term("mog", "爆杀魔人もぐにんにん", "爆殺魔人もぐにんにん", "名词线索", "高", "敌人主题／稀有牌", "红魔乡造物的专名很鲜明，但属于敌人。", ["m144", "mog"], "日文拼写据二手索引；本篇14卷对照功能。它用的爆発与惠惠的爆裂不同，不是惠惠的游击称号。")
term("name", "吾名惠惠", "我が名はめぐみん", "原文台词", "高", "宣言牌／演出", "报姓名把原本通用的施法准备变成惠惠的登场仪式。", ["b156"], "中文为意译；不是额外技能，长咒词不按记忆整段还原。")
term("art", "爆裂即艺术", "Explosion is Art（公开译文篇名）", "篇名题材", "高", "能力牌／鉴赏套件", "体现对爆裂美感的追求，区别于单纯魔法伤害增加。", ["ss3"], "中文篇名为工作译法；不是小说固定增伤技能。")
term("detective", "爆裂侦探", "Explosion Detective（英译章节题材）", "篇名题材", "高", "事件／稀有牌", "一度禁用爆裂、调查连环爆炸与蘑菇连锁，喜剧记忆点强。", ["y12"], "未核对授权中文版的完整章名。")
term("dragon", "屠龙者惠惠", "Megumin the Dragon Slayer（英译篇名）", "篇名题材", "中", "稀有牌／称号", "比通用‘屠龙者’更有角色辨识度，来自碎岩工作与幼年飞龙场景。", ["ss1"], "不是惠惠常驻职业；页面卷号与URL存在差异，以篇名定位。")
term("do", "爆裂道", "爆裂道", "授权周边", "高", "总主题／能力牌名", "授权贴图直接以此命名，强调钻研同一魔法的道路。", ["bakuretsudo"], "本轮仅确认授权贴图用词，未确认小说同名技能。适合借名，不继承联动游戏效果。")
term("bakuen", "爆焰", "爆焔", "作品标题", "中", "总主题／稀有牌名", "与外传作品标题有关，具作品联想，但作为机制含义不清。", ["school"], "不是已经确认的第四种爆炸系魔法。")
term("yunyun", "悠悠的自称对手", "自称ライバル", "原作题材", "高", "接力／回应牌", "竞争与关心同时存在，比‘宿敌’更准确也更贴两人关系。", ["bakuenchar", "b34"], "ライバル是对手／竞争者；‘宿敌’容易误导成真正敌对。")
term("wolbach", "沃尔巴克／红之宿命", "ウォルバク／紅の宿命（卷名）", "原作用词", "高", "传承／稀有事件", "童年启蒙者与后期对决连接成长和情感代价。", ["m9pub", "m95", "b1p"], "人物身份与序章需交叉确认；‘红之宿命’是卷名，不是技能。")
term("railgun", "轨道炮／小米抢先开火", "Railgun（英译称呼）", "剧情题材", "中", "稀有牌／遗物", "轨道炮本身不独特；吸收爆裂充能、妹妹抢扳机这个组合很有素晴辨识度。", ["m55"], "小米射击兵器不等于学会爆裂；小说与电影扩写分开。")
term("aftercare", "背回家／担架上的功臣", "剧情行为标签", "剧情题材", "高", "防御／恢复／循环牌", "最强一击与随后的狼狈反差，比通用‘过载’更贴惠惠。", ["b156", "m64", "dustss"], "题材化命名；不自动产生必须跳过回合的规则。")
term("drain", "Drain Touch／魔力转移", "ドレインタッチ", "原作用词", "中", "队友补给牌", "吸取类法术本身通用，但和真从阿库娅转魔给惠惠、补到能走路的情境鲜明。", ["m25", "m92"], "按队友技能命名；不是惠惠自己学会的法术。")
term("teleport", "悠悠的传送", "テレポート／Teleport", "原作题材", "中", "撤退／回收／循环", "Teleport本身通用，加上悠悠与爆裂袭击撤退，才能产生作品辨识度。", ["m95"], "传送支援者是悠悠；惠惠仍是爆裂的主炮。")
term("chant", "咏唱／吟唱", "詠唱／呪文詠唱", "原作用词", "低", "核心状态／条件词", "原作确实使用，玩家也易理解；大量作品共用，辨识度主要来自宣言、咒文和爆裂。", ["b114", "m171"], "本项目当前状态采用‘吟唱’；旧词表的待触发‘咏唱：’建议不是当前规则。")
term("condense", "魔力凝练／魔力凝缩", "据練り上げられる魔力等描写提炼", "原文提炼", "低", "蓄力状态／卡名", "与首次施法准备的描写贴近，读得懂，但单看词并不比其他魔法作品独特。", ["b156"], "是据原文提炼的中文名，不是已确认的官方技能名。")
term("storage", "魔力积蓄", "项目自拟机制名", "项目命名", "低", "当前核心牌区", "存手牌、生成爆裂、开吟唱返手的具体循环才形成玩法特色。", [], "用户已采用的游戏机制；小说没有独立存牌区或返手规则。")
term("mana", "魔力", "魔力", "原作用词", "低", "资源解释", "术语普遍；不宜单凭‘魔力流’作为素晴特有流派。", ["b148", "school"])
term("skillpoint", "技能点／冒险者卡", "スキルポイント／冒険者カード", "原作用词", "中", "成长／专精奖励", "多数异世界作品共有，但用冒险者卡决定只学爆裂，能体现人物选择。", ["b148", "b155"], "成长资源，不默认与每回合能量或牌区数量等同。")
term("hierarchy", "炸裂／爆发／爆裂", "炸裂魔法／爆発魔法／爆裂魔法", "原作用词", "中", "分类说明／外援", "作品明确区分三种魔法，能避免只把Explosion看成普通火球升级。", ["b113"], "惠惠没有因此学全三种；中文相近也不能混成同一个技能。")
term("spellskills", "爆发系魔法威力上升", "爆発系魔法威力上昇（索引拼写）", "名词线索", "低", "专精能力牌", "功能上贴成长，名称本身偏通用，适合配爆裂狂主题包装。", ["m13", "skills"], "功能与技能名拼写分开；具体名称以二手索引为线索，未完成授权日文逐页对照。")
term("upper", "上级魔法／大魔法师", "上級魔法／アークウィザード", "原作用词", "低", "职业／专精对照", "名词通用；‘可以学却主动只学爆裂’才是个性。", ["b148", "characters"])
term("lucky", "冒险者／幸运／盗贼／Steal", "冒険者／幸運／盗賊／スティール", "原作题材", "低", "和真或克莉丝支援", "单独都很通用，人物限定与临场调度可以强化素晴联想。", ["characters", "stealofficial"], "不因此新增惠惠偷取系统；Steal名称确认与精确技能规则分开。")
term("aqua", "大祭司／女神／回复魔法／宴会才艺", "アークプリースト／女神／回復魔法／宴会芸", "官方动画", "低", "阿库娅支援", "单看都通用，恢复与宴会才艺并置才有阿库娅的反差。", ["characters"], "宴会才艺是类别，不是单个法术。角色人名本身不充数成一种流派。")
term("crusader", "十字骑士／可靠的前排", "クルセイダー", "官方动画", "低", "达克妮丝防御牌", "职业普遍，达克妮丝强耐久与攻击难命中的反差构成辨识度。", ["characters", "y13"], "只用于支援题材，不默认惠惠能无代价扛住自己的爆裂。")
term("vanir", "见通／假面", "見通す／仮面", "官方动画", "低", "巴尼尔预知／遗物", "通用描述；与巴尼尔、恶感情、维兹店铺绑定后更有特色。", ["characters"], "此处只确认描述，未把‘见通’扩写为完整正式技能名。")
term("gram", "魔剑格拉姆", "魔剣グラム", "官方动画", "中", "外援／稀有遗物", "素晴里由御剑使用；Gram也是其他神话与作品会使用的名字，且离惠惠核心较远。", ["characters"])
term("barrier", "结界防御／紧急任务", "結界防御／緊急クエスト", "原作题材", "低", "条件／战斗主题", "通用名词，搭配毁灭者来袭与协作破防才有具体记忆点。", ["m25", "destroyer"])
term("equipment", "法杖／眼罩／卷轴", "杖／眼帯／巻物", "原作题材", "低", "道具／遗物", "物件普遍；同学赠礼、阿露赠眼罩、悠悠购买卷轴的关系使它们独特。", ["b22", "b34", "b156"], "眼罩未证实真实封印；卷轴效果不等于她习得其他魔法。")
term("terrain", "爆心／冲击波／余波", "现象描述，未确认统一技能名", "剧情题材", "低", "局部效果／演出", "原作确有爆心偏移和冲击后果，但词本身通用，不能单靠改名变成独特流派。", ["ss4", "c25", "ss3"], "持续余波、残留伤害场需要自行设计；不认定原作固定持续数回合。")
term("seal", "力量封印／借来的魔眼", "情节提炼，非统一能力名称", "剧情题材", "中", "事件／带代价道具", "抽魔的玩笑、戒指借力、欠款禁咒都有情境；混成真正眼罩封印会失真。", ["c25", "y31", "b22"], "这是三个不同因果，不能据此赋予惠惠常驻第二形态。")

for key, name, japanese, use, note in [
    ("highspeed", "高速咏唱", "高速詠唱", "加速准备／稀有牌", "TRPG中可确认该名；小说惠惠实际习得情况不能只凭衍生规则断定。"),
    ("powerup", "魔法威力上升", "魔法威力上昇", "通用强化", "不要与二手索引的‘爆発系魔法威力上昇’自动合并成同一原文技能。"),
    ("longrange", "超远魔法", "超遠魔法", "射程题材", "回合卡牌是否需要射程系统是设计选择。"),
    ("cancel", "魔法消除", "マジックキャンセラー", "外援驱散", "不是确认惠惠在小说中习得该技能。"),
    ("weather", "天候控制", "ウェザー・オブ・コントロール", "环境题材", "不宜用它将惠惠变成多元素法师。"),
    ("physical", "物理耐性", "物理耐性スキル", "达克妮丝支援", "小说与TRPG的数值规则分开。"),
    ("magicres", "魔法耐性", "魔法耐性スキル", "防御支援", "名称和功能都常见，不提供明显作品区分度。"),
    ("armor", "圣铠", "聖鎧", "阿库娅支援", "信仰相关衍生防护，不等于惠惠固有能力。"),
]:
    term(key, name, japanese, "官方TRPG", "低", use, "可借用正式衍生词库；名称普遍，不优先作为惠惠主流派。", ["trpg"], note)

term("fastchant-personal", "高速咏唱（本人提及）", "Fast Chanting／高速詠唱", "原作用词", "低", "施法速度／准备窗口", "惠惠在第一卷谈及的具体技能名，能作为命名素材。", ["m13", "m56", "m95", "skills"], "高速施法的表现与具体购买技能的加点史分开。它与本表TRPG版‘高速咏唱’的规则不混用。")
term("nochant-personal", "无咏唱爆裂", "施法技巧描述，未确认冒险者卡上的同名技能", "剧情题材", "中", "抢先施放／直接兑现", "第九卷她亲自用这一技巧击倒沃尔巴克，有具体动作与成长情境。", ["m95", "m171"])
term("eye-bind", "魔眼束缚", "Crimson Eye Bind（英译招名）", "原作用词", "高", "控制牌／戒指套件", "她使用戒指魔眼，令目标不能移动。", ["y31"], "中文为工作译名；能力由道具赋予。")
term("eye-lightning", "魔眼雷击", "Crimson Eye Lightning（英译招名）", "原作用词", "高", "反噬攻击／戒指套件", "惠惠从眼睛释放电击，自身眼睛也受伤。", ["y31"], "魔眼会消耗她自身魔力；不是常规学会的雷系法术。")
term("ripper-sword", "开膛手Shack的诅咒剑", "Shack the Ripper：原持有者的名称", "剧情题材", "高", "斩物／拆障／遗物", "惠惠能靠自身高魔力斩开物体，但剑不能伤害生物。", ["ss2"], "不是她正式转职剑士；短篇的剑豪台词还借用了《鲁邦三世》的梗，不宜当惠惠独创术语。")
term("eye-megumin", "魔眼惠惠", "Demon Eye Megumin（英译自称）", "原文台词", "高", "道具能力／临时形态", "她在获得戒指魔眼后使用的具体自称。", ["y31"], "眼罩自身的设定与这枚戒指分开。")
term("megumin-thieves", "惠惠盗贼团", "我ら、めぐみん盗賊団", "作品标题", "高", "她的冒险身份／事件", "小说副标题及她自行组建的团队，直接带角色名。", ["meguminthieves"], "不证明她学会了盗贼技能。")

BOUNDARIES = [
    ("把三个通用词改名成三个流派", "魔力、凝练、咏唱可能只是同一条准备→释放链。", "按单发质量、窗口出牌数、跨回合循环区分玩法；名字再体现爆裂狂、红魔族与日课。"),
    ("火焰／灼烧主流派", "已有短篇把爆裂说明为纯粹魔力释放，不带元素属性。", "火光可作演出。若加持续灼烧，明确是Mod改编，不作为默认原作机制。"),
    ("眼罩解封／真正魔眼", "眼罩赠礼没有证实内藏常驻力量；魔眼场景来自外借戒指。", "用宣言、装备或单次事件表达中二题材。"),
    ("逗之助常驻回魔召唤流", "黑猫是保护与伴随对象，现有资料没有自动魔力电池设定。", "陪伴、守护、遗物或少量支援卡即可。"),
    ("三阶元素或全魔法精通", "炸裂、爆发、爆裂虽有分类，但惠惠的主动选择是只学爆裂。", "不同元素和传送由人物外援或道具承担，保持惠惠专精。"),
    ("不施法就逐日无限蓄能", "《爆焰》3只出现惠惠对隔日魔力异常的推测，没有叠层公式。", "可用作积蓄意象，固定层数、上限、转化倍率都标为原创。"),
    ("必扣血、必跳过回合、矿石必过热", "施法脱力、其他人仍能行动、后期鼻血分别有语境。", "可以设计成本，但具体规则应服务可操作性，不能宣称统一原作公式。"),
    ("把爆杀魔人当惠惠称号", "爆杀魔人もぐにんにん是红魔乡的魔像；它的爆発不等于惠惠的爆裂。", "用于敌人或稀有牌主题。游击方向用悠悠传送、沃尔巴克袭击作为依据。"),
    ("用联动、TRPG、动画特效倒推小说", "这些版本的效果可能不同；本轮新核实的‘爆裂道’也只定位到授权周边名。", "可借名，保留来源层级。小说事实、角色行为、设计建议分别标注。"),
]


def route_html(r):
    return f'''<article class="direction" id="route-{r['id']}"><header><span class="pill {('primary' if r['rank']=='主轴' else '')}">{r['rank']}</span><span class="quiet">辨识度：{r['identity']}</span><h3>{r['name']}</h3><p class="lead">{r['summary']}</p></header>
<div class="loop" aria-label="改编玩法循环">{''.join(f'<span>{esc(s)}</span>' for s in r['loop'])}</div>
<div class="direction-grid"><div><h4>原作依据</h4><p>{r['fact']}</p><h4>玩家的取舍</h4><p>{r['decision']}</p></div><div><h4>改编成牌池</h4><p>{r['proposal']}</p><h4>{r['fit']}</h4><p>{r['current']}</p></div></div>
<details><summary>命名、边界与卷章出处</summary><div class="detail-body"><p><b>命名性质：</b>{r['origin']}</p><p><b>可用词：</b>{r['vocab']}</p><p>{r['examples']}</p><p class="boundary"><b>边界：</b>{r['limit']}</p>{links(r['refs'])}{index_links(r['entries'])}</div></details></article>'''


def term_html(t):
    search = ' '.join(str(t[k]) for k in ['name', 'japanese', 'kind', 'use', 'reason', 'note'])
    tone = {"高": "high", "中": "medium", "低": "low"}[t['distinction']]
    return f'''<tr id="term-{t['id']}" data-term data-search="{esc(search.lower(), quote=True)}" data-level="{t['distinction']}" data-kind="{t['kind']}"><th scope="row"><a class="term-link" href="#term-{t['id']}">{esc(t['name'])}</a><small>{esc(t['japanese'])}</small></th><td><span class="pill">{t['kind']}</span><span class="level {tone}">{t['distinction']}</span><small>{t['use']}</small></td><td><p>{esc(t['reason'])}</p>{f'<p class="quiet">{esc(t["note"])}</p>' if t['note'] else ''}<details class="source-detail"><summary>查看依据</summary>{links(t['refs']) if t['refs'] else '<p>当前项目规则与本轮设计提案；不作为小说技能。</p>'}</details></td></tr>'''


def old_terms():
    path = ROOT / "参考资料" / "原作名词与命名素材.md"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"\| (?:\d{2}|T\d{2}) \|", line):
            cells = [v.strip() for v in line.split('|')[1:-1]]
            rows.append((cells[0], cells[1]))
    assert len(rows) == 40, len(rows)
    return rows


OLD_TERM_MAP = {
    "01": "explosion", "02": "explosion", "03": "chant", "04": "mana", "05": "skillpoint", "06": "upper", "07": "upper", "08": "crimson", "09": "fanatic", "10": "bakuen",
    "11": "lucky", "12": "lucky", "13": "lucky", "14": "lucky", "15": "drain", "16": "aqua", "17": "aqua", "18": "aqua", "19": "aqua", "20": "crusader",
    "21": "vanir", "22": "vanir", "23": "yunyun", "24": "village", "25": "school", "26": "axis", "27": "shop", "28": "gram", "29": "destroyer", "30": "barrier", "31": "barrier", "32": "manatite",
    "T01": "highspeed", "T02": "powerup", "T03": "longrange", "T04": "cancel", "T05": "weather", "T06": "physical", "T07": "magicres", "T08": "armor",
}


def audit_html():
    mapping = {}
    for r in ROUTES:
        for key in r['entries']:
            mapping.setdefault(key, []).append(r)
    rows = []
    for e in ENTRIES:
        routes = mapping.get(e['id'], [])
        if e['category'] == '误区':
            use = '设定边界：限制错误改编，不单独立流派'
        elif routes:
            use = '；'.join(r['name'] for r in routes)
        elif e['category'] == '人物道具':
            use = '人物／道具命名：按角色关系用于支援或遗物'
        elif e['id'] in {'s-resist', 's-explosives', 's-energy'}:
            use = '分类与强度边界：不默认必杀、不混炸药、不锁火属性'
        else:
            use = '剧情／卡名／事件：单次情境或人设细节，暂不独立建系统'
        search = (e['where'] + e['title'] + e['category'] + use).lower()
        rows.append(f'<tr data-audit data-search="{esc(search, quote=True)}"><td>{e["category"]}<small>{e["where"]}</small></td><th scope="row"><a href="{INDEX}#{e["id"]}">{esc(e["title"])}</a></th><td>{esc(use)}</td></tr>')
    return ''.join(rows)


def build():
    assert len(ENTRIES) == 105
    entry_ids = {e['id'] for e in ENTRIES}
    term_ids = {t['id'] for t in TERMS}
    assert len(term_ids) == len(TERMS)
    for r in ROUTES:
        assert set(r['entries']) <= entry_ids, r['id']
        assert set(r['refs']) <= SOURCES.keys(), r['id']
    for t in TERMS:
        assert set(t['refs']) <= SOURCES.keys(), t['id']
    for p in PERSONAL:
        assert set(p['refs']) <= SOURCES.keys(), p['name']
    for _, _, _, refs in PERSONAL_NAMES:
        assert set(refs) <= SOURCES.keys()
    assert set(OLD_TERM_MAP.values()) <= term_ids
    old = old_terms()
    assert set(k for k, _ in old) == OLD_TERM_MAP.keys()
    curated = {t['id']: t for t in TERMS}
    old_audit = ''.join(f'<tr><td>{key}</td><th scope="row">{esc(name)}</th><td><a href="#term-{OLD_TERM_MAP[key]}">{curated[OLD_TERM_MAP[key]]["name"]}</a></td></tr>' for key, name in old)
    source_rows = ''.join(f'<tr><th scope="row"><a href="{esc(s["url"], quote=True)}" target="_blank" rel="noopener noreferrer">{esc(s["title"])} ↗</a></th><td>{esc({"A":"官方小说正文", "B":"非官方小说译文", "C":"官方简介／二手线索"}.get(s["kind"], s["kind"]))}</td><td>{esc(s["note"])}</td></tr>' for s in SOURCES.values())
    replacements = {
        "@@PERSONAL@@": personal_html(), "@@PERSONAL_NAMES@@": personal_names_html(),
        "@@PERSONAL_COUNT@@": str(len(PERSONAL)), "@@PERSONAL_NAME_COUNT@@": str(len(PERSONAL_NAMES)),
        "@@ROUTES@@": ''.join(route_html(r) for r in ROUTES),
        "@@TERMS@@": ''.join(term_html(t) for t in TERMS),
        "@@BOUNDARIES@@": ''.join(f'<tr><th scope="row">{esc(a)}</th><td>{esc(b)}</td><td>{esc(c)}</td></tr>' for a, b, c in BOUNDARIES),
        "@@AUDIT@@": audit_html(), "@@OLD_AUDIT@@": old_audit, "@@SOURCES@@": source_rows,
        "@@TERM_COUNT@@": str(len(TERMS)), "@@SOURCE_COUNT@@": str(len(SOURCES)),
        "@@EXTRA_COUNT@@": str(len(EXTRA)),
        "@@KIND_OPTIONS@@": ''.join(f'<option>{esc(k)}</option>' for k in dict.fromkeys(t['kind'] for t in TERMS)),
    }
    page = PAGE
    for key, value in replacements.items():
        page = page.replace(key, value)
    assert not re.search(r'@@[A-Z_]+@@', page)
    OUT.write_text(page, encoding="utf-8")
    # The skill's default artifact directory also holds a portable copy.
    portable = Path.home() / ".agent" / "diagrams" / OUT.name
    portable.parent.mkdir(parents=True, exist_ok=True)
    # Local links in this copy resolve to the canonical workspace sources.
    copy_page = page.replace('href="' + INDEX, 'href="' + (ROOT / INDEX).as_uri())
    for filename in ["惠惠核心设计简明版.html", "惠惠角色特点与设计素材.md", "参考资料/原作名词与命名素材.md", "参考资料/网络来源与访问记录.md"]:
        copy_page = copy_page.replace('href="' + filename + '"', 'href="' + (ROOT / filename).as_uri() + '"')
    portable.write_text(copy_page, encoding="utf-8")
    print(json.dumps(dict(output=str(OUT), portable=str(portable), routes=len(ROUTES), terms=len(TERMS), reviewed_entries=len(ENTRIES), reviewed_old_terms=len(old), sources=len(SOURCES)), ensure_ascii=False))


PAGE = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><title>惠惠本人：技能、招式与原作名词</title>
<style>
:root{--bg:#f4efe4;--surface:#fffaf1;--surface2:#eae2d3;--border:#d6cbb9;--text:#272820;--text-dim:#65655b;--red:#92382f;--green:#345f52;--gold:#946421;--blue:#435f75;--header:#f4efe4f5;--shadow:0 8px 30px #3a30210a;color-scheme:light}
:root[data-theme=dark]{--bg:#1c211f;--surface:#242b26;--surface2:#30382f;--border:#465045;--text:#eee7d8;--text-dim:#b5b5a5;--red:#eda18c;--green:#a8cbb3;--gold:#dfbc7b;--blue:#a9c5dc;--header:#1c211ff5;--shadow:none;color-scheme:dark}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.75 "Segoe UI","Microsoft YaHei","PingFang SC",sans-serif}a{color:var(--green);text-underline-offset:3px}a:hover{color:var(--red)}button,input,select{font:inherit}button,select{cursor:pointer}button{background:var(--surface);border:1px solid var(--border);color:var(--text);padding:7px 13px;border-radius:5px}button:hover{border-color:var(--green)}:focus-visible{outline:3px solid var(--gold);outline-offset:3px}p{margin:0 0 12px}h1,h2,h3,h4{line-height:1.35}h1,h2{font-family:Georgia,"Noto Serif SC","Source Han Serif SC","SimSun",serif}h1{font-size:clamp(32px,4.3vw,54px);font-weight:500;letter-spacing:-1px;margin:16px 0 20px}h1 em{font-style:normal;color:var(--red)}h2{font-size:29px;font-weight:500;margin:0 0 10px}h3{font-size:23px;margin:10px 0}h4{font-size:13px;color:var(--green);margin:20px 0 8px;letter-spacing:.04em}small{display:block;color:var(--text-dim);font-size:12px;font-weight:400;margin-top:5px;line-height:1.55}.quiet{color:var(--text-dim)}.eyebrow{font:12px/1.5 Consolas,"Microsoft YaHei",monospace;letter-spacing:.12em;color:var(--green)}.wrap{max-width:1440px;margin:auto;padding:35px 42px 65px;display:grid;grid-template-columns:190px minmax(0,1fr);gap:42px}.main{min-width:0}.toc{position:sticky;top:26px;align-self:start;max-height:calc(100dvh - 52px);overflow-y:auto}.toc-title{font-size:13px;color:var(--red);font-weight:700;margin:0 0 12px}.toc a{display:block;text-decoration:none;color:var(--text-dim);padding:8px 10px;border-left:2px solid transparent;font-size:13px}.toc a:hover,.toc a.active{color:var(--green);border-color:var(--green);background:var(--surface)}.toc .tools{display:flex;gap:6px;flex-wrap:wrap;margin-top:22px}.toc .tools button{font-size:12px}.hero{padding:5px 0 30px}.hero .intro{max-width:770px;font-size:17px}.metrics{display:flex;gap:25px;flex-wrap:wrap;padding:20px 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border);margin-top:24px}.metrics b{font:28px/1.1 Georgia,serif;display:block;color:var(--red)}.metrics span{font-size:12px;color:var(--text-dim)}.note{background:var(--surface);border-left:3px solid var(--gold);padding:14px 18px;font-size:13px;margin:18px 0}.note p:last-child{margin-bottom:0}.section{margin-top:50px;scroll-margin-top:24px}.section-head{padding-bottom:20px;border-bottom:2px solid var(--border);margin-bottom:22px}.section-head .eyebrow{display:block;margin-bottom:8px}.section-head p{max-width:820px;color:var(--text-dim);margin-bottom:0}.recommendations{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;border:1px solid var(--border);background:var(--surface)}.recommendations article{min-width:0;padding:22px;border-right:1px solid var(--border)}.recommendations article:last-child{border-right:0}.recommendations h3{font-size:20px;margin:7px 0 12px}.recommendations p{font-size:14px}.recommendations a{font-size:13px}.mark{font:12px/1.5 Consolas,monospace;color:var(--red)}.flowline{margin:20px 0;display:flex;gap:5px;flex-wrap:wrap}.flowline span{padding:6px 12px;background:var(--surface2);font-size:13px}.flowline span+span::before{content:"→ ";color:var(--red)}.direction{margin:0 0 26px;padding:24px 26px;background:var(--surface);border:1px solid var(--border);border-top:3px solid var(--green);scroll-margin-top:24px;box-shadow:var(--shadow)}.direction:has(.primary){border-top-color:var(--red)}.direction .quiet{font-size:12px;margin-left:12px}.direction .lead{font-size:16px}.pill{display:inline-block;border:1px solid var(--border);padding:2px 8px;border-radius:3px;color:var(--text-dim);font-size:11px;line-height:1.6}.pill.primary{background:var(--red);border-color:var(--red);color:var(--bg)}.loop{display:flex;flex-wrap:wrap;gap:6px;margin:16px 0 2px}.loop span{background:var(--surface2);padding:4px 10px;font-size:12px}.loop span+span::before{content:"→ ";color:var(--green)}.direction-grid{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-bottom:18px}.direction-grid>div{min-width:0}.direction p{font-size:14px}.direction details{border-top:1px solid var(--border);padding-top:10px}summary{cursor:pointer;color:var(--green);font-size:13px;line-height:1.6}summary:hover{color:var(--red)}.detail-body{padding:16px 0 0}.boundary{border-left:2px solid var(--gold);padding-left:13px;color:var(--text-dim)}.refs{display:flex;flex-wrap:wrap;gap:5px 12px;margin-top:12px}.refs a{font-size:12px}.local-refs a{color:var(--text-dim)}.table-wrap{overflow:auto;border:1px solid var(--border);background:var(--surface);max-width:100%;scrollbar-color:var(--border) var(--surface)}table{width:100%;border-collapse:collapse;font-size:13px;table-layout:fixed}th,td{text-align:left;vertical-align:top;padding:15px 17px;border-bottom:1px solid var(--border);overflow-wrap:anywhere}thead th{font-size:12px;background:var(--surface2);font-weight:600;color:var(--text-dim)}tbody th{font-weight:600}tbody tr:last-child>*{border-bottom:0}tbody tr:hover{background:var(--surface2)}td p{margin-bottom:7px}td p:last-child{margin-bottom:0}table.lexicon th:first-child{width:27%}table.lexicon th:nth-child(2){width:20%}table.lexicon th:nth-child(3){width:53%}.term-link{text-decoration:none;color:var(--text)}tr:target{background:var(--surface2);outline:2px solid var(--gold);outline-offset:-2px}.level{font-size:11px;display:inline-block;border-radius:2px;padding:2px 7px;margin-left:6px;white-space:nowrap}.high{color:var(--red);border:1px solid var(--red)}.medium{color:var(--gold);border:1px solid var(--gold)}.low{color:var(--text-dim);border:1px solid var(--border)}.filters{display:grid;grid-template-columns:minmax(200px,1fr) 130px 160px auto;gap:10px;align-items:end;margin:20px 0 10px}.filters label{font-size:12px;color:var(--text-dim)}input,select{width:100%;background:var(--surface);color:var(--text);border:1px solid var(--border);padding:9px 10px;border-radius:4px;min-width:0}label span{display:block;margin-bottom:5px}.result-line{font-size:12px;color:var(--text-dim);margin:0 0 12px}.empty{border:1px dashed var(--border);padding:25px;text-align:center}.source-detail{margin-top:8px}.source-detail .refs{margin-top:8px}.matrix th:first-child{width:21%}.matrix th:nth-child(2){width:29%}.matrix th:nth-child(3){width:50%}.audit th:first-child{width:21%}.audit th:nth-child(2){width:38%}.audit th:nth-child(3){width:41%}.old-audit th:first-child{width:12%}.old-audit th:nth-child(2){width:48%}.old-audit th:nth-child(3){width:40%}.sources th:first-child{width:35%}.sources th:nth-child(2){width:19%}.sources th:nth-child(3){width:46%}.fold{border:1px solid var(--border);background:var(--surface);margin:15px 0}.fold>summary{padding:17px 20px;font-size:15px}.fold>.fold-body{padding:0 20px 20px}.fold .table-wrap{margin-top:15px}.inputs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px;margin:20px 0}.inputs article{border-bottom:1px solid var(--border);padding:12px 0;min-width:0}.inputs h3{font-size:16px;margin:0 0 8px}.inputs p{font-size:13px}.footer{font-size:12px;color:var(--text-dim);border-top:1px solid var(--border);margin-top:40px;padding-top:20px}.skip{position:absolute;top:-80px;left:15px;background:var(--surface);padding:10px;z-index:1000}.skip:focus{top:10px}[hidden]{display:none!important}
@media(max-width:1050px){.wrap{grid-template-columns:150px 1fr;gap:25px;padding:24px}.toc a{font-size:12px}.recommendations{grid-template-columns:1fr}.recommendations article{border-right:0;border-bottom:1px solid var(--border)}.recommendations article:last-child{border-bottom:0}.filters{grid-template-columns:1fr 120px}.filters label:first-child{grid-column:1/-1}.direction{padding:20px}}
@media(max-width:760px){.wrap{display:block;padding:0 17px 35px}.toc{top:0;max-height:none;display:flex;gap:4px;overflow:auto;position:sticky;background:var(--header);border-bottom:1px solid var(--border);margin:0 -17px;padding:9px 17px;z-index:10;align-items:center}.toc a{white-space:nowrap;flex-shrink:0;border-left:0;border-bottom:2px solid transparent;padding:6px 8px}.toc-title{display:none}.toc .tools{margin:0 0 0 8px;flex-wrap:nowrap;flex-shrink:0}.hero{padding-top:26px}h1{font-size:34px}.hero .intro{font-size:15px}h2{font-size:25px}.metrics{gap:20px}.section{margin-top:38px;scroll-margin-top:68px}.direction{padding:18px 16px;scroll-margin-top:68px}.direction-grid{grid-template-columns:1fr;gap:0}.direction .quiet{margin-left:7px}.inputs{grid-template-columns:1fr}.table-wrap table{min-width:650px}.table-wrap{border-radius:0}.fold>.fold-body{padding:0 10px 15px}tr:target{scroll-margin-top:70px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{html{scroll-behavior:auto}body{font-size:11px;background:#fff;color:#111}.wrap{display:block;max-width:none;padding:0}.toc,.filters,.tools,.skip,.result-line{display:none}.hero{padding:0}.hero h1{font-size:30px}.section{margin-top:24px}.section-head{margin-bottom:12px;padding-bottom:8px}.direction{box-shadow:none;padding:12px;background:#fff;break-inside:avoid}.direction-grid{gap:18px}table{font-size:10px;min-width:0!important}th,td{padding:8px}.table-wrap{overflow:visible}.refs a{font-size:9px}.note{padding:10px}.recommendations article{padding:12px}.metrics{padding:12px}.fold>.fold-body{padding:0}.sources a{overflow-wrap:anywhere}.fold{border:0}.footer{margin-top:20px}.source-detail p{font-size:10px}}
.personal.section{margin-top:12px}.personal-table th:first-child{width:27%}.personal-table th:nth-child(2){width:48%}.personal-table th:nth-child(3){width:25%}.personal-table .pill{margin-top:10px}.personal-names th:first-child{width:36%}.personal-shortlist{display:flex;flex-wrap:wrap;gap:8px 18px;margin:20px 0;font-size:14px}
</style></head><body><a href="#overview" class="skip">跳到正文</a><div class="wrap"><nav class="toc" aria-label="章节导航"><p class="toc-title">惠惠 · 本人素材</p><a href="#overview">先看惠惠本人</a><a href="#personal">技能、技巧与道具</a><a href="#personal-names">她自己的称呼</a><a href="#fit">与当前核心的关系</a><a href="#routes">背景玩法参考</a><a href="#terms">全部名词检索</a><a href="#boundaries">不宜直接套用</a><a href="#coverage">资料覆盖核对</a><a href="#sources">来源入口</a><div class="tools"><button type="button" id="theme" aria-pressed="false">切换暗色</button><button type="button" id="print">打印</button></div></nav>
<main class="main"><header class="hero" id="overview"><div class="eyebrow">KONOSUBA / MEGUMIN HERSELF / 2026.10.08</div><h1>惠惠本人，<br><em>到底会什么。</em></h1><p class="intro">从她明确提及的技能和亲自使过的招式入手。除了爆裂专精，还查到<strong>魔眼束缚、魔眼雷击、无咏唱爆裂</strong>，以及那把靠魔力斩物的诅咒剑。</p><div class="personal-shortlist" aria-label="本人技能快捷入口"><a href="#personal-2">爆裂威力提升</a><a href="#personal-3">高速咏唱</a><a href="#personal-4">无咏唱爆裂</a><a href="#personal-5">魔眼束缚</a><a href="#personal-6">魔眼雷击</a></div><div class="metrics"><div><b>@@PERSONAL_COUNT@@</b><span>本人技能、技巧与道具</span></div><div><b>@@PERSONAL_NAME_COUNT@@</b><span>本人称呼与身份材料</span></div><div><b>@@TERM_COUNT@@</b><span>全表可检索名词</span></div><div><b>105</b><span>既有原作资料条目</span></div></div><div class="note"><p><b>这次的重点：</b>直接给出招名、动作、代价和卷章。魔眼来自戒指、隐身来自卷轴；它们都是她亲自用过的能力，分别标明来源。</p><p><b>译名：</b>后期及特典以非官方小说译文定位；中文多为工作译名。未核对授权日文的招名保留英文检索词，不自行补写日文。</p></div></header>

<section class="section personal" id="personal"><header class="section-head"><span class="eyebrow">MEGUMIN / PERSONAL SKILLS & MOVES</span><h2>她实际提过、学过、用过什么</h2><p>“技能名”“施法技巧”“道具给予的招式”分别标出。最后一列是改编方向，前两列为来源定位。</p></header><div class="table-wrap" tabindex="0" role="region" aria-label="惠惠本人技能与招式表"><table class="personal-table"><thead><tr><th>具体名词与性质</th><th>她在原作里做了什么／出处</th><th>可以抓住的动作</th></tr></thead><tbody>@@PERSONAL@@</tbody></table></div><div class="note"><b>最有区分度的新素材：魔眼。</b>束缚与雷击是有具体招名的本人动作，戒指还有恶魔化风险。可做“借用力量→控制／反噬→魔力不足”的小套件；与她长期强化的爆裂专精分别理解。这是玩法提炼，未修改当前牌池。</div></section>

<section class="section" id="personal-names"><header class="section-head"><span class="eyebrow">MEGUMIN / PERSONAL WORDS</span><h2>与她本人绑定的称呼和名词</h2><p>这些可以当卡名或主题名；每项说明是自称、绰号、标题还是团队身份。</p></header><div class="table-wrap" tabindex="0" role="region" aria-label="惠惠本人称呼与身份表"><table class="personal-names"><thead><tr><th>名词／检索线索</th><th>原作语境与用法</th></tr></thead><tbody>@@PERSONAL_NAMES@@</tbody></table></div><p class="quiet" style="margin-top:15px;font-size:13px">“爆裂道”目前核到授权贴图名，详见词表；“魔力积蓄”“压缩魔力”属于当前设计和原文描写提炼，未核成她的正式技能名。下方保留上一版的背景研究，供回查来源和设计建议。</p></section>

<section class="section" id="fit"><header class="section-head"><span class="eyebrow">01 / CURRENT DESIGN</span><h2>围绕“魔力积蓄＋吟唱”展开</h2><p>沿用当前记录：存牌；缺少爆裂时生成一张；0费爆裂开吟唱并取回全部积蓄；回合末按吟唱期间实际出牌数造成群伤；吟唱中不能再次打爆裂。</p></header><div class="flowline"><span>存入手牌</span><span>开吟唱取回</span><span>实际打出组合</span><span>回合末爆裂</span><span>下轮继续准备</span></div><div class="table-wrap" tabindex="0" role="region" aria-label="流派与当前核心适配表"><table class="matrix"><thead><tr><th>候选分支</th><th>玩家追求什么</th><th>可以怎样接入当前方案</th></tr></thead><tbody><tr><th scope="row">爆裂狂 · 极致一发</th><td>集中投入，强化单次兑现。</td><td>关键牌保存、压缩减费、明确的爆裂强化。注意：高费牌本身不会按当前计数公式自动增加更多群伤。</td></tr><tr><th scope="row">红魔族 · 宣言连奏</th><td>在一次吟唱里完成更多出牌。</td><td>咒文续接、免费积蓄牌、有限回能。它是当前基础公式最直接支持的方向。</td></tr><tr><th scope="row">爆裂散步 · 日课循环</th><td>每轮输出后仍保有下轮组合。</td><td>回流一击、自行入区、吟唱中继续存牌、下一回合兑现；不在当前吟唱里再打一次爆裂。</td></tr><tr><th scope="row">Manatite · 外部供能</th><td>把稀缺库存换成施放机会。</td><td>跨回合供能和准备可接入。同回合连续多发与用户已确认的限制冲突，单列为替代候选。</td></tr><tr><th scope="row">伙伴接力／传送袭击</th><td>安全输出并继续循环。</td><td>作为上述方向的支援套件。回合末爆裂后的抽牌收益须放到可兑现的时点。</td></tr></tbody></table></div><p class="quiet" style="margin-top:13px;font-size:13px">这里只讨论来源和设计空间，未改动当前卡牌、伤害公式、初始遗物或规则。<a href="惠惠核心设计简明版.html">查看当前方案 →</a></p></section>

<section class="section" id="routes"><header class="section-head"><span class="eyebrow">02 / PLAYABLE DIRECTIONS</span><h2>哪些内容足以支撑玩法</h2><p>先看三项主轴，再看替代候选、小套件、成本与单牌题材。独立流派需要不同的操作取舍；同一套操作换三个名字不算三个流派。</p></header>@@ROUTES@@</section>

<section class="section" id="terms"><header class="section-head"><span class="eyebrow">03 / NAMING & IDENTITY</span><h2>专有名词与命名材料</h2><p>高辨识度优先用于流派主题、能力牌和稀有遗物；低辨识度词适合让规则清楚。一个词有原作依据，不代表这个词在其他作品中不存在。</p></header><div class="note"><b>最值得优先保留：</b>爆裂狂、红魔族、爆裂散步题材、爆裂鉴赏、Manatite、Red Prison、逗之助、维兹的魔道具店。<br><b>有名称但适用面窄：</b>毁灭者、Coronatite、爆杀魔人、阿克西斯教团。<br><b>适合清楚描述规则：</b>吟唱、魔力积蓄、凝练；它们的辨识度主要靠具体玩法和人物情境补足。</div>
<form class="filters" id="term-filters" role="search" aria-label="名词筛选"><label><span>搜索名词、用途或边界</span><input type="search" id="term-search" placeholder="例如：矿石 / 流派 / 同回合 / 眼罩" autocomplete="off"></label><label><span>辨识度</span><select id="level"><option value="">全部</option><option>高</option><option>中</option><option>低</option></select></label><label><span>命名性质</span><select id="kind"><option value="">全部性质</option>@@KIND_OPTIONS@@</select></label><button type="reset">重置</button></form><p class="result-line" id="term-count" aria-live="polite">@@TERM_COUNT@@ 条名词</p><p class="empty" id="term-empty" hidden>没有匹配的名词。请减少条件或重置筛选。</p><noscript><p class="note">全部内容仍可直接阅读，可用浏览器Ctrl+F查找。</p></noscript><div class="table-wrap" tabindex="0" role="region" aria-label="名词与辨识度表"><table class="lexicon"><thead><tr><th>中文名／原文检索线索</th><th>性质、辨识度与用途</th><th>为什么适合，以及不能误读的地方</th></tr></thead><tbody>@@TERMS@@</tbody></table></div></section>

<section class="section" id="boundaries"><header class="section-head"><span class="eyebrow">04 / DESIGN BOUNDARIES</span><h2>这些方向需要补上改编说明</h2><p>不否定设计空间，先避免把自己的游戏规则记成原作既有设定。</p></header><div class="table-wrap" tabindex="0" role="region" aria-label="改编边界表"><table class="matrix"><thead><tr><th>容易直接套上的方向</th><th>现有资料支持到哪里</th><th>更贴近惠惠的用法</th></tr></thead><tbody>@@BOUNDARIES@@</tbody></table></div></section>

<section class="section" id="coverage"><header class="section-head"><span class="eyebrow">05 / COVERAGE AUDIT</span><h2>全部既有资料，去向可查</h2><p>这次以现有研究包为全集。下面保留105条原作索引和40条旧词表的逐项去向；没有把未核实的外链写成已读小说正文。</p></header><div class="inputs"><article><h3>105条索引＋68个原来源</h3><p>设定、剧情、人物道具、误区全部回看，并保留回到具体条目的链接。</p><a href="素晴爆裂魔法原作资料索引.html">原作资料索引 →</a></article><article><h3>32个名词＋8个TRPG词</h3><p>逐项归并到本页；合并同义项和职业组，不用别名和人名充数。</p><a href="参考资料/原作名词与命名素材.md">旧词表 →</a></article><article><h3>人物与设计素材</h3><p>性格、日课、关系、装备、成长与误区均纳入；旧文的未核实项目仍保持边界。</p><a href="惠惠角色特点与设计素材.md">人物材料 →</a></article><article><h3>网络访问记录</h3><p>保留失败入口、二手来源与版本区别；本轮额外核对官方名词、传送袭击和授权爆裂道用词。</p><a href="参考资料/网络来源与访问记录.md">访问记录 →</a></article></div><div class="note"><b>旧建议与当前规则：</b>旧词表曾把“咏唱：”建议成未来进入预备时触发的待登记效果；当前用户规则中的“吟唱：”是已经处于吟唱状态的条件效果。本报告按当前规则理解，不把旧建议升级为既定规则。</div>
<details class="fold" id="entry-audit"><summary>展开全部105条索引的设计去向</summary><div class="fold-body"><label for="audit-search" class="quiet">筛选卷章、标题或用途</label><input type="search" id="audit-search" placeholder="例如：正篇9 / 误区 / 主轴" autocomplete="off"><p class="result-line" id="audit-count" aria-live="polite">105 / 105 条资料</p><p class="empty" id="audit-empty" hidden>没有匹配的资料。</p><div class="table-wrap" tabindex="0" role="region" aria-label="105条原作条目去向"><table class="audit"><thead><tr><th>类别／卷章</th><th>原索引条目</th><th>本轮设计用途</th></tr></thead><tbody>@@AUDIT@@</tbody></table></div></div></details>
<details class="fold" id="old-term-audit"><summary>展开全部40条旧词表的归并去向</summary><div class="fold-body"><p class="quiet">编号沿用原表；合并不等于删去。原作、动画、TRPG与自拟名称的证据层级见对应新词条。</p><div class="table-wrap" tabindex="0" role="region" aria-label="旧词表归并对照"><table class="old-audit"><thead><tr><th>旧编号</th><th>旧词条</th><th>本页对应条目</th></tr></thead><tbody>@@OLD_AUDIT@@</tbody></table></div></div></details></section>

<section class="section" id="sources"><header class="section-head"><span class="eyebrow">06 / SOURCE LEDGER</span><h2>@@SOURCE_COUNT@@ 个来源入口</h2><p>68个既有入口加@@EXTRA_COUNT@@个命名补充入口。官方小说正文最适合核设定；非官方译文用于定位后期卷章；动画、TRPG、周边分别标版本。外链可联网查阅，本页本身离线可用。</p></header><details class="fold" id="source-ledger"><summary>展开来源与证据说明</summary><div class="fold-body"><div class="table-wrap" tabindex="0" role="region" aria-label="来源入口与证据说明"><table class="sources"><thead><tr><th>来源</th><th>类型</th><th>读取范围与用途</th></tr></thead><tbody>@@SOURCES@@</tbody></table></div></div></details></section><footer class="footer">2026-10-08 · 原作事实与设计建议分开整理。候选流派尚未做卡池实装或平衡验证；当前核心规则保持原有记录。版权正文仅链接，页面采用自主概括。</footer></main></div>
<script>
(()=>{'use strict';const $=s=>document.querySelector(s),$$=s=>Array.from(document.querySelectorAll(s));const form=$('#term-filters'),rows=$$('[data-term]');
function filterTerms(){const q=$('#term-search').value.trim().toLowerCase(),level=$('#level').value,kind=$('#kind').value;let n=0;rows.forEach(r=>{r.hidden=!!((q&&!r.dataset.search.includes(q))||(level&&r.dataset.level!==level)||(kind&&r.dataset.kind!==kind));if(!r.hidden)n++;});$('#term-count').textContent=`${n} / ${rows.length} 条名词`;$('#term-empty').hidden=n!==0;}
form.addEventListener('input',filterTerms);form.addEventListener('change',filterTerms);form.addEventListener('reset',()=>setTimeout(filterTerms,0));filterTerms();
const audits=$$('[data-audit]');$('#audit-search').addEventListener('input',()=>{const q=$('#audit-search').value.trim().toLowerCase();let n=0;audits.forEach(r=>{r.hidden=!!(q&&!r.dataset.search.includes(q));if(!r.hidden)n++;});$('#audit-count').textContent=`${n} / ${audits.length} 条资料`;$('#audit-empty').hidden=n!==0;});
const themeButton=$('#theme');function setTheme(t){document.documentElement.dataset.theme=t;themeButton.textContent=t==='dark'?'切换浅色':'切换暗色';themeButton.setAttribute('aria-pressed',String(t==='dark'));}let stored;try{stored=localStorage.getItem('konosuba-lore-archetypes-theme');}catch{}setTheme(stored==='dark'?'dark':'light');themeButton.addEventListener('click',()=>{const t=document.documentElement.dataset.theme==='dark'?'light':'dark';setTheme(t);try{localStorage.setItem('konosuba-lore-archetypes-theme',t);}catch{}});
let printState=[];window.addEventListener('beforeprint',()=>{if(printState.length)return;printState=$$('details').map(d=>[d,d.open]);$$('details').forEach(d=>d.open=true);});window.addEventListener('afterprint',()=>{printState.forEach(([d,open])=>d.open=open);printState=[];});$('#print').addEventListener('click',()=>window.print());
function revealHash(){let key;try{key=decodeURIComponent(location.hash.slice(1));}catch{return;}if(!key)return;const target=document.getElementById(key);if(!target)return;if(target.hasAttribute('data-term')&&target.hidden){form.reset();filterTerms();}let parent=target;while(parent){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement;}requestAnimationFrame(()=>target.scrollIntoView({block:'start'}));}window.addEventListener('hashchange',revealHash);revealHash();
const nav=$$('.toc>a');if('IntersectionObserver'in window){const io=new IntersectionObserver(items=>{const active=items.filter(i=>i.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top)[0];if(!active)return;nav.forEach(a=>{const on=a.hash==='#'+active.target.id;a.classList.toggle('active',on);if(on)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});},{rootMargin:'-8% 0px -75% 0px'});$$('#overview,.section').forEach(el=>io.observe(el));}
})();
</script></body></html>'''


if __name__ == "__main__":
    build()
