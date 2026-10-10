using System.Reflection;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Modding;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes;

namespace MeguminMod;

[ModInitializer(nameof(Initialize))]
public static class ModEntry
{
    internal static readonly string Directory = Path.GetDirectoryName(typeof(ModEntry).Assembly.Location)!;
    internal static bool IsLab => System.Environment.GetEnvironmentVariable("MEGUMIN_LAB") == "1";
    public static void Initialize()
    {
        new Harmony("megumin.animation.lab").PatchAll(Assembly.GetExecutingAssembly());
        // BaseLib registers custom models during ModelDb.Init, after mod initializers.
        if (IsLab) LabApi.Start();
        GD.Print($"[Megumin] Initialized. Lab={IsLab}; user_data={OS.GetUserDataDir()}");
    }
}

// The lab starts minimized. Avoid the game's delayed graphics initialization
// restoring that window, while leaving ordinary installations unaffected.
[HarmonyPatch(typeof(NGame), nameof(NGame.ApplyDisplaySettings))]
internal static class LabDisplayPatch
{
    private static bool Prefix() => !ModEntry.IsLab || System.Environment.GetEnvironmentVariable("MEGUMIN_LAB_VISIBLE") == "1";
}
