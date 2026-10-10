"""Build the offline, source-linked KonoSuba Explosion research index.

Run with Python 3; the HTML has no runtime dependencies. Summaries are original
Chinese paraphrases, not reproduced novel chapters. Research date: 2026-09-30.
"""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "素晴爆裂魔法原作资料索引.html"
SOURCES = {}
ENTRIES = []


def source(key, title, url, kind="B", note="非官方英译；用于定位卷章，未与授权日文全卷逐页校勘。"):
    SOURCES[key] = dict(title=title, url=url, kind=kind, note=note)


def entry(key, category, series, where, title, summary, refs, tags, *notes, grade=None):
    assert all(r in SOURCES for r in refs), (key, refs)
    ENTRIES.append(dict(id=key, category=category, series=series, where=where,
                        title=title, summary=summary, refs=refs, tags=tags,
                        notes=notes, grade=grade or max(SOURCES[r]["kind"] for r in refs)))


K = "https://kakuyomu.jp/works/1177354054880950791/episodes/"
C = "https://cgtranslations.me/"
source("official", "角川：系列书目", "https://sneakerbunko.jp/series/konosuba/", "C", "官方书目；用于确认作品与系列，页面更新进度不等于全部出版进度。")
source("kaku", "角川官方公开小说目录", "https://kakuyomu.jp/works/1177354054880950791", "A", "角川スニーカー文庫发布的小说试读／公开正文；不是早期已删的 Web 连载版。")
source("b1p", "《爆焰》1·序章", K + "1177354054881047828", "A", "官方日文正文：童年邂逅、巨兽与教魔法的约定。")
source("b113", "《爆焰》1·1-3", K + "1177354054881047866", "A", "官方日文正文：炸裂、爆发、爆裂的分类及实用性。")
source("b114", "《爆焰》1·1-4", K + "1177354054881047871", "A", "官方日文正文：咏唱速度、准确发音与魔法控制。")
source("b148", "《爆焰》1·4-8", K + "1177354054881179079", "A", "官方日文正文：技能点、一天一发、选择爆裂的动机。")
source("b155", "《爆焰》1·5-5", K + "1177354054881215191", "A", "官方日文正文：救人时曾考虑改学上级魔法。")
source("b156", "《爆焰》1·5-6", K + "1177354054881215195", "A", "官方日文正文：首次爆裂、无杖施法、魔力与体力耗尽。")
source("b21", "《爆焰》2·第1章", C + "2018/01/16/explosion-spinoff-2-chapter-1/")
source("b22", "《爆焰》2·第2章", C + "2018/01/16/explosion-spinoff-2-chapter-2/")
source("b24", "《爆焰》2·第4章", C + "2018/01/17/explosion-spinoff-2-chapter-4/")
source("b25", "《爆焰》2·第5章", C + "2018/01/17/explosion-spinoff-2-chapter-5/")
source("b3pub", "Yen Press：《爆焰》3 简介", "https://yenpress.com/titles/9781975387051-konosuba-an-explosion-on-this-wonderful-world-vol-3-light-novel", "C", "官方英文出版简介；不是整卷正文。")
source("b34", "《爆焰》3·第4章及幕间", C + "2018/01/19/explosion-spinoff-3-chapter-4-interlude/")
source("m13", "正篇1·第3章", C + "2017/12/30/konosuba-volume-1-chapter-3/")
source("m14", "正篇1·第4章", C + "2017/12/30/konosuba-volume-1-chapter-4/")
source("m21", "正篇2·第1章", C + "2017/12/31/konosuba-volume-2-chapter-1/")
source("m25", "正篇2·第5章", C + "2017/12/31/konosuba-volume-2-chapter-5/")
source("m34", "正篇3·第4章", C + "2018/01/02/konosuba-volume-3-chapter-4/")
source("m45", "正篇4·第5章", C + "2018/01/04/konosuba-volume-4-chapter-5/")
source("m55", "正篇5·第5章", C + "2018/01/07/konosuba-volume-5-chapter-5/")
source("m56", "正篇5·第6章", C + "2018/01/07/konosuba-volume-5-chapter-6/")
source("m64", "正篇6·第4章", C + "2018/01/09/konosuba-volume-6-chapter-4/")
source("m72", "正篇7·第2章", C + "2018/01/22/konosuba-volume-7-chapter-2/")
source("m81", "正篇8·第1章", C + "2018/01/24/konosuba-volume-8-chapter-1/")
source("m9p", "正篇9·序章", C + "2018/01/25/konosuba-volume-9-prologue-crimson-destiny/")
source("m92", "正篇9·第2章", C + "2018/01/25/konosuba-volume-9-chapter-2/")
source("m94", "正篇9·第4章", C + "2018/01/25/konosuba-volume-9-chapter-4/")
source("m95", "正篇9·第5章", C + "2018/01/25/konosuba-volume-9-chapter-5/")
source("m9pub", "角川：正篇9《红之宿命》", "https://www.kadokawa.co.jp/product/321510000449/", "C", "官方出版简介，用于核对卷名与故事背景。")
source("m104", "正篇10·第4章", "https://crimsonmagic.me/2017/01/03/gifting-10-4/")
source("m112", "正篇11·第2章", "https://crimsonmagic.me/2017/07/02/gifting-11-2/")
source("m113", "正篇11·第3章", "https://crimsonmagic.me/2017/07/16/gifting-11-3/")
source("m12syn", "正篇12·剧情索引", "https://konosuba.fandom.com/wiki/Konosuba_Light_Novel_Volume_12/Synopsis", "C", "读者维护的剧情摘要；本页第12卷条目仍需授权正文复核。")
source("m135", "正篇13·第5章", C + "2018/05/11/konosuba-volume-13-chapter-5/")
source("m143", "正篇14·第3章检索入口", C + "2018/09/07/konosuba-volume-14-chapter-3/", "C", "搜索摘要可见，正文访问失败；仅用于提示缺口，不把细节当成已核验。")
source("m144", "正篇14·第4章", C + "2018/09/14/konosuba-volume-14-chapter-4/")
source("m155", "正篇15·第5章", C + "2019/02/02/konosuba-volume-15-chapter-5/")
source("m165", "正篇16·第5章及尾声", C + "2019/10/19/konosuba-volume-16-chapter-5-epilogue/")
source("m171", "正篇17·第1章", C + "2020/07/18/konosuba-volume-17-chapter-1/")
source("m174", "正篇17·第4章", C + "2020/08/08/konosuba-volume-17-chapter-4/")
source("m17pub", "角川：正篇17《为冒险者们献上祝福！》", "https://www.kadokawa.co.jp/product/322002000284/", "C", "官方简介直接确认：大量魔力矿石、爆裂魔法、魔王城结界突破；发行日2020-05-01。")
source("c14", "《续·爆焰》1·第4章", "https://crimsonmagic.me/2017/05/31/continued-explosions-4-2/")
source("c21", "《续·爆焰》2·第1章", C + "2019/06/08/continued-explosions-2-chapter-1/")
source("c24", "《续·爆焰》2·第4章", C + "2019/06/29/continued-explosions-2-chapter-4/")
source("c25", "《续·爆焰》2·第5章及尾声", C + "2019/07/06/continued-explosions-2-chapter-5/")
source("masked", "《向这位蒙面恶魔咨询！》·第5章", C + "2018/01/31/consulting-with-this-masked-devil-chapter-5/")
source("dust7", "达斯特外传7·第2章", C + "2020/11/01/konosuba-dust-spinoff-7-chapter-2/", "B", "非官方英译；达斯特外传作者为昼熊，按授权外传单列，不冒称暁なつめ亲笔正篇。")
source("dustss", "达斯特外传特典·观察惠惠", C + "2018/03/22/dust-short-story-2-observing-megumin/")
source("y12", "《寄道》1·第2章：阿克塞尔的爆裂侦探", C + "2020/02/26/konosuba-yorimichi-chapter-2/")
source("y13", "《寄道》1·第3章：需要保护的十字骑士", C + "2020/02/29/konosuba-yorimichi-chapter-3/")
source("y17", "《寄道》1·第7章：当心冒牌货", C + "2020/03/25/konosuba-yorimichi-chapter-7/")
source("y2", "《寄道》2 收录：赤流／红色波涛的爆裂", C + "2019/08/10/konosuba-bd-short-story-3/", "B", "非官方英译；原为2019年动画第2季BOX特典短篇，短篇目录记载后收入《寄道》2。")
source("y31", "《寄道》3·第1章：邪恶的红魔族", "https://hberrytranslations.blogspot.com/2024/03/konosuba-yorimichi-vol3-chapter-1-evil.html", "B", "H. Berry 非官方英译；注意文末实际禁咒与《续·爆焰》2的抽魔玩笑不同。")
source("y33", "《寄道》3·第3章：前干部的认真决斗", "https://hberrytranslations.blogspot.com/2024/05/konosuba-yorimichi-vol3-chapter-3.html", "B", "H. Berry 非官方英译；区分维兹的爆裂开路、矿石补魔及魔道具自爆。")
source("y35", "《寄道》3·第5章：赐我外挂", "https://hberrytranslations.blogspot.com/2024/08/konosuba-yorimichi-vol3-chapter-5-cheat.html", "B", "H. Berry 非官方英译；含重来情节，不能直接拿来改写正篇时间线。")
source("y41", "《寄道》4·第1章：领主的工作", "https://hberrytranslations.blogspot.com/2026/05/konosuba-yorimichi-vol-4-chapter-1.html", "B", "H. Berry 非官方英译；本次只核对第1章的相关段落，未全卷校勘。")
source("y4pub", "角川：《寄道》第4集", "https://sneakerbunko.jp/product/konosuba/322511000212.html", "C", "官方书目；2026-02-28出版，全篇新作。收录范围已更新至本集，内容核验仍不完整。")
source("ss1", "特典：屠龙者惠惠", C + "2018/04/09/volume-2-short-story-megumin-the-dragon-slayer/", "B", "页面标题标第1卷，URL含volume-2，存在编号差异；本页按篇名定位，不据URL断定中文版本卷次。")
source("ss2", "第2卷特典：Megumin the Ripper", "https://crimsonmagic.me/2016/09/14/konosuba-short-story-megumin-the-ripper/")
source("ss3", "第3卷特典：爆裂即艺术", C + "2018/03/30/volume-3-short-story-explosion-is-art/")
source("ss4", "第4卷特典：赤眼的新人杀手", C + "2018/02/15/crimson-eyed-rookie-killer-volume-4-short-story/")
source("ss5", "第5卷特典：偶尔来场爆裂约会", C + "2018/08/03/volume-5-short-story-a-once-in-awhile-explosive-date/")
source("sslist", "H. Berry：短篇与特典目录", "https://hberrytranslations.blogspot.com/2025/01/konosuba-short-story-list.html", "C", "非官方书目线索；用于发现大量店铺、BD、杂志特典与重收录关系，不代表所有短篇均已读过。")
source("skills", "Wiki：技能名索引", "https://konosuba.fandom.com/wiki/Skills", "C", "二手术语索引，含日文技能名称；结合正篇1第3章核对功能。")
source("wolbach", "Wiki：沃尔巴克", "https://konosuba.fandom.com/wiki/Wolbach", "C", "二手人物索引；童年人物身份与正篇9相互参照。")
source("mog", "Wiki：爆杀魔人もぐにんにん", "https://konosuba.fandom.com/wiki/Mad_Bomber_Moguninnin", "C", "二手人物／魔法名称索引；注意其Detonation为爆発，与Explosion爆裂不同。")
source("movie", "剧场版《红传说》剧情索引", "https://en.wikipedia.org/wiki/KonoSuba:_God%27s_Blessing_on_This_Wonderful_World!_Legend_of_Crimson", "C", "动画电影二手梗概，只用于标注改编扩写，不作为小说设定证据。")

