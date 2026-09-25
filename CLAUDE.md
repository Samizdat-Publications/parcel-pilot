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

- `python tools/build_assets.py [--only name]` rebuild models, previews, icons
- `python tools/build_audio.py` then `python tools/audio_report.py` rebuild and check sounds
- `python tools/check.py --milestone <m> [--showcase]` the full gate
- `python tools/lookdev.py variants.json` compare lighting variants side by side
- `python tools/snap.py "caption"` add a progress snapshot to docs/progress
- `python tools/make_clip.py` record gameplay into docs/media/gameplay.webp
- Autoloads must not `preload` assets (they compile before a fresh clone's first import).
- Quit from scenarios and tests only after `await Audio.shutdown()` so nothing leaks.
