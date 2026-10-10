using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Nodes.Screens.Map;

namespace KarenSTS2MCP;

public static partial class McpMod
{
    // The travel console command changes IsDebugTravelEnabled, not point.State.
    // Use the same selection rules and ordering for state and action indices.
    private static List<NMapPoint> GetSelectableMapPoints(NMapScreen mapScreen)
    {
        if (mapScreen.IsTraveling || (!mapScreen.IsDebugTravelEnabled && !mapScreen.IsTravelEnabled))
            return new List<NMapPoint>();

        return FindAll<NMapPoint>(mapScreen)
            .Where(mp => mp.Point != null && (mapScreen.IsDebugTravelEnabled || mp.State == MapPointState.Travelable))
            .OrderBy(mp => mp.Point.coord.col)
            .ThenBy(mp => mp.Point.coord.row)
            .ToList();
    }

    private static Dictionary<string, object?> ExecuteChooseMapNode(Dictionary<string, JsonElement> data)
    {
        var mapScreen = NMapScreen.Instance;
        if (mapScreen == null || (!mapScreen.IsOpen && !IsNodeVisible(mapScreen)))
            return Error("Map screen is not open");
        if (mapScreen.IsTraveling)
            return Error("Already traveling to a room; wait for the transition to finish");

        if (!data.TryGetValue("index", out var indexElem) || indexElem.ValueKind != JsonValueKind.Number
            || !indexElem.TryGetInt32(out int index))
            return Error("Missing or invalid 'index' (integer map node index from next_options)");

        var travelable = GetSelectableMapPoints(mapScreen);
        if (travelable.Count == 0)
            return Error("No travelable map nodes available");
        if (index < 0 || index >= travelable.Count)
            return Error($"Map node index {index} out of range ({travelable.Count} options available)");

        return SelectMapPoint(mapScreen, travelable[index]);
    }

    private static Dictionary<string, object?> ExecuteEnterMapRoom(Dictionary<string, JsonElement> data)
    {
        var mapScreen = NMapScreen.Instance;
        if (mapScreen == null || (!mapScreen.IsOpen && !IsNodeVisible(mapScreen)))
            return Error("Map screen is not open");
        if (!mapScreen.IsDebugTravelEnabled)
            return Error("Travel mode is disabled. Enable it with run_command('travel') before entering any room");
        if (mapScreen.IsTraveling)
            return Error("Already traveling to a room; wait for the transition to finish");

        if (!data.TryGetValue("col", out var colElem) || colElem.ValueKind != JsonValueKind.Number
            || !colElem.TryGetInt32(out int col)
            || !data.TryGetValue("row", out var rowElem) || rowElem.ValueKind != JsonValueKind.Number
            || !rowElem.TryGetInt32(out int row))
            return Error("Missing or invalid 'col'/'row' (integer coordinates from map.nodes or map.next_options)");

        var target = GetSelectableMapPoints(mapScreen)
            .FirstOrDefault(mp => mp.Point.coord.col == col && mp.Point.coord.row == row);
        if (target == null)
            return Error($"No map room at ({col},{row}) in the current act");

        return SelectMapPoint(mapScreen, target);
    }

    private static Dictionary<string, object?> SelectMapPoint(NMapScreen mapScreen, NMapPoint target)
    {
        var pt = target.Point;
        // Preserve the game's action queue, room setup and multiplayer voting.
        mapScreen.OnMapPointSelectedLocally(target);
        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = $"Traveling to {pt.PointType} at ({pt.coord.col},{pt.coord.row})",
            ["col"] = pt.coord.col,
            ["row"] = pt.coord.row,
            ["type"] = pt.PointType.ToString()
        };
    }
}
