# Parcel Pilot: project guide for Claude

This folder is its own git repo inside the `Opu5.5 Game Prompt` master folder. Other games
in sibling folders are built by other sessions: never touch files outside `parcel-pilot/`.

Read `docs/DESIGN.md` (spec) and `docs/PLAN.md` (milestones) first.

## Non-negotiables

- Every model comes from a Blender Python script in `blender/assets/` built with the kit in
  `blender/lib/`. The `.glb` files in `game/assets/models/` are outputs: never hand-edit them,
  never commit `.blend` files. Rebuild with `python tools/build_assets.py`.
- Every sound comes from the synthesizer in `tools/synth/`. No downloaded or generated-by-AI
  assets of any kind.
- Colors come only from `blender/lib/palette.py`.
- Node naming contract (Blender object names read by Godot code): `MK_*` gameplay sockets,
  `FX_*` effect sockets, `SPIN_*` spinning parts, `-col` / `-convcolonly` collision.
- Models face +Y in Blender (Godot -Z). Meters. Seeded randomness only.
- Typed GDScript, tabs. Tunables live in `game/data/*.tres`; rules are pure functions in
  `game/scripts/rules/` with unit tests.
- No em dash characters anywhere (code, comments, docs, commits).

## Workflow

Build, then RUN and look. `python tools/check.py` is the gate: asset build, headless import,
headless tests (including a bot playthrough), windowed captures from the player camera into
`docs/devlog/`, and a log scan that fails on any error or warning. Review the screenshots
before calling anything done. Commit at every working milestone.

Tools: Godot 4.7.2 console build and Blender 5.1.2 are auto-detected by `tools/toolpaths.py`
(override with the `GODOT` and `BLENDER` environment variables).
