"""Save a progress snapshot into docs/progress/ and log it in docs/progress/LOG.md.

  python tools/snap.py "First real island"                    # title + flight frames
  python tools/snap.py "Sky shader" --shots flight            # just the in-flight frame
  python tools/snap.py "Plane v2" --preview plane --no-game   # an asset contact sheet only

Frames come from the running game (player camera + UI), numbered in order so the
folder reads as a timeline of the build.
"""

import argparse
import datetime
import glob
import os
import re
import shutil
import subprocess

from toolpaths import BUILD, GAME, ROOT, godot

PROGRESS = os.path.join(ROOT, "docs", "progress")
LOG = os.path.join(PROGRESS, "LOG.md")
HEADER = ("# Progress log\n\nA timeline of Parcel Pilot's build, one entry per snapshot "
          "(`python tools/snap.py`). Frames are the player camera unless noted.\n")


def next_index():
    nums = [int(m.group(1)) for f in os.listdir(PROGRESS)
            if (m := re.match(r"^(\d{3})_", f))]
    if os.path.exists(LOG):
        with open(LOG, encoding="utf-8") as fh:
            nums += [int(n) for n in re.findall(r"^## (\d{3}) ", fh.read(), re.M)]
    return max(nums, default=0) + 1


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:40]


def git_sha():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True).stdout.strip()
    except OSError:
        return "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("caption")
    ap.add_argument("--shots", default="title,flight")
    ap.add_argument("--preview", action="append", default=[], help="asset contact sheet to include")
    ap.add_argument("--no-game", action="store_true")
    ap.add_argument("--extra", action="append", default=[], help="another image file to include")
    ap.add_argument("--note", default="", help="extra text under the heading")
    args = ap.parse_args()
    os.makedirs(PROGRESS, exist_ok=True)

    idx = next_index()
    prefix = f"{idx:03d}_{slugify(args.caption)}"
    images = []

    if not args.no_game:
        tmp = os.path.join(BUILD, "snap")
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp)
        cmd = [godot(), "--path", GAME, "--resolution", "1600x900", "--", "--scenario=snapshot",
               f"--shots={args.shots}", "--seed=7", f"--out={tmp}"]
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, errors="replace")
        if proc.returncode != 0:
            print(proc.stdout[-2000:], proc.stderr[-2000:])
        for shot in args.shots.split(","):
            src = os.path.join(tmp, f"{shot}.png")
            if os.path.exists(src):
                dst = os.path.join(PROGRESS, f"{prefix}_{shot}.png")
                shutil.copyfile(src, dst)
                images.append((shot, dst))

    for name in args.preview:
        src = os.path.join(ROOT, "docs", "previews", f"{name}.png")
        if os.path.exists(src):
            dst = os.path.join(PROGRESS, f"{prefix}_preview_{name}.png")
            shutil.copyfile(src, dst)
            images.append((f"{name} (Blender preview)", dst))

    for path in args.extra:
        if os.path.exists(path):
            dst = os.path.join(PROGRESS, f"{prefix}_{slugify(os.path.splitext(os.path.basename(path))[0])}.png")
            shutil.copyfile(path, dst)
            images.append((os.path.basename(path), dst))

    new_log = not os.path.exists(LOG)
    with open(LOG, "a", encoding="utf-8", newline="\n") as fh:
        if new_log:
            fh.write(HEADER)
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        fh.write(f"\n## {idx:03d} {args.caption}\n\n{stamp}, commit `{git_sha()}`\n\n")
        if args.note:
            fh.write(args.note + "\n\n")
        for label, path in images:
            fh.write(f"![{label}]({os.path.basename(path)})\n")
    for _, path in images:
        print("[snap]", os.path.relpath(path, ROOT))
    print(f"[snap] logged entry {idx:03d} in docs/progress/LOG.md")


if __name__ == "__main__":
    main()