# Settings: conditions, costs, growth, practical limits.
entry("s-family", "设定", "爆焰", "爆焰1·1-3", "炸裂、爆发、爆裂是三种魔法", "日文依次为炸裂魔法、爆発魔法、爆裂魔法。老师把这一系与初级／中级／上级魔法的通常分类分开讲。", ["b113"], ["分类"], "炸裂可碎岩用于工程；爆发威力更强而耗魔大；爆裂的学习与施放门槛尤其高。这里的名称不能当成同义词互换。")
entry("s-energy", "设定", "短篇", "寄道2·赤流爆裂", "爆裂是纯粹魔力的释放", "短篇明确解释其不带元素属性，能伤及有形生物、精灵乃至神兽。画面里的火光不等于火属性判定。", ["y2"], ["分类", "威力"], "能造成伤害与能够一击必杀是两件事。该篇的大精灵在连续攻击后仍然存活。")
entry("s-learn", "设定", "爆焰", "爆焰1·4-8", "技能点与魔力是两道门槛", "爆裂在各职业技能中需要极多点数；学会也可能因为魔力不足而无法施放。惠惠早已够学上级魔法，却继续攒点。", ["b148"], ["学习", "魔力"], "正文把‘习得技能’与‘实际施法’分开。常见的固定MP消耗、升级曲线不能由此推导。")
entry("s-choice", "设定", "爆焰", "爆焰1·4-8、5-5", "只学爆裂是主动选择", "惠惠知道实用性很差仍执意选择；但救小米和悠悠时，她也曾准备放弃梦想、改学上级魔法。", ["b148", "b155"], ["学习", "人物"], "她并非天生不能学习其他魔法，也不是任何情况下都只顾放爆裂。")
entry("s-once", "设定", "正篇", "正篇2·第5章", "一天一发不是不可突破的冷却", "毁灭者战中，和真用Drain Touch把阿库娅的魔力转给惠惠，让她在已经施放后再次爆裂。", ["m25"], ["魔力", "连发"], "该限制描述日常魔力预算，不能写成必须等待24小时的技能锁。")
entry("s-collapse", "设定", "爆焰", "爆焰1·5-6", "施法后的脱力来自消耗", "第一次施放不只耗尽魔力，也消耗体力，惠惠失去行动能力，需要同伴保护。", ["b156"], ["魔力", "风险"], "不能把‘所有爆裂施法者必然昏迷’当规则；其他施法者的余力另有剧情表现。")
entry("s-growth", "设定", "正篇", "正篇9·序章", "升级后仍倒地，是加点方向的结果", "和真盼她的魔力成长足以站稳；惠惠却说明自己一直把升级点数继续投入爆裂威力，让消耗与容量不断追赶。", ["m9p"], ["成长", "魔力"], "这段解释了为何成长并不自然消除脱力。不是每个法师的固定升级结果。")
entry("s-skills", "设定", "正篇", "正篇1·第3章；5·第6章；9·第5章；技能索引", "爆裂相关强化：威力与咏唱速度", "第一卷惠惠本人提及爆裂威力提升与高速咏唱；第五卷揭示她曾预留技能点，并实际将这些点数投入爆裂强化。后期能快速乃至无咏唱施法。日文索引提供『爆発系魔法威力上昇』『高速詠唱』的术语线索。", ["m13", "m56", "m95", "skills"], ["成长", "咏唱"], "早期自述、实际加点与训练后的施法技巧不能直接等同。爆発系是类别名，不说明她学了下位爆发魔法；高速咏唱的具体购买状态未完成日文逐页核验。", grade="C")
entry("s-pronunciation", "设定", "爆焰", "爆焰1·1-4", "准确发音与快速咏唱有技术意义", "课堂中惠惠指出，咏唱速度与准确发音会影响魔法控制；红魔族同时追求帅气演说，属于另一个层面的文化偏好。", ["b114"], ["咏唱", "学习"])
entry("s-chant", "设定", "正篇", "正篇17·第1章", "咏唱用于稳定魔法、提高威力", "后期说明固定咏唱能防止魔法失控并提高威力；熟练的惠惠已经可以无咏唱施放。", ["m171"], ["咏唱", "成长"], "没有统一的‘少念一句降低多少伤害’数值。动画中每段长咒词也不能直接视为小说必念台词。")
entry("s-nochants", "设定", "正篇", "正篇9·第5章", "无咏唱能成为决定胜负的优势", "与沃尔巴克的最后对决中，惠惠赶在对方咏唱结束前直接施放爆裂。", ["m95"], ["咏唱", "战术"], "这是实际剧情证据，足以否定‘爆裂永远必须长时间咏唱’。")
entry("s-staff", "设定", "爆焰", "爆焰1·5-6；爆焰2·第4章", "法杖放大威力，徒手也能施法", "惠惠首次施放没有法杖；后来也能空手爆裂。她在相关场景估计无杖威力约减半。", ["b156", "b24"], ["道具", "威力"], "‘约一半’是这些场景中的人物判断，不宜写成所有法杖一律提供固定×2倍率。")
entry("s-gem", "设定", "正篇", "正篇16·第5章及尾声", "最高级魔力矿石可以替代施法魔力", "Manatite能作为外部施法魔力；普通品质不足以支撑爆裂，惠惠需要最高级品。使用后矿石消失。", ["m165"], ["道具", "魔力", "连发"], "高品质小块价格堪比房屋，成堆库存是结局连发的经济前提。不是永久增加最大魔力。")
entry("s-transfer", "设定", "正篇", "正篇9·第2章", "供魔可以只补到能够行动", "日常练习后，和真会以Drain Touch补少量魔力，使惠惠能自行走路。恢复行动与补足下一发是不同预算。", ["m92"], ["魔力", "日常"])
entry("s-wiz", "设定", "外传", "达斯特7·第2章", "施放后倒地不是所有人的必然结果", "维兹以爆裂重创攻城部队后仍能行动，继续与巴尼尔秘密削弱敌军。", ["dust7"], ["魔力", "人物"], "这能证明‘施放爆裂’本身不强制倒地；不能因此假定惠惠也能无代价连发。")
entry("s-area", "设定", "爆焰", "爆焰1·1-3", "地形破坏与噪音是实际限制", "爆裂会改变地形，地下城可能坍塌，声响还会引来怪物；因此学校把它视为难以实用的魔法。", ["b113"], ["风险", "战术"], "强度与队伍适用性不能简单划等号。")
entry("s-team", "设定", "短篇", "寄道1·第3章", "安心施法依赖前排保护", "达克妮丝失常时惠惠也会害怕；她说自己平常能专注咏唱，是因为相信达克妮丝会挡住危险。", ["y13"], ["战术", "人物"])
entry("s-miss", "设定", "短篇", "第4卷特典·赤眼新人杀手", "爆心与冲击波可以产生不同结果", "惠惠把爆心放在新人杀手旁边，怪物只受冲击、无大碍，附近贵族等人却被震昏。", ["ss4"], ["威力", "战术"], "这是有意偏移的场景，不等于她能精确保全一切友军，或爆裂自动免伤同伴。")
entry("s-resist", "设定", "正篇", "正篇2·第1章", "伤害覆盖广，不代表任何敌人一击死亡", "面对冬将军，惠惠说明高阶精灵魔防很强，一发未必能解决；她也不愿冒险攻击。", ["m21"], ["威力", "风险"], "‘最强攻击魔法’是作中对威力的评价，不是忽略抗性与战局的必杀保证。")
entry("s-practice", "设定", "爆焰", "爆焰1·5-6", "第一次施法之前，已练习咒文多年", "惠惠从童年记住咒文、每日练习；首次真正成功施放时，直接使用最高难度的爆裂。", ["b156"], ["学习", "咏唱"], "初次咏唱的魔力外泄与静电等表现，被她自己联系到控制生疏；不要推广成永恒统一的施法特效。")
entry("s-rating", "设定", "正篇", "正篇5·第6章；9·序章", "和真的评分属于私人鉴赏", "评分会考虑威力、热风与弹坑形状；第5卷有120分。它不是官方技能等级或统一伤害单位。", ["m56", "m9p"], ["日常", "成长"])
entry("s-explosives", "设定", "正篇", "正篇9·第2章", "炸药与爆裂魔法不是同一个技能", "和真用爆炸药剂制作简易炸药，喊Explosion只是恶作剧；惠惠斥其为假货，实际威力远不及自己的魔法。", ["m92"], ["分类", "道具"])

