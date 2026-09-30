# Megumin casting v2

A standalone editable Godot 4.6 key-pose animation study. Open `project.godot`, press Space to replay. VFX are off by default.

- Review movie: `preview/megumin_casting_v2.mp4`
- Integration / event timing / limitations: `docs/INTEGRATION.md`
- Art direction and provenance: `docs/V2_ART_DIRECTION.md`, `docs/ART_PROVENANCE.md`
- Source-art moiré checks: `docs/MOIRE_CHECK.txt`
- Native logic tests: `tools/run_tests.sh`
- Rebuild no-window review: `render_software_preview.sh` (Godot, Python + NumPy/Pillow, ffmpeg)

The MP4 is an explicitly labeled software raster preview of actual Godot animation/mesh output. A real Godot graphical capture and STS2 integration have not been verified. Attack is now 3.50s with a single impact marker at 1.55s; v1's 0.72s timing does not apply.
