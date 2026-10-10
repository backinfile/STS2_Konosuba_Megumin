using System.Collections.Generic;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Runs;

namespace KarenSTS2MCP;

public static partial class McpMod
{
    private static Dictionary<string, object?> ExecuteAbandonRun()
    {
        var run = RunManager.Instance;
        if (!run.IsInProgress)
            return Error("No run in progress");
        if (run.NetService.Type != NetGameType.Singleplayer)
            return Error("abandon_run is only available in singleplayer runs");
        if (run.IsCleaningUp)
            return Error("Run cleanup is in progress; wait for the main menu");
        if (run.IsGameOver)
            return Error("Run has already ended. Use menu_select('main_menu') from the game-over screen");

        if (!run.IsAbandoned)
        {
            // Same entry point as confirming Give Up in the game's pause menu.
            // The game handles death, run history and save cleanup asynchronously.
            run.Abandon();
        }

        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["async"] = true,
            ["message"] = "Abandoning the current run. Read game state until game_over, then use menu_select('main_menu')"
        };
    }
}