# Story index. Main series follows volume order; parallel works retain their own group.
entry("p-b-origin", "剧情", "爆焰", "爆焰1·序章", "童年：一道爆裂决定了梦想", "惠惠解开谜题封印后，兜帽女性以爆裂轰击黑色巨兽，再把受创巨兽缩成幼兽重新封印。惠惠索要的回报是学习这道魔法。", ["b1p"], ["学习", "人物"], "当场并未用爆裂杀死巨兽。女性的身份在后来的沃尔巴克线中揭示。")
entry("p-b-first", "剧情", "爆焰", "爆焰1·第5章", "首次爆裂：救下朋友，也守住梦想", "救小米、悠悠与黑猫的危机中，惠惠发现点数已够，学会爆裂后轰击飞行魔物群，随即脱力。", ["b155", "b156"], ["学习", "战斗"], "后来才揭示这次爆裂还误毁了另一个邪神的封印；不能与童年解谜释放沃尔巴克混成一件事。")
entry("p-b-work", "剧情", "爆焰", "爆焰2·第1章", "找工作困难：力量难以转换成生计", "精细狩猎、土地工作都难用爆裂完成；夜间放魔法还让村民误以为遭魔王军袭击。练习后的运输也靠妹妹、悠悠帮忙。", ["b21"], ["日常", "风险"])
entry("p-b-gifts", "剧情", "爆焰", "爆焰2·第2章", "启程的法杖与眼罩", "同学搜集材料、由芙妮芙拉的父亲制作法杖，阿露赠送眼罩。装备也是红魔乡友情的纪念。", ["b22"], ["道具", "人物"])
entry("p-b-pool", "剧情", "爆焰", "爆焰2·第4章", "阿尔坎雷堤亚：轰出大型浴池", "惠惠在阿库西斯教徒的鼓动与许可下，徒手向岩盘施放爆裂，给水与温泉之都留下大型浴池与巨大声响。", ["b24"], ["日常", "地形"], "原文写的是挖出池体，不宜简化成‘爆裂凭空造出温泉水’。")
entry("p-b-arnes", "剧情", "爆焰", "爆焰2·第5章", "阿涅斯：利用空隙抢先施法", "追逐逗之助的恶魔阿涅斯出现破绽，悠悠救下黑猫，惠惠完成准备，以爆裂抢在对方咒雷之前击中她。", ["b25"], ["战斗", "咏唱"])
entry("p-b-party", "剧情", "爆焰", "爆焰3", "阿克塞尔：队伍需要的不只是威力", "会最强魔法却一天只能一发，让惠惠的求组队之路处处受挫。冒险职业的实用性与她的坚持形成冲突。", ["b3pub"], ["日常", "人物"], "此条依据官方简介，未把全卷每次试组队经过逐次列尽。")
entry("p-b-hoost", "剧情", "爆焰", "爆焰3·第4章", "霍斯特：爆裂收尾依赖众人的铺垫", "悠悠准备隐身卷轴等支援；受过多次攻击的霍斯特陷入麻痹，惠惠以爆裂收尾。", ["b34"], ["战斗", "道具"], "隐身来自道具，不是另学魔法；霍斯特称若满状态或许能撑住。惠惠也猜想前日未施法使当天魔力异常充沛，这只是人物推测，不建立按天叠加的数值规则。")
entry("p-1-castle", "剧情", "正篇", "正篇1·第3章", "贝尔迪亚：日常练习变成外交事故", "和真陪惠惠向旧城堡练习爆裂，后来得知城堡住着魔王军干部。持续轰炸引来了无头骑士的抗议。", ["m13"], ["日常", "风险"])
entry("p-1-undead", "剧情", "正篇", "正篇1·第4章", "亡灵骑士群：先聚拢，再用爆裂清场", "惠惠与阿库娅没有停止城堡轰炸；贝尔迪亚带兵来袭后，爆裂用于清除集中起来的亡灵骑士，干部本体另由队伍解决。", ["m14"], ["战斗", "战术"])
entry("p-2-snow", "剧情", "正篇", "正篇2·第1章", "雪精狩猎与冬将军", "爆裂批量击倒雪精，却招来危险的冬将军。惠惠后来拒绝把爆裂当作能稳胜这位高阶精灵的方案。", ["m21"], ["战斗", "风险"])
entry("p-2-swap", "剧情", "正篇", "正篇2·第1章", "交换队伍：达斯特体验一发后的空档", "被称赞之后惠惠先向空地炫技、耗尽魔力；接着遭遇新人杀手，达斯特的临时队伍陷入困境。", ["m21"], ["日常", "战术"], "这一段同时说明噪音引怪与过早用掉关键技能的代价。")
entry("p-2-destroyer", "剧情", "正篇", "正篇2·第5章", "毁灭者：双爆裂与同日追加一发", "阿库娅解除屏障后，惠惠与维兹的爆裂破坏机体；随后和真转移阿库娅魔力，让惠惠追加施放处理残余危机。", ["m25"], ["战斗", "连发"], "维兹是巫妖，阿库娅的神圣魔力不适合直接供给她；爆裂与传送动力核心各承担不同任务。")
entry("p-3-vanir", "剧情", "正篇", "正篇3·第4章", "巴尼尔：把附身者与前排一起轰击", "地下城不适合施放爆裂；在外部决战中，达克妮丝与附身的巴尼尔一起承受惠惠的攻击。", ["m34"], ["战斗", "风险"], "它破坏巴尼尔的这次现身，而不是永久消灭恶魔的一切生命；达克妮丝的耐久也不能等同于友军免伤。")
entry("p-4-hans", "剧情", "正篇", "正篇4·第5章", "汉斯：爆裂拆散，冻结与净化收尾", "毒史莱姆的扩散是风险。和真制造机会，惠惠用爆裂将汉斯炸散，维兹冻结残余，阿库娅完成净化。", ["m45"], ["战斗", "战术"], "小说采用多人连携；不能把结局归为惠惠一人一发消灭所有毒害。")
entry("p-5-sylvia", "剧情", "正篇", "正篇5·第5章", "席尔维亚：爆裂被兵器吸收并充能", "惠惠向席尔维亚发射魔法，却被轨道炮的吸魔部分中途吸收。满能量的兵器由小米抢先扣动扳机，击穿席尔维亚。", ["m55"], ["战斗", "道具"], "这不是一次爆裂正面命中后被免疫的实验。电影之后增加的复活决战需要单列。")
entry("p-5-choice", "剧情", "正篇", "正篇5·第6章", "和真替她选择继续走爆裂之路", "惠惠因担心拖累队伍，请和真帮她学上级魔法；和真却把点数投入爆裂增强。她再次施放，得到120分的评价。", ["m56"], ["成长", "人物"], "爆裂从任性选择变为被同伴明确接纳的专长。")
entry("p-6-capital", "剧情", "正篇", "正篇6·第4章", "王都防卫：担架上的功臣", "魔王军攻击后，惠惠因爆裂消灭敌军指挥官而受称赞，即使被用担架送回，仍被视为战斗中的重要功臣。", ["m64"], ["战斗", "人物"])
entry("p-7-hydra", "剧情", "正篇", "正篇7·第2章", "九龙海德拉：削弱后才是必杀机会", "多人魔法与悠悠的光之剑参与削弱海德拉，惠惠的爆裂作为关键收尾。强敌战需要铺垫。", ["m72"], ["战斗", "战术"])
entry("p-8-walk", "剧情", "正篇", "正篇8·第1章", "爆裂散步：轰鸣掩盖感情回应", "和真尝试回应惠惠的感情，却被爆裂巨响遮住话语；日常练习已经成为两人的固定相处方式。", ["m81"], ["日常", "人物"])
entry("p-9-style", "剧情", "正篇", "正篇9·序章", "爆裂鉴赏：连热风与弹坑都要评分", "惠惠尝试让热浪适应夏季，和真从威力、风与弹坑圆度评价这一发；爆裂也被她当成创作和审美对象。", ["m9p"], ["日常", "成长"])
entry("p-9-bomb", "剧情", "正篇", "正篇9·第2章", "假Explosion与小型炸药", "和真制作药剂炸药并假装学会爆裂，激怒惠惠；阿库娅缩小的那根炸药随后在战场派上用场。", ["m92"], ["道具", "日常"])
entry("p-9-raids", "剧情", "正篇", "正篇9·第4—5章", "沃尔巴克：爆裂＋传送的攻防循环", "敌人反复轰击要塞后传送离开；阿库娅维修城墙，和真、惠惠、悠悠则反向袭击魔王军营地。每日重击拖垮敌军。", ["m94", "m95"], ["战斗", "战术"], "同一魔法在持续补给、传送与修筑支援下，能改变整场战役。")
entry("p-9-mentor", "剧情", "正篇", "正篇9·第5章", "击倒启蒙者：无咏唱与感谢", "惠惠面对童年憧憬的沃尔巴克一度动摇；和真用小型炸药扰乱战局，惠惠最后以无咏唱爆裂抢先击倒她。", ["m95"], ["人物", "咏唱", "战斗"], "这是成长与情感代价交汇的段落；不把沃尔巴克的所有隐瞒动机作为已证事实。")
entry("p-10-arrest", "剧情", "正篇", "正篇10·第4章", "埃尔罗德：夜间爆裂导致被捕", "在城外的深夜施法，让惠惠及同行者被拘留；她坚持‘每天一发是自己的职责’，体现价值观与社会规则的冲突。", ["m104"], ["日常", "风险"], "测谎没有否定她的信念，不等于世界法则要求她每天施放。")
entry("p-11-routine", "剧情", "正篇", "正篇11·第2章", "让和真陪散步，也可以称作惩罚", "惠惠把陪她完成每日爆裂当作对和真的‘惩罚’，延续两人的日常与感情互动。", ["m112"], ["日常", "人物"])
entry("p-11-seal", "剧情", "正篇", "正篇11·第3章", "首发的后果：雷吉娜的封印被误毁", "回到红魔乡后的解释指出，惠惠当年第一次爆裂意外破坏了操纵与复仇女神雷吉娜的封印，给后续塞蕾娜线埋下因果。", ["m113"], ["地形", "人物"], "这是首次施法的追加信息；童年解谜打开的沃尔巴克封印是另一件事。")
entry("p-12-date", "剧情", "正篇", "正篇12", "约会仍然会回到爆裂散步", "本卷剧情索引记载约会、同行者以及河边爆裂捕鱼等日常。爆裂继续承担恋爱与队伍生活的连接作用。", ["m12syn"], ["日常", "人物"], "目前依据二手卷摘要，具体对白、约会顺序与每次发射尚待小说正文复核。")
entry("p-13-wiz", "剧情", "正篇", "正篇13·第5章", "维兹也会用爆裂表达愤怒", "与堕天使杜克的魔法决斗及误会落幕后，维兹情绪爆发，咏唱后向杜克施放Explosion。", ["m135"], ["战斗", "人物"], "惠惠观看别人的华丽魔法时也会嫉妒，想把大家的注意力拉回爆裂。")
entry("p-14-robot", "剧情", "正篇", "正篇14·第4章", "爆杀魔人：先受损，后被完全摧毁", "高速、自我修复的魔像曾承受爆裂后留下损伤；决战中和真牵制并破坏其行动，惠惠完成咏唱将其摧毁。", ["m144"], ["战斗", "战术"], "前一次命中、威力与具体施法经过主要在第3章，本次未取得该章完整可读正文，因此不补写精确倍率。")
entry("p-14-recognition", "剧情", "正篇", "正篇14·第4章", "红魔族造物对她的力量给出认可", "爆杀魔人临终承认惠惠的魔法超过原先预计；她保守战斗秘密，让悠悠的族长试炼成果不被抢走。", ["m144"], ["成长", "人物"])
entry("p-15-plan", "剧情", "正篇", "正篇15·第5章", "将每日爆裂升级为攻城计划", "和真提出在魔王城附近设置传送点、让惠惠反复轰击的方案。此时是计划，后来的矿石库存才让连发攻城成为现实。", ["m155"], ["战术", "连发"])
entry("p-16-gift", "剧情", "正篇", "正篇16·第5章及尾声", "昂贵的魔力矿石，成为终局的补给", "和真购入最高级Manatite交给惠惠，用财富把她的单发专长转换成持续输出。卷末开始攻击，密集连发在第17卷展开。", ["m165"], ["道具", "连发", "人物"])
entry("p-17-castle", "剧情", "正篇", "正篇17·第1章", "魔王城：矿石支持下连续轰击", "惠惠从有利位置反复释放爆裂，压制出城的守军和强敌，并对魔王城结界施加持续压力。", ["m171", "m17pub"], ["连发", "战斗"], "这是外部魔力突破日常次数限制的终局实例。页面不虚构每分钟发射次数或弹药冷却。", grade="B")
entry("p-17-kazuma", "剧情", "正篇", "正篇17·第4章", "和真的最终一发", "和真把魔王传送到地下城，利用从日常观察中学到的爆裂与最高级矿石施法，造成坍塌并与已经被削弱的魔王同归于尽，之后复活。", ["m174"], ["学习", "战斗", "道具"], "爆裂承接了他长期陪伴惠惠的经验，也是把‘地下城会塌’这一缺点反转成战术。")
entry("p-17-last", "剧情", "正篇", "正篇17·第4章后段", "城上的连续爆裂，逼退另一支敌军", "惠惠背着矿石，从魔王城继续轰击魔王之女一方军队，迫使敌方撤退；段落也写到她流鼻血。", ["m174"], ["连发", "风险"], "鼻血是已出现的描写；本次没有证据把它定成‘矿石中毒’或量化的连发惩罚公式。")
entry("p-c1", "剧情", "续爆焰", "续·爆焰1·第4章", "盗贼团：不只追求漂亮的一发", "惠惠、悠悠、爱丽丝、克莉丝等人的活动中，惠惠仍会用爆裂救援被魔物围困的人，并带着疲惫返回队伍日常。", ["c14"], ["人物", "战斗"], "本系列发生于正篇途中；具体篇章插入哪两卷之间不强行采用互有差异的民间阅读顺序。")
entry("p-c2-toad", "剧情", "续爆焰", "续·爆焰2·第1章", "蛙王：巨大目标依然伴随溅射麻烦", "惠惠用爆裂攻击巨大的King Toad；队伍还要处理青蛙黏液等附带后果，爱丽丝的保护也有作用。", ["c21"], ["战斗", "风险"])
entry("p-c2-cover", "剧情", "续爆焰", "续·爆焰2·第4章", "王都近郊：伪造已讨伐珍兽的说法", "水晶狮虎偷走项链后逃走，惠惠在附近施放爆裂，准备声称珍兽与项链已一同化灰，以掩护稀有动物消息；结果因违规施法被拘留。", ["c24"], ["日常", "风险"], "这时的爆裂并没有实际击杀逃跑的水晶狮虎，真正后续处理在下一章。")
entry("p-c2-drain", "剧情", "续爆焰", "续·爆焰2·第5章", "和真的‘封印’，其实是抽走部分魔力", "和真以Drain Touch把惠惠的魔力抽到不够放爆裂，阻止她继续闹事；她用‘力量被封印’的中二说法回应。", ["c25"], ["魔力", "日常"], "该章后续还有水晶狮虎与宝石的爆裂处理；不要把玩笑封印记成新魔法技能。")
entry("p-c2-nest", "剧情", "续爆焰", "续·爆焰2·第5章及尾声", "再一次‘打偏’：炸毁兽巢，留下珍兽", "找回国宝项链后，惠惠把爆裂射向水晶狮虎身后的兽巢，毁掉宝石库存，却留下怪物本身。阿库娅为宝石损失与所谓失准抱怨。", ["c25"], ["人物", "战术"], "尾声的水晶狮虎仍然存活，不能把这一发记成击杀珍兽。与第4卷赤眼新人杀手短篇形成呼应。")
entry("p-masked", "剧情", "外传", "蒙面恶魔外传·第5章", "维兹人类时期：爆裂仍是昂贵的选项", "过去与维兹交手时，巴尼尔说想耗掉他一条命恐怕要学爆裂；维兹当时没有该魔法，提到‘下次’再学。", ["masked"], ["学习", "人物"], "这是过去的对话和资源判断，不应扩大成‘普通人绝对不可能学爆裂’。")
entry("p-dust7", "剧情", "外传", "达斯特7·第2章", "留守阿克塞尔：维兹假扮惠惠轰击敌军", "为隐藏身份，维兹穿上惠惠式服装、报惠惠的名字，以爆裂重创魔王军；此后仍与巴尼尔继续行动。", ["dust7"], ["战斗", "人物"], "达斯特估计约四成敌人被击倒，是现场估算，不是爆裂固定杀敌比例。")
entry("p-dust-observe", "剧情", "短篇", "达斯特外传特典·观察惠惠", "悠悠的后勤：填坑与背人", "惠惠继续在荒地制造弹坑，悠悠用魔法填平并熟练背她回城；回城时她已经恢复到可以自己走路。", ["dustss"], ["日常", "魔力"], "至少说明‘放完一整天都必定完全动不了’过于绝对；这里没有给出固定恢复分钟数。")
entry("p-y1-mushroom", "剧情", "短篇", "寄道1·第2章", "爆裂侦探：无辜嫌疑，真实连锁反应", "惠惠被怀疑引发连环爆炸，一度被要求停用爆裂；调查发现会受强魔力刺激爆炸的蘑菇，她的日常施法正好触发连锁。", ["y12"], ["地形", "风险"], "她声称红魔族不放魔力会死，被和真当场斥为胡说。不是生理设定。")
entry("p-y1-front", "剧情", "短篇", "寄道1·第3章", "失去可靠的盾，爆裂法师也会恐惧", "达克妮丝被削弱后的危机，暴露惠惠对前排的信赖；她解释自己能安心咏唱，正因为有达克妮丝在。", ["y13"], ["人物", "战术"])
entry("p-y1-copy", "剧情", "短篇", "寄道1·第7章", "面对冒牌队伍，展示真正的战斗方式", "对峙后来转成共同应对狼群：和真射杀首领，达克妮丝吸引群狼，惠惠爆裂清场，让冒牌队伍理解实力差距。", ["y17"], ["战斗", "战术"])
entry("p-y2-storm", "剧情", "短篇", "寄道2·赤流／红色波涛的爆裂", "风暴大精灵：悠悠、维兹与惠惠接力", "悠悠用雷魔法、维兹和惠惠相继爆裂，大精灵受伤后消耗多余魔力恢复，台风平息。精灵并未被杀。", ["y2"], ["战斗", "威力"], "爆裂能伤及无实体的精灵；这一战的目的与结果是停止暴走。篇名中文译法并不统一。")
entry("p-y3-ring", "剧情", "短篇", "寄道3·第1章", "恶魔戒指、魔眼招式与真正的禁用诅咒", "惠惠借诅咒戒指获得魔眼力量，亲自使过束缚和雷击。雷击还伤到自己的眼睛，魔眼耗尽其魔力；戒指被净化毁坏后，赔偿欠款引发巴尼尔诅咒：付清前无法施放爆裂。", ["y31"], ["道具", "魔力"], "魔眼招名和反噬详见本人技能报告。戒指能力与常规习得法术、抽魔的玩笑封印分别理解。")
entry("p-y3-wiz", "剧情", "短篇", "寄道3·第3章", "维兹用爆裂开路，不会自动躺在入口", "维兹筹资攻略地下城时造成大洞，爆裂后仍深入迷宫。后面与巴尼尔对决又使用矿石，主要以其他魔法持续攻击。", ["y33"], ["战斗", "魔力"], "该篇女仆魔道具的自爆也很猛烈，但自爆与法师施放Explosion不是同一个术。")
entry("p-y3-redo", "剧情", "短篇", "寄道3·第5章", "重来情节：绕开爆裂少女也没那么容易", "和真试图重新规划异世界生活，却仍遭遇熟悉的爆裂与惠惠。它利用读者对本篇组队过程的了解制造喜剧。", ["y35"], ["人物", "日常"], "重来情节按该短篇自身叙事理解，不用它覆盖正篇原有事件先后。")
entry("p-y4-town", "剧情", "短篇", "寄道4·第1章（2026）", "爆裂成为下班钟，也制造城市热害", "阿克塞尔居民用傍晚爆裂当作下班信号；惠惠争取建塔施法、作为观光项目，被代理领主达克妮丝否决。调查又把异常炎热联系到她的日常爆裂。", ["y41"], ["日常", "地形"], "本次核对到第1章，尚未对第4集其余篇章做完整爆裂清单。")
entry("p-ss-dragon", "剧情", "短篇", "特典·屠龙者惠惠", "采石工作与‘屠龙者’头衔", "惠惠承接碎岩任务时遇到飞龙幼兽，本来有所迟疑，得知能获得屠龙称号后便施放爆裂。", ["ss1"], ["日常", "人物"], "按短篇篇名定位；公开页面卷号与URL不一致。")
entry("p-ss-art", "剧情", "短篇", "第3卷特典·爆裂即艺术", "艺术家邀约与拆屋事故", "艺术家请求展示爆裂，几次危险目标被和真制止；最终转向需要拆除的宅邸，冲击波仍波及周围窗户。", ["ss3"], ["日常", "风险"])
entry("p-ss-kind", "剧情", "短篇", "第4卷特典·赤眼新人杀手", "一发故意打偏的爆裂", "面对新人杀手与纠缠的贵族，惠惠把爆心移开，让怪物得以逃离而贵族等人被震昏。她随后让和真背回去。", ["ss4"], ["人物", "战术"])
entry("p-ss-date", "剧情", "短篇", "第5卷特典·偶尔来场爆裂约会", "被跟踪的原因，是对爆裂的憧憬", "惠惠与和真约会后去城外练习，发现跟随的青年并不是追求她，而是被Explosion吸引，想拜她为师。", ["ss5"], ["日常", "学习"])

