"""Film the game for the landing page and the README.

  python tools/film.py [shift] [features] [islands] [--fps 60] [--size 1920x1080]

Godot renders tests/scenarios/film.gd frame by frame under its movie maker (a fixed
frame rate, so the footage is smooth whatever the machine's speed) into an MJPEG .avi
with the game's own audio. This script turns each shoot into build/film/<shoot>.mp4 (a
near-lossless master) and build/film/<shoot>.json (the scenario's event marks, in
seconds), then deletes the bulky .avi. tools/make_media.py cuts everything from those.
"""

import argparse
import json
import os
import re
import subprocess
import time

from toolpaths import BUILD, GAME, ROOT, ffmpeg, godot

FILM = os.path.join(BUILD, "film")
SHOOTS = ["shift", "features", "islands"]


def film(shoot, fps, size):
    os.makedirs(FILM, exist_ok=True)
    avi = os.path.join(FILM, f"{shoot}.avi")
    mp4 = os.path.join(FILM, f"{shoot}.mp4")
    started = time.time()
    cmd = [godot(), "--path", GAME, "--resolution", size, "--fixed-fps", str(fps), "--write-movie", avi,
           "--", "--scenario=film", f"--shoot={shoot}", "--seed=7"]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, errors="replace")
    out = proc.stdout + proc.stderr
    problems = [line for line in out.splitlines() if "ERROR" in line or "WARNING" in line or "FAILED" in line]
    for line in problems:
        print("  " + line)
    if proc.returncode != 0 or not os.path.exists(avi):
        print(out[-3000:])
        raise SystemExit(f"[film] {shoot}: the scenario failed")

    marks = []
    for m in re.finditer(r"^\[mark\] (\d+) (\S+) ?(.*)$", out, re.M):
        marks.append({"t": round(int(m.group(1)) / fps, 3), "kind": m.group(2), "label": m.group(3).strip()})
    stats = {}
    m = re.search(r"^\[film\] stats (.*)$", out, re.M)
    if m:
        for pair in m.group(1).split():
            key, value = pair.split("=", 1)
            stats[key] = int(value) if value.isdigit() else value.replace("_", " ")

    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", avi, "-c:v", "libx264", "-preset", "medium",
                    "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    mp4], check=True)
    os.remove(avi)
    duration = _duration(mp4)
    with open(os.path.join(FILM, f"{shoot}.json"), "w", encoding="utf-8") as fh:
        json.dump({"shoot": shoot, "fps": fps, "size": size, "duration": duration, "stats": stats,
                   "marks": marks}, fh, indent=1)
    print(f"[film] {shoot}: {duration:.1f} s, {len(marks)} marks, "
          f"{os.path.getsize(mp4) / 1e6:.0f} MB master, {time.time() - started:.0f} s to film")


def _duration(path):
    probe = subprocess.run([ffmpeg(), "-i", path], capture_output=True, text=True, errors="replace").stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", probe).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shoots", nargs="*", default=SHOOTS, choices=SHOOTS)
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--size", default="1920x1080")
    args = ap.parse_args()
    for shoot in args.shoots:
        film(shoot, args.fps, args.size)


if __name__ == "__main__":
    main()
