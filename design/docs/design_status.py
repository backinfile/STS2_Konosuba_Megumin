"""Add a visible current-design link to older generated design documents."""
from html import escape

NOTICES = {'legacy-core': ('上一版核心与历次候选', '当前为玩家Buff爆裂狂、3费保留消耗的爆裂，回合末按本人吟唱期间技能数加卡牌提供的额外增伤造成一次群伤。威力已降为爆裂内的小配套，不再设关键词；卡面直接写“下一次爆裂魔法造成的伤害提高X点”，结算后清除已用增伤。旧0费积蓄、全部出牌计数与卡组仅供历史追溯。宣言已改为悬挂后连续3张技能触发卡面后续效果，回合结束进度归零；本页格挡条件仅为历史。'), 'other-research': ('机制探索资料', '当前为玩家Buff爆裂狂、3费保留消耗的爆裂，回合末按本人吟唱期间技能数加卡牌提供的额外增伤造成一次群伤。威力已降为爆裂内的小配套，不再设关键词；卡面直接写“下一次爆裂魔法造成的伤害提高X点”，结算后清除已用增伤。局外技能点、爆裂鉴赏及其他候选以当前总览为准。'), 'might-rework': ('具体卡牌待重做', '当前为玩家Buff爆裂狂、3费保留消耗的爆裂，回合末按本人吟唱期间技能数加卡牌提供的额外增伤造成一次群伤。威力已降为爆裂内的小配套，不再设关键词；卡面直接写“下一次爆裂魔法造成的伤害提高X点”，结算后清除已用增伤。旧11张牌、广义增伤、常驻／临时划分、每牌+1威力及多段算例均为历史。'), 'old-damage': ('旧版伤害成长方案', '当前为玩家Buff爆裂狂、3费保留消耗的爆裂，回合末按本人吟唱期间技能数加卡牌提供的额外增伤造成一次群伤。威力已降为爆裂内的小配套，不再设关键词；卡面直接写“下一次爆裂魔法造成的伤害提高X点”，结算后清除已用增伤。相似的单段公式不恢复本页旧牌数口径或5张旧配套。'), 'nonattack-reference': ('已停止的广义威力研究', '当前为玩家Buff爆裂狂、3费保留消耗的爆裂，回合末按本人吟唱期间技能数加卡牌提供的额外增伤造成一次群伤。威力已降为爆裂内的小配套，不再设关键词；卡面直接写“下一次爆裂魔法造成的伤害提高X点”，结算后清除已用增伤。非攻击伤害流已停止，下文仅保留来源研究和旧评估。'), 'nonattack-retired': ('非攻击伤害流：已停止探索', '当前为玩家Buff爆裂狂、3费保留消耗的爆裂，回合末按本人吟唱期间技能数加卡牌提供的额外增伤造成一次群伤。威力已降为爆裂内的小配套，不再设关键词；卡面直接写“下一次爆裂魔法造成的伤害提高X点”，结算后清除已用增伤。本页8张候选与旧算例均不进入新版技能连打构筑。')}

def with_design_notice(page, key):
    title, text = NOTICES[key]
    notice = f'''<aside data-design-status="{escape(key)}" aria-label="文档状态" style="margin:0;padding:16px max(20px,calc((100vw - 1320px)/2));background:#eee0cf;border-bottom:2px solid #92332c;color:#392d25;font:14px/1.8 'Microsoft YaHei','Segoe UI',sans-serif"><b>{escape(title)}</b> · {escape(text)} <a style="color:#8d2824;font-weight:700" href="惠惠当前设计总览.html">打开当前设计总览 →</a></aside>'''
    return page.replace('<body>', '<body>'+notice, 1)