# Character / tool lookup is intentionally short, linking back to the fuller events.
entry("n-megumin", "人物道具", "爆焰", "爆焰1；正篇5、9", "惠惠／めぐみん／Megumin", "从童年的憧憬走到专精：把技能点持续投入爆裂，接受同伴帮助，也会为救朋友考虑改变选择。", ["b148", "b155", "m56"], ["人物", "成长"])
entry("n-wolbach", "人物道具", "正篇", "爆焰1序章；正篇9", "沃尔巴克／ウォルバク／Wolbach", "童年魔法的启蒙者，后来成为必须面对的敌人；使用爆裂与传送配合。其邪神身份与逗之助的关联在后期揭示。", ["b1p", "m94", "wolbach"], ["人物", "战术"], "序章本身没有直接写出她的姓名，身份需要后文交叉确认。", grade="C")
entry("n-wiz", "人物道具", "外传", "蒙面恶魔；正篇2、13", "维兹／ウィズ／Wiz", "会爆裂，也会其他魔法；人类时期与巴尼尔的对话和后来巫妖时期的实际施法，要分开看。", ["masked", "m135"], ["人物", "学习"])
entry("n-kazuma", "人物道具", "正篇", "正篇2、9、17", "和真／カズマ／Kazuma", "陪练、背人、评分与供魔；最终亲自借矿石施放从长期观察中学会的爆裂。", ["m92", "m174"], ["人物", "魔力", "学习"])
entry("n-yunyun", "人物道具", "爆焰", "爆焰1、3；正篇9", "悠悠／ゆんゆん／Yunyun", "作为走实用魔法路线的对照，同样给惠惠提供救援、道具与传送支援。她的支持使爆裂专精能够运作。", ["b155", "b34", "m95"], ["人物", "战术"])
entry("n-darkness", "人物道具", "短篇", "正篇3；寄道1·第3章", "达克妮丝／ダクネス／Darkness", "前排保护与诱敌保障咏唱；曾承受爆裂相关冲击，但她能扛住不代表队伍全员免伤。", ["m34", "y13"], ["人物", "风险"])
entry("n-chomusuke", "人物道具", "爆焰", "爆焰1；正篇9", "逗之助／ちょむすけ／Chomusuke", "黑猫与沃尔巴克线连接童年封印和后续追逐战，是惠惠首次爆裂时保护的对象之一。", ["b1p", "b155", "wolbach"], ["人物"], "没有把它当作给惠惠自动回魔的宠物。")
entry("n-komekko", "人物道具", "正篇", "正篇5·第5章", "小米／こめっこ／Komekko", "惠惠的妹妹，在席尔维亚战中抢先扣下由爆裂充能的兵器扳机。这个击杀分工是小说明确的笑点。", ["m55"], ["人物", "道具"])
entry("n-mog", "人物道具", "正篇", "正篇14", "爆杀魔人もぐにんにん", "红魔乡相关的高速、自修复魔像；它自身的爆発（Detonation）与惠惠的爆裂（Explosion）需要按日文分开。", ["m144", "mog"], ["人物", "分类"], "中文译名存在差异，保留日文作为检索锚点。", grade="C")
entry("t-staff", "人物道具", "爆焰", "爆焰2·第2章；正篇1", "法杖：增幅器与同学的礼物", "启程法杖来自同学们的准备；后续装备升级也改善威力。可徒手施法，所以杖不是解锁Explosion的钥匙。", ["b22", "m13", "b156"], ["道具"])
entry("t-eye", "人物道具", "爆焰", "爆焰2·第2章", "眼罩：阿露的赠礼", "眼罩与红魔族的帅气装束有关。当前核验段落没有证明它封印着惠惠真正的爆裂力量。", ["b22"], ["道具", "人物"])
entry("t-card", "人物道具", "爆焰", "爆焰1·5-5", "冒险者卡：检查并习得技能", "危机时惠惠查看冒险者卡，确认技能点条件后选择爆裂。学会技能和补足魔力仍是两回事。", ["b155"], ["道具", "学习"])
entry("t-manatite", "人物道具", "正篇", "正篇16—17", "魔力矿石／マナタイト／Manatite", "储存魔力的消耗品。终局的最高级品为惠惠与和真提供施法资源；要区分矿石供魔与含矿石装备的增幅用途。", ["m165", "m174"], ["道具", "魔力", "连发"])
entry("t-coronatite", "人物道具", "正篇", "正篇2·第5章", "Coronatite／コロナタイト：毁灭者核心", "毁灭者的危险动力核心，由维兹传送处理。它不是结局拿在手中用于补魔连发的Manatite。", ["m25"], ["道具", "分类"])
entry("t-railgun", "人物道具", "正篇", "正篇5·第5章", "轨道炮：吸收爆裂后发射", "吸魔部分截获惠惠的魔法，为兵器充能；小米扣动扳机是兵器射击，不是她学会了爆裂。", ["m55"], ["道具", "战术"])
entry("t-scroll", "人物道具", "爆焰", "爆焰3·第4章", "卷轴：不改加点也能提供别种效果", "悠悠购买并安排隐身等卷轴支持战斗。道具施法与惠惠主动习得其他魔法不能混为一谈。", ["b34"], ["道具", "学习"])

