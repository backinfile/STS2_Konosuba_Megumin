#!/usr/bin/env bash
# Run from an existing local graphical session. This script starts no display server.
set -euo pipefail
cd "$(dirname "$0")"
if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
  echo 'A local graphical session is required. Open this project in Godot, or run this script from a desktop terminal.' >&2
  echo 'The supplied MP4 is already rendered. Headless logic tests remain available through tools/run_tests.sh.' >&2
  exit 2
fi
command -v godot >/dev/null
command -v ffmpeg >/dev/null
mkdir -p preview
godot --path . --rendering-method gl_compatibility --audio-driver Dummy --fixed-fps 30 --write-movie preview/megumin_reel.avi -- --capture 2>&1 | tee preview/render.log
godot --path . --rendering-method gl_compatibility --audio-driver Dummy res://scenes/export_runtime.tscn 2>&1 | tee preview/export.log
ffmpeg -y -i preview/megumin_reel.avi -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart -an preview/megumin_reel.mp4 >preview/encode.log 2>&1
