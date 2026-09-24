# Parcel Pilot: design spec

Status: approved by delegation (the brief granted full creative control). Owner: Claude.

## 1. Pitch

You fly a chunky little mail plane across an archipelago of floating islands at golden
hour. Every delivery hands you the next parcel, so the shift is one continuous chain of
flights: thread the delivery hoop, grab a time bonus, keep the combo alive. Crazy Taxi's
clock pressure, in a toy-diorama sky.

A run lasts 2 to 5 minutes. It is fun inside 10 seconds and has a score worth beating.

## 2. Pillars

1. **Feels good to fly.** Arcade handling, auto-banking, speed you can feel (FOV, wind,
   particles). No stalls, no fuel management, no punishing crashes.
2. **Handmade by code.** Every model is a Blender Python script; every sound is synthesized
   by a Python script. No downloaded, bought, or AI-generated assets.
3. **Readable at a glance.** One active destination, a beacon you can see from anywhere,
   an arrow when it is off screen, a tip that visibly drains.
4. **Always verifiable.** Every milestone ends with an automated run that captures errors
   and screenshots from the player camera, and a human-quality review of those shots.

## 3. Core loop and rules

```
start shift at the Post Office with a parcel
  -> fly to the destination island (beacon + HUD arrow)
  -> pass through its delivery hoop
       tip = base(distance) x speed factor x damage factor x combo
       time bonus added to the shift clock
       recipient hands you the next parcel (new destination)
  -> repeat until the clock hits 0 -> results (score, rank, best)
```

| Rule | Value (tunable in `game/data/rules.tres`) |
|---|---|
| Starting clock | 90 s |
| Par time | distance / 24 m/s x 1.25 + 5 s |
| Base tip | 60 + 0.12 x distance (m) |
| Tip decay | 100% at pickup, 50% at par, 25% at 2x par (floor 25%) |
| Time bonus | Express (<= 60% par) +15 s, On time (<= par) +10 s, Late +5 s |
| Combo | Express or on-time deliveries with no crash: x1.0, x1.25, x1.5, x1.75, x2.0 (cap) |
| Crash | parcel damage: tip x0.85, breaks the combo, 1 s bounce and brief invulnerability |
| Stamps (collectibles) | +25 points, +3 s, respawn after 45 s |
| Boost | meter 0..1, drains 0.35/s, passive refill 0.06/s, boost ring +0.35 |
| Falling into the cloud sea | respawn above the Post Office, -5 s |
| Ranks | Trainee, Courier (400), Ace Courier (900), Sky Postmaster (1500) |

Destination choice: random island other than the current one, weighted toward 250 to 600 m
flights so legs stay interesting. The first leg of a shift is always a short one.

## 4. Controls

| Action | Keyboard | Gamepad |
|---|---|---|
| Climb / dive | W / S (or Up / Down) | Left stick Y |
| Turn (auto-banks) | A / D (or Left / Right) | Left stick X |
| Boost | Shift or Space | A / RT |
| Pause | Esc / P | Start |
| Confirm / start | Enter / Space | A |

Settings: invert pitch, master / music / SFX volume, fullscreen. Saved to `user://save.cfg`.

## 5. World

Ten destination islands around a central hub, spread over roughly 1 km, tops between
-15 m and +70 m. A sea of clouds sits at -70 m; a soft ceiling at 200 m; a soft boundary at
850 m from the hub.

| Island | Look | Role |
|---|---|---|
| Post Office Peak | brick post office, flag, crates | hub and first stop |
| Mossy Mill | windmill with spinning sails, crop rows | destination |
| Beacon Point | striped lighthouse on a tall spire | destination, landmark |
| Kettle Hollow | cluster of cottages and a well | destination |
| Orchard Rest | fruit trees in rows, cottage | destination |
| Pinewhistle | dense pines, log cabin | destination |
| Cloudberry Farm | barn, silo, pumpkins | destination |
| Bellfry | chapel with a bell tower | destination |
| Stargazer's Perch | observatory dome, highest island | destination |
| Hollow Arch | natural rock arch you can fly through | destination, stamp route |

Plus small rocky islets (obstacles and scenery), drifting clouds, hot air balloons, bird
flocks, and two slow storm clouds (hazard: counts as a crash).

## 6. Art direction

* Low-poly, flat-shaded, chunky toy proportions. Slight hand-cut irregularity from seeded
  jitter so nothing looks like a raw primitive.
* One shared palette (`blender/lib/palette.py`): warm cream plaster, terracotta and teal
  roofs, sage and spring greens, rock strata in sandstone, clay and plum under the islands.
* Golden hour: low warm sun, lavender-blue sky, hazy aerial perspective, glowing windows.
* Custom sky shader, animated cloud-sea shader, fog that thickens toward the cloud sea,
  glow on emissive windows, beacons and boost rings.

## 7. Audio direction

All audio is synthesized by `tools/synth/` (numpy, offline) into WAV files:
engine drone loop (pitch follows speed), wind loop (volume follows speed), pickup chime,
delivery fanfare, hoop whoosh, boost, crash thud, stamp ding, countdown ticks, UI clicks,
thunder, results jingle, and a looping music track (plucked Karplus-Strong arpeggios, bell
melody, soft pads, bass, light percussion).