# Misconceptions are separately searchable for quick consultation.
entry("q-24h", "误区", "正篇", "正篇2、16—17", "‘一天一发’＝固定24小时冷却？", "不是。供魔与高品质矿石都有突破次数限制的实例；仍需面对魔力、支援和成本。", ["m25", "m165"], ["魔力", "连发"])
entry("q-other", "误区", "爆焰", "爆焰1·4-8、5-5", "惠惠因为资质差才学不会其他魔法？", "相反，她具备学习条件，只把点数留给所爱的魔法；救人时还准备过改学上级魔法。", ["b148", "b155"], ["学习", "人物"])
entry("q-die", "误区", "短篇", "寄道1·第2章", "不每天放爆裂，红魔族就会死？", "这是惠惠被禁用时的辩词，被和真直接拆穿。不能作为强制每日施法的身体机制。", ["y12"], ["日常", "魔力"])
entry("q-allcollapse", "误区", "外传", "达斯特7·第2章", "凡是施放Explosion都必定倒地？", "维兹施放后仍能行动，已构成反例。惠惠的脱力要联系她自己的消耗与加点。", ["dust7"], ["魔力", "人物"])
entry("q-chant", "误区", "正篇", "正篇9·第5章；17·第1章", "每次必须念完动画里的整段长咒文？", "小说后期有无咏唱实例，也说明咏唱的稳定与增幅功能。技术咏唱、耍帅演说、动画演出文本需分清。", ["m95", "m171"], ["咏唱"])
entry("q-fire", "误区", "短篇", "寄道2·赤流爆裂", "爆裂只是一个超级大火球？", "该篇明确说明其为无元素属性的魔力爆发。强光、热浪和动画火焰特效不足以证明火属性。", ["y2"], ["分类", "威力"])
entry("q-oneshot", "误区", "正篇", "正篇2·第1章；14·第4章", "最强魔法＝对任何敌人一发必杀？", "冬将军的高魔防、曾受损后继续活动的爆杀魔人，都要求区别威力评价、命中条件与敌人状态。", ["m21", "m144"], ["威力", "战术"])
entry("q-movie", "误区", "改编", "正篇5与剧场版《红传说》", "电影追加的席尔维亚决战就是原小说经过？", "小说本卷明确是爆裂被兵器吸收、小米射击。电影对席尔维亚后续战斗作了扩写，应按改编单独记录。", ["m55", "movie"], ["版本", "战斗"], "这里比较事件结构，不把电影扩写反向写成小说新设定。", grade="C")
entry("q-seals", "误区", "正篇", "爆焰1序章；正篇11·第3章", "爆裂轰开了童年沃尔巴克的封印？", "童年惠惠以解谜打开封印；后来首次爆裂误毁的是雷吉娜的封印。人物与时间不同。", ["b1p", "m113"], ["人物", "版本"])
entry("q-mineral", "误区", "正篇", "正篇2与16", "毁灭者核心和连发矿石是同一种东西？", "不是：Coronatite与Manatite有不同日文名、剧情用途与危险背景。中文‘魔石’的笼统称呼易造成混淆。", ["m25", "m165"], ["道具", "分类"])
entry("q-seal-real", "误区", "短篇", "续·爆焰2·第5章；寄道3·第1章", "和真抽魔的‘封印’与巴尼尔禁咒一样？", "前者是剩余魔力不够的玩笑说法；后者的短篇确实叙述了欠款付清前不能用爆裂的诅咒。", ["c25", "y31"], ["魔力", "版本"])

GRADE_NAMES = {"A": "官方正文", "B": "非官方译文核对", "C": "简介／二手索引"}
CATEGORIES = ["设定", "剧情", "人物道具", "误区"]
SERIES = ["爆焰", "正篇", "续爆焰", "外传", "短篇", "改编"]


def refs_html(refs):
    return '<div class="citations">' + ''.join(
        f'<a href="{escape(SOURCES[r]["url"], quote=True)}" target="_blank" rel="noopener noreferrer">'
        f'{escape(SOURCES[r]["title"])} <span aria-hidden="true">↗</span></a>'
        for r in refs) + '</div>'


def render_entry(e, number):
    tags = ''.join(f'<span class="tag">{escape(t)}</span>' for t in e['tags'])
    notes = ''.join(f'<p>{escape(n)}</p>' for n in e['notes'])
    haystack = ' '.join([e['title'], e['summary'], e['where'], e['series'],
                         *e['tags'], *e['notes'], *(SOURCES[r]['title'] for r in e['refs'])])
    return f'''<details class="entry" id="{e['id']}" data-series="{e['series']}" data-grade="{e['grade']}" data-search="{escape(haystack, quote=True)}">
<summary><span class="entry-number">{number:02d}</span><span class="summary-content"><span class="entry-meta">{escape(e['where'])}<span class="grade grade-{e['grade']}">{GRADE_NAMES[e['grade']]}</span></span><span class="entry-title">{escape(e['title'])}</span><span class="entry-lead">{escape(e['summary'])}</span></span><span class="expand-mark" aria-hidden="true"></span></summary>
<div class="entry-body">{notes}<div class="tags">{tags}</div>{refs_html(e['refs'])}<a class="permalink" href="#{e['id']}" aria-label="定位条目：{escape(e['title'], quote=True)}">§ 条目定位</a></div></details>'''


def coverage_row(name, status, detail, refs=()):
    return f'<tr><th scope="row">{escape(name)}</th><td><span class="coverage-state">{escape(status)}</span></td><td>{detail}{refs_html(refs) if refs else ""}</td></tr>'


