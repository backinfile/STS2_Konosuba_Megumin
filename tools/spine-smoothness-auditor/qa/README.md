# Independent reliability QA

All fixtures in this directory are synthetic and may be redistributed. None contains game artwork, game skeletons, textures, or proprietary animation data.

Regenerate fixtures:

```sh
node qa/generate-fixtures.mjs
```

## Expected behavior

- `stationary`: zero point/angular motion; no NaN/Infinity.
- `constant_velocity`: root moves 100 coordinate units per second. `constant_velocity_long` has the same speed for twice as long. `constant_velocity_short` tests an endpoint off the regular sample grid.
- `adversarial-scaled10.json`: coordinates, bone lengths, bounds, and mesh deformation are all 10×. Scale-normalized motion should match the base file.
- `closed_velocity_kink`: endpoint positions agree but endpoint velocities point in opposite directions. It must not pass a velocity-continuity test simply because the pose matches.
- `smooth_loop`: dense samples of a sine wave give approximately continuous position and endpoint velocity. It is a piecewise-linear approximation, not an analytic smooth curve.
- `rotation_across_world_wrap`: 170° to 190° over one second is 20°/second, despite world-angle extraction wrapping at ±180°.
- `genuine_spin`: 720° over one second is a real two-turn spin and must not vanish into an endpoint equivalence or create a wrap-boundary velocity spike.
- `aliasing_spin`: intentionally exceeds the angular Nyquist limit at 60 FPS. Any shortest-arc world-angle method cannot reconstruct it without additional information. The tool must document this limitation rather than promise all spins are resolved.
- `stepped_jump`: a genuine visible positional jump at 0.5 seconds.
- `attachment_swap`: replaces mesh geometry with a different mesh 1,000 units away. Report a discrete swap; do not infer a massive continuous vertex velocity from unrelated vertices.
- `attachment_hide`: attachment removal is a discrete visibility change, not NaN or an arbitrary point interpolation.
- `deform_only`: bones stay still while one visible mesh vertex deforms. Geometry analysis must detect motion.
- `zero_duration`: valid empty animation; report no usable derivatives and finite output.
- `weighted-mesh.json`: same four vertex positions using Spine weighted-vertex encoding.
- `region.json`: texture-region geometry rather than a mesh. Without an atlas, document region trimming/offset limitations.
- `physics.json`: spring constraint. Physics update must be sequential and materially differ from `none`; initial transient must not be called a settled periodic loop.
- Invalid cases must yield useful errors: incompatible version, malformed JSON, missing bone, unsorted key times, and nonfinite runtime transforms.

## Interpretation limits

These tests verify numerical and runtime behavior, not artistic quality. A high acceleration or jerk may be intentional animation timing; a low value does not prove readable acting, appealing poses, successful game integration, or stable rendered pixels. Atlas metadata cannot substitute for actual texture/pixel rendering, clipping/occlusion, camera transforms, or in-game controller playback.
