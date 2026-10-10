using System;
using System.Collections.Generic;
using System.Net;
using Godot;

namespace KarenSTS2MCP;

public static partial class McpMod
{
    private static void HandleBackgroundGame(HttpListenerResponse response)
    {
        try
        {
            var result = RunOnMainThread(ExecuteBackgroundGame).GetAwaiter().GetResult();
            SendJson(response, result);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[Karen STS2 MCP] Background game failed: {ex}");
            SendError(response, 500, $"Background game failed: {ex.Message}");
        }
    }

    private static Dictionary<string, object?> ExecuteBackgroundGame()
    {
        var tree = Engine.GetMainLoop() as SceneTree
            ?? throw new InvalidOperationException("Game scene tree is unavailable");
        if (tree.Root == null)
            throw new InvalidOperationException("Game window is unavailable");
        DisplayServer.WindowSetMode(DisplayServer.WindowMode.Minimized);
        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = "Game window minimized",
            ["window_mode"] = "minimized"
        };
    }
}