def build():
    sections = []
    titles = {"设定": ("01", "设定速查", "先看条件、消耗与成长，再谈这道魔法有多强。"),
              "剧情": ("02", "剧情索引", "按系列与卷序整理。前传、正篇、平行外传保留各自顺序。"),
              "人物道具": ("03", "人物与道具", "名字、分工和资源，集中检索。"),
              "误区": ("04", "容易混淆的说法", "将角色辩词、改编演出和小说事实拆开看。")}
    for category in CATEGORIES:
        items = [e for e in ENTRIES if e['category'] == category]
        no, title, intro = titles[category]
        groups = []
        for series in SERIES:
            subset = [e for e in items if e['series'] == series]
            if not subset:
                continue
            rendered = ''.join(render_entry(e, items.index(e) + 1) for e in subset)
            groups.append(f'<div class="entry-group" data-group="{series}"><h3 class="group-heading">{series} <span>{len(subset):02d}</span></h3>{rendered}</div>')
        sections.append(f'<section class="catalog-section" id="section-{CATEGORIES.index(category)}" data-category="{category}" aria-labelledby="heading-{no}"><header class="section-heading"><span class="section-no">{no}</span><div><h2 id="heading-{no}">{title} <span class="section-count">{len(items)}</span></h2><p>{intro}</p></div></header>{"".join(groups)}</section>')

    main_topics = [
        "城堡练习；亡灵骑士清场", "雪精与冬将军；交换队伍；毁灭者供魔", "地下城限制；巴尼尔与达克妮丝", "汉斯：爆裂—冻结—净化", "席尔维亚／轨道炮；继续专精的选择", "王都防衛：爆裂击倒指挥官", "九龙海德拉的多人连携", "爆裂散步与感情回应", "加点与评分；炸药；沃尔巴克与无咏唱", "埃尔罗德夜间施法被捕", "日常散步；首发误毁雷吉娜封印", "约会与爆裂捕鱼（正文待核）", "维兹对杜克施放爆裂", "爆杀魔人；悠悠的试炼；部分经过待核", "传送点＋反复攻城的计划", "最高级Manatite购入与首发", "矿石连发；破结界；和真的终局爆裂"]
    main_refs = ["m13", "m25", "m34", "m45", "m55", "m64", "m72", "m81", "m95", "m104", "m113", "m12syn", "m135", "m144", "m155", "m165", "m174"]
    coverage = ''.join(coverage_row(f"正篇 {i} 卷", "重点卷章已定位" if i not in (12, 14) else "含复核缺口", t, [r]) for i, (t, r) in enumerate(zip(main_topics, main_refs), 1))
    coverage += coverage_row("《爆焰》1—3", "重点已核对", "第1卷关键段落直接读官方日文；第2—3卷以公开译文及简介定位。", ["kaku", "b34"])
    coverage += coverage_row("《续·爆焰》1—2", "重点已定位", "救援、蛙王、水晶狮虎、魔力抽取；平行篇章不强行排入正篇某两卷之间。", ["c14", "c25"])
    coverage += coverage_row("蒙面恶魔外传", "相关段落已核对", "维兹人类时期与巴尼尔交手的爆裂讨论。其他随口提及未作逐句清单。", ["masked"])
    coverage += coverage_row("达斯特外传1—7", "局部核对", "重点收录第7卷维兹假扮惠惠与一篇观察特典。作者昼熊；其余卷尚未逐章穷尽检索。", ["dust7", "dustss"])
    coverage += coverage_row("《寄道》1—2", "重点短篇已定位", "爆裂侦探、前排保护、冒牌队伍、风暴精灵。其他短篇中的全部散步和施放没有逐次校勘。", ["y12", "y2"])
    coverage += coverage_row("《寄道》3", "重点短篇已定位", "恶魔戒指、巴尼尔诅咒、维兹爆裂开路与重来情节；第4章等零散段落尚未穷尽。", ["y31", "y33", "y35"])
    coverage += coverage_row("《寄道》4（2026）", "第1章局部核对", "已确认本集出版及领主篇中的爆裂内容；其余新篇不冒称已全读。", ["y41", "y4pub"])
    coverage += coverage_row("店铺／BD／杂志特典", "选篇核对", "收录屠龙、艺术、赤眼新人杀手、爆裂约会等；大量特典仍只找到目录线索。篇名并不能保证内容全与爆裂有关。", ["sslist"])
    coverage += coverage_row("早期Web版／漫画／动画／游戏／TRPG", "版本边界", "正式小说版为主体。Web版差异不并入；漫画动画仅做差异提示；游戏与TRPG数值不据此写成小说规则。", ["kaku", "movie"])

    ledger = []
    for index, (key, s) in enumerate(SOURCES.items(), 1):
        used = [e for e in ENTRIES if key in e['refs']]
        backlinks = ''.join(f'<a href="#{e["id"]}">{escape(e["title"])}</a>' for e in used)
        ledger.append(f'<details class="source-row" id="source-{key}"><summary><span class="source-num">{index:02d}</span><span><span class="grade grade-{s["kind"]}">{GRADE_NAMES[s["kind"]]}</span> {escape(s["title"])}</span><span aria-hidden="true">＋</span></summary><div class="source-body"><p>{escape(s["note"])}</p><a class="source-url" href="{escape(s["url"], quote=True)}" target="_blank" rel="noopener noreferrer">打开原来源 ↗</a><span class="source-domain">{escape(s["url"].split("/")[2])}</span><div class="source-backlinks">{backlinks or "书目／范围依据"}</div></div></details>')
    numbers = {c: len([e for e in ENTRIES if e['category'] == c]) for c in CATEGORIES}
    document = HTML.replace("{{SECTIONS}}", ''.join(sections)).replace("{{COVERAGE}}", coverage).replace("{{SOURCES}}", ''.join(ledger))
    document = document.replace("{{TOTAL}}", str(len(ENTRIES))).replace("{{SOURCE_COUNT}}", str(len(SOURCES)))
    document = document.replace("{{SETTING_COUNT}}", str(numbers['设定'])).replace("{{PLOT_COUNT}}", str(numbers['剧情']))
    document = document.replace("{{CATEGORY_OPTIONS}}", ''.join(f'<option value="{c}">{c} · {numbers[c]}</option>' for c in CATEGORIES))
    document = document.replace("{{SERIES_OPTIONS}}", ''.join(f'<option value="{s}">{s}</option>' for s in SERIES))
    OUT.write_text(document, encoding="utf-8")
    print(json.dumps(dict(file=str(OUT), entries=len(ENTRIES), sources=len(SOURCES), categories=numbers), ensure_ascii=False))


