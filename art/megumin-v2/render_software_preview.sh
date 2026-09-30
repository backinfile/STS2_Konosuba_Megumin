#!/usr/bin/env bash
# No display server, network listener, or source-image modification.
set -euo pipefail
cd "$(dirname "$0")"
export XDG_CACHE_HOME=/tmp/megumin-cache XDG_CONFIG_HOME=/tmp/megumin-config XDG_DATA_HOME=/tmp/megumin-data
mkdir -p "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" preview/software
godot --headless --path . --editor --import --quit
godot --headless --path . --script scripts/export_software_review.gd
python tools/render_software_review.py --parallel
ffmpeg -y -framerate 30 -i preview/software/frame_%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart -an preview/megumin_casting_v2.mp4
