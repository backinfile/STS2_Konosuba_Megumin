using Godot;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace MeguminMod;

internal static class MeguminVisuals
{
    private static GodotObject? _data;
    internal static Node2D? LastSprite;

    internal static NCreatureVisuals Create()
    {
        if (_data is null)
        {
            var directory = Path.Combine(ModEntry.Directory, "animation").Replace('\\', '/');
            var file = ClassDB.Instantiate("SpineSkeletonFileResource").AsGodotObject();
            var result = file.Call("load_from_file", directory + "/megumin.spine-json").AsInt32();
            if (result != 0) throw new InvalidOperationException($"Spine skeleton load failed: {result}");
            var atlas = ClassDB.Instantiate("SpineAtlasResource").AsGodotObject();
            result = atlas.Call("load_from_atlas_file", directory + "/megumin.atlas").AsInt32();
            if (result != 0) throw new InvalidOperationException($"Spine atlas load failed: {result}");
            _data = ClassDB.Instantiate("SpineSkeletonDataResource").AsGodotObject();
            _data.Set("skeleton_file_res", file);
            _data.Set("atlas_res", atlas);
        }
        var root = new NCreatureVisuals { Name = "MeguminVisuals" };
        var sprite = (Node2D)ClassDB.Instantiate("SpineSprite").AsGodotObject();
        sprite.Name = "Visuals";
        sprite.Set("skeleton_data_res", _data);
        Add(root, sprite);
        Add(root, new Control { Name = "Bounds", Position = new(-110, -330), Size = new(240, 330), MouseFilter = Control.MouseFilterEnum.Ignore });
        Add(root, new Marker2D { Name = "IntentPos", Position = new(0, -350) });
        Add(root, new Marker2D { Name = "CenterPos", Position = new(0, -160) });
        Add(root, new Marker2D { Name = "OrbPos", Position = new(-100, -200) });
        Add(root, new Marker2D { Name = "TalkPos", Position = new(70, -290) });
        LastSprite = sprite;
        GD.Print("[Megumin] Native Spine visuals created.");
        return root;
    }

    private static void Add(Node root, Node node)
    {
        root.AddChild(node);
        node.Owner = root;
        node.UniqueNameInOwner = true;
    }
}