HTML = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="description" content="素晴轻小说爆裂魔法：设定、卷章剧情、人物道具、改编差异与来源。离线搜索与筛选，含完整结局剧透。"><title>爆裂魔法｜素晴原作资料索引</title>
<style>
:root{--paper:#f8f4ec;--surface:#fffcf6;--ink:#252522;--muted:#68665e;--line:#d8d0c2;--red:#9a3329;--gold:#965a16;--soft:#eee7db;--blue:#35575e;--serif:"Noto Serif CJK SC","Source Han Serif SC","Songti SC","SimSun",serif;--sans:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;--mono:Consolas,monospace}
html[data-theme="dark"]{--paper:#1d211f;--surface:#242925;--ink:#ece8dc;--muted:#b6b6a8;--line:#46504a;--red:#f0907b;--gold:#deb778;--soft:#30372f;--blue:#a7c7c8}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:32px}body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.75;font-size:15px}a{color:var(--red);text-decoration-thickness:1px;text-underline-offset:4px;overflow-wrap:anywhere}button,input,select{font:inherit;color:inherit}button,select{cursor:pointer}button{background:var(--surface);border:1px solid var(--line);border-radius:3px;padding:7px 13px;min-height:42px}button:hover{border-color:var(--red);color:var(--red)}:focus-visible{outline:3px solid var(--gold);outline-offset:4px}[hidden]{display:none!important}.skip-link{position:fixed;top:-100px;left:16px;background:var(--ink);color:var(--paper);z-index:30;padding:10px}.skip-link:focus{top:12px}
.layout{display:grid;grid-template-columns:230px minmax(0,1fr);max-width:1530px;margin:auto;min-height:100vh}.sidebar{position:sticky;top:0;height:100vh;padding:32px 24px 24px;border-right:1px solid var(--line);display:flex;flex-direction:column;gap:25px}.brand{font:700 21px var(--serif);letter-spacing:.1em}.brand small{display:block;font:11px var(--mono);letter-spacing:.1em;color:var(--muted);margin-top:9px}.side-index{display:flex;flex-direction:column;gap:3px}.side-index a{color:var(--muted);text-decoration:none;padding:9px 8px;font-size:13px;border-left:2px solid transparent}.side-index a.active{color:var(--red);border-left-color:var(--red);background:var(--soft)}.side-index b{display:inline-block;width:27px;font:11px var(--mono);opacity:.7}.side-bottom{margin-top:auto;color:var(--muted);font-size:11px}.side-bottom p{margin:8px 0}.actions{display:flex;gap:7px;flex-wrap:wrap}.actions button{font-size:12px;padding:5px 9px}.main{min-width:0;padding:48px clamp(24px,4vw,70px) 30px}.eyebrow{font:11px var(--mono);letter-spacing:.17em;color:var(--red);text-transform:uppercase}.hero{position:relative;overflow:hidden;border-bottom:2px solid var(--ink);padding:12px 0 30px}.hero-top{display:flex;justify-content:space-between;gap:16px;font-size:11px;color:var(--muted);position:relative;z-index:1}.hero h1{font:700 clamp(62px,7.5vw,110px)/1.08 var(--serif);letter-spacing:.01em;margin:32px 0 20px}.hero h1 span{display:block;font:400 clamp(22px,2.9vw,36px)/1.45 var(--serif);letter-spacing:.09em;margin-top:13px}.hero p{max-width:610px;color:var(--muted);font-size:15px;margin:16px 0}.seal{position:absolute;right:-35px;top:49px;width:270px;height:270px;border:1px solid var(--red);border-radius:50%;opacity:.15;transform:rotate(-18deg);pointer-events:none}.seal:before,.seal:after{content:"";position:absolute;border:1px solid var(--red);inset:24px;border-radius:50%}.seal:after{inset:51px;border-radius:0;transform:rotate(45deg)}.seal i{position:absolute;inset:93px;background:var(--red);border-radius:50%}.hero-stat{display:flex;gap:30px;flex-wrap:wrap;padding-top:15px}.hero-stat div{font-size:11px;color:var(--muted)}.hero-stat strong{font:400 30px var(--serif);color:var(--ink);margin-right:5px}.notice{border-left:3px solid var(--red);padding:12px 17px;background:var(--soft);margin:24px 0;font-size:13px}.notice strong{color:var(--red)}.notice p{margin:4px 0}.notice a{white-space:normal}
.quick{padding:24px 0 27px;border-bottom:1px solid var(--line)}.quick-heading{font:600 18px var(--serif);margin:0 0 19px}.quick-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.quick-item{border-top:1px solid var(--red);padding-top:10px;min-width:0}.quick-item em{font:10px var(--mono);color:var(--red);display:block;margin-bottom:5px}.quick-item a{font-size:16px;color:var(--ink);font-weight:600;text-decoration:none}.quick-item p{font-size:12px;color:var(--muted);margin:7px 0}.flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));margin-top:22px;border:1px solid var(--line);padding:14px 10px}.flow div{position:relative;padding:0 15px;font-size:12px}.flow div:not(:last-child):after{content:"→";position:absolute;right:-4px;top:4px;color:var(--red)}.flow b{font-weight:600;display:block}.flow span{color:var(--muted);font-size:11px}.flow-caption{font-size:10px;color:var(--muted);margin:6px 0 0}
.controls{margin:34px 0 18px;padding:20px;background:var(--surface);border:1px solid var(--line)}.search-label{font-size:12px;font-weight:600;display:block;margin-bottom:8px}.search-row{position:relative}.search-row input{width:100%;background:var(--paper);border:1px solid var(--line);padding:11px 70px 11px 14px;border-radius:3px;min-height:48px}.search-row kbd{position:absolute;right:15px;top:12px;padding:1px 6px;border:1px solid var(--line);border-radius:3px;font:12px/1.6 var(--mono);color:var(--muted)}.filter-row{display:flex;flex-wrap:wrap;gap:12px;margin-top:15px;align-items:end}.filter-row label{display:flex;flex-direction:column;font-size:11px;color:var(--muted);gap:5px;flex:1;min-width:145px}.filter-row select{width:100%;min-height:40px;border:1px solid var(--line);border-radius:3px;background:var(--paper);padding:7px 9px}.filter-row button{font-size:12px}.toolbar{display:flex;gap:12px;justify-content:space-between;align-items:center;margin-top:15px;flex-wrap:wrap;font-size:12px}.toolbar span{color:var(--muted)}.toolbar .actions{gap:6px}.toolbar button{font-size:11px;min-height:34px;padding:5px 10px}.noscript{font-size:13px}.empty{padding:35px 20px;border:1px dashed var(--line);text-align:center}.empty p{color:var(--muted)}
.catalog-section{margin-top:40px;scroll-margin-top:24px}.section-heading{display:flex;align-items:baseline;gap:14px;border-bottom:2px solid var(--ink);padding-bottom:12px;margin-bottom:22px}.section-no{font:12px var(--mono);color:var(--red)}.section-heading h2{font:600 27px/1.3 var(--serif);margin:0}.section-heading p{margin:7px 0 0;font-size:12px;color:var(--muted)}.section-count{font:11px var(--mono);vertical-align:middle;border:1px solid var(--line);padding:3px 6px;border-radius:3px;margin-left:6px;color:var(--muted)}.entry-group{margin:25px 0}.group-heading{font:600 13px var(--sans);letter-spacing:.12em;color:var(--red);margin:0;padding:8px 0;border-bottom:1px solid var(--line)}.group-heading span{font:11px var(--mono);margin-left:7px;opacity:.6}.entry{border-bottom:1px solid var(--line);background:transparent;scroll-margin-top:25px}.entry[open]{background:var(--surface)}.entry:target{outline:2px solid var(--red);outline-offset:3px}.entry summary{cursor:pointer;list-style:none;display:grid;grid-template-columns:32px minmax(0,1fr) 20px;gap:10px;padding:20px 12px 20px 0}.entry summary::-webkit-details-marker{display:none}.entry summary:hover .entry-title{color:var(--red)}.entry-number{font:10px var(--mono);color:var(--muted);padding-top:5px;text-align:center}.summary-content{min-width:0}.entry-meta{display:flex;gap:7px 12px;flex-wrap:wrap;font-size:11px;color:var(--muted);align-items:center;line-height:1.5;margin-bottom:8px}.grade{font-size:10px;white-space:nowrap;border:1px solid var(--line);border-radius:2px;padding:2px 5px;color:var(--muted);font-weight:400;display:inline-block}.grade-A{color:var(--blue);border-color:var(--blue)}.grade-B{color:var(--gold)}.entry-title{font-size:17px;line-height:1.55;font-weight:600;display:block;margin-bottom:7px}.entry-lead{display:block;font-size:13px;line-height:1.85;color:var(--muted)}.expand-mark{color:var(--red);font-size:17px;padding-top:19px}.expand-mark:before{content:"＋"}.entry[open] .expand-mark:before{content:"−"}.entry-body{margin-left:42px;margin-right:35px;padding:0 0 20px;font-size:13px}.entry-body p{margin:0 0 13px;color:var(--ink);padding-left:12px;border-left:2px solid var(--line)}.tags{display:flex;gap:5px;flex-wrap:wrap;margin:8px 0}.tag{font-size:10px;background:var(--soft);padding:1px 7px;color:var(--muted);border-radius:3px}.citations{display:flex;gap:6px 15px;flex-wrap:wrap;font-size:11px;margin-top:10px}.citations a{display:inline-block;line-height:1.65}.permalink{display:inline-block;font-size:10px;color:var(--muted);margin-top:12px}
.reading-note{font-size:13px;margin:25px 0;color:var(--muted)}.reading-note b{color:var(--ink)}.table-wrap{overflow:auto;border:1px solid var(--line);background:var(--surface)}table{border-collapse:collapse;width:100%;font-size:12px;min-width:520px}th,td{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}thead th{font-weight:600;background:var(--soft);font-size:11px}tbody th{width:130px;font-weight:600}tbody td:nth-child(2){width:125px;color:var(--muted)}tbody tr:last-child th,tbody tr:last-child td{border-bottom:0}.coverage-state{font-size:11px}.evidence-key{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin-bottom:20px}.evidence-key p{font-size:12px;color:var(--muted);margin:7px 0}.source-row{border-bottom:1px solid var(--line);font-size:12px}.source-row summary{display:grid;grid-template-columns:27px minmax(0,1fr) 20px;gap:10px;padding:14px 5px;list-style:none;cursor:pointer}.source-row summary::-webkit-details-marker{display:none}.source-num{font:10px var(--mono);color:var(--muted);padding-top:5px}.source-body{padding:0 20px 18px 42px}.source-body p{color:var(--muted);margin:0 0 8px}.source-domain{margin-left:12px;color:var(--muted);font:10px var(--mono);overflow-wrap:anywhere}.source-backlinks{display:flex;gap:5px 12px;flex-wrap:wrap;margin-top:10px}.source-backlinks a{font-size:10px;color:var(--muted)}.pending{background:var(--soft);padding:20px 22px;border-top:2px solid var(--gold);margin:25px 0}.pending h3{font:600 17px var(--serif);margin:0 0 12px}.pending ul{margin:0;padding-left:19px;font-size:12px;color:var(--muted)}.pending li{margin:8px 0}.footer{border-top:1px solid var(--line);padding:20px 0;margin-top:35px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:10px;color:var(--muted)}.backtop{position:fixed;bottom:18px;right:18px;z-index:4;background:var(--ink);color:var(--paper);text-decoration:none;border-radius:3px;padding:8px 14px;font-size:12px;box-shadow:0 2px 8px #0002}
@media(min-width:1100px){.hero p{max-width:65%}}
@media(max-width:1050px){.layout{grid-template-columns:190px minmax(0,1fr)}.sidebar{padding:28px 15px}.main{padding:34px 25px}.seal{width:215px;height:215px;top:74px}.hero h1{font-size:68px}.hero-stat{gap:17px}.quick-grid{gap:14px}.flow div{padding:0 8px}}
@media(max-width:760px){html{scroll-padding-top:88px}.layout{display:block}.sidebar{height:auto;position:sticky;top:0;z-index:10;padding:10px 16px 0;background:var(--paper);border-right:0;border-bottom:1px solid var(--line);gap:5px}.brand{font-size:15px;display:flex;align-items:center;justify-content:space-between}.brand small{display:none}.brand:after{content:"ORIGINAL NOVEL INDEX";font:9px var(--mono);color:var(--muted);letter-spacing:.05em}.side-index{flex-direction:row;overflow-x:auto;gap:8px;scrollbar-width:thin;padding-bottom:5px}.side-index a{flex:0 0 auto;padding:7px 3px;border-left:0;border-bottom:2px solid transparent;font-size:11px}.side-index a.active{border-left:0;border-bottom-color:var(--red);background:none}.side-index b{width:auto;margin-right:5px;font-size:9px}.side-bottom{display:none}.main{padding:25px 18px 25px}.hero-top{font-size:9px;gap:10px}.hero h1{font-size:64px;margin-top:28px}.hero h1 span{font-size:23px;letter-spacing:.04em}.hero p{font-size:13px;max-width:100%}.seal{width:180px;height:180px;top:78px;right:-55px;opacity:.1}.hero-stat{gap:19px}.hero-stat strong{font-size:25px}.hero-stat div{font-size:10px}.notice{padding:11px 13px;font-size:12px}.quick-grid{grid-template-columns:1fr;gap:15px}.quick-item{display:grid;grid-template-columns:44px minmax(0,1fr);gap:1px 8px}.quick-item em{grid-row:span 2;margin-top:5px}.quick-item a{font-size:15px}.quick-item p{margin:3px 0 0;grid-column:2}.flow{grid-template-columns:1fr;padding:5px 14px}.flow div{padding:9px 0;display:grid;grid-template-columns:115px minmax(0,1fr);border-bottom:1px solid var(--line)}.flow div:last-child{border:0}.flow div:not(:last-child):after{display:none}.controls{padding:14px;margin-top:27px}.filter-row{gap:10px}.filter-row label{min-width:120px}.filter-row label:last-of-type{flex-basis:100%}.section-heading h2{font-size:23px}.section-heading{gap:10px}.catalog-section{margin-top:30px;scroll-margin-top:85px}.entry{scroll-margin-top:88px}.entry summary{grid-template-columns:22px minmax(0,1fr) 14px;gap:7px;padding:16px 3px 16px 0}.entry-meta{font-size:10px;gap:5px}.entry-title{font-size:15px}.entry-lead{font-size:12px}.entry-body{margin-left:29px;margin-right:12px;font-size:12px}.expand-mark{font-size:15px}.evidence-key{grid-template-columns:1fr;gap:9px}.evidence-key p{margin:3px 0}.source-row summary{grid-template-columns:22px minmax(0,1fr) 14px;gap:6px}.source-body{padding-left:29px}.source-domain{display:block;margin-left:0;margin-top:5px}.backtop{bottom:12px;right:12px}.pending{padding:17px}.footer{padding-bottom:35px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
@media print{html{scroll-padding:0;scroll-behavior:auto}body{font-size:10pt;background:#fff;color:#111}.layout{display:block}.sidebar,.controls,.backtop,.permalink,.expand-mark,.seal{display:none!important}.main{padding:0}.hero h1{font-size:38pt}.hero h1 span{font-size:18pt}.hero-stat strong{font-size:19pt}.hero p{max-width:100%}.entry summary{padding:10px 0}.entry-body{padding-bottom:10px}.entry-title{font-size:11pt}.entry-lead,.entry-body{font-size:9pt}.entry-meta,.grade,.tag,.citations{font-size:8pt}.entry{break-inside:avoid;background:#fff!important}.section-heading{break-after:avoid}.table-wrap{overflow:visible}table{min-width:0;font-size:8pt}.quick-grid{grid-template-columns:repeat(3,1fr)}.flow{grid-template-columns:repeat(5,1fr)}.source-row{break-inside:avoid}.catalog-section{margin-top:22px}.notice,.pending{background:#f4f4f4}.footer{font-size:8pt}a{color:#333}#scope,#sources{break-before:page}}
</style></head><body><a class="skip-link" href="#content">跳到正文</a><div class="layout"><aside class="sidebar" aria-label="页面目录"><div class="brand">爆裂资料室<small>KONOSUBA / FIELD NOTES</small></div><nav class="side-index"><a href="#overview" class="active"><b>00</b>阅读起点</a><a href="#section-0"><b>01</b>设定速查</a><a href="#section-1"><b>02</b>剧情索引</a><a href="#section-2"><b>03</b>人物与道具</a><a href="#section-3"><b>04</b>常见误区</a><a href="#scope"><b>05</b>卷册覆盖</a><a href="#sources"><b>06</b>来源与证据</a></nav><div class="side-bottom"><div class="actions"><button type="button" data-theme-button>切换暗色</button><button type="button" data-print>打印</button></div><p>本页离线可读<br>来源链接需联网访问</p><p>检索日期 · 2026.09.30<br>含正篇结局与外传剧透</p></div></aside>
<main class="main" id="content"><header class="hero" id="overview"><div class="hero-top"><span class="eyebrow">EXPLOSION / 原作研究索引</span><span>暁なつめ作品 · 资料整理</span></div><div class="seal" aria-hidden="true"><i></i></div><h1>爆裂魔法<span>设定、剧情与那一发之后</span></h1><p>从红魔乡的第一道光，到魔王城前的连续轰鸣。把分散在《素晴》轻小说中的条件、代价、成长与故事，整理成可查阅的卷章索引。</p><div class="hero-stat"><div><strong>{{SETTING_COUNT}}</strong>设定条目</div><div><strong>{{PLOT_COUNT}}</strong>剧情条目</div><div><strong>{{SOURCE_COUNT}}</strong>来源入口</div><div><strong>17</strong>正篇卷册定位</div></div></header>
<div class="notice"><strong>完整剧透 · 以正式出版轻小说为主体</strong><p>涵盖正篇1—17、《爆焰》与《续·爆焰》，并补入授权外传、特典及《寄道》至2026年第4集的可核对内容。<b>这是尽量广泛的主题索引，未对全部出版物逐页穷尽校勘。</b>每条区分官方正文、非官方译文与二手证据，缺口见<a href="#scope">卷册覆盖</a>。</p></div>
<section class="quick" aria-label="三条阅读线索"><h2 class="quick-heading">先抓住三个关键点</h2><div class="quick-grid"><div class="quick-item"><em>01 / MP</em><a href="#s-once">一天一发，来自魔力预算</a><p>外部供魔能突破；施放次数与行动恢复分开看。</p></div><div class="quick-item"><em>02 / SKILL</em><a href="#s-choice">只学爆裂，是惠惠的选择</a><p>天赋、技能点与个人坚持共同塑造专精。</p></div><div class="quick-item"><em>03 / STORY</em><a href="#p-17-kazuma">决战一发，和真亲自施放</a><p>日常陪练的经验，最终成为决战的答案。</p></div></div><div class="flow" aria-label="施法条件示意"><div><b>习得</b><span>技能点与学习</span></div><div><b>准备魔力</b><span>自身／供魔／矿石</span></div><div><b>控制</b><span>咏唱、熟练与法杖</span></div><div><b>释放</b><span>爆心、冲击与地形</span></div><div><b>恢复／支援</b><span>行动与下一发分开</span></div></div><p class="flow-caption">概念关系示意，非原作数值公式。具体条件见下方带出处的条目。</p></section>
<form class="controls" id="filters" role="search" aria-label="搜索资料条目"><label class="search-label" for="search">搜索 {{TOTAL}} 条资料 <span style="font-weight:400;color:var(--muted)">· 标题、说明、日文名、卷章、标签</span></label><div class="search-row"><input type="search" id="search" placeholder="试试：无咏唱 / 沃尔巴克 / 魔力矿石 / 正篇17" autocomplete="off"><kbd aria-hidden="true">/</kbd></div><div class="filter-row"><label>内容<select id="category"><option value="">全部内容</option>{{CATEGORY_OPTIONS}}</select></label><label>系列<select id="series"><option value="">全部系列</option>{{SERIES_OPTIONS}}</select></label><label>证据<select id="grade"><option value="">全部证据</option><option value="A">官方日文正文</option><option value="B">非官方译文核对</option><option value="C">官方简介／二手索引</option></select></label><button type="reset">重置筛选</button></div><div class="toolbar"><span id="result-count" aria-live="polite" aria-atomic="true">共 {{TOTAL}} 条资料</span><div class="actions"><button type="button" id="expand-all">展开结果与出处</button><button type="button" id="collapse-all">收起结果</button><button type="button" data-theme-button>切换暗色</button><button type="button" data-print>打印当前结果</button></div></div></form><noscript><p class="noscript">JavaScript未启用：全部资料仍可阅读，点击条目展开来源；可用浏览器Ctrl+F查找。</p></noscript><div class="empty" id="empty" hidden><b>没有找到匹配条目</b><p>可尝试人物别名、减少关键词，或重置筛选。</p><button type="button" id="empty-reset">显示全部资料</button></div><div id="catalog">{{SECTIONS}}</div>
<section class="catalog-section" id="scope" aria-labelledby="scope-heading"><header class="section-heading"><span class="section-no">05</span><div><h2 id="scope-heading">卷册覆盖与未核验范围</h2><p>‘已定位重点卷章’不等于该卷每次提及都已逐句收录。</p></div></header><p class="reading-note"><b>如何使用：</b>要找一场战斗，先查剧情索引；要核对机制，优先点开官方正文条目。这里的卷号始终指轻小说，漫画第17卷不等于小说第17卷。各语言译名可能不同，保留日文或英文名便于回查。</p><div class="table-wrap" tabindex="0" role="region" aria-label="卷册覆盖表，可横向滚动"><table><thead><tr><th scope="col">作品</th><th scope="col">核对进度</th><th scope="col">本页覆盖／边界</th></tr></thead><tbody>{{COVERAGE}}</tbody></table></div><div class="pending"><h3>仍需原文或实体书进一步核验的项目</h3><ul><li>全部日常施放次数、每段咒文及每次伤害，未做逐页穷尽统计；正篇12、14的部分情节目前证据较弱。</li><li>《寄道》4剩余篇章、达斯特外传其余卷、未公开翻译的店铺／杂志／BD特典，不能宣布“没有爆裂相关内容”。</li><li>固定学习点数（常见索引称50）、MP数值、最大射程、半径、明确恢复时间、无咏唱伤害倍率，本次未取得足够官方正文证据，未填写成确定规则。</li><li>网络所称“惠惠必然强于维兹”“逗之助自动补魔”“矿石连发必有固定鼻血阈值”，缺乏足够统一证据，不据此建立设定。</li><li>长篇动画咒文、早期Web版、漫画追加对白、游戏联动与TRPG规则，需分别标版本；不要直接混进小说的能力条目。</li></ul></div></section>
<section class="catalog-section" id="sources" aria-labelledby="sources-heading"><header class="section-heading"><span class="section-no">06</span><div><h2 id="sources-heading">来源与证据</h2><p>{{SOURCE_COUNT}} 个入口 · 每条来源可展开查看用途及所关联的资料条目。</p></div></header><div class="evidence-key"><div><span class="grade grade-A">A · 官方正文</span><p>角川官方发布的日文小说段落，可直接核对措辞与上下文。</p></div><div><span class="grade grade-B">B · 非官方译文核对</span><p>读到公开英译中的相关段落并定位卷章，尚未与授权日文全卷逐页校勘。</p></div><div><span class="grade grade-C">C · 简介／二手索引</span><p>包括官方出版简介与读者Wiki。每个来源另写性质；不能替代正文细节。</p></div></div><p class="reading-note">本页采用原创中文概括，未转载整章小说或完整长咒文。来源中的正文与评论区分开使用；作者、译者猜测不作为已证设定。中文篇名为便于查阅的工作译名，正式中文版本可能采用其他译法。</p>{{SOURCES}}</section><footer class="footer"><span>素晴 · 爆裂魔法资料索引 / 2026.09.30</span><span>自包含HTML · 无外部字体或脚本 · 联网仅用于打开来源</span></footer></main></div><a class="backtop" href="#overview" aria-label="回到页面起点">↑ 顶部</a>
<script>
(()=>{'use strict';
const $=s=>document.querySelector(s),$$=s=>Array.from(document.querySelectorAll(s));
const entries=$$('.entry'),sections=$$('.catalog-section[data-category]'),form=$('#filters');
const inputs=['search','category','series','grade'].map(id=>$('#'+id));
let filtering=false;
const normalize=s=>s.toLocaleLowerCase().normalize('NFKC').replace(/\s+/g,' ').trim();
const visible=()=>entries.filter(e=>!e.hidden);
const apply=()=>{const terms=normalize(inputs[0].value).split(' ').filter(Boolean),cat=inputs[1].value,series=inputs[2].value,grade=inputs[3].value;
 const nextFiltering=Boolean(terms.length||cat||series||grade);
 if(nextFiltering&&!filtering)entries.forEach(e=>e.dataset.beforeFilter=e.open?'1':'0');
 for(const e of entries){const match=(!cat||e.closest('section').dataset.category===cat)&&(!series||e.dataset.series===series)&&(!grade||e.dataset.grade===grade)&&terms.every(t=>normalize(e.dataset.search).includes(t));e.hidden=!match;if(terms.length&&match)e.open=true;else if(!nextFiltering&&filtering)e.open=e.dataset.beforeFilter==='1';}
 filtering=nextFiltering;
 for(const s of sections){const groups=Array.from(s.querySelectorAll('.entry-group'));for(const g of groups)g.hidden=!Array.from(g.querySelectorAll('.entry')).some(e=>!e.hidden);const count=s.querySelectorAll('.entry:not([hidden])').length;s.hidden=count===0;s.querySelector('.section-count').textContent=count;}
 const count=visible().length;$('#result-count').textContent=nextFiltering?`找到 ${count} / ${entries.length} 条 · 卷册表与来源仍完整保留`:`共 ${entries.length} 条资料`;$('#empty').hidden=count!==0;
};
form.addEventListener('submit',e=>e.preventDefault());inputs.forEach(el=>el.addEventListener(el.type==='search'?'input':'change',apply));
form.addEventListener('reset',()=>setTimeout(apply,0));$('#empty-reset').addEventListener('click',()=>form.reset());
$('#expand-all').addEventListener('click',()=>visible().forEach(e=>e.open=true));$('#collapse-all').addEventListener('click',()=>visible().forEach(e=>e.open=false));
document.addEventListener('keydown',e=>{if(e.key==='/'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)){e.preventDefault();inputs[0].focus();}if(e.key==='Escape'&&document.activeElement===inputs[0]){inputs[0].value='';apply();}});
const themeButtons=$$('[data-theme-button]');let stored;try{stored=localStorage.getItem('explosion-reference-theme');}catch{}
const theme=val=>{document.documentElement.dataset.theme=val;themeButtons.forEach(b=>{b.textContent=val==='dark'?'切换浅色':'切换暗色';b.setAttribute('aria-pressed',val==='dark'?'true':'false');});};
theme(stored==='dark'?'dark':'light');themeButtons.forEach(b=>b.addEventListener('click',()=>{const val=document.documentElement.dataset.theme==='dark'?'light':'dark';theme(val);try{localStorage.setItem('explosion-reference-theme',val);}catch{}}));
let printState=[];window.addEventListener('beforeprint',()=>{if(printState.length)return;printState=$$('details').map(d=>[d,d.open]);$$('details').filter(d=>!d.hidden).forEach(d=>d.open=true);});window.addEventListener('afterprint',()=>{printState.forEach(([d,o])=>d.open=o);printState=[];});$$('[data-print]').forEach(b=>b.addEventListener('click',()=>window.print()));
const revealHash=()=>{let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}const el=document.getElementById(id);if(!el)return;if(el.classList.contains('entry')){if(el.hidden){form.reset();setTimeout(()=>{el.open=true;el.scrollIntoView();},10);}else{el.open=true;requestAnimationFrame(()=>el.scrollIntoView());}}else if(el.tagName==='DETAILS')el.open=true;};window.addEventListener('hashchange',revealHash);revealHash();
const navLinks=$$('.side-index a'),tracked=$$('#overview,.catalog-section');
if('IntersectionObserver'in window){const observer=new IntersectionObserver(records=>{const hit=records.filter(r=>r.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top)[0];if(hit)navLinks.forEach(a=>{const active=a.getAttribute('href')==='#'+hit.target.id;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});},{rootMargin:'-8% 0px -70% 0px',threshold:0});tracked.forEach(s=>observer.observe(s));}
apply();
})();
</script></body></html>'''

if __name__ == "__main__":
    build()
