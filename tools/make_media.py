"""Cut the landing page's media and the README's animations from the filmed footage.

  python tools/film.py            # first: build/film/{shift,features,islands}.mp4 + .json
  python tools/make_media.py      # then: site/media/* and docs/media/*
  python tools/make_media.py --only clips readme    # just some steps, after one re-shoot

Every cut is placed by an event mark the film scenario printed (a delivery, a ring,
a zap, the results), so a new recording re-cuts itself. Outputs:
  site/media/hero.mp4            muted loop of island approaches for the page hero
  site/media/<clip>.mp4 + .jpg   short muted loops (depart, rings, stamp, storm, deliver, results)
  site/media/island-<id>.*       one short approach per island
  site/media/shift.mp4 + .jpg    one whole shift with the game's own sound, under 24 MiB
  site/media/chapters.json       the whole shift's events, for the page's timeline
  site/media/sound/*.m4a         the synthesized music and a few effects
  site/media/{logo,plane}.webp   the game's own renders (tests/scenarios/stills.gd)
  site/media/m1..m4.jpg          the same shot at each milestone, for the before/after slider
  site/media/og.jpg              the social card
  docs/media/*.webp              animated clips for the README
"""

import argparse
import io
import json
import math
import os
import shutil
import subprocess

from PIL import Image

from toolpaths import BUILD, GAME, ROOT, ffmpeg, godot

FILM = os.path.join(BUILD, "film")
SITE_MEDIA = os.path.join(ROOT, "site", "media")
DOCS_MEDIA = os.path.join(ROOT, "docs", "media")
MAX_BYTES = int(23.5 * 1024 * 1024)

ISLAND_IDS = {
    "PostOffice": "post-office", "MossyMill": "mossy-mill", "BeaconPoint": "beacon-point",
    "KettleHollow": "kettle-hollow", "OrchardRest": "orchard-rest", "Pinewhistle": "pinewhistle",
    "CloudberryFarm": "cloudberry-farm", "Bellfry": "bellfry", "StargazersPerch": "stargazers-perch",
    "HollowArch": "hollow-arch",
}
HERO_ISLANDS = ["BeaconPoint", "KettleHollow", "HollowArch", "Pinewhistle", "StargazersPerch", "OrchardRest"]
SOUNDS = ["music", "express", "deliver", "stamp", "ring", "boost", "thunder", "new_best", "parachute"]


