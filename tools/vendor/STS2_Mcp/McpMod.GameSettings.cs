using System;
using System.Collections.Generic;
using System.Net;
using System.Text.Json;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Audio.Debug;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Audio;
using MegaCrit.Sts2.Core.Platform;
using MegaCrit.Sts2.Core.Saves;

namespace KarenSTS2MCP;

public static partial class McpMod
{
    private sealed record GameSettingsRequest(
        bool? Fullscreen, bool? Muted, bool? SkipTutorial, bool? SkipFirstPrompt,
        int? WindowWidth, int? WindowHeight);

    private static GameSettingsRequest? _startupSettings;

    private static void LoadStartupSettings(JsonElement config)
    {
        if (TryParseGameSettings(config, out var settings, out var error))
            _startupSettings = settings is { Fullscreen: null, Muted: null, SkipTutorial: null,
                SkipFirstPrompt: null, WindowWidth: null, WindowHeight: null } ? null : settings;
        else
            GD.PrintErr($"[Karen STS2 MCP] Ignoring startup settings: {error}");
    }

    private static bool TryParseGameSettings(JsonElement data, out GameSettingsRequest settings, out string error)
    {
        settings = new(null, null, null, null, null, null);
        error = "";
        if (data.ValueKind != JsonValueKind.Object)
        {
            error = "Settings must be a JSON object";
            return false;
        }

        bool? ReadBool(string name)
        {
            if (!data.TryGetProperty(name, out var value)) return null;
            if (value.ValueKind == JsonValueKind.True) return true;
            if (value.ValueKind == JsonValueKind.False) return false;
            throw new ArgumentException($"'{name}' must be a boolean");
        }

        int? ReadInt(string name)
        {
            if (!data.TryGetProperty(name, out var value)) return null;
            if (value.ValueKind == JsonValueKind.Number && value.TryGetInt32(out int number)) return number;
            throw new ArgumentException($"'{name}' must be an integer");
        }

        try
        {
            settings = new(
                ReadBool("fullscreen"), ReadBool("muted"), ReadBool("skip_tutorial"),
                ReadBool("skip_first_prompt"), ReadInt("window_width"), ReadInt("window_height"));
            if (settings.WindowWidth.HasValue != settings.WindowHeight.HasValue)
                throw new ArgumentException("'window_width' and 'window_height' must be provided together");
            if (settings.WindowWidth is < 320 or > 7680 || settings.WindowHeight is < 240 or > 4320)
                throw new ArgumentException("Window size must be between 320x240 and 7680x4320");
            if (settings.Fullscreen == true && settings.WindowWidth.HasValue)
                throw new ArgumentException("Cannot set fullscreen and window size in the same request");
            return true;
        }
        catch (ArgumentException ex)
        {
            error = ex.Message;
            return false;
        }
    }