## 8. UI and UX

* **Title:** 3D logo over the Post Office while the bot flies an attract-mode loop. Best
  score and controls card.
* **Countdown:** 3, 2, 1, GO.
* **HUD:** shift clock (pulses red under 10 s), score with count-up, combo badge,
  deliveries, destination card (name, distance, draining tip bar), boost gauge,
  edge-of-screen arrow to the target, diamond marker over the target hoop.
* **Moments:** "Express! +15 s", "+132", "Combo x1.5", "Parcel damaged", "Stamp +3 s".
* **Pause:** resume, restart, title, quit, volumes, invert pitch, fullscreen.
* **Results:** stats count up, rank reveal, new-best celebration, fly again.

## 9. Technical architecture

### Asset pipeline (Blender 5.1, Python)

```
blender/
  lib/       palette (shared materials), geo (bmesh kit), scene, export, registry
  kit/       reusable generators: trees, buildings, rocks, islands, clouds
  assets/    one module per asset family; @asset("name") registers a builder
  build.py   reset scene -> build -> export .glb -> stats -> preview renders
tools/build_assets.py   runs Blender headless, writes contact sheets to docs/previews/
```

Conventions: meters, Blender Z-up, models face +Y (Godot -Z), deterministic seeds.
The .glb files in `game/assets/models/` are build outputs, committed so the game runs from
a fresh clone, and never edited by hand.

**Node naming contract** (the only coupling between Blender and Godot):

| Prefix / suffix | Meaning in Godot |
|---|---|
| `MK_Delivery` | delivery hoop socket (-Z faces away from the island) |
| `MK_Stamp*`, `MK_Spawn*` | collectible and spawn sockets |
| `MK_Parcel` | carried-parcel socket on the plane |
| `FX_Smoke*`, `FX_Light*`, `FX_Mist*`, `FX_Exhaust`, `FX_WingTip*` | effect sockets |
| `SPIN_*` | spun about local forward (Godot -Z) by `spinner.gd`; speed from name |
| `-col`, `-convcolonly`, `-colonly` | Godot import-time collision (built-in suffixes) |

A post-import script (`game/pipeline/post_import.gd`) applies engine-side material tweaks
by palette name (emission energy, glass, cloud softness) so Blender stays the source of
truth for geometry and color.

### Game (Godot 4.7, GDScript, Forward+)

```
autoloads: Game (state machine, score, clock), Audio, Save, Controls, Dev (harness)
scenes/main.tscn
  World        environment, sun, cloud sea, archipelago, decor, hazards
  Plane        CharacterBody3D, flight model, input source (player or autopilot)
  ChaseCamera  spring follow, look-ahead, FOV by speed, trauma shake
  Deliveries   destination choice, tip clock, hoop activation
  UI           HUD, title, pause, results (CanvasLayers)
```

* Pure rules live in `scripts/rules/delivery_rules.gd` (static functions, unit tested).
* Flight feel lives in `data/flight.tres`; scoring rules in `data/rules.tres`.
* Input is an interface: `PlayerInput` and `Autopilot` both produce (turn, climb, boost),
  so the bot exercises exactly the code a player does.
* Physics at 60 Hz with physics interpolation; camera updates per rendered frame from the
  interpolated plane transform.

## 10. Verification protocol (every milestone)

`python tools/check.py` runs, in order:

1. Asset build (Blender headless) and asset report sanity (tri budgets, required markers).
2. Godot headless import: zero import errors.
3. Headless test suite: unit tests for rules, plus a bot playthrough at fixed 60 fps that
   must complete deliveries and reach the results screen.
4. Windowed scenario runs that capture PNGs from the player camera at scripted moments into
   `docs/devlog/<milestone>/`.
5. Log scan: any `ERROR`, `SCRIPT ERROR`, or `WARNING` line fails the check.

Then a manual review of every screenshot against the milestone checklist. Anything wrong is
fixed and the whole check re-run before the milestone is committed.

## 11. Milestones

| # | Name | Definition of done |
|---|---|---|
| M0 | Foundations | repo, Blender pipeline, Godot project, capture harness, spike proven |
| M1 | Greybox loop | blockout assets through the real pipeline; title -> play -> results loop; bot completes deliveries; HUD text; check.py green |
| M2 | Art pass | final models for every asset; sky, fog, cloud sea, lighting, post; spinners and FX sockets live; 60 fps |
| M3 | Juice | synthesized audio and music, particles, camera feel, polished HUD and menus, 3D logo |
| M4 | Ship | README with gallery and GIF, docs, final check, GitHub repo |

## 12. Budgets

60 fps at 1080p on a mid-range GPU. Islands under 15k triangles each, plane under 3k,
whole scene under 300k. Under 1500 draw calls. Load in under 3 s.

## 13. Out of scope

Multiplayer, level editor, story, landing and takeoff, fuel, damage models, mobile/touch,
localization, exported builds (Godot export templates are not installed).
