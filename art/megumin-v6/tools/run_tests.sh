#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export XDG_CACHE_HOME=/tmp/megumin-v6-cache XDG_CONFIG_HOME=/tmp/megumin-v6-config XDG_DATA_HOME=/tmp/megumin-v6-data
mkdir -p "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME"
godot --headless --path . --editor --import --quit > tests/import.log 2>&1
godot --headless --path . --script scripts/export_software_review.gd > tests/export.log 2>&1
python tools/validate_v6.py
godot --headless --path . --script tests/test_continuity.gd > tests/continuity.log 2>&1
godot --headless --path . --quit-after 12 > tests/preview_smoke.log 2>&1
if grep -E 'ERROR:|SCRIPT ERROR|Parse Error' tests/preview_smoke.log tests/continuity.log; then exit 1; fi
