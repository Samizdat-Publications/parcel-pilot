"""Build the public site (the landing page at /, the game at /play/) and publish it.

  python tools/build_site.py            # export the web build and assemble site-dist/
  python tools/build_site.py --serve    # ... then serve it at http://localhost:8788
  python tools/build_site.py --deploy   # ... then publish it to Cloudflare Pages

The landing page is site/ (plain HTML, CSS and JS; media cut by tools/make_media.py).
The game is Godot's Web export (Compatibility renderer, no threads, so no special
headers are needed) with the custom shell game/web/shell.html.

Cloudflare Pages serves files of up to 25 MiB. Godot's engine (index.wasm) is about
40 MB, so it is split into parts that the shell streams back together; each part keeps
a .wasm name so Cloudflare still compresses it on the way out. Videos get byte ranges
from functions/media (Safari needs them).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

from toolpaths import BUILD, GAME, ROOT, godot

DIST = os.path.join(ROOT, "site-dist")
WEB = os.path.join(BUILD, "web")
PAGES_LIMIT = 25 * 1024 * 1024
PART_BYTES = 20 * 1024 * 1024
PROJECT = "parcel-pilot"
WRANGLER = ["npx", "--yes", "wrangler@4"]

HEADERS = """/media/*
  Cache-Control: public, max-age=86400
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
"""


def export_web():
    shutil.rmtree(WEB, ignore_errors=True)
    os.makedirs(WEB)
    proc = subprocess.run([godot(), "--headless", "--path", GAME, "--export-release", "Web",
                           os.path.join(WEB, "index.html")], cwd=ROOT, capture_output=True, text=True, errors="replace")
    problems = [line for line in (proc.stdout + proc.stderr).splitlines() if "ERROR" in line or "WARNING" in line]
    if proc.returncode != 0 or problems or not os.path.exists(os.path.join(WEB, "index.wasm")):
        print("\n".join(problems) or (proc.stdout + proc.stderr)[-3000:])
        raise SystemExit("[site] the web export failed")


def assemble():
    shutil.rmtree(DIST, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "site"), DIST)
    play = os.path.join(DIST, "play")
    os.makedirs(play)
    for name in os.listdir(WEB):
        if name != "index.wasm":
            shutil.copy2(os.path.join(WEB, name), play)

    parts = []
    with open(os.path.join(WEB, "index.wasm"), "rb") as fh:
        while True:
            chunk = fh.read(PART_BYTES)
            if not chunk:
                break
            name = f"index.part{len(parts) + 1}.wasm"
            with open(os.path.join(play, name), "wb") as out:
                out.write(chunk)
            parts.append(name)
    shell = os.path.join(play, "index.html")
    with open(shell, encoding="utf-8") as fh:
        html = fh.read()
    marker = "const WASM_PARTS = [];"
    if marker not in html:
        raise SystemExit("[site] the web shell has no WASM_PARTS marker (is game/web/shell.html in the preset?)")
    html = html.replace(marker, f"const WASM_PARTS = {json.dumps(parts)};")
    with open(shell, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)

    with open(os.path.join(DIST, "_headers"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(HEADERS)
    media = os.path.join(DIST, "media")
    videos = sorted(f"/media/{f}" for f in os.listdir(media) if f.endswith(".mp4"))
    with open(os.path.join(DIST, "_routes.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"version": 1, "include": videos, "exclude": []}, fh, indent=1)
    sizes = {v: os.path.getsize(os.path.join(DIST, v.lstrip("/"))) for v in videos}
    with open(os.path.join(ROOT, "functions", "media", "sizes.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(sizes, fh, indent=1)
        fh.write("\n")

    count, total = 0, 0
    for folder, _dirs, files in os.walk(DIST):
        for f in files:
            size = os.path.getsize(os.path.join(folder, f))
            count += 1
            total += size
            if size > PAGES_LIMIT:
                raise SystemExit(f"[site] {os.path.relpath(os.path.join(folder, f), DIST)} is over 25 MiB")
    print(f"[site] site-dist: {count} files, {total / 1e6:.1f} MB, engine in {len(parts)} parts")


def wrangler(args):
    cmd = WRANGLER + args
    if sys.platform == "win32":
        cmd = ["cmd", "/c"] + cmd
    subprocess.run(cmd, cwd=ROOT, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--skip-export", action="store_true", help="reuse build/web from the last export")
    args = ap.parse_args()
    if not args.skip_export:
        export_web()
    assemble()
    if args.deploy:
        wrangler(["pages", "deploy", "site-dist", "--project-name", PROJECT, "--branch", "main",
                  "--commit-dirty=true"])
    elif args.serve:
        wrangler(["pages", "dev", "site-dist", "--port", "8788"])


if __name__ == "__main__":
    main()
