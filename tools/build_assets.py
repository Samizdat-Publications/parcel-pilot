"""Rebuild every procedural model with Blender, then compose QA contact sheets.

  python tools/build_assets.py                 # everything
  python tools/build_assets.py --only plane    # one asset (or one module)
  python tools/build_assets.py --no-preview    # skip preview renders (faster)

Outputs:
  game/assets/models/<name>.glb     exported models (the game reads these)
  build/asset_report.json           triangles, bounds, materials, markers
  docs/previews/<name>.png          2x2 contact sheet per asset
"""

import argparse
import json
import os
import subprocess
import sys
import time

from toolpaths import BUILD, ROOT, blender

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # previews are optional
    Image = None

PREVIEW_DIR = os.path.join(ROOT, "docs", "previews")
KEEP_PREFIXES = ("[asset]", "[build]", "Traceback", "  File", "Error", "Exception", "KeyError",
                 "ValueError", "TypeError", "AttributeError", "NameError", "RuntimeError",
                 "IndexError", "ZeroDivisionError")


def run_blender(args):
    cmd = [blender(), "--background", "--factory-startup", "--python-exit-code", "1",
           "--python", os.path.join(ROOT, "blender", "build.py"), "--"]
    if args.only:
        cmd += ["--only", args.only]
    if args.no_preview:
        cmd += ["--no-preview"]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, errors="replace")
    out = proc.stdout + proc.stderr
    with open(os.path.join(BUILD, "blender_build.log"), "w", encoding="utf-8") as fh:
        fh.write(out)
    for line in out.splitlines():
        if args.verbose or line.startswith(KEEP_PREFIXES):
            print(line)
    print(f"[build_assets] blender exited {proc.returncode} after {time.time() - t0:.1f} s")
    return proc.returncode


def _gradient(size, top=(236, 242, 248), bottom=(252, 244, 232)):
    w, h = size
    img = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        draw.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t)
                                                for i in range(3)))
    return img


def compose_sheets(names):
    if Image is None:
        print("[build_assets] Pillow not installed; skipping contact sheets")
        return
    with open(os.path.join(BUILD, "asset_report.json"), encoding="utf-8") as fh:
        report = json.load(fh)
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    try:
        font = ImageFont.load_default(size=20)
        small = ImageFont.load_default(size=15)
    except TypeError:
        font = small = ImageFont.load_default()
    for name in names:
        views = [os.path.join(BUILD, "previews", name, f"view_{i}.png") for i in range(4)]
        if not all(os.path.exists(v) for v in views):
            continue
        tiles = [Image.open(v).convert("RGBA") for v in views]
        tw, th = tiles[0].size
        header = 56
        sheet = _gradient((tw * 2, th * 2 + header)).convert("RGBA")
        for i, tile in enumerate(tiles):
            sheet.alpha_composite(tile, ((i % 2) * tw, header + (i // 2) * th))
        draw = ImageDraw.Draw(sheet)
        st = report.get(name, {})
        draw.text((16, 8), name, fill=(58, 44, 36), font=font)
        size = " x ".join(f"{v:g}" for v in st.get("size", []))
        info = (f"{st.get('triangles', '?')} tris   {size} m   "
                f"{len(st.get('materials', []))} materials   {len(st.get('markers', []))} markers")
        draw.text((16, 32), info, fill=(110, 96, 86), font=small)
        sheet.convert("RGB").save(os.path.join(PREVIEW_DIR, f"{name}.png"), optimize=True)
    print(f"[build_assets] contact sheets -> {os.path.relpath(PREVIEW_DIR, ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--no-preview", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    os.makedirs(BUILD, exist_ok=True)

    code = run_blender(args)
    if not args.no_preview and os.path.exists(os.path.join(BUILD, "asset_report.json")):
        with open(os.path.join(BUILD, "asset_report.json"), encoding="utf-8") as fh:
            names = list(json.load(fh).keys())
        if args.only:
            wanted = set(args.only.split(","))
            names = [n for n in names if n in wanted
                     or any(n.startswith(w) for w in wanted)] or names
        compose_sheets(names)
    sys.exit(code)


if __name__ == "__main__":
    main()
