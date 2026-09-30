# Five-state PNG inspection

Review scope: offline software rasterization of native Godot Polygon2D geometry, not a Godot window recording. This review does not claim gameplay integration or video-playback acceptance.

## Actually inspected

Five full 1440×960 PNGs, each containing the fixed large view and 320 px reference:
- Idle 1.35 s: `preview/five_states/key_idle_01.png`
- Cast 2.20 s: `preview/five_states/key_cast_01.png`
- Attack 3.50 s: `preview/five_states/key_attack_02.png`
- Hit 0.22 s: `preview/five_states/key_hit_01.png`
- Relaxed 1.50 s: `preview/five_states/key_relaxed_02.png`

All 22 exact authored samples were additionally inspected through their large-view contact sheets:
- Idle: 0.00, 1.35, 3.00 s
- Cast: 0.65, 2.20, 2.95, 4.80 s
- Attack: 0.95, 2.65, 3.50, 3.80, 4.60, 7.20 s
- Hit: 0.08, 0.22, 0.42, 0.95 s
- Relaxed: 0.32, 0.95, 1.50, 2.55, 3.40 s

Contact sheets: `preview/five_states/contact_{idle,cast,attack,hit,relaxed}.png`.

## Observations limited to those samples

- Idle retains the neutral silhouette; its intentionally small breath is subtle in still images.
- Cast clearly raises the staff arm and free elbow into a chant/hold posture; the sampled recovery returns to the same neutral stance.
- Attack preserves the supplied mage chain. The 3.50 s sample extends the free hand toward screen-right; it is not a horizontal staff strike.
- Hit shows a brief chest/shoulder backward lean with following wrist/head movement and a neutral ending.
- Relaxed is distinguished by forward torso/head fatigue and lowered shoulders while the legs stay close to the repaired neutral stance.
- In these samples, the head, hands, boots, and sleeve connections remain visually attached. No new isolated limb fragment or obvious open joint seam was identified.
- The boot anchors appear consistent in the contact sheets. Absence of foot drift is supported by the separate all-frame geometry tests, rather than inferred from one still.
- The staff passes in front of the white-leg/boot silhouette during Cast and Relaxed, as it does in the supplied motion chain. This is visible depth overlap, not proof of gameplay collision behavior.
- State labels, local/total time, fixed camera, 320 px reference, and software-raster disclosure are readable in the inspected full PNGs.

## Separate verification stages

- Numeric: all 581 movie samples plus 22 exact key samples have automated bone-length, anchor, scale, reachability, signed-triangle-area, and state-boundary checks in `tests/five_states_validation.json`.
- Rendered: completion and MP4 properties are reported by the final render checks, not by this note.
- Visually inspected: the five full PNGs and 22 contact-sheet samples listed above only. The full movie has not been watched in a graphical player; there is no graphical session available in this task.
- Dead: excluded entirely. No death-pose or death-transition acceptance is implied.
