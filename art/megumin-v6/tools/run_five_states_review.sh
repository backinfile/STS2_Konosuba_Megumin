#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export XDG_CACHE_HOME=/tmp/megumin-five-cache XDG_CONFIG_HOME=/tmp/megumin-five-config XDG_DATA_HOME=/tmp/megumin-five-data
mkdir -p "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" preview/five_states
# Existing rig/resources must already be imported. No source/track builder runs.
godot --headless --path . --script scripts/export_five_states_review.gd > tests/five_states_export.log 2>&1
python -B tools/test_five_states_review.py --no-images > tests/five_states_validation.log 2>&1
python -B tools/render_five_states_review.py --parallel > tests/five_states_render.log 2>&1
python -B tools/contact_five_states_review.py > tests/five_states_contacts.log 2>&1
ffmpeg -hide_banner -y -framerate 30 -i preview/five_states/frame_%04d.png -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart preview/megumin_v6_five_states_review.mp4 > tests/five_states_encode.log 2>&1
python -B tools/test_five_states_review.py > tests/five_states_validation.log 2>&1
# Manual inspection of key PNGs remains separate from these automatic checks.
