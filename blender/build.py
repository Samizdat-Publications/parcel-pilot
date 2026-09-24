"""Build every registered asset: reset scene, run its builder, export .glb, render previews.

Normally run through tools/build_assets.py. Direct use:
  blender --background --factory-startup --python-exit-code 1 \
      --python blender/build.py -- [--only name1,name2] [--no-preview]
"""

import argparse
import importlib
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from lib import export, registry, scene  # noqa: E402


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="build.py")
    p.add_argument("--only", default="", help="comma separated asset or module names")
    p.add_argument("--no-preview", action="store_true")
    p.add_argument("--models", default=os.path.join(ROOT, "game", "assets", "models"))
    p.add_argument("--previews", default=os.path.join(ROOT, "build", "previews"))
    p.add_argument("--report", default=os.path.join(ROOT, "build", "asset_report.json"))
    return p.parse_args(argv)


def import_asset_modules():
    assets_dir = os.path.join(HERE, "assets")
    for root, _dirs, files in os.walk(assets_dir):
        for f in sorted(files):
            if f.endswith(".py") and not f.startswith("_"):
                rel = os.path.relpath(os.path.join(root, f), HERE)
                importlib.import_module(rel[:-3].replace(os.sep, "."))


def main():
    args = parse_args()
    import_asset_modules()
    wanted = {s.strip() for s in args.only.split(",") if s.strip()}

    report = {}
    if wanted and os.path.exists(args.report):
        with open(args.report, "r", encoding="utf-8") as fh:
            report = json.load(fh)

    failures = []
    built = 0
    for name, entry in registry.ASSETS.items():
        module_short = entry["module"].split(".")[-1]
        if wanted and name not in wanted and module_short not in wanted:
            continue
        t0 = time.time()
        try:
            scene.reset()
            entry["build"]()
            export.export_glb(os.path.join(args.models, name + ".glb"))
            st = export.stats()
            if entry["icon"] is not None:
                az, el = entry["icon"]
                export.render_icon(os.path.join(ROOT, "game", "assets", "icons", name + ".png"), az, el)
            if entry["preview"] and not args.no_preview:
                export.render_previews(os.path.join(args.previews, name))
            st["seconds"] = round(time.time() - t0, 2)
            st["module"] = entry["module"]
            report[name] = st
            built += 1
            print(f"[asset] {name}: {st['triangles']} tris, size {st['size']} m, "
                  f"{len(st['markers'])} markers, {st['seconds']} s")
        except Exception:  # keep building the rest, report at the end
            traceback.print_exc()
            failures.append(name)

    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(dict(sorted(report.items())), fh, indent=2)

    print(f"[build] {built} built, {len(failures)} failed")
    if failures:
        print("[build] FAILED: " + ", ".join(failures))
        sys.exit(1)


main()
