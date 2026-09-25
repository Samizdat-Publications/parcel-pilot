# Handoff: Parcel Pilot

Read this first in a new session. Project root: `C:\Users\stewa\ClaudeProjects\Opu5.5 Game Prompt\parcel-pilot`
(its own git repo; private GitHub repo https://github.com/Samizdat-Publications/parcel-pilot).
The parent folder holds other sessions' games (`woolgather/`, `colossus/`, `5 game test/`): never touch them,
never write at the parent root. Also read `CLAUDE.md` (rules) and `README.md` (overview).

## State (2026-09-24)

Milestones M0 to M4 are done and pushed: a complete arcade sky-courier game in Godot 4.7.2 with every model a
Blender 5.1 Python script and every sound synthesized in Python. `python tools/check.py --milestone m4 --showcase`
passed all eight steps (assets, audio, import, unit, input, bot, capture, showcase). A fresh clone imports with zero
errors and passes the headless tests without Blender.

## Run the game

PowerShell (note the `&` call operator):
```powershell
& "C:\Users\stewa\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64.exe" --path "C:\Users\stewa\ClaudeProjects\Opu5.5 Game Prompt\parcel-pilot\game"
```
Or open `game/project.godot` in the Godot editor and press F5.

## Build the Windows .exe (the open task)

`game/export_presets.cfg` already has a "Windows Desktop" preset (single exe, pck embedded) that writes
`build/export/ParcelPilot.exe` (build/ is gitignored). The only missing piece is Godot's export templates:

1. Download the official templates for this exact version:
   https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_export_templates.tpz
   (a zip, roughly 1 GB). Easier alternative: in the editor, Editor > Manage Export Templates > Download and Install.
2. If installing by hand: extract the files inside the archive's `templates/` folder into
   `%APPDATA%\Godot\export_templates\4.7.2.stable\` (the folder must contain `version.txt` and
   `windows_release_x86_64.exe`).
3. Export (from the project root, Git Bash):
   `"/c/Users/stewa/Downloads/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe" --headless --path game --export-release "Windows Desktop" ../build/export/ParcelPilot.exe`
4. Check: launch the exe and fly a shift. `build/export/ParcelPilot.exe -- --scenario=tour --out=<dir>` also works
   in the exported build (the Dev harness is included) if you want automated captures from it.
If the export complains about `application/modify_resources` (icon editing), set it to `false` in the preset.

## Daily commands (from the project root)

- `python tools/check.py --milestone <name> [--showcase]` the gate; must be ALL GREEN before any commit
- `python tools/build_assets.py [--only name]` rebuild models (+ previews, icons) after editing `blender/`
- `python tools/build_audio.py` then `python tools/audio_report.py` after editing `tools/synth/`
- `python tools/lookdev.py <variants.json>` side-by-side lighting variants
- `python tools/snap.py "caption"` add a progress entry to `docs/progress/LOG.md`
- `python tools/make_clip.py` re-record `docs/media/gameplay.webp` (about 8 minutes)

## Where things live

- Flight: `game/scripts/flight/plane.gd` (class `MailPlane`), `autopilot.gd`, tuning in `game/data/flight.tres`
- Rules: `game/scripts/rules/delivery_rules.gd` (pure, unit tested), numbers in `game/data/rules.tres`
- Flow and feel: `game/scripts/main.gd`; state machine `game/scripts/autoload/game.gd`
- Level layout: `game/scenes/world/world.tscn`; island sockets read by `game/scripts/world/island.gd`
- UI: `game/scripts/ui/` (design system in `ui_kit.gd`); effects `game/scripts/fx/`; shaders `game/shaders/`
- Models: `blender/assets/` (islands in `blender/assets/archipelago/`), kit in `blender/kit/`, palette `blender/lib/palette.py`

## Gotchas already learned

- `Plane` is a built-in Godot type: the plane class is `MailPlane`.
- Sky shader: clamp every `pow()` base (an unclamped zenith sample made NaN radiance and a black world).
- Autoloads must not `preload` assets; they compile before a fresh clone's first import. Load in `_ready`.
- Scenarios and the test runner quit only after `await Audio.shutdown()`, or streams leak at exit and fail the gate.
- Island tops are at local z=0 in Blender; models face +Y (Godot -Z); only object names couple Blender and Godot.
- `cd` in the Bash tool changes the session's working directory: use absolute paths.
- The user's terminal is PowerShell: give PowerShell syntax (`&` for quoted exe paths).
- Never use the em dash character anywhere (user rule).

## Ideas if continuing

- Rank thresholds (400 / 900 / 1500) were tuned against the bot, which never mistakes; playtest and adjust.
- Optional: publish a private Artifact devlog from `docs/progress` and `docs/devlog`; add a GitHub release with the exe.
