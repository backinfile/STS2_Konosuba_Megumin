using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Godot;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Ftue;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;
using MegaCrit.Sts2.Core.Nodes.Screens.MainMenu;
using MegaCrit.Sts2.Core.Nodes.Screens.Timeline;

namespace KarenSTS2MCP;

public static partial class McpMod
{
    // State and dispatch use the same snapshot, so a prompt can never redirect a
    // click to another screen underneath it.
    private sealed record PromptOption(string Name, NClickableControl Button, bool Enabled);

    private sealed record UiPrompt(Node Owner, string Screen, string Message, string? Body,
        bool IsTutorial, List<PromptOption> Options)
    {
        public object? Page => GetInstanceFieldValue(Owner, "_currentPage");
        public string Id => $"{Owner.GetInstanceId()}:{Page}";

        public Dictionary<string, object?> ToState() => new()
        {
            ["status"] = "ok",
            ["active"] = true,
            ["blocking"] = true,
            ["state_type"] = "menu",
            ["menu_screen"] = Screen,
            ["prompt_id"] = Id,
            ["prompt_type"] = Owner.GetType().Name,
            ["is_tutorial"] = IsTutorial,
            ["message"] = Message,
            ["body"] = Body,
            ["current_page"] = Page,
            ["ready"] = Options.Any(option => option.Enabled),
            ["options"] = Options.Select(option => new Dictionary<string, object?>
            {
                ["name"] = option.Name,
                ["label"] = GetClickableControlLabel(option.Button),
                ["enabled"] = option.Enabled
            }).ToList()
        };
    }

    private static Node? GetOpenModalNode()
    {
        var modal = NModalContainer.Instance?.OpenModal as Node;
        return IsLiveNode(modal) ? modal : null;
    }

    private static bool IsControlVisibleOrActionable(NClickableControl? control) =>
        IsNodeVisible(control) && control!.IsEnabled;

    private static UiPrompt? FindVisiblePrompt(Node root)
    {
        var modal = GetOpenModalNode();
        // The modal owns input even while its animation hides/disables all buttons.
        if (modal != null) return DescribePrompt(modal, true);

        var disclaimer = FindAll<NEarlyAccessDisclaimer>(root).FirstOrDefault(IsNodeVisible);
        if (disclaimer != null) return DescribePrompt(disclaimer, false);
        var ftue = FindAll<NFtue>(root).FirstOrDefault(IsNodeVisible);
        if (ftue != null) return DescribePrompt(ftue, false);
        var timeline = FindAll<NTimelineTutorial>(root).FirstOrDefault(IsNodeVisible);
        if (timeline != null) return DescribePrompt(timeline, false);
        var popup = FindAll<NVerticalPopup>(root).FirstOrDefault(IsNodeVisible);
        if (popup != null) return DescribePrompt(popup, false);
        return null;
    }

