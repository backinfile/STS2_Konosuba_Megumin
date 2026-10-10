using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Godot;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Nodes.Cards;
using MegaCrit.Sts2.Core.Nodes.Cards.Holders;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KarenSTS2MCP;

public static partial class McpMod
{
    private static NHandCardHolder? _hoverHolder;
    private static NCard? _hoverCard;

    private static Dictionary<string, object?> ExecuteHoverCard(Player player, Dictionary<string, JsonElement> data)
    {
        if (!CombatManager.Instance.IsInProgress || !IsPlayPhase(player))
            return Error("Card hover requires the player's combat play phase");
        if (CombatManager.Instance.PlayerActionsDisabled || !player.Creature.IsAlive)
            return Error("Player actions are currently disabled");
        var hand = player.PlayerCombatState?.Hand;
        var ui = NCombatRoom.Instance?.Ui?.Hand;
        if (hand == null || ui == null)
            return Error("No hand available");
        if (ui.InCardPlay || ui.CurrentMode != NPlayerHand.Mode.Play)
            return Error("Cannot hover during card play or card selection");
        if (!data.TryGetValue("card_index", out var indexValue) || indexValue.ValueKind != JsonValueKind.Number
            || !indexValue.TryGetInt32(out int index))
            return Error("card_index must be an integer");
        if (index < 0 || index >= hand.Cards.Count)
            return Error($"card_index {index} out of range (hand has {hand.Cards.Count} cards)");
        var card = hand.Cards[index];
        Creature? target = null;
        string? targetId = null;
        if (data.TryGetValue("target", out var targetValue) && targetValue.ValueKind != JsonValueKind.Null)
        {
            if (targetValue.ValueKind != JsonValueKind.String || string.IsNullOrWhiteSpace(targetValue.GetString()))
                return Error("target must be a non-empty enemy entity_id string or null");
            if (card.TargetType != TargetType.AnyEnemy)
                return Error("An explicit hover target is only supported for single-enemy cards; omit target for this card");
            targetId = targetValue.GetString();
            var state = player.Creature.CombatState;
            target = state == null ? null : ResolveTarget(state, targetId!);
            if (target == null) return Error($"Target '{targetId}' not found among alive enemies");
        }
        // Match by model identity: the animated UI order need not match hand indices.
        var holder = ui.ActiveHolders.FirstOrDefault(h => h.CardNode?.Model == card);
        if (holder?.CardNode == null || holder.FocusMode == Control.FocusModeEnum.None)
            return Error("Card UI is not ready for hover");

        ClearCardHover();
        holder.GrabFocus();
        if (!holder.HasFocus()) return Error("Could not focus card UI");
        _hoverHolder = holder;
        _hoverCard = holder.CardNode;
        holder.HolderUnfocused += OnHoveredCardUnfocused;
        holder.TreeExiting += OnHoveredCardExiting;
        _hoverCard.SetPreviewTarget(target);
        return new Dictionary<string, object?>
        {
            ["status"] = "ok", ["card_index"] = index, ["target"] = targetId,
            ["message"] = $"Hovering '{card.Title}'", ["played"] = false
        };
    }

    private static void OnHoveredCardUnfocused(NHandCardHolder holder) => ClearCardHover(releaseFocus: false);
    private static void OnHoveredCardExiting() => ClearCardHover(releaseFocus: false);

    private static void ClearCardHover(bool releaseFocus = true)
    {
        var holder = _hoverHolder;
        var card = _hoverCard;
        _hoverHolder = null;
        _hoverCard = null;
        if (GodotObject.IsInstanceValid(holder))
        {
            holder!.HolderUnfocused -= OnHoveredCardUnfocused;
            holder.TreeExiting -= OnHoveredCardExiting;
            if (releaseFocus && holder.HasFocus()) holder.ReleaseFocus();
        }
        if (GodotObject.IsInstanceValid(card) && card!.IsInsideTree()) card.SetPreviewTarget(null);
    }

    private static Dictionary<string, object?> ExecuteUnhoverCard()
    {
        ClearCardHover();
        return new Dictionary<string, object?> { ["status"] = "ok", ["message"] = "Cleared card hover" };
    }
}
