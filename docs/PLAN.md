# Parcel Pilot implementation plan

> Executed inline by the author (full creative control was delegated). Code lives in the
> repo, not in this plan; each task lists files, interfaces, and how it is verified.
>
> **Status: complete.** M0 to M4 each landed as a commit that passed `tools/check.py`;
> captures for every milestone are in `docs/devlog/`, the timeline in `docs/progress/LOG.md`.

**Goal:** a complete, polished arcade sky-courier game whose every model is a Blender
script and every sound is synthesized, verified by automated player-camera captures.

**Architecture:** Blender headless builds `.glb` files from Python generators; Godot 4.7
imports them through a post-import script and a node naming contract; gameplay rules are
pure functions; an autopilot drives the same input interface as the player for tests.

**Tech stack:** Godot 4.7.2 (GDScript, Forward+), Blender 5.1.2 (bpy, bmesh), Python 3.11+
(numpy, Pillow) for tooling and audio synthesis.

**Spec:** `docs/DESIGN.md`

## Global constraints

* No downloaded, purchased, or AI-generated assets of any kind.
* Blender scripts are the source of truth; exports are never hand-edited.
* Deterministic: seeded RNG everywhere in generators and gameplay.
* Node naming contract from DESIGN.md section 9 is the only Blender/Godot coupling.
* Typed GDScript; tunables in `game/data/*.tres`.
* Never use the em dash character in any file, comment, doc, or commit message.
* Every milestone passes `python tools/check.py` and a screenshot review before commit.

## File map

```
blender/lib/            palette, geo, scene, export, registry            (M0, done)
blender/kit/            trees, buildings, rocks, islands, clouds         (M2)
blender/assets/         plane, parcel, hoop, rings, islands, props, logo (M1 blockout, M2 final)
tools/build_assets.py   Blender driver + contact sheets                  (M0, done)
tools/check.py          the verification gate                            (M1)
tools/synth/            audio synthesizer                                (M3)
game/pipeline/          post_import.gd                                   (M1)
game/data/              flight.tres, rules.tres                          (M1)
game/scripts/autoload/  game, controls, save, dev                        (M1)
game/scripts/rules/     delivery_rules.gd, game_rules.gd                 (M1)
game/scripts/flight/    plane.gd, flight_tuning.gd, player_input.gd, autopilot.gd (M1)
game/scripts/camera/    chase_camera.gd                                  (M1)
game/scripts/world/     island.gd, hoop.gd, pickup.gd, spinner.gd, world.gd (M1)
game/scripts/ui/        hud.gd, title.gd, results.gd, pause.gd           (M1, polished M3)
game/scenes/            main, world, island, plane, hoop, stamp, boost ring, ui scenes
game/shaders/           sky, cloud sea, speed lines                      (M2, M3)
game/tests/             runner scene, unit tests, scenarios              (M1)
docs/devlog/<m>/        milestone captures
```

## M1: greybox loop

1. **Blockout assets.** `blender/assets/{parcel,hoop,rings,islands,props}.py` with the final
   node contract (`MK_Delivery`, `SPIN_*`, `-col` proxies). Verify: contact sheets, report
   lists `MK_Delivery` on every destination island.
2. **Import conventions.** `game/pipeline/post_import.gd` + `[importer_defaults]` (no LODs,
   no tangents). Verify: headless import clean, collision bodies present on islands.
3. **Rules core.** `delivery_rules.gd` (tip, par time, time bonus, combo, rank, destination
   weighting), `game_rules.gd` resource. Verify: unit tests in `tests/unit/`.
4. **Flight.** `flight_tuning.gd`, `plane.gd` (CharacterBody3D, floating motion), input
   interface `get_controls() -> Vector3(turn, climb, boost)`, `player_input.gd`,
   `autopilot.gd`. Verify: scenario flies straight, turns, climbs; bot reaches a hoop.
5. **Camera.** `chase_camera.gd`: spring follow on the interpolated transform, look-ahead,
   FOV by speed, trauma shake API `add_trauma(amount)`.
6. **World + deliveries.** `island.gd` exposes `delivery_socket()`; `hoop.gd` emits
   `passed(island)`; `world.gd` owns islands, destination choice and pickups;
   `Game` autoload owns state machine `TITLE -> COUNTDOWN -> PLAYING <-> PAUSED -> RESULTS`.
7. **UI (plain).** HUD labels, title, pause, results; `Save` autoload persists best score.
8. **Gate.** `tools/check.py`, `tests/test_runner.tscn`, scenarios `bot_playthrough`
   (headless) and `tour` (windowed captures). Commit M1.

## M2: art pass

1. `blender/kit/` generators; final plane (lofted fuselage, biplane wings, pilot), parcel,
   hoop with pennants, boost ring, stamp, clouds, balloon, birds, storm cloud.
2. Ten island dioramas with strata undersides, dressing, sockets; islets.
3. Environment: sky shader, fog, cloud-sea shader, sun, post-processing; material tweaks in
   `post_import.gd`; spinners and FX sockets alive. Gate, review, commit M2.

## M3: juice

1. `tools/synth/`: DSP helpers, SFX set, music track, `build_audio.py`; `Audio` autoload
   with engine and wind loops tied to speed.
2. Particles: exhaust, wingtip trails, confetti, sparkles, crash debris, chimney smoke,
   waterfall mist, speed lines; camera trauma; hit-stop on crash.
3. UI polish: theme, tweens, destination card, edge arrow, popups, 3D title logo, results
   count-up and rank reveal, settings. Gate, review, commit M3.

## M4: ship

README (gallery, GIF via `--write-movie`), docs pass, final gate, private GitHub repo, push.