    private static UiPrompt DescribePrompt(Node owner, bool isModal)
    {
        if (owner is NEarlyAccessDisclaimer)
        {
            var button = FindAll<NDisclaimerProceedButton>(owner).FirstOrDefault(IsNodeVisible);
            var options = new List<PromptOption>();
            if (button != null)
            {
                // CloseScreen starts a tween without disabling the button. Do not
                // restart that tween on retries while the screen is closing.
                options.Add(new("proceed", button,
                    IsControlVisibleOrActionable(button) && GetInstanceFieldValue(owner, "_tween") == null));
            }
            return new(owner, "early_access_disclaimer", "Early Access notice. Use proceed, then poll state.",
                ReadPromptText(owner, "%Description"), false, options);
        }

        if (owner is NAcceptTutorialsFtue)
        {
            var popup = GetInstanceFieldValue(owner, "_verticalPopup") as NVerticalPopup;
            var options = new List<PromptOption>();
            if (popup != null)
            {
                AddPromptButton(options, "no", popup.NoButton);
                AddPromptButton(options, "yes", popup.YesButton);
            }
            return new(owner, "tutorial_prompt", "Enable tutorials? Choose yes or no.",
                popup == null ? null : ReadPromptProperty(popup, "BodyLabel"), true, options);
        }

        if (owner is NFtue || owner is NTimelineTutorial)
        {
            var options = new List<PromptOption>();
            // Only known forward controls. An arbitrary button can be a previous
            // page arrow or the cannot-play tutorial's end-turn hitbox.
            foreach (var field in new[] { "_confirmButton", "_nextButton", "_advanceButton",
                         "_proceedButton", "_acknowledgeButton", "_rightArrowButton" })
            {
                if (GetInstanceFieldValue(owner, field) is not NClickableControl button) continue;
                AddPromptButton(options, "advance", button);
                AddPromptButton(options, "proceed", button);
                break;
            }
            // Ascension FTUEs wire their confirm node directly in _Ready instead
            // of keeping a field. Match the known control, never arbitrary buttons.
            if (options.Count == 0)
            {
                var confirm = owner.GetNodeOrNull<NClickableControl>("%FtueConfirmButton")
                    ?? FindAll<NFtueConfirmButton>(owner).FirstOrDefault();
                AddPromptButton(options, "advance", confirm);
                AddPromptButton(options, "proceed", confirm);
            }
            return new(owner, "tutorial", ReadPromptField(owner, "_header") ?? "Tutorial active. Advance one step, then poll state.",
                ReadPromptField(owner, "_description", "_bodyText", "_text"), true, options);
        }

        // NMultiplayerWarningPopup inherits NVerticalPopup but initializes an
        // embedded _verticalPopup instead of the inherited button properties.
        var vertical = GetInstanceFieldValue(owner, "_verticalPopup") as NVerticalPopup
            ?? owner as NVerticalPopup ?? FindAll<NVerticalPopup>(owner).FirstOrDefault(IsNodeVisible);
        var popupOptions = new List<PromptOption>();
        if (vertical != null)
        {
            AddPromptButton(popupOptions, "yes", vertical.YesButton);
            AddPromptButton(popupOptions, "no", vertical.NoButton);
        }
        else if (isModal)
        {
            foreach (var button in FindAll<NClickableControl>(owner).Where(IsNodeVisible))
            {
                var name = button is NPopupYesNoButton yesNo ? (yesNo.IsYes ? "yes" : "no")
                    : NormalizeMenuOptionName(GetClickableControlLabel(button)) ?? "option";
                if (popupOptions.Any(option => option.Name == name)) name += $"_{popupOptions.Count}";
                AddPromptButton(popupOptions, name, button);
            }
        }
        return new(owner, "popup", vertical == null ? "Blocking popup active. Select an advertised option."
            : ReadPromptProperty(vertical, "TitleLabel") ?? "Blocking popup active.",
            vertical == null ? ReadPromptText(owner, "%Description") : ReadPromptProperty(vertical, "BodyLabel"), false, popupOptions);
    }

    private static void AddPromptButton(List<PromptOption> options, string name, NClickableControl? button)
    {
        if (IsLiveNode(button))
            options.Add(new(name, button!, IsControlVisibleOrActionable(button)));
    }

    private static Dictionary<string, object?> BuildUiPromptState()
    {
        var root = (Engine.GetMainLoop() as SceneTree)?.Root;
        if (root == null) return Error("Cannot access scene tree");
        return FindVisiblePrompt(root)?.ToState() ?? new Dictionary<string, object?>
        {
            ["status"] = "ok", ["active"] = false, ["blocking"] = false
        };
    }

    private static Dictionary<string, object?>? BuildVisibleFtueState(Node root) => FindVisiblePrompt(root)?.ToState();
    private static bool IsAnyFtueVisible(Node root) => FindVisiblePrompt(root) != null;

