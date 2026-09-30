#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/megumin-cache}" XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-/tmp/megumin-config}" XDG_DATA_HOME="${XDG_DATA_HOME:-/tmp/megumin-data}"
mkdir -p "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME"
godot --headless --path . --editor --import --quit
godot --headless --path . --script tests/test_rig.gd 2>&1 | tee tests/godot_test.log
