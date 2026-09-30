# Megumin casting v2 — standalone Godot 4.6

This is an editable standalone character-animation study. It is not integrated with STS2, and no game code or damage values were changed. v1 is frozen separately.

## Run and edit

Open `project.godot`. The default scene is `scenes/casting_review.tscn`: VFX off, large view plus 320px reference-scale view. Press Space to replay. The optional `scenes/preview.tscn` retains the six-state inspection UI.

The actor scene is `scenes/megumin.tscn`. Copy its `assets`, `animations`, and all scripts in `scripts/`, adjusting `res://` paths if needed. Native `AnimationPlayer` property tracks remain editable in `animations/*.tres`.

```gdscript
var visuals: MeguminRig = preload("res://scenes/megumin.tscn").instantiate()
visuals.effects_enabled = false # also the v2 default
visuals.auto_return_to_idle = false
add_child(visuals)
visuals.position = ground_position
visuals.scale = Vector2.ONE * (320.0 / 1100.0)
visuals.attack_impact.connect(on_attack_impact)
visuals.play_animation("Attack")
```

`Attack` is now the complete 3.50s sequence: coil → elbow lift → chant → full-body release → follow-through → exhaustion. The impact marker moved from v1's 0.72s to v2's **1.55s**. Do not reuse the old delay. With `animation_speed`, wall-clock impact time is `1.55 / animation_speed`.

`Cast` lasts 1.55s and contains the preparation/lift/chant section. `Relaxed` shows the new exhausted stance. `Idle`, `Hit`, and `Dead` retain the earlier authored source system. `Dead` locks ordinary animation requests until `reset_character()`.

Methods: `play_animation(state) -> bool`, `reset_character()`, and `seek_pose(seconds)` for event-free visual scrubbing. Use `seek_pose`, not raw AnimationPlayer event-bearing seeks, for inspectors, thumbnails, and previews.

Signals: `animation_state_changed(state)`, `animation_completed(state)`, `attack_impact`, and `marker_reached("damage")`. The actor only emits a marker; it does not modify game health. Never use both a delay path and the signal to apply damage twice.

## Art and native rig

Six authored pose images live in `assets/poses/v2/`; two additional upper-body/cape occlusion-repair images let chant and exhaustion reuse the preparation's leg cutouts without stretching legs or exposing missing art.

`casting_pose_mesh.gd` creates dense Polygon2D meshes, a shared rigid staff, the back-cape / leg / front-skirt layers, and secondary shoulder/elbow/waist/head/knee/cape channels. Pose switches are discrete and opaque. There is no pose crossfade. Source PNG pixels are retained, with geometry/shader masks removing the redundant drawn staff.

Every casting pose has the same sole anchors `(-443, 0)` and `(443, -45)`. The raised right sole is the illustration's ground-plane perspective. Release uses its own newly drawn weight-bearing legs; chant and exhaustion use the same preparation legs. The common staff uses one source asset and fixed scale; it is never shortened to fit a pose.

`tools/build_pose_metadata.py` regenerates registration/mask metadata. `tools/build_v2_animation.py` regenerates v2 native timelines. Do not run legacy `tools_build.py` over v2 timelines: it is retained only as provenance for the earlier cutout geometry.

## Preview and verification limits

`preview/megumin_casting_v2.mp4` is a 30fps deterministic **software raster preview of actual Godot-exported AnimationPlayer/Polygon2D geometry**, not a Godot graphical screen recording. The cloud environment blocked creation of a local Unix display socket; TCP listening was not used. Godot graphical composition, shader compilation on a real GPU, and final STS2 in-game appearance remain unverified.

`tests/test_rig.gd` checks native state logic, six poses, fixed sole anchors, shared staff length and hand alignment, opaque pose selection, interruption, reset/death, repeated visual seeks, and damage timing under both immediate-test and normal deferred callbacks. The checked result is in `tests/results.json`.

The preview preserves fixed character scale across frames. Mipmapped linear texture filtering is configured; the offline preview uses premultiplied-alpha box mips and trilinear sampling. This addresses reduction shimmer without blurring the source artwork. See `MOIRE_CHECK.txt` for the dedicated source-art detection tests and the decision to retain the originals.

This remains key-pose animation with continuous secondary articulation, not newly painted frame-by-frame animation. Some fast pose transitions and minor matte/prop-edge specks remain review items. The movie is a review candidate, not a claim of final user acceptance.
