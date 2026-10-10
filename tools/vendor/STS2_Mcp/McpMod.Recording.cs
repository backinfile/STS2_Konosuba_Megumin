using System;
using System.IO;
using System.Net;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Godot;
using Environment = System.Environment;

namespace KarenSTS2MCP;

public static partial class McpMod
{
    private static readonly object _recordingGate = new();
    private static VideoRecording? _recording;

    private static void HandleRecording(HttpListenerRequest request, HttpListenerResponse response, string path)
    {
        if (path == "/api/v1/recording" && request.HttpMethod == "GET")
        {
            lock (_recordingGate)
                SendJson(response, _recording?.Snapshot() ?? new { status = "idle" });
            return;
        }
        if (request.HttpMethod != "POST" || path == "/api/v1/recording")
        {
            SendError(response, 405, "Method not allowed");
            return;
        }
        if (path == "/api/v1/recording/stop")
        {
            lock (_recordingGate)
            {
                _recording?.Stop();
                SendJson(response, _recording?.Snapshot() ?? new { status = "idle" });
            }
            return;
        }

        try
        {
            using var reader = new StreamReader(request.InputStream, request.ContentEncoding);
            string body = reader.ReadToEnd();
            using var doc = JsonDocument.Parse(string.IsNullOrWhiteSpace(body) ? "{}" : body);
            var options = doc.RootElement;
            if (options.ValueKind != JsonValueKind.Object)
                throw new ArgumentException("Expected a JSON object");
            int fps = RecordingInt(options, "fps", 15, 1, 30);
            int seconds = RecordingInt(options, "max_duration_seconds", 300, 1, 3600);
            int width = RecordingInt(options, "width", 1280, 2, 1920);
            int height = RecordingInt(options, "height", 720, 2, 1080);
            bool audio = false;
            if (options.TryGetProperty("audio", out var audioOption))
            {
                if (audioOption.ValueKind is not (JsonValueKind.True or JsonValueKind.False))
                    throw new ArgumentException("audio must be a boolean");
                audio = audioOption.GetBoolean();
            }
            if (width % 2 != 0 || height % 2 != 0)
                throw new ArgumentException("width and height must be even for H.264 video");

            lock (_recordingGate)
            {
                if (_recording?.IsActive == true)
                {
                    SendError(response, 409, "A recording is already active or finalizing");
                    return;
                }
                string directory = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "KarenSTS2MCP", "recordings");
                Directory.CreateDirectory(directory);
                string output = Path.Combine(directory, $"sts2-{DateTime.UtcNow:yyyyMMdd-HHmmss}-{Guid.NewGuid():N}.mp4");
                string executable = Environment.GetEnvironmentVariable("STS2_MCP_FFMPEG") ?? "ffmpeg";
                _recording = new VideoRecording(executable, output, fps, seconds, width, height,
                    token => CaptureRecordingFrame(width, height, token), audio);
                response.StatusCode = 202;
                SendJson(response, _recording.Snapshot());
            }
        }
        catch (Exception ex) when (ex is JsonException or ArgumentException)
        { SendError(response, 400, ex.Message); }
        catch (System.ComponentModel.Win32Exception ex)
        { SendError(response, 503, $"Cannot start FFmpeg. Install ffmpeg with libx264 on PATH or set STS2_MCP_FFMPEG before launching the game. {ex.Message}"); }
        catch (PlatformNotSupportedException ex)
        { SendError(response, 503, ex.Message); }
        catch (Exception ex)
        { SendError(response, 500, $"Could not start recording: {ex.Message}"); }
    }

    private static int RecordingInt(JsonElement options, string key, int fallback, int min, int max)
    {
        if (!options.TryGetProperty(key, out var value)) return fallback;
        if (value.ValueKind != JsonValueKind.Number || !value.TryGetInt32(out int number) || number < min || number > max)
            throw new ArgumentException($"{key} must be an integer between {min} and {max}");
        return number;
    }

    private static Task<byte[]> CaptureRecordingFrame(int width, int height, CancellationToken token)
    {
        return RunOnMainThread(() =>
        {
            // Timed-out captures must not accumulate GPU readbacks when the game resumes.
            token.ThrowIfCancellationRequested();
            var tree = Engine.GetMainLoop() as SceneTree
                ?? throw new InvalidOperationException("Game scene tree is unavailable");
            // The project lab intentionally runs minimized. Refresh its live
            // viewport on every capture; otherwise Godot returns a stale image.
            // Animation time keeps advancing normally at the game's own rate.
            if (Environment.GetEnvironmentVariable("MEGUMIN_LAB") == "1")
                RenderingServer.ForceDraw(false);
            using var image = tree.Root.GetTexture().GetImage();
            if (image == null || image.IsEmpty())
                throw new InvalidOperationException("Game viewport image is empty");
            // Fixed canvas with letterboxing also handles window resizes during recording.
            float scale = Math.Min((float)width / image.GetWidth(), (float)height / image.GetHeight());
            int scaledWidth = Math.Clamp((int)(image.GetWidth() * scale), 1, width);
            int scaledHeight = Math.Clamp((int)(image.GetHeight() * scale), 1, height);
            image.Resize(scaledWidth, scaledHeight);
            image.Convert(Image.Format.Rgb8);
            using var canvas = Image.CreateEmpty(width, height, false, Image.Format.Rgb8);
            canvas.Fill(Colors.Black);
            canvas.BlitRect(image, new Rect2I(0, 0, scaledWidth, scaledHeight),
                new Vector2I((width - scaledWidth) / 2, (height - scaledHeight) / 2));
            // PNG compression here blocked the game thread for ~140ms per 720p frame.
            // Send tightly packed RGB24 directly to the background encoder instead.
            return canvas.GetData();
        });
    }
}
