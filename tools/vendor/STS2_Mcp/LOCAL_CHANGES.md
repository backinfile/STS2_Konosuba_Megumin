# Project-local changes

The imported revision and original source are recorded in `PROVENANCE.json`.

- `McpMod.Recording.cs`: when `MEGUMIN_LAB=1`, refresh the native viewport immediately before each recording readback. The project launcher deliberately minimizes the game; without this refresh, Godot returns a stale frame even though animation time continues advancing. Ordinary installations keep the upstream recording behavior. Recording still follows real wall-clock playback, without seeking animation frames.
