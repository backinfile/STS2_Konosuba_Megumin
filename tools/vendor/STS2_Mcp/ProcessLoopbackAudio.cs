using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;

namespace KarenSTS2MCP;

// Windows process loopback: includes only this process tree, never microphones
// or unrelated apps. All COM access and file writes run on a dedicated MTA thread.
// Public so the nested COM callback's IAgileObject interface is visible to Windows.
public sealed class ProcessLoopbackAudio : IDisposable
{
    internal const int SampleRate = 44100;
    private const int BlockAlign = 4; // stereo PCM16
    private readonly ManualResetEvent _stop = new(false);
    private readonly TaskCompletionSource _ready = new(TaskCreationOptions.RunContinuationsAsynchronously);
    private readonly TaskCompletionSource _done = new(TaskCreationOptions.RunContinuationsAsynchronously);
    private double _duration;
    private readonly string _path;

    public ProcessLoopbackAudio(string path)
    {
        if (!OperatingSystem.IsWindowsVersionAtLeast(10, 0, 20348))
            throw new PlatformNotSupportedException("Game audio recording requires Windows build 20348 or newer (including Windows 11)");
        _path = path;
        var thread = new Thread(Capture) { IsBackground = true, Name = "KarenSTS2MCP_Audio" };
        thread.SetApartmentState(ApartmentState.MTA);
        thread.Start();
    }

    public Task Ready => _ready.Task;

    public void ThrowIfFailed()
    {
        if (_done.Task.IsFaulted) _done.Task.GetAwaiter().GetResult();
    }

    public async Task Finish(double seconds)
    {
        _duration = seconds;
        _stop.Set();
        await _done.Task.WaitAsync(TimeSpan.FromSeconds(10));
    }

    public void Dispose()
    {
        _stop.Set();
        // Never dispose the event while the capture thread can still use it.
        try { _done.Task.Wait(TimeSpan.FromSeconds(10)); } catch (AggregateException) { }
        if (_done.Task.IsCompleted) _stop.Dispose();
    }

    private void Capture()
    {
        if (!OperatingSystem.IsWindows()) return;
        IAudioClient? client = null;
        IAudioCaptureClient? capture = null;
        try
        {
            client = Activate();
            if (_stop.WaitOne(0)) throw new OperationCanceledException("Audio capture startup cancelled");
            var format = new WaveFormat { Tag = 1, Channels = 2, SamplesPerSecond = SampleRate,
                AverageBytesPerSecond = SampleRate * BlockAlign, BlockAlign = BlockAlign, Bits = 16 };
            using var samplesReady = new AutoResetEvent(false);
            Check(client.Initialize(0, 0x80060000, 0, 0, ref format, IntPtr.Zero)); // convert PCM, loopback, event callback
            Check(client.SetEventHandle(samplesReady.SafeWaitHandle.DangerousGetHandle()));
            Guid captureId = typeof(IAudioCaptureClient).GUID;
            Check(client.GetService(ref captureId, out object service));
            capture = (IAudioCaptureClient)service;
            using var file = new FileStream(_path, FileMode.CreateNew, FileAccess.ReadWrite, FileShare.Read);
            file.Write(new byte[44]);
            Check(client.Start());
            double start100ns = Stopwatch.GetTimestamp() * (10000000.0 / Stopwatch.Frequency);
            _ready.TrySetResult();
            byte[] buffer = new byte[SampleRate * BlockAlign];
            var waits = new WaitHandle[] { _stop, samplesReady };
            long position = 0;
            while (!_stop.WaitOne(0))
            {
                if (WaitHandle.WaitAny(waits, 100) == 0) break;
                Check(capture.GetNextPacketSize(out uint available));
                while (available > 0 && !_stop.WaitOne(0))
                {
                    Check(capture.GetBuffer(out IntPtr data, out uint frames, out uint flags, out _, out ulong qpc));
                    try
                    {
                        int bytes = checked((int)frames * BlockAlign);
                        if (buffer.Length < bytes) buffer = new byte[bytes];
                        // Timestamp error: fall back to contiguous samples. Otherwise preserve
                        // silence gaps and align the first packet to recording start, not first sound.
                        long target = (flags & 4) != 0 ? position :
                            (long)Math.Round(((double)qpc - start100ns) * SampleRate / 10000000.0);
                        target = Math.Clamp(target, -SampleRate, (long)SampleRate * 3601);
                        if (target > position)
                        {
                            file.Position = 44 + target * BlockAlign;
                            position = target;
                        }
                        int skip = (int)Math.Min(frames, Math.Max(0, position - target));
                        if ((flags & 2) != 0) Array.Clear(buffer, 0, bytes);
                        else Marshal.Copy(data, buffer, 0, bytes);
                        file.Write(buffer, skip * BlockAlign, bytes - skip * BlockAlign);
                        position += frames - skip;
                    }
                    finally { Check(capture.ReleaseBuffer(frames)); }
                    Check(capture.GetNextPacketSize(out available));
                }
            }
            Check(client.Stop());
            long length = (long)Math.Round(Math.Clamp(_duration, 0, 3600) * SampleRate) * BlockAlign;
            // Extending a file supplies silence when the game made no sound.
            file.SetLength(44 + length);
            file.Position = 0;
            using var writer = new BinaryWriter(file, System.Text.Encoding.ASCII, leaveOpen: true);
            writer.Write(System.Text.Encoding.ASCII.GetBytes("RIFF")); writer.Write((uint)(36 + length));
            writer.Write(System.Text.Encoding.ASCII.GetBytes("WAVEfmt ")); writer.Write(16);
            writer.Write((short)1); writer.Write((short)2); writer.Write(SampleRate);
            writer.Write(SampleRate * BlockAlign); writer.Write((short)BlockAlign); writer.Write((short)16);
            writer.Write(System.Text.Encoding.ASCII.GetBytes("data")); writer.Write((uint)length);
        }
        catch (Exception ex)
        {
            _ready.TrySetException(ex);
            _done.TrySetException(ex);
        }
        finally
        {
            if (client != null) { try { client.Stop(); } catch { } }
            if (capture != null) Marshal.ReleaseComObject(capture);
            if (client != null) Marshal.ReleaseComObject(client);
            _done.TrySetResult();
        }
    }

