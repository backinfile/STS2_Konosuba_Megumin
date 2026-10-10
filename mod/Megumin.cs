using BaseLib.Abstracts;
using Godot;
using MegaCrit.Sts2.Core.Animation;
using MegaCrit.Sts2.Core.Bindings.MegaSpine;
using MegaCrit.Sts2.Core.Entities.Characters;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace MeguminMod;

// Deliberately uses complete vanilla content pools until the gameplay design is final.
// This includes rewards, shops, potions and the starter-relic upgrade event.
public sealed class Megumin : PlaceholderCharacterModel
{
    private static Ironclad TestContent => ModelDb.Character<Ironclad>();
    public override Color NameColor => new("CB493B");
    public override Color EnergyLabelOutlineColor => new("77342A");
    public override CharacterGender Gender => CharacterGender.Feminine;
    public override int StartingHp => 70;
    public override CardPoolModel CardPool => TestContent.CardPool;
    public override RelicPoolModel RelicPool => TestContent.RelicPool;
    public override PotionPoolModel PotionPool => TestContent.PotionPool;
    public override IEnumerable<CardModel> StartingDeck => TestContent.StartingDeck;
    public override IReadOnlyList<RelicModel> StartingRelics => TestContent.StartingRelics;
    public override List<(string, string)> Localization => new CharacterLoc(
        "惠惠（测试）", "惠惠", "红魔族的大魔法师。NL当前使用原版卡牌与遗物作为测试数据，用于验证动画和游戏接入。",
        "她", "她", "她的", "她的", "爆裂魔法", "轮到你了！", "魔力耗尽了……", "还没结束！", "测试用金币。",
        "惠惠测试卡组", "原版战士卡牌，正式玩法尚未接入。", ("unlockText", "测试角色默认解锁。"));
    public override NCreatureVisuals CreateCustomVisuals() => MeguminVisuals.Create();
    public override CreatureAnimator? SetupCustomAnimationStates(MegaSprite controller) =>
        SetupAnimationState(controller, "idle_loop", deadName: "dead", hitName: "hit",
            attackName: "attack_short", castName: "cast_short", relaxedName: "relaxed_loop");
}
