"""Record gameplay with Godot's movie maker and cut an animated clip for the README.

  python tools/make_clip.py [--before 7] [--after 3] [--fps 15] [--width 640]

Godot renders the `movie` scenario frame by frame (fixed 30 fps, so the footage is
smooth whatever the machine's speed) into a PNG sequence; this script keeps the
seconds around the first delivery and writes docs/media/gameplay.webp (animated)
and a smaller docs/media/gameplay.gif.
"""

import argparse
import glob
import os
import re
import shutil
import subprocess

from PIL import Image

from toolpaths import BUILD, GAME, ROOT, godot

MEDIA = os.path.join(ROOT, "docs", "media")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", type=float, default=7.0)
    ap.add_argument("--after", type=float, default=3.0)
    ap.add_argument("--fps", type=int, default=15)
    ap.add_argument("--width", type=int, default=640)
    args = ap.parse_args()

    frames_dir = os.path.join(BUILD, "movie")
    shutil.rmtree(frames_dir, ignore_errors=True)
    os.makedirs(frames_dir)
    cmd = [godot(), "--path", GAME, "--resolution", "960x540", "--fixed-fps", "30",
           "--write-movie", os.path.join(frames_dir, "frame.png"), "--", "--scenario=movie", "--seed=7"]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, errors="replace")
    out = proc.stdout + proc.stderr
    m = re.search(r"\[movie\] delivery_frame=(\d+)", out)
    frames = sorted(glob.glob(os.path.join(frames_dir, "frame*.png")))
    if not m or not frames:
        print(out[-3000:])
        raise SystemExit("no footage recorded")
    first = int(re.search(r"(\d+)\.png$", frames[0]).group(1))
    hit = int(m.group(1)) - first
    lo = max(0, hit - int(args.before * 30))
    hi = min(len(frames), hit + int(args.after * 30))
    step = max(1, round(30 / args.fps))
    picked = frames[lo:hi:step]
    height = round(args.width * 9 / 16)
    images = [Image.open(f).convert("RGB").resize((args.width, height), Image.LANCZOS) for f in picked]
    os.makedirs(MEDIA, exist_ok=True)
    webp = os.path.join(MEDIA, "gameplay.webp")
    images[0].save(webp, save_all=True, append_images=images[1:], duration=int(1000 / args.fps), loop=0,
                   quality=72, method=6)
    gif = os.path.join(MEDIA, "gameplay.gif")
    small = [im.resize((args.width * 3 // 4, height * 3 // 4), Image.LANCZOS) for im in images]
    pal = [im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for im in small]
    pal[0].save(gif, save_all=True, append_images=pal[1:], duration=int(1000 / args.fps), loop=0, optimize=True)
    for path in (webp, gif):
        print(f"[clip] {os.path.relpath(path, ROOT)}: {len(images)} frames, {os.path.getsize(path) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