    private static IAudioClient Activate()
    {
        if (!OperatingSystem.IsWindows()) throw new PlatformNotSupportedException();
        IntPtr parameters = Marshal.AllocHGlobal(12);
        IActivateOperation? operation = null;
        try
        {
            Marshal.WriteInt32(parameters, 0, 1); // PROCESS_LOOPBACK
            Marshal.WriteInt32(parameters, 4, Environment.ProcessId);
            Marshal.WriteInt32(parameters, 8, 0); // INCLUDE_TARGET_PROCESS_TREE
            var variant = new PropVariant { Type = 65, Size = 12, Data = parameters }; // VT_BLOB
            var completion = new ActivationCompletion();
            Guid id = typeof(IAudioClient).GUID;
            Check(ActivateAudioInterfaceAsync("VAD\\Process_Loopback", ref id, ref variant, completion, out operation));
            // Keep callback and activation memory alive until the OS completes activation.
            object result = completion.Result.Task.GetAwaiter().GetResult();
            GC.KeepAlive(completion);
            return (IAudioClient)result;
        }
        finally
        {
            if (operation != null) Marshal.ReleaseComObject(operation);
            Marshal.FreeHGlobal(parameters);
        }
    }

    private static void Check(int result) => Marshal.ThrowExceptionForHR(result);

    [ComVisible(true), ClassInterface(ClassInterfaceType.None)]
    public sealed class ActivationCompletion : IActivationCompletion, IAgileObject
    {
        internal readonly TaskCompletionSource<object> Result = new(TaskCreationOptions.RunContinuationsAsynchronously);
        public int ActivateCompleted(IActivateOperation operation)
        {
            try
            {
                Check(operation.GetActivateResult(out int result, out object client));
                Check(result);
                Result.TrySetResult(client);
            }
            catch (Exception ex) { Result.TrySetException(ex); }
            return 0;
        }
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct PropVariant
    {
        public ushort Type, Reserved1, Reserved2, Reserved3;
        public uint Size;
        public IntPtr Data;
    }
    [StructLayout(LayoutKind.Sequential, Pack = 2)]
    private struct WaveFormat
    {
        public ushort Tag, Channels;
        public uint SamplesPerSecond, AverageBytesPerSecond;
        public ushort BlockAlign, Bits, Extra;
    }
    [DllImport("Mmdevapi.dll", ExactSpelling = true, CharSet = CharSet.Unicode)]
    private static extern int ActivateAudioInterfaceAsync(string device, ref Guid iid, ref PropVariant parameters,
        IActivationCompletion completion, out IActivateOperation operation);

    [ComVisible(true), Guid("41D949AB-9862-444A-80F6-C261334DA5EB"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IActivationCompletion { [PreserveSig] int ActivateCompleted(IActivateOperation operation); }
    [ComVisible(true), Guid("94EA2B94-E9CC-49E0-C0FF-EE64CA8F5B90"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IAgileObject { }
    [ComImport, Guid("72A22D78-CDE4-431D-B8CC-843A71199B6D"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IActivateOperation
    { [PreserveSig] int GetActivateResult(out int result, [MarshalAs(UnmanagedType.IUnknown)] out object client); }
    [ComImport, Guid("1CB9AD4C-DBFA-4C32-B178-C2F568A703B2"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    private interface IAudioClient
    {
        [PreserveSig] int Initialize(int mode, uint flags, long duration, long periodicity, ref WaveFormat format, IntPtr session);
        [PreserveSig] int GetBufferSize(out uint frames);
        [PreserveSig] int GetStreamLatency(out long latency);
        [PreserveSig] int GetCurrentPadding(out uint frames);
        [PreserveSig] int IsFormatSupported(int mode, IntPtr format, out IntPtr closest);
        [PreserveSig] int GetMixFormat(out IntPtr format);
        [PreserveSig] int GetDevicePeriod(out long normal, out long minimum);
        [PreserveSig] int Start();
        [PreserveSig] int Stop();
        [PreserveSig] int Reset();
        [PreserveSig] int SetEventHandle(IntPtr handle);
        [PreserveSig] int GetService(ref Guid iid, [MarshalAs(UnmanagedType.IUnknown)] out object service);
    }
    [ComImport, Guid("C8ADBD64-E71E-48A0-A4DE-185C395CD317"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    private interface IAudioCaptureClient
    {
        [PreserveSig] int GetBuffer(out IntPtr data, out uint frames, out uint flags, out ulong position, out ulong qpc);
        [PreserveSig] int ReleaseBuffer(uint frames);
        [PreserveSig] int GetNextPacketSize(out uint frames);
    }
}
