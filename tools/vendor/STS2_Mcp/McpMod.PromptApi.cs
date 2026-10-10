using System;
using System.Net;
using System.Text.Json;

namespace KarenSTS2MCP;

public static partial class McpMod
{
    // Available before a run and in either game mode. Local modal interaction
    // must not go through the singleplayer/multiplayer gameplay guards.
    private static void HandleUiPrompt(HttpListenerRequest request, HttpListenerResponse response)
    {
        try
        {
            if (request.HttpMethod == "GET")
            {
                SendJson(response, RunOnMainThread(BuildUiPromptState).GetAwaiter().GetResult());
                return;
            }
            if (request.HttpMethod != "POST")
            {
                SendError(response, 405, "Method not allowed");
                return;
            }
            using var document = JsonDocument.Parse(request.InputStream);
            var body = document.RootElement;
            if (body.ValueKind != JsonValueKind.Object ||
                !body.TryGetProperty("option", out var option) || option.ValueKind != JsonValueKind.String ||
                string.IsNullOrWhiteSpace(option.GetString()))
            {
                SendError(response, 400, "Missing non-empty 'option' string");
                return;
            }
            string? promptId = null;
            if (body.TryGetProperty("prompt_id", out var id))
            {
                if (id.ValueKind != JsonValueKind.String)
                {
                    SendError(response, 400, "'prompt_id' must be a string");
                    return;
                }
                promptId = id.GetString();
            }
            SendJson(response, RunOnMainThread(() => ExecuteUiPrompt(option.GetString()!, promptId)).GetAwaiter().GetResult());
        }
        catch (JsonException) { SendError(response, 400, "Invalid JSON"); }
        catch (Exception ex) { SendError(response, 500, $"UI prompt operation failed: {ex.Message}"); }
    }
}
