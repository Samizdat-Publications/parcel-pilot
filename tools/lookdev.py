"""Render one frozen gameplay moment under several lighting variants, side by side.

  python tools/lookdev.py variants.json [--at 9] [--cols 3]

variants.json is a list of {"name": ..., "env.fog_density": 0.0005, "sky.zenith_color":
[r, g, b], "sun.light_energy": 2.0, ...}; the first entry is usually the baseline {}.
Output: build/lookdev/<name>.png and a labeled sheet build/lookdev_sheet.png.
"""

import argparse
import json
import os
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

from toolpaths import BUILD, GAME, ROOT, godot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variants")
    ap.add_argument("--at", default="9.0")
    ap.add_argument("--cols", type=int, default=3)
    args = ap.parse_args()
    with open(args.variants, encoding="utf-8") as fh:
        variants = json.load(fh)
    os.makedirs(BUILD, exist_ok=True)
    with open(os.path.join(BUILD, "lookdev_variants.json"), "w", encoding="utf-8") as fh:
        json.dump(variants, fh)
    out = os.path.join(BUILD, "lookdev")
    shutil.rmtree(out, ignore_errors=True)
    cmd = [godot(), "--path", GAME, "--resolution", "1280x720", "--", "--scenario=lookdev",
           "--seed=7", f"--at={args.at}", f"--out={out}"]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, errors="replace")
    for line in (proc.stdout + proc.stderr).splitlines():
        if "ERROR" in line or "WARNING" in line:
            print(line)
    tiles = []
    for v in variants:
        p = os.path.join(out, f"{v['name']}.png")
        if os.path.exists(p):
            tiles.append((v["name"], Image.open(p).convert("RGB").resize((640, 360))))
    if not tiles:
        print("no captures")
        return
    cols = min(args.cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 640, rows * 390), (30, 30, 34))
    try:
        font = ImageFont.load_default(size=18)
    except TypeError:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(tiles):
        x, y = (i % cols) * 640, (i // cols) * 390
        sheet.paste(im, (x, y + 30))
        draw.text((x + 10, y + 6), name, fill=(240, 235, 225), font=font)
    path = os.path.join(BUILD, "lookdev_sheet.png")
    sheet.save(path)
    print("[lookdev]", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
