# Handoff: Parcel Pilot

Read this first in a new session. Project root: `C:\Users\stewa\ClaudeProjects\Opu5.5 Game Prompt\parcel-pilot`
(its own git repo; private GitHub repo https://github.com/Samizdat-Publications/parcel-pilot).
The parent folder holds other sessions' games (`woolgather/`, `colossus/`, `5 game test/`): never touch them,
never write at the parent root. Also read `CLAUDE.md` (rules) and `README.md` (overview).

## State (2026-09-26)

Milestones M0 to M5 are done and pushed: a complete arcade sky-courier game in Godot 4.7.2 with every model a
Blender 5.1 Python script and every sound synthesized in Python. `python tools/check.py --milestone m5 --skip-assets`
passed (import, unit, input, bot, capture); M4 passed all eight steps. A fresh clone imports with zero errors and
passes the headless tests without Blender.

M5 (2026-09-26) is the public site, live on Cloudflare Pages:
- Landing page: https://parcel-pilot-1ms.pages.dev/ (`parcel-pilot.pages.dev` was taken, so Cloudflare added `-1ms`)
- The game in the browser: https://parcel-pilot-1ms.pages.dev/play/
- Pages project `parcel-pilot` (production branch `main`), deployed with wrangler 4 from this machine's login.

## Run the game

PowerShell (note the `&` call operator):
```powershell
& "C:\Users\stewa\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64.exe" --path "C:\Users\stewa\ClaudeProjects\Opu5.5 Game Prompt\parcel-pilot\game"
```
Or open `game/project.godot` in the Godot editor and press F5.

## Windows .exe (done)

Built and verified on 2026-09-24: `build/export/ParcelPilot.exe` (single 114 MB file, game data embedded;
build/ is gitignored so it is not in the repo). The exported exe ran the full capture tour with zero errors at
212 fps. Only the Windows templates were installed (from the official 4.7.2 archive) into
`%APPDATA%\Godot\export_templates\4.7.2.stable\`; other platforms would need the full template set.
Launch it from PowerShell:
```powershell
& "C:\Users\stewa\ClaudeProjects\Opu5.5 Game Prompt\parcel-pilot\build\export\ParcelPilot.exe"
```
To rebuild after changes, run step 3 below. For a fresh machine, the full recipe:

`game/export_presets.cfg` has a "Windows Desktop" preset (single exe, pck embedded) that writes
`build/export/ParcelPilot.exe`. It needs Godot's export templates:

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

## The public site (M5)

Three commands, from the project root:
1. `python tools/film.py [shift] [features] [islands]` films reels under Godot's movie maker (1080p; the shift at
   `--fps 30`, the others at 60) into `build/film/<shoot>.mp4` + `.json` marks. About 4 to 10 minutes each; the
   MJPEG .avi is converted and deleted as it goes.
2. `python tools/make_media.py [--only stills milestones sounds hero og clips islands shift readme]` cuts
   `site/media/` (committed) and `docs/media/*.webp` (README) from those, placed by the marks. About 15 minutes.
3. `python tools/build_site.py --deploy` exports the Web preset to `build/web`, assembles `site-dist/` (gitignored)
   and runs `npx --yes wrangler@4 pages deploy site-dist --project-name parcel-pilot --branch main --commit-dirty=true`.
   `--serve` runs `wrangler pages dev` on http://localhost:8788 instead (the Range function works there too).

How the web build works, and why:
- Web export preset "Web": no threads (no COOP/COEP headers needed), Compatibility renderer, custom shell
  `game/web/shell.html` (themed loader, controls hint, touch-only warning, warm-up message).
- The engine `index.wasm` is ~40 MB, over Pages' 25 MiB file limit: `build_site.py` splits it into
  `index.part1.wasm` + `index.part2.wasm` and injects the list into the shell, whose fetch shim streams them back as
  one response. The parts keep a .wasm name so Cloudflare compresses them.
- Compatibility has no SSAO and fogs the cloud sea brighter: `world.gd` sets a deeper sea and no height fog there
  (matched to Forward+ with lookdev). Flags don't wave there (`ambient_fx.gd`), and the pause menu has no Quit.
- Draw calls: every palette color used to be its own surface (~40 per island). `post_import.gd` `_merge_palette`
  merges each mesh's palette surfaces into one for `shaders/palette.gdshader` (COLOR = sRGB color + roughness,
  UV2 = metallic + glow); soft cloud, unshaded and transparent surfaces stay separate (water was made opaque so it
  merges). Draw calls ~490 -> ~100 (desktop too), same look (checked against the M4 captures). Flag colors are read
  from vertex colors now (`ambient_fx.gd wave_flag`).
- First visit cost is shader compilation: Chrome on Windows (ANGLE D3D11) takes ~2.5 s per distinct material
  shader, twice (plain and instanced). One palette shader cut a cold start from ~60 s to ~30 s (live site, network
  included). A warm start (browser shader cache) is ~5 s. What's left: Godot's own fallback shaders (~10 s), the
  soft cloud material and the cloud sea. To measure again, instrument `WebGL2RenderingContext.prototype.linkProgram`
  in Chrome via Playwright (`channel="chrome"`, `--use-angle=d3d11 --enable-gpu --ignore-gpu-blocklist`).
- Frame rate: the web build was CPU-bound on a GPU sync, not on game logic. Emscripten's `blitOffscreenFramebuffer`
  calls `gl.getParameter(SCISSOR_TEST)` every frame, which waits for the GPU process; the shell tracks that state
  itself. Measured in a visible Chrome at 1600x900: ~44 fps -> 54 (machine busy with other sessions' bots) / 68
  (idle). Caching Godot's per-frame `checkFramebufferStatus` too was measured and did not help, so it's not in.
  The web build also uses 2 shadow cascades over 300 m (`world.gd`): shadows were over half the draw calls.
- Videos: Pages ignores Range requests, which Safari needs; `functions/media/[[path]].js` answers them for the
  .mp4 files only (`_routes.json` and `functions/media/sizes.json` are written by `build_site.py`).
- Tooling needs `pip install imageio-ffmpeg` (ffmpeg with x264; `tools/toolpaths.py ffmpeg()`), Node for npx, and
  Playwright only for browser testing.

## Daily commands (from the project root)

- `python tools/check.py --milestone <name> [--showcase]` the gate; must be ALL GREEN before any commit
- `python tools/build_assets.py [--only name]` rebuild models (+ previews, icons) after editing `blender/`
- `python tools/build_audio.py` then `python tools/audio_report.py` after editing `tools/synth/`
- `python tools/lookdev.py <variants.json>` side-by-side lighting variants
- `python tools/snap.py "caption"` add a progress entry to `docs/progress/LOG.md`
- `python tools/make_clip.py` re-record `docs/media/gameplay.webp` (about 8 minutes)
- `python tools/build_site.py --serve` / `--deploy` the public site (see above)

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

- The Windows exe is not on the site: Pages can't host a 114 MB file. A public GitHub release would need the repo
  to be public (it is private), or use R2. Ask Stewart before making anything public.
- Web cold start could drop further by giving the cloud puffs the shared palette shader (costs their rim light).

- Rank thresholds (400 / 900 / 1500) were tuned against the bot, which never mistakes; playtest and adjust.
- Optional: publish a private Artifact devlog from `docs/progress` and `docs/devlog`; add a GitHub release with the exe.
