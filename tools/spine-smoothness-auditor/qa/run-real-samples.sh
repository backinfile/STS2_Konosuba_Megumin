#!/usr/bin/env bash
# Read-only input smoke tests. Original-game assets must be supplied locally.
set -euo pipefail
cd "$(dirname "$0")/.."
MEGUMIN_JSON="${MEGUMIN_JSON:-../../art/megumin-quartet-spine/actions-v9/export/megumin.json}"
OUTPUT_ROOT="${OUTPUT_ROOT:-out-real-samples}"

node bin/spine-audit.mjs --input "$MEGUMIN_JSON" --animations idle_loop,chant_enter,chant_loop --loops idle_loop,chant_loop --transition chant_enter:chant_loop --mix 0.2 --out "$OUTPUT_ROOT/megumin"

if [[ -n "${IRONCLAD_SKEL:-}" ]]; then
  node bin/spine-audit.mjs --input "$IRONCLAD_SKEL" --animations idle_loop,attack --loops idle_loop --transition attack:idle_loop --mix 0.2 --out "$OUTPUT_ROOT/ironclad"
else
  printf '%s\n' 'Skipped Ironclad: set IRONCLAD_SKEL to a legally available local .skel file.'
fi

if [[ -n "${LAGAVULIN_SKEL:-}" ]]; then
  node bin/spine-audit.mjs --input "$LAGAVULIN_SKEL" --animations idle_loop,wake_up,_tracks/eyes_closed_loop --loops idle_loop --transition wake_up:idle_loop --mix 0.2 --out "$OUTPUT_ROOT/lagavulin"
else
  printf '%s\n' 'Skipped Lagavulin: set LAGAVULIN_SKEL to a legally available local .skel file.'
fi