    private static Dictionary<string, object?> BuildSettingsState()
    {
        var save = SaveManager.Instance;
        if (save.SettingsSave == null || !save.IsProfileInitialized)
            return Error("Game settings are still loading");
        var settings = save.SettingsSave;
        var size = DisplayServer.WindowGetSize();
        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["fullscreen"] = settings.Fullscreen,
            ["muted"] = settings.VolumeMaster == 0f,
            ["volume_master"] = settings.VolumeMaster,
            ["skip_tutorial"] = !save.Progress.EnableFtues,
            ["skip_first_prompt"] = settings.SeenEaDisclaimer,
            ["window_width"] = size.X,
            ["window_height"] = size.Y,
            ["saved_window_width"] = settings.WindowSize.X,
            ["saved_window_height"] = settings.WindowSize.Y
        };
    }

    private static Dictionary<string, object?> ApplyGameSettings(GameSettingsRequest request)
    {
        var save = SaveManager.Instance;
        if (save.SettingsSave == null || !save.IsProfileInitialized || NGame.Instance == null)
            return Error("Game settings are still loading");
        if ((request.Fullscreen == false || request.WindowWidth.HasValue) &&
            PlatformUtil.GetSupportedWindowMode().ShouldForceFullscreen())
            return Error("This platform does not support windowed mode");

        var settings = save.SettingsSave;
        bool displayChanged = false;
        if (request.WindowWidth is int width && request.WindowHeight is int height)
        {
            settings.WindowSize = new Vector2I(width, height);
            settings.Fullscreen = false;
            displayChanged = true;
        }
        else if (request.Fullscreen is bool fullscreen)
        {
            settings.Fullscreen = fullscreen;
            displayChanged = true;
        }
        if (displayChanged)
            NGame.Instance.ApplyDisplaySettings();

        if (request.Muted is bool muted)
        {
            settings.VolumeMaster = muted ? 0f : 0.5f;
            NAudioManager.Instance?.SetMasterVol(settings.VolumeMaster);
            NDebugAudioManager.Instance?.SetMasterAudioVolume(settings.VolumeMaster);
        }
        if (request.SkipTutorial is bool skipTutorial)
        {
            save.SetFtuesEnabled(!skipTutorial);
            if (skipTutorial)
            {
                var tree = Engine.GetMainLoop() as SceneTree;
                if (tree?.Root != null && FindVisiblePrompt(tree.Root) is { Screen: "tutorial_prompt" } prompt)
                    ExecuteUiPrompt(prompt, "no");
            }
        }
        if (request.SkipFirstPrompt is bool skipFirstPrompt)
        {
            settings.SeenEaDisclaimer = skipFirstPrompt;
            if (skipFirstPrompt)
            {
                var tree = Engine.GetMainLoop() as SceneTree;
                if (tree?.Root != null && FindVisiblePrompt(tree.Root) is { Screen: "early_access_disclaimer" } prompt)
                    ExecuteUiPrompt(prompt, "proceed");
            }
        }
        save.SaveSettings();
        var result = BuildSettingsState();
        // Disabling future tutorials does not complete callbacks awaited by an
        // already-open tutorial. Expose it so callers can advance it normally.
        result["ui_prompt"] = BuildUiPromptState();
        return result;
    }

    private static void HandleGetSettings(HttpListenerResponse response)
    {
        try { SendJson(response, RunOnMainThread(BuildSettingsState).GetAwaiter().GetResult()); }
        catch (Exception ex) { SendError(response, 500, $"Read settings failed: {ex.Message}"); }
    }

    private static void HandlePostSettings(HttpListenerRequest request, HttpListenerResponse response)
    {
        try
        {
            using var body = JsonDocument.Parse(request.InputStream);
            if (!TryParseGameSettings(body.RootElement, out var settings, out var error))
            {
                SendError(response, 400, error);
                return;
            }
            SendJson(response, RunOnMainThread(() => ApplyGameSettings(settings)).GetAwaiter().GetResult());
        }
        catch (JsonException) { SendError(response, 400, "Invalid JSON"); }
        catch (Exception ex) { SendError(response, 500, $"Set settings failed: {ex.Message}"); }
    }

    // The game loads account settings before Mod initializers run. Apply startup
    // overrides just before it reads them for display initialization.
    [HarmonyPatch(typeof(NGame), "InitializeGraphicsPreferences")]
    private static class StartupAccountSettingsPatch
    {
        private static void Prefix()
        {
            if (_startupSettings is not { } request) return;
            var save = SaveManager.Instance;
            var settings = save.SettingsSave;
            if (request.WindowWidth is int width && request.WindowHeight is int height)
            {
                settings.WindowSize = new Vector2I(width, height);
                settings.Fullscreen = false;
            }
            else if (request.Fullscreen is bool fullscreen)
                settings.Fullscreen = fullscreen;
            if (request.Muted is bool muted)
            {
                settings.VolumeMaster = muted ? 0f : 0.5f;
                NAudioManager.Instance?.SetMasterVol(settings.VolumeMaster);
                NDebugAudioManager.Instance?.SetMasterAudioVolume(settings.VolumeMaster);
            }
            if (request.SkipFirstPrompt is bool skipFirstPrompt)
                settings.SeenEaDisclaimer = skipFirstPrompt;
            save.SaveSettings();
        }
    }

    // Progress is profile-scoped and is loaded again when switching profiles.
    [HarmonyPatch(typeof(SaveManager), nameof(SaveManager.InitProgressData))]
    private static class StartupProfileSettingsPatch
    {
        private static void Postfix()
        {
            if (_startupSettings?.SkipTutorial is bool skipTutorial)
                SaveManager.Instance.SetFtuesEnabled(!skipTutorial);
        }
    }
}
