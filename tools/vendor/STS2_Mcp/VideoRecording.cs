using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace KarenSTS2MCP;

// Owns encoder lifetime. Only the capture callback may touch the game thread.
internal sealed class VideoRecording
{
    private readonly object _gate = new();
    private readonly Process _encoder;
    private readonly Stopwatch _clock = Stopwatch.StartNew();
    private readonly CancellationTokenSource _stop = new();
    private readonly int _fps;
    private readonly int _maxSeconds;
    private readonly string _path;
    private readonly int _width;
    private readonly int _height;
    private readonly int _frameBytes;
    private readonly bool _audio;
    private readonly string _executable;
    private readonly string _videoPath;
    private string _status = "recording";
    private string? _error;
    private string _encoderError = "";
    private int _frames;
    private int _captures;
    private int _repeated;
    private double _captureMs;
    private double _captureMaxMs;
    private double _captureSeconds;
    private double _elapsed;

    public VideoRecording(string executable, string path, int fps, int maxSeconds, int width, int height,
        Func<CancellationToken, Task<byte[]>> capture, bool audio = false)
    {
        if (fps is < 1 or > 30 || maxSeconds is < 1 or > 3600)
            throw new ArgumentOutOfRangeException(nameof(fps), "Invalid frame rate or duration");
        if (width is < 2 or > 1920 || height is < 2 or > 1080 || width % 2 != 0 || height % 2 != 0)
            throw new ArgumentOutOfRangeException(nameof(width), "Invalid RGB24 video dimensions");
        _fps = fps;
        _maxSeconds = maxSeconds;
        _path = path;
        _width = width;
        _height = height;
        _frameBytes = checked(width * height * 3);
        if (audio && !OperatingSystem.IsWindowsVersionAtLeast(10, 0, 20348))
            throw new PlatformNotSupportedException("Game audio recording requires Windows build 20348 or newer (including Windows 11)");
        _audio = audio;
        _executable = executable;
        _videoPath = audio ? path + ".video.mp4" : path;
        var info = new ProcessStartInfo(executable)
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardInput = true,
            RedirectStandardError = true
        };
        foreach (string arg in new[] { "-hide_banner", "-loglevel", "error", "-n",
            "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", $"{width}x{height}",
            "-framerate", fps.ToString(System.Globalization.CultureInfo.InvariantCulture),
            "-i", "pipe:0", "-an", "-c:v", "libx264",
            "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", _videoPath })
            info.ArgumentList.Add(arg);
        _encoder = new Process { StartInfo = info };
        _encoder.ErrorDataReceived += (_, e) =>
        {
            if (!string.IsNullOrEmpty(e.Data))
                lock (_gate) _encoderError = e.Data.Length > 2000 ? e.Data[..2000] : e.Data;
        };
        try
        {
            _encoder.Start();
            _encoder.BeginErrorReadLine();
        }
        catch
        {
            _encoder.Dispose();
            _stop.Dispose();
            throw;
        }
        _ = Task.Run(() => Record(capture));
    }

    public bool IsActive
    {
        get { lock (_gate) return _status is "recording" or "stopping"; }
    }

    public object Snapshot()
    {
        lock (_gate) return new
        {
            status = _status, output_path = _path, fps = _fps, max_duration_seconds = _maxSeconds,
            width = _width, height = _height,
            frames_written = _frames, video_duration_seconds = (double)_frames / _fps,
            frames_captured = _captures, frames_repeated = _repeated,
            capture_fps = _captures / Math.Max(0.001, _captureSeconds > 0 ? _captureSeconds : _clock.Elapsed.TotalSeconds),
            capture_average_ms = _captures == 0 ? 0 : _captureMs / _captures,
            capture_max_ms = _captureMaxMs,
            elapsed_seconds = IsActive ? _clock.Elapsed.TotalSeconds : _elapsed,
            audio = _audio, audio_source = _audio ? "game_process" : null, error = _error
        };
    }

    public void Stop()
    {
        lock (_gate)
        {
            if (_status != "recording") return;
            _status = "stopping";
            _stop.Cancel();
        }
    }

    private async Task Record(Func<CancellationToken, Task<byte[]>> capture)
    {
        string? failure = null;
        ProcessLoopbackAudio? audioCapture = null;
        try
        {
            if (_audio)
            {
                audioCapture = new ProcessLoopbackAudio(_path + ".audio.wav");
                await audioCapture.Ready.WaitAsync(TimeSpan.FromSeconds(10));
            }
            using var duration = new CancellationTokenSource(TimeSpan.FromSeconds(_maxSeconds));
            using var captureStop = CancellationTokenSource.CreateLinkedTokenSource(_stop.Token, duration.Token);
            byte[]? previous = null;
            int written = 0;
            _clock.Restart();
            try
            {
                while (true)
                {
                    captureStop.Token.ThrowIfCancellationRequested();
                    audioCapture?.ThrowIfFailed();
                    using var timeout = CancellationTokenSource.CreateLinkedTokenSource(captureStop.Token);
                    timeout.CancelAfter(TimeSpan.FromSeconds(5));
                    byte[] frame;
                    long captureStart = Stopwatch.GetTimestamp();
                    try { frame = await capture(timeout.Token).WaitAsync(timeout.Token); }
                    catch (OperationCanceledException) when (!captureStop.IsCancellationRequested)
                    { throw new TimeoutException("Game viewport capture timed out after 5 seconds"); }
                    if (frame.Length != _frameBytes)
                        throw new InvalidDataException($"Expected {_frameBytes} RGB24 bytes, received {frame.Length}");
                    double captureMs = Stopwatch.GetElapsedTime(captureStart).TotalMilliseconds;
                    lock (_gate)
                    {
                        _captures++;
                        _captureMs += captureMs;
                        _captureMaxMs = Math.Max(_captureMaxMs, captureMs);
                    }

                    // Repeat the previous frame over missed ticks to preserve wall-clock playback speed.
                    int target = Math.Min(_maxSeconds * _fps,
                        (int)Math.Floor(_clock.Elapsed.TotalSeconds * _fps) + 1);
                    while (written < target)
                    {
                        bool repeated = written != target - 1;
                        await WriteFrame(repeated ? previous ?? frame : frame, repeated);
                        written++;
                    }
                    previous = frame;
                    double delay = (double)written / _fps - _clock.Elapsed.TotalSeconds;
                    if (delay > 0)
                        await Task.Delay(TimeSpan.FromSeconds(delay), captureStop.Token);
                }
            }
            catch (OperationCanceledException) when (captureStop.IsCancellationRequested) { }
            lock (_gate) _captureSeconds = _clock.Elapsed.TotalSeconds;

            // Cover the final partial interval when stop arrives during a capture.
            int finalFrames = Math.Min(_maxSeconds * _fps,
                (int)Math.Ceiling(_clock.Elapsed.TotalSeconds * _fps));
            while (previous != null && written < finalFrames)
            {
                await WriteFrame(previous, true);
                written++;
            }
            lock (_gate) _status = "stopping";
            if (audioCapture != null) await audioCapture.Finish((double)written / _fps);
            _encoder.StandardInput.Close();
            using var finishTimeout = new CancellationTokenSource(TimeSpan.FromSeconds(15));
            await _encoder.WaitForExitAsync(finishTimeout.Token);
            if (_encoder.ExitCode != 0 || written == 0)
                throw new IOException("FFmpeg produced no complete video. " + _encoderError);
            if (_audio) await MuxAudio((double)written / _fps);
        }
        catch (Exception ex)
        {
            failure = ex.Message;
            lock (_gate)
                if (_encoderError.Length > 0 && !failure.Contains(_encoderError))
                    failure += " " + _encoderError;
        }
        finally
        {
            audioCapture?.Dispose();
            try
            {
                if (!_encoder.HasExited) _encoder.Kill(entireProcessTree: true);
                _encoder.WaitForExit(2000);
            }
            catch (Exception ex) { failure ??= ex.Message; }
            _encoder.Dispose();
            if (_audio)
            {
                try
                {
                    File.Delete(_path + ".audio.wav");
                    File.Delete(_videoPath);
                }
                catch (Exception ex) { failure ??= $"Temporary recording cleanup failed: {ex.Message}"; }
            }
            lock (_gate)
            {
                _elapsed = _clock.Elapsed.TotalSeconds;
                if (_captureSeconds == 0) _captureSeconds = _elapsed;
                _error = failure;
                _status = failure == null ? "completed" : "failed";
                _stop.Dispose();
            }
        }
    }

    private async Task MuxAudio(double seconds)
    {
        var info = new ProcessStartInfo(_executable)
        {
            UseShellExecute = false, CreateNoWindow = true, RedirectStandardError = true
        };
        foreach (string arg in new[] { "-hide_banner", "-loglevel", "error", "-n",
            "-i", _videoPath, "-i", _path + ".audio.wav", "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", "apad",
            "-t", seconds.ToString(System.Globalization.CultureInfo.InvariantCulture),
            "-movflags", "+faststart", _path }) info.ArgumentList.Add(arg);
        using var process = Process.Start(info) ?? throw new IOException("Could not start audio muxer");
        Task<string> error = process.StandardError.ReadToEndAsync();
        try
        {
            // AAC encoding time grows with recording duration; video is copied, not re-encoded.
            using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(Math.Max(30, seconds / 4)));
            await process.WaitForExitAsync(timeout.Token);
            if (process.ExitCode != 0) throw new IOException("Audio mux failed: " + await error);
        }
        finally
        {
            if (!process.HasExited) { process.Kill(entireProcessTree: true); await process.WaitForExitAsync(); }
        }
    }

    private async Task WriteFrame(byte[] frame, bool repeated)
    {
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(5));
        await _encoder.StandardInput.BaseStream.WriteAsync(frame, timeout.Token);
        lock (_gate)
        {
            _frames++;
            if (repeated) _repeated++;
        }
    }
}
