"""The verification gate. Every milestone must pass this before it is committed.

  python tools/check.py --milestone m1          # everything, captures to docs/devlog/m1
  python tools/check.py --skip-assets           # reuse the current .glb files
  python tools/check.py --skip-capture          # headless only (no window)

Steps:
  1. assets    Blender rebuild + contract check (markers, triangle budgets)
  2. import    Godot headless import
  3. unit      headless unit tests (tests/test_runner.tscn)
  4. bot       headless bot playthrough of a full shift at a fixed 60 fps
  5. capture   windowed tour, screenshots from the player camera
Every Godot log is scanned; any ERROR or WARNING line fails the gate.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

from toolpaths import BUILD, GAME, ROOT, godot

ANSI = re.compile(r"\x1b\[[0-9;]*m")
BAD_LINE = re.compile(r"^\s*(ERROR|SCRIPT ERROR|USER ERROR|WARNING|USER WARNING)\b|Parse Error|\[check\] FAILED")
# Known-benign lines (keep this list short and justified).
ALLOW = [
]

TRI_BUDGET = {"island_": 15000, "islet_": 4000, "plane": 3000}
REQUIRED_MARKERS = {
    "plane": ["FX_Exhaust", "FX_WingTipL", "FX_WingTipR", "MK_Parcel"],
    "island_post_office": ["MK_Delivery", "MK_Spawn"],
}


class Gate:
    def __init__(self):
        self.results = []

    def record(self, step, ok, detail, seconds):
        self.results.append((step, ok, detail, seconds))
        mark = "PASS" if ok else "FAIL"
        print(f"[check] {step:<8} {mark}  {detail}  ({seconds:.1f} s)")

    def ok(self):
        return all(r[1] for r in self.results)


def scan(text):
    problems = []
    for line in ANSI.sub("", text).splitlines():
        if BAD_LINE.search(line) and not any(a in line for a in ALLOW):
            problems.append(line.strip())
    return problems


def run(cmd, log_name, timeout):
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, errors="replace",
                              timeout=timeout)
        out, code = proc.stdout + proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") + (exc.stderr or "") if isinstance(exc.stdout, str) else ""
        out += f"\n[check] TIMEOUT after {timeout} s"
        code = -1
    with open(os.path.join(BUILD, "logs", log_name), "w", encoding="utf-8") as fh:
        fh.write(out)
    return code, out, time.time() - t0


def step_assets(gate):
    t0 = time.time()
    code = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_assets.py")],
                          cwd=ROOT).returncode
    problems = []
    with open(os.path.join(BUILD, "asset_report.json"), encoding="utf-8") as fh:
        report = json.load(fh)
    for name, st in report.items():
        for prefix, budget in TRI_BUDGET.items():
            if name.startswith(prefix) and st["triangles"] > budget:
                problems.append(f"{name}: {st['triangles']} tris > {budget}")
        if name.startswith("island_") and "MK_Delivery" not in st["markers"]:
            problems.append(f"{name}: missing MK_Delivery")
        for marker in REQUIRED_MARKERS.get(name, []):
            if marker not in st["markers"]:
                problems.append(f"{name}: missing {marker}")
    for p in problems:
        print("   ", p)
    total = sum(st["triangles"] for st in report.values())
    gate.record("assets", code == 0 and not problems,
                f"{len(report)} assets, {total} triangles total, {len(problems)} contract issues",
                time.time() - t0)


def step_audio(gate):
    t0 = time.time()
    code = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_audio.py")], cwd=ROOT,
                          capture_output=True, text=True).returncode
    rep = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "audio_report.py")], cwd=ROOT,
                         capture_output=True, text=True)
    lines = [l for l in rep.stdout.splitlines()[1:] if l and not l.startswith("[")]
    bad = [l for l in lines if not l.rstrip().endswith(" ok")]
    for l in bad:
        print("   ", l)
    gate.record("audio", code == 0 and rep.returncode == 0 and not bad,
                f"{len(lines)} sounds synthesized, {len(bad)} with level, DC or loop-seam problems",
                time.time() - t0)


def step_godot(gate, step, args, log_name, timeout, expect_zero=True):
    code, out, secs = run([godot()] + args, log_name, timeout)
    problems = scan(out)
    for p in problems[:15]:
        print("   ", p)
    summary = ""
    perf = ""
    for line in ANSI.sub("", out).splitlines():
        if line.startswith(("[tests]", "[bot] finished", "[scenario] done")):
            summary = line.strip()
        if line.startswith("[perf]"):
            perf = " " + line.strip()
    summary += perf
    ok = (code == 0 or not expect_zero) and not problems
    gate.record(step, ok, f"exit {code}, {len(problems)} log problems. {summary}", secs)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--milestone", default="wip")
    ap.add_argument("--skip-assets", action="store_true")
    ap.add_argument("--skip-capture", action="store_true")
    ap.add_argument("--showcase", action="store_true", help="also capture the island gallery")
    ap.add_argument("--seed", default="7")
    args = ap.parse_args()
    os.makedirs(os.path.join(BUILD, "logs"), exist_ok=True)
    gate = Gate()

    if not args.skip_assets:
        step_assets(gate)
        step_audio(gate)
    step_godot(gate, "import", ["--headless", "--path", GAME, "--import"], "import.log", 600)
    step_godot(gate, "unit", ["--headless", "--path", GAME, "--scene", "res://tests/test_runner.tscn"],
               "unit.log", 300)
    step_godot(gate, "bot", ["--headless", "--fixed-fps", "60", "--disable-vsync", "--path", GAME,
                             "--", "--scenario=bot_shift", f"--seed={args.seed}"], "bot.log", 900)
    if not args.skip_capture:
        out_dir = os.path.join(ROOT, "docs", "devlog", args.milestone)
        step_godot(gate, "capture", ["--path", GAME, "--resolution", "1600x900", "--disable-vsync", "--",
                                     "--scenario=tour", f"--seed={args.seed}", f"--out={out_dir}"],
                   "capture.log", 400)
        if args.showcase:
            step_godot(gate, "showcase", ["--path", GAME, "--resolution", "1600x900", "--",
                                          "--scenario=showcase", f"--seed={args.seed}",
                                          f"--out={os.path.join(out_dir, 'gallery')}"], "showcase.log", 400)
        print(f"[check] screenshots in {os.path.relpath(out_dir, ROOT)}")

    print("[check] " + ("ALL GREEN" if gate.ok() else "FAILED"))
    sys.exit(0 if gate.ok() else 1)


if __name__ == "__main__":
    main()
