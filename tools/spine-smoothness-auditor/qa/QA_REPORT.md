# Independent smoothness-auditor QA

Verified 2026-10-10 with Node v24.19.0 and official Spine runtime 4.2.120.

## Result

**33 independent adversarial tests pass. No outstanding correctness blocker found within the tested scope.** Real-data smoke checks also completed for Megumin v9 JSON, Ironclad binary, and Lagavulin Matriarch binary, with their existing matching atlas files. No game skeletons, textures, or other source assets are bundled here.

This verifies numerical/runtime behavior. It does not establish an artistic smoothness standard, visual quality score, or faithful reproduction of a game's multi-track controller.

## Defects found and corrected during review

1. Initial parser syntax error was corrected before integration testing.
2. Aggregate-statistic maximum calculations were made safe for large arrays, avoiding JavaScript argument-spread limits.
3. **Loop velocity false positive corrected:** A mathematically periodic 720°/second rotation originally reported a spurious velocity gap of 11.1254 normalized units/second. First/last one-frame secants represented different phases. The implementation now uses five-point endpoint derivative estimates and exposes a three-point comparison as a heuristic truncation uncertainty. A risk requires a gap beyond both the configured threshold and uncertainty. The periodic spin passes at 30, 60, and 120 FPS; a real endpoint velocity kink remains detected at all three rates.
4. Attachment identities were made deterministic across repeated loads, rather than relying on a global runtime object counter.
5. Unsorted/nonfinite input data and invalid transition windows/thresholds now fail explicitly.

The loop uncertainty remains a heuristic, not a rigorous error bound. Fewer than five matching samples yield unavailable velocity diagnostics instead of a false assurance.

## What the 33 tests cover

- Seconds-based derivatives; constant velocity at different durations; nonuniform derivative time grids; exact final sample with uniform actual intervals.
- Tenfold coordinate scaling preserves normalized motion.
- Position and velocity loop continuity, including smooth sine motion, real velocity kinks, periodic multi-turn spins, and short/zero-duration clips.
- World-angle ±180° crossing produces no wrap spike; true two-turn motion remains measurable; extreme authored angular rates emit an aliasing warning.
- Configurable source phase and source looping in transitions; actual AnimationState blending; zero-mix instantaneous cuts.
- Attachment swaps/removal are discrete events and do not fabricate vertex speeds.
- Mesh-only deformation, weighted meshes, region geometry with atlas metadata, deliberate region omission without an atlas, and triangle collapse detection.
- Sequential physics differs from disabled physics and repeats deterministically.
- Incompatible Spine versions, malformed JSON, missing bones, unsorted keys, overflowing transforms, invalid transition windows and invalid attachment/draw-order thresholds fail.
- All inspected result trees remain finite; unavailable derivative values are null.

## Real asset smoke results

All runs requested 60 FPS, used physics `none`, and used a 0.2-second transition mix. Input hashes, runtime metadata, final numerical values and exact code hashes are recorded in `real-sample-summary.json`.

- **Megumin:** idle_loop and chant_loop each have zero continuous signals and exact endpoint position agreement; their estimated endpoint velocity gaps are approximately 0.0000132 and 0.0000134 normalized units/second. chant_enter has 18 continuous signals, 52 discrete events and 67 geometry hints. chant_enter → chant_loop has zero continuous signals.
- **Ironclad:** idle_loop has zero continuous signals and no position/velocity seam alarm. attack has 5,509 point×time×metric signals, 109 discrete events and 19 geometry hints. attack → idle_loop has 105 signals under the selected generic mix.
- **Lagavulin Matriarch:** idle_loop has zero continuous signals and no position/velocity seam alarm. wake_up has 163 signals, 5 discrete events and 28 geometry hints. wake_up → idle_loop has zero signals. The actual zero-duration _tracks/eyes_closed_loop yields one valid frame and no derivative crash.

**These counts must not be ranked as aesthetic scores or interpreted as defect counts.** The original attack demonstrates why intentional impacts, swaps, rig density and runtime controller configuration require contextual review. Geometry-collapse hints can reflect intentional flattening, mirroring or existing thin triangles.

## Exact reproduction commands

From the auditor's project directory:

```sh
node qa/generate-fixtures.mjs
node --test qa/reliability.test.mjs
npm test
bash qa/run-real-samples.sh
```

`run-real-samples.sh` uses the repository-relative Megumin v9 input by default. Override `MEGUMIN_JSON` and optionally `OUTPUT_ROOT` when using a standalone copy. Original-game samples are optional: provide `IRONCLAD_SKEL` and `LAGAVULIN_SKEL` as legally available local file paths to run those checks; otherwise they are explicitly skipped. Matching same-basename atlas files are auto-detected; no texture PNG decoding is needed. Real assets are not required for the synthetic regression suite.

## Remaining limits

- Discrete events are sampled; subframe changes and high-frequency motion can be missed. Increase FPS for suspect intervals. Fast-spin key-rate hints cannot eliminate all aliasing from constraints, combined bones or nonlinear curves.
- Motion uses selected world-space landmarks, with a configurable per-mesh vertex cap; localized deformation at an unsampled vertex may be missed by motion derivatives. Triangle checks use all mesh vertices.
- Visible geometry means active attachments above the alpha threshold before clipping/occlusion. No pixel rendering, texture/silhouette comparison, camera motion, anti-aliasing, or real frame pacing is analyzed.
- Physics starts from reset and is not pre-settled. A first-cycle seam is not a verdict on a settled physical loop.
- Transition sampling is one track with specified phase/mix. A game's multi-track state machine, interruptions, external physics offsets, or other settings can differ.
- Only Spine 4.2 exports are supported by the pinned runtime.