    private static Dictionary<string, object?> ExecuteUiPrompt(string option, string? promptId = null)
    {
        var root = (Engine.GetMainLoop() as SceneTree)?.Root;
        if (root == null) return Error("Cannot access scene tree");
        var prompt = FindVisiblePrompt(root);
        if (prompt == null) return Error("No blocking prompt is active; read game state before continuing");
        return ExecuteUiPrompt(prompt, option, promptId);
    }

    private static Dictionary<string, object?> ExecuteUiPrompt(UiPrompt prompt, string option, string? promptId = null)
    {
        if (promptId != null && promptId != prompt.Id)
            return Error("Prompt changed; call get_ui_prompt and use its current prompt_id and options");
        option = option.Trim();
        if (prompt.Screen == "early_access_disclaimer" && option.Equals("advance", StringComparison.OrdinalIgnoreCase))
            option = "proceed";
        var selected = prompt.Options.FirstOrDefault(candidate => candidate.Name.Equals(option, StringComparison.OrdinalIgnoreCase));
        // Preserve previously advertised localized menu_select option IDs for popups.
        selected ??= prompt.Screen == "popup" ? prompt.Options.FirstOrDefault(candidate =>
            NormalizeMenuOptionName(GetClickableControlLabel(candidate.Button))?.Equals(option, StringComparison.OrdinalIgnoreCase) == true) : null;
        if (selected == null)
            return Error($"Unknown prompt option '{option}'. Use get_ui_prompt to read the available options");
        if (!selected.Enabled || !IsControlVisibleOrActionable(selected.Button))
            return Error($"Prompt option '{selected.Name}' is not ready; poll get_ui_prompt before retrying");
        var actedOnId = prompt.Id;
        selected.Button.ForceClick();
        return new Dictionary<string, object?>
        {
            ["status"] = "ok", ["prompt_id"] = actedOnId, ["option"] = selected.Name,
            ["message"] = "Advanced prompt one step. Poll state before the next action."
        };
    }

    private static string? ReadPromptField(Node owner, params string[] fields) =>
        fields.Select(field => GetNodeText(GetInstanceFieldValue(owner, field))).FirstOrDefault(text => !string.IsNullOrWhiteSpace(text));

    private static string? ReadPromptText(Node owner, string path) => GetNodeText(owner.GetNodeOrNull<Node>(path));

    private static string? ReadPromptProperty(Node owner, string name)
    {
        const System.Reflection.BindingFlags flags = System.Reflection.BindingFlags.Public |
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.DeclaredOnly;
        for (var type = owner.GetType(); type != null; type = type.BaseType)
        {
            var property = type.GetProperty(name, flags);
            if (property != null) return GetNodeText(property.GetValue(owner));
        }
        return null;
    }

    private static string? GetClickableControlLabel(NClickableControl button)
    {
        foreach (var field in new[] { "_label", "_textLabel", "_title", "_buttonLabel" })
        {
            var text = GetNodeText(GetInstanceFieldValue(button, field));
            if (!string.IsNullOrWhiteSpace(text)) return text;
        }
        return GetNodeText(button) ?? FindAll<Control>(button).Select(GetNodeText).FirstOrDefault(text => !string.IsNullOrWhiteSpace(text))
            ?? button.Name.ToString();
    }

    private static string? GetNodeText(object? node)
    {
        if (node == null) return null;
        foreach (var property in new[] { "Text", "BbcodeText" })
        {
            var text = SafeGetText(() => node.GetType().GetProperty(property)?.GetValue(node));
            if (!string.IsNullOrWhiteSpace(text)) return text;
        }
        return null;
    }

    private static string? NormalizeMenuOptionName(string? text)
    {
        if (string.IsNullOrWhiteSpace(text)) return null;
        var sb = new StringBuilder();
        foreach (var ch in StripRichTextTags(text).Trim().ToLowerInvariant())
        {
            if (char.IsLetterOrDigit(ch)) sb.Append(ch);
            else if (sb.Length > 0 && sb[^1] != '_') sb.Append('_');
        }
        var normalized = sb.ToString().Trim('_');
        return normalized.Length == 0 ? null : normalized;
    }
}