def load(shoot):
    with open(os.path.join(FILM, f"{shoot}.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    data["path"] = os.path.join(FILM, f"{shoot}.mp4")
    return data


def marks(data, kind, label=None):
    return [m for m in data["marks"] if m["kind"] == kind and (label is None or m["label"] == label)]


def first(data, kind, label=None, after=0.0):
    for m in marks(data, kind, label):
        if m["t"] >= after:
            return m["t"]
    raise SystemExit(f"[media] no '{kind} {label or ''}' mark in {data['shoot']}")


def run(args):
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error"] + args, check=True)


def clip(src, start, dur, out, width=1280, crf=23, fps=None, poster_at=None):
    vf = f"scale={width}:-2:flags=lanczos" + (f",fps={fps}" if fps else "")
    run(["-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", src, "-vf", vf, "-c:v", "libx264", "-preset", "slow",
         "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", out])
    poster(src, start + (dur * 0.5 if poster_at is None else poster_at), out[:-4] + ".jpg", width)
    return out


def poster(src, t, out, width=1280):
    run(["-ss", f"{t:.3f}", "-i", src, "-frames:v", "1", "-update", "1", "-vf", f"scale={width}:-2:flags=lanczos",
         "-q:v", "3", out])


def frame(src, t, width=1920):
    png = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1", "-vf",
                          f"scale={width}:-2:flags=lanczos", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGB")


def hero(islands, out):
    """Island approaches joined with soft crossfades into one seamless-ish loop."""
    seg, fade = 3.6, 0.6
    inputs, chains, parts = [], [], []
    for i, name in enumerate(HERO_ISLANDS):
        t = first(islands, "island", name) + 0.9
        inputs += ["-ss", f"{t:.3f}", "-t", f"{seg:.3f}", "-i", islands["path"]]
        chains.append(f"[{i}:v]setpts=PTS-STARTPTS,scale=1600:-2:flags=lanczos,fps=60,format=yuv420p[v{i}]")
    last = "v0"
    for i in range(1, len(HERO_ISLANDS)):
        offset = i * (seg - fade)
        chains.append(f"[{last}][v{i}]xfade=transition=fade:duration={fade}:offset={offset:.3f}[x{i}]")
        last = f"x{i}"
    run(inputs + ["-filter_complex", ";".join(chains), "-map", f"[{last}]", "-c:v", "libx264", "-preset", "slow",
                  "-crf", "25", "-maxrate", "3200k", "-bufsize", "6400k", "-pix_fmt", "yuv420p",
                  "-movflags", "+faststart", "-an", out])
    poster(islands["path"], first(islands, "island", HERO_ISLANDS[0]) + 2.6, out[:-4] + ".jpg", 1600)


def whole_shift(shift, out):
    """The uncut shift with sound, sized to stay under the Pages file limit."""
    start = first(shift, "title")
    end = first(shift, "end")
    dur = end - start
    audio_kbps = 96
    kbps = min(1800, math.floor(MAX_BYTES * 8 / 1000 / dur) - audio_kbps - 16)
    run(["-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", shift["path"], "-vf", "scale=960:-2:flags=lanczos",
         "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-maxrate", f"{kbps}k", "-bufsize", f"{kbps * 2}k",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", f"{audio_kbps}k", "-movflags", "+faststart", out])
    poster(shift["path"], first(shift, "delivery") + 0.4, out[:-4] + ".jpg", 1280)
    events = []
    for m in shift["marks"]:
        if m["kind"] in ("go", "delivery", "stamp", "ring", "zap", "crash", "results"):
            events.append({"t": round(m["t"] - start, 2), "kind": m["kind"], "label": m["label"]})
    with open(os.path.join(SITE_MEDIA, "chapters.json"), "w", encoding="utf-8", newline="
") as fh:
        json.dump({"duration": round(dur, 2), "stats": shift["stats"], "events": events}, fh, indent=1)
    return dur, kbps


def sounds():
    folder = os.path.join(SITE_MEDIA, "sound")
    os.makedirs(folder, exist_ok=True)
    for name in SOUNDS:
        src = os.path.join(GAME, "assets", "audio", f"{name}.wav")
        rate = "128k" if name == "music" else "112k"
        run(["-i", src, "-c:a", "aac", "-b:a", rate, "-movflags", "+faststart", os.path.join(folder, f"{name}.m4a")])


def stills():
    """The game renders its own logo and plane with transparent backgrounds."""
    out = os.path.join(BUILD, "stills")
    shutil.rmtree(out, ignore_errors=True)
    subprocess.run([godot(), "--path", GAME, "--resolution", "1280x720", "--", "--scenario=stills", f"--out={out}"],
                   cwd=ROOT, check=True, capture_output=True)
    for name, width in (("logo", 1400), ("plane", 900)):
        im = Image.open(os.path.join(out, f"{name}.png")).convert("RGBA")
        box = im.getchannel("A").getbbox()
        pad = 12
        im = im.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad),
                      min(im.height, box[3] + pad)))
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(os.path.join(SITE_MEDIA, f"{name}.webp"), quality=90, method=6)
        if name == "logo":
            im.save(os.path.join(SITE_MEDIA, "logo.png"), optimize=True)


def milestones():
    for i in range(1, 5):
        im = Image.open(os.path.join(ROOT, "docs", "devlog", f"m{i}", "03_flight.png")).convert("RGB")
        im.resize((1280, 720), Image.LANCZOS).save(os.path.join(SITE_MEDIA, f"m{i}.jpg"), quality=86)


def og_card(islands):
    card = frame(islands["path"], first(islands, "island", "BeaconPoint") + 2.4).resize((1200, 675), Image.LANCZOS)
    card = card.crop((0, 22, 1200, 652))
    logo = Image.open(os.path.join(SITE_MEDIA, "logo.png")).convert("RGBA")
    logo = logo.resize((720, round(logo.height * 720 / logo.width)), Image.LANCZOS)
    card = card.convert("RGBA")
    card.alpha_composite(logo, ((1200 - logo.width) // 2, 36))
    card.convert("RGB").save(os.path.join(SITE_MEDIA, "og.jpg"), quality=86)


def webp(src, start, dur, out, width=560, fps=15):
    """An animated WebP for the README (GitHub plays these inline)."""
    raw = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", src,
                          "-vf", f"fps={fps},scale={width}:-2:flags=lanczos", "-f", "image2pipe", "-vcodec", "png",
                          "-"], capture_output=True, check=True).stdout
    frames, pos = [], 0
    sig = b"\x89PNG\r\n\x1a\n"
    while True:
        nxt = raw.find(sig, pos + 1)
        chunk = raw[pos:] if nxt == -1 else raw[pos:nxt]
        frames.append(Image.open(io.BytesIO(chunk)).convert("RGB"))
        if nxt == -1:
            break
        pos = nxt
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=round(1000 / fps), loop=0,
                   quality=70, method=6)


STEPS = ["stills", "milestones", "sounds", "hero", "og", "clips", "islands", "shift", "readme"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", choices=STEPS, help="redo just these steps (default: all)")
    args = ap.parse_args()
    steps = set(args.only or STEPS)
    os.makedirs(SITE_MEDIA, exist_ok=True)
    os.makedirs(DOCS_MEDIA, exist_ok=True)
    shift, features, islands = load("shift"), load("features"), load("islands")
    m = SITE_MEDIA

    if "stills" in steps:
        stills()
    if "milestones" in steps:
        milestones()
    if "sounds" in steps:
        sounds()
    if "hero" in steps:
        hero(islands, os.path.join(m, "hero.mp4"))
    if "og" in steps:
        og_card(islands)

    rings_at = first(features, "shot", "rings")
    stamp_shot = first(features, "shot", "stamp")
    stamp = first(features, "stamp", after=stamp_shot)
    storm = first(features, "shot", "storm")
    zap = first(features, "zap", after=storm)
    delivered = first(features, "delivery", after=first(features, "shot", "deliver"))
    results = first(shift, "results")
    if "clips" in steps:
        countdown = first(shift, "countdown")
        clip(shift["path"], countdown - 0.2, first(shift, "go") - countdown + 3.8, os.path.join(m, "depart.mp4"),
             poster_at=0.4)
        clip(features["path"], rings_at + 0.4, 6.4, os.path.join(m, "rings.mp4"),
             poster_at=first(features, "ring", after=rings_at) - rings_at - 0.4 + 0.05)
        clip(features["path"], stamp_shot + 0.4, stamp - stamp_shot + 1.4, os.path.join(m, "stamp.mp4"),
             poster_at=stamp - stamp_shot - 0.4 + 0.35)
        clip(features["path"], storm + 0.4, zap - storm + 1.3, os.path.join(m, "storm.mp4"),
             poster_at=zap - storm - 0.8)
        clip(features["path"], delivered - 3.4, 6.6, os.path.join(m, "deliver.mp4"), poster_at=3.6)
        clip(shift["path"], results - 0.3, 8.0, os.path.join(m, "results.mp4"), poster_at=4.8)

    if "islands" in steps:
        for name, slug in ISLAND_IDS.items():
            t = first(islands, "island", name)
            clip(islands["path"], t + 0.5, 4.4, os.path.join(m, f"island-{slug}.mp4"), width=960, crf=24, fps=30,
                 poster_at=2.6)

    if "shift" in steps:
        dur, kbps = whole_shift(shift, os.path.join(m, "shift.mp4"))
        print(f"[media] whole shift {dur:.0f} s at {kbps} kb/s")

    if "readme" in steps:
        readme = [("deliver", features, delivered - 3.4, 6.0), ("rings", features, rings_at + 1.8, 5.0),
                  ("storm", features, storm + 1.8, zap - storm - 0.6), ("stamp", features, stamp - 2.6, 3.8),
                  ("islands", islands, first(islands, "island", "BeaconPoint") + 0.8, 4.0),
                  ("results", shift, results + 0.2, 6.0)]
        for name, data, start, length in readme:
            webp(data["path"], start, length, os.path.join(DOCS_MEDIA, f"{name}.webp"))

    total = 0
    for folder in (SITE_MEDIA, os.path.join(SITE_MEDIA, "sound")):
        for f in sorted(os.listdir(folder)):
            p = os.path.join(folder, f)
            if os.path.isfile(p):
                size = os.path.getsize(p)
                total += size
                if size > MAX_BYTES:
                    raise SystemExit(f"[media] {f} is {size / 1e6:.1f} MB, over the Pages limit")
    print(f"[media] site/media totals {total / 1e6:.1f} MB")
    for f in sorted(os.listdir(DOCS_MEDIA)):
        print(f"[media] docs/media/{f}: {os.path.getsize(os.path.join(DOCS_MEDIA, f)) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
