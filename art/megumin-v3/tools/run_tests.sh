#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export XDG_CACHE_HOME=/tmp/megumin-v3-cache XDG_CONFIG_HOME=/tmp/megumin-v3-config XDG_DATA_HOME=/tmp/megumin-v3-data
mkdir -p "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME"
godot --headless --path . --editor --import --quit > tests/import.log 2>&1
godot --headless --path . --script scripts/export_software_review.gd | tee tests/godot_export.log
godot --headless --path . --script tests/test_timeline.gd | tee tests/godot_timeline.log
python tools/validate_continuous.py
# Native scene can instantiate and tick without requiring a display server.
godot --headless --path . --quit-after 12 > tests/preview_smoke.log 2>&1
if grep -E 'SCRIPT ERROR|Parse Error|ERROR:' tests/preview_smoke.log; then exit 1; fi
