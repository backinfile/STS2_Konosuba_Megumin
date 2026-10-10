using System.Collections.Concurrent;
using System.Net;
using System.Text.Json;
using Godot;
using MegaCrit.Sts2.Core.Models;

namespace MeguminMod;

// Local developer companion to the separate MCP game-control bridge.
// Enabled only by the project launcher. All engine access runs on the main thread.
internal static class LabApi
{
    private static readonly ConcurrentQueue<Action> Pending = new();
    private static readonly HashSet<string> Clips = [];
    private static bool _renderReady;
    internal static void Start()
    {
        using var json = JsonDocument.Parse(File.ReadAllText(Path.Combine(ModEntry.Directory, "animation", "megumin.spine-json")));
        foreach (var clip in json.RootElement.GetProperty("animations").EnumerateObject())
            if (!clip.Name.StartsWith("_bind/")) Clips.Add(clip.Name);
        ((SceneTree)Engine.GetMainLoop()).ProcessFrame += () =>
        {
            for (var i = 0; i < 8 && Pending.TryDequeue(out var action); i++) action();
        };
        var listener = new HttpListener();
        listener.Prefixes.Add("http://127.0.0.1:15529/");
        listener.Start();
        _ = Task.Run(async () =>
        {
            while (listener.IsListening)
            {
                var context = await listener.GetContextAsync();
                _ = Handle(context);
            }
        });
    }

    private static async Task Handle(HttpListenerContext context)
    {
        try
        {
            if (context.Request.Headers["Origin"] is not null) { context.Response.StatusCode = 403; return; }
            var request = context.Request;
            JsonElement body = default;
            if (request.HttpMethod == "POST")
            {
                if (request.ContentLength64 > 8192) throw new ArgumentException("Body too large.");
                using var document = await JsonDocument.ParseAsync(request.InputStream);
                body = document.RootElement.Clone();
            }
            var done = new TaskCompletionSource<object>(TaskCreationOptions.RunContinuationsAsynchronously);
            Pending.Enqueue(() =>
            {
                try { done.SetResult(Execute(request.Url!.AbsolutePath, request.HttpMethod, body)); }
                catch (Exception e) { done.SetException(e); }
            });
            var result = await done.Task.WaitAsync(TimeSpan.FromSeconds(15));
            context.Response.ContentType = "application/json; charset=utf-8";
            await JsonSerializer.SerializeAsync(context.Response.OutputStream, result);
        }
        catch (Exception error)
        {
            context.Response.StatusCode = 400;
            await JsonSerializer.SerializeAsync(context.Response.OutputStream, new { error = error.Message });
        }
        finally { context.Response.Close(); }
    }

    private static object Execute(string path, string method, JsonElement body)
    {
        var sprite = MeguminVisuals.LastSprite;
        var valid = sprite is not null && GodotObject.IsInstanceValid(sprite) && sprite.IsInsideTree();
        if (path == "/health" && method == "GET")
            return new { status = "ok", character = ModelDb.Character<Megumin>().Id.Entry, user_data = OS.GetUserDataDir(), native_spine = valid, animations = Clips.Order().ToArray() };
        if (path == "/render" && method == "POST")
        {
            var viewport = ((SceneTree)Engine.GetMainLoop()).Root;
            RenderingServer.ViewportSetUpdateMode(viewport.GetViewportRid(), RenderingServer.ViewportUpdateMode.Always);
            if (!_renderReady)
            {
                RenderingServer.ViewportSetActive(viewport.GetViewportRid(), false);
                RenderingServer.ViewportSetActive(viewport.GetViewportRid(), true);
                _renderReady = true;
            }
            RenderingServer.ForceDraw(false);
            return new { status = "rendered", mode = DisplayServer.WindowGetMode().ToString() };
        }
        if (path == "/animation" && method == "POST")
        {
            if (!valid) throw new InvalidOperationException("Enter a Megumin combat first.");
            var name = body.GetProperty("name").GetString()!;
            if (!Clips.Contains(name)) throw new ArgumentException("Unknown animation.");
            var loop = body.TryGetProperty("loop", out var l) && l.GetBoolean();
            var state = sprite!.Call("get_animation_state").AsGodotObject();
            state.Call("clear_tracks");
            var track = state.Call("set_animation", name, loop, 0).AsGodotObject();
            if (body.TryGetProperty("time", out var t))
            {
                var time = t.GetDouble();
                if (!double.IsFinite(time) || time < 0) throw new ArgumentException("Time must be finite and nonnegative.");
                track.Call("set_track_time", time);
                track.Call("set_time_scale", 0.0);
            }
            return new { status = "ok", name, loop };
        }
        if (path == "/quit" && method == "POST")
        {
            Callable.From(() => ((SceneTree)Engine.GetMainLoop()).Quit()).CallDeferred();
            return new { status = "quitting" };
        }
        throw new ArgumentException("Unknown endpoint or method.");
    }
}
