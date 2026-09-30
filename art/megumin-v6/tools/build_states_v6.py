"""Build independent v6 animation resources without changing the approved MageCast.

All numeric body channels are authored in source pixels / degrees and sampled at
60 Hz with the same minimum-jerk easing and LINEAR interpolation as build_timeline.
This builder owns only animations/{Idle,Cast,Attack,Hit,Relaxed}.tres.

Lower-body movement follows the revised front-flexing knee rig: no pelvic roll,
at most 1 px lateral hip travel, and 0..1.5 px hip sink (Hit may use 2 px).
Fatigue is carried by shoulders, torso, and head rather than a deep crouch.
Dead.tres is deliberately excluded: its separate contact-constrained design is
owned by the rig author; the obsolete deep-crouch draft must not be regenerated.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FPS = 60
BODY_PROPERTIES = (
    "hip_x", "hip_drop", "pelvis_roll", "torso_lean", "head_tilt",
    "R_shoulder", "R_elbow", "R_wrist", "L_shoulder", "L_elbow", "L_wrist",
    "cape_strength",
)
NUMERIC_PROPERTIES = BODY_PROPERTIES + ("staff_ground_contact",)
BASE = {prop: 0.0 for prop in NUMERIC_PROPERTIES}
BASE["cape_strength"] = 0.35


@dataclass(frozen=True)
class State:
    duration: float
    keys: tuple[tuple[float, dict[str, float]], ...]
    loop: bool = False
    face_keys: tuple[tuple[float, int], ...] = ((0.0, 0),)
    note: str = ""


# Every pose is a complete offset from BASE: unspecified fields are neutral,
# rather than inheriting an accidental state from a previous clip.
STATES = {
    "Idle": State(3.0, (
        (0.0, {}),
        (0.60, {"hip_x": -0.05, "hip_drop": 0.35,
                "torso_lean": -0.15, "head_tilt": -0.12,
                "R_shoulder": 0.22, "R_elbow": -0.18, "R_wrist": 0.10,
                "L_shoulder": -0.20, "L_elbow": -0.25, "L_wrist": 0.10,
                "cape_strength": 0.37}),
        (1.35, {"hip_x": 0.05, "hip_drop": 0.90,
                "torso_lean": 0.30, "head_tilt": -0.25,
                "R_shoulder": 0.45, "R_elbow": -0.35, "R_wrist": -0.40,
                "L_shoulder": -0.45, "L_elbow": -0.50, "L_wrist": 0.20,
                "cape_strength": 0.43}),
        (2.15, {"hip_x": 0.02, "hip_drop": 0.40,
                "torso_lean": 0.10, "head_tilt": 0.10,
                "R_shoulder": 0.15, "R_elbow": -0.10, "R_wrist": -0.20,
                "L_shoulder": -0.15, "L_elbow": -0.20, "L_wrist": -0.10,
                "cape_strength": 0.40}),
        (3.0, {}),
    ), loop=True, note="3 s resting breath; hip_drop 0..0.9 px, no pelvic roll; rig supplies the matching 3 s cape phase."),
    "Cast": State(4.8, (
        (0.0, {}),
        (0.20, {}),
        (0.65, {"hip_x": -0.30, "hip_drop": 0.75, "torso_lean": -3, "head_tilt": -1,
                "R_shoulder": 8, "R_elbow": -5, "R_wrist": -5,
                "L_shoulder": -12, "L_elbow": -12, "L_wrist": -6,
                "cape_strength": 0.50}),
        (1.60, {"hip_x": -0.40, "hip_drop": 0.60, "torso_lean": -3, "head_tilt": -2,
                "R_shoulder": 35, "R_elbow": 12, "R_wrist": -40,
                "L_shoulder": -58, "L_elbow": -62, "L_wrist": -10,
                "cape_strength": 0.80}),
        (2.20, {"hip_x": -0.25, "hip_drop": 0.40, "torso_lean": -3, "head_tilt": -3,
                "R_shoulder": 40, "R_elbow": 15, "R_wrist": -42,
                "L_shoulder": -75, "L_elbow": -80, "L_wrist": 0,
                "cape_strength": 1.05}),
        (2.95, {"hip_x": -0.25, "hip_drop": 0.60, "torso_lean": -3, "head_tilt": -3,
                "R_shoulder": 40, "R_elbow": 15, "R_wrist": -42,
                "L_shoulder": -75, "L_elbow": -80, "L_wrist": 0,
                "cape_strength": 1.12}),
        (3.65, {"hip_x": -0.25, "hip_drop": 0.65, "torso_lean": -2, "head_tilt": 1,
                "R_shoulder": 22, "R_elbow": 5, "R_wrist": -24,
                "L_shoulder": -38, "L_elbow": -38, "L_wrist": -5,
                "cape_strength": 0.65}),
        (4.55, {}),
        (4.8, {}),
    ), note="Gather, raise elbow/staff, chant/charge hold 2.20..2.95 s, lower and return to Idle; no release or damage event."),
    "Hit": State(0.95, (
        (0.0, {}),
        (0.08, {"hip_x": -0.20, "hip_drop": 0.60,
                "torso_lean": -6, "head_tilt": -2,
                "R_shoulder": -2, "R_elbow": 3, "R_wrist": 4,
                "L_shoulder": 3, "L_elbow": -5, "L_wrist": -3,
                "cape_strength": 0.55}),
        (0.22, {"hip_x": -0.60, "hip_drop": 2.0,
                "torso_lean": -10, "head_tilt": -5,
                "R_shoulder": -2, "R_elbow": 4, "R_wrist": 6,
                "L_shoulder": 6, "L_elbow": -10, "L_wrist": -4,
                "cape_strength": 0.95}),
        (0.42, {"hip_x": -0.20, "hip_drop": 1.10,
                "torso_lean": 2, "head_tilt": 3,
                "R_shoulder": 4, "R_elbow": -4, "R_wrist": -1,
                "L_shoulder": -3, "L_elbow": -8, "L_wrist": 3,
                "cape_strength": 0.85}),
        (0.68, {"hip_x": -0.10, "hip_drop": 0.30, "torso_lean": 0.5,
                "head_tilt": 0.5, "R_shoulder": 1, "R_elbow": -1,
                "L_shoulder": -1, "L_elbow": -2, "cape_strength": 0.48}),
        (0.95, {}),
    ), note="Short chest/shoulder recoil, at most 2 px hip sink, delayed wrist/head rebound; feet remain constrained by the rig."),
    "Relaxed": State(3.4, (
        (0.0, {}),
        (0.32, {"hip_x": -0.30, "hip_drop": 0.75,
                "torso_lean": 3, "head_tilt": 6,
                "R_shoulder": 6, "R_elbow": -3, "R_wrist": -3,
                "L_shoulder": -5, "L_elbow": -12, "L_wrist": 0,
                "cape_strength": 0.60}),
        (0.95, {"hip_x": -0.90, "hip_drop": 1.50,
                "torso_lean": 12, "head_tilt": 17,
                "R_shoulder": 13, "R_elbow": -5, "R_wrist": -6,
                "L_shoulder": -10, "L_elbow": -20, "L_wrist": 0,
                "cape_strength": 0.65}),
        (1.50, {"hip_x": -0.90, "hip_drop": 1.50,
                "torso_lean": 12, "head_tilt": 17,
                "R_shoulder": 13, "R_elbow": -5, "R_wrist": -6,
                "L_shoulder": -10, "L_elbow": -20, "L_wrist": 0,
                "cape_strength": 0.42}),
        (2.55, {"hip_x": -0.20, "hip_drop": 0.60,
                "torso_lean": 3, "head_tilt": 5,
                "R_shoulder": 4, "R_elbow": -1, "R_wrist": -2,
                "L_shoulder": -3, "L_elbow": -6, "L_wrist": 0,
                "cape_strength": 0.36}),
        (3.10, {}),
        (3.40, {}),
    ), note="Brief post-explosion fatigue carried by head/shoulders/torso; at most 1.5 px hip sink, pause, then recover to Idle."),

}


def minimum_jerk(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)


def sample(state: State, time: float) -> dict[str, float]:
    """Exactly the segment semantics of the approved timeline generator."""
    index = 0
    for index in range(len(state.keys) - 1):
        if time <= state.keys[index + 1][0] + 1e-8:
            break
    t0, a = state.keys[index]
    t1, b = state.keys[index + 1]
    s = minimum_jerk((time - t0) / (t1 - t0))
    return {prop: a.get(prop, BASE[prop]) +
            (b.get(prop, BASE[prop]) - a.get(prop, BASE[prop])) * s
            for prop in NUMERIC_PROPERTIES}


def dense_samples(state: State) -> list[tuple[float, dict[str, float]]]:
    count = round(state.duration * FPS)
    assert math.isclose(count / FPS, state.duration, abs_tol=1e-9)
    return [(i / FPS, sample(state, i / FPS)) for i in range(count + 1)]


def value_track(index: int, prop: str, pairs, *, loop: bool = False,
                discrete: bool = False) -> str:
    pairs = list(pairs)
    times = ", ".join(f"{time:.7f}" for time, _ in pairs)
    transitions = ", ".join("1" for _ in pairs)
    values = ", ".join(str(int(value)) if discrete else f"{value:.7f}"
                       for _, value in pairs)
    return (
        f'tracks/{index}/type = "value"\n'
        f'tracks/{index}/path = NodePath(".:{prop}")\n'
        f'tracks/{index}/interp = {0 if discrete else 1}\n'
        f'tracks/{index}/loop_wrap = {str(loop).lower()}\n'
        f'tracks/{index}/enabled = true\n'
        f'tracks/{index}/keys = {{\n'
        f'"times": PackedFloat32Array({times}),\n'
        f'"transitions": PackedFloat32Array({transitions}),\n'
        f'"update": {1 if discrete else 0},\n'
        f'"values": [{values}]\n}}\n'
    )


def render_state(name: str, state: State) -> str:
    dense = dense_samples(state)
    text = ('[gd_resource type="Animation" format=3]\n\n[resource]\n'
            f'resource_name = "{name}"\nlength = {state.duration:g}\n'
            f'loop_mode = {1 if state.loop else 0}\n')
    for index, prop in enumerate(NUMERIC_PROPERTIES):
        text += value_track(index, prop,
                            ((time, pose[prop]) for time, pose in dense),
                            loop=state.loop)
    face = list(state.face_keys)
    if face[-1][0] < state.duration:
        face.append((state.duration, face[-1][1]))
    text += value_track(len(NUMERIC_PROPERTIES), "face_state", face,
                        loop=state.loop, discrete=True)
    return text


def render_attack() -> str:
    """Copy approved track bytes, then append resets and one impact method key."""
    source = (ROOT / "animations/MageCast.tres").read_text()
    assert source.count('resource_name = "MageCast"') == 1
    assert re.findall(r'tracks/(\d+)/type', source) == [str(i) for i in range(12)]
    assert 'length = 7.2' in source
    assert all(f'NodePath(".:{prop}")' in source for prop in BODY_PROPERTIES)
    # Attack is never silently clamped: a source regression must fail the build.
    for index, prop in enumerate(BODY_PROPERTIES[:3]):
        block = re.search(rf'tracks/{index}/keys = \{{(.*?)\n\}}', source, re.S)
        assert block is not None, prop
        values = re.search(r'"values": \[(.*?)\]', block.group(1), re.S)
        assert values is not None, prop
        samples = [float(value.strip()) for value in values.group(1).split(",")]
        if prop == "hip_x":
            assert all(abs(value) <= 1.0 for value in samples), "Attack hip_x source regression"
        elif prop == "hip_drop":
            assert all(0 <= value <= 1.5 for value in samples), "Attack hip_drop source regression"
        else:
            assert all(value == 0 for value in samples), "Attack pelvis_roll source regression"
    text = source.replace('resource_name = "MageCast"', 'resource_name = "Attack"', 1)
    if not text.endswith("\n"):
        text += "\n"
    text += value_track(12, "staff_ground_contact", ((0, 0), (7.2, 0)))
    text += value_track(13, "face_state", ((0, 0), (7.2, 0)), discrete=True)
    text += ('tracks/14/type = "method"\n'
             'tracks/14/path = NodePath(".")\n'
             'tracks/14/interp = 1\n'
             'tracks/14/loop_wrap = false\n'
             'tracks/14/enabled = true\n'
             'tracks/14/keys = {\n'
             '"times": PackedFloat32Array(3.5),\n'
             '"transitions": PackedFloat32Array(1),\n'
             '"values": [{"method": &"_emit_attack_impact", "args": []}]\n}\n')
    assert text.split('tracks/12/type')[0] == source.replace(
        'resource_name = "MageCast"', 'resource_name = "Attack"', 1)
    return text


def validate_authored_states() -> None:
    """Checks resource data only; cannot replace native geometry/visual review."""
    anatomy = json.loads((ROOT / "assets/anatomy_v6.json").read_text())
    assert set(anatomy["bone_lengths_px"]) == {"R", "L"}
    reference = json.loads((ROOT / "animations/art_directed_keys.json").read_text())
    assert tuple(reference["properties"]) == BODY_PROPERTIES
    assert reference["duration"] == 7.2
    for name, state in STATES.items():
        assert state.keys[0][0] == 0 and state.keys[-1][0] == state.duration, name
        assert all(t1 > t0 for (t0, _), (t1, _) in zip(state.keys, state.keys[1:])), name
        assert all(set(pose) <= set(NUMERIC_PROPERTIES) for _, pose in state.keys), name
        dense = dense_samples(state)
        assert all(math.isfinite(value) for _, pose in dense for value in pose.values()), name
        assert all(0 <= pose["staff_ground_contact"] <= 1 for _, pose in dense), name
        assert all(value in (0, 1) for _, value in state.face_keys), name
        assert dense[0][1] == BASE and dense[-1][1] == BASE, name
        max_drop = 2.0 if name == "Hit" else 1.5
        assert all(0 <= pose["hip_drop"] <= max_drop for _, pose in dense), name
        assert all(abs(pose["hip_x"]) <= 1.0 for _, pose in dense), name
        assert all(pose["pelvis_roll"] == 0.0 for _, pose in dense), name
        assert all(pose["staff_ground_contact"] == 0.0 for _, pose in dense), name
        assert all(value == 0 for _, value in state.face_keys), name



def main() -> None:
    validate_authored_states()
    outputs = {name: render_state(name, state) for name, state in STATES.items()}
    outputs["Attack"] = render_attack()
    for name in ("Idle", "Cast", "Attack", "Hit", "Relaxed"):
        path = ROOT / "animations" / f"{name}.tres"
        path.write_text(outputs[name])
        duration = STATES[name].duration if name in STATES else 7.2
        print(f"{name}: {duration:g} s -> {path.relative_to(ROOT)}")
        print("  " + (STATES[name].note if name in STATES else
              "Exact approved MageCast body tracks; _emit_attack_impact once at 3.5 s; game damage synchronization not yet verified."))
    print("Numeric authoring checks passed. Native resource/runtime/visual checks are separate.")
    print("Dead.tres was not generated or modified.")


if __name__ == "__main__":
    main()
