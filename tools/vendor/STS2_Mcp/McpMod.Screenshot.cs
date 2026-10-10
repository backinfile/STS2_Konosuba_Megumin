using System;
using System.Net;
using Godot;

namespace KarenSTS2MCP;

public static partial class McpMod
{
    private static void HandleGetScreenshot(HttpListenerResponse response)
    {
        try
        {
            // Viewport textures belong to Godot's render thread. Capture and encode
            // on the game thread; only write the finished PNG on the HTTP thread.
            byte[] png = RunOnMainThread(CaptureScreenshot).GetAwaiter().GetResult();
            response.ContentType = "image/png";
            response.Headers["Cache-Control"] = "no-store";
            response.ContentLength64 = png.Length;
            response.OutputStream.Write(png, 0, png.Length);
            response.Close();
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[Karen STS2 MCP] Screenshot failed: {ex}");
            SendError(response, 500, $"Screenshot failed: {ex.Message}");
        }
    }

    private static byte[] CaptureScreenshot()
    {
        var tree = Engine.GetMainLoop() as SceneTree
            ?? throw new InvalidOperationException("Game scene tree is unavailable");
        var texture = tree.Root?.GetTexture()
            ?? throw new InvalidOperationException("Game viewport texture is unavailable");
        using var image = texture.GetImage();
        if (image == null || image.IsEmpty())
            throw new InvalidOperationException("Game viewport image is empty");
        byte[] png = image.SavePngToBuffer();
        if (png.Length == 0)
            throw new InvalidOperationException("Could not encode game screenshot as PNG");
        return png;
    }
}
