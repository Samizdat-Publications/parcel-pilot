"""Locate Blender, Godot and ffmpeg. Override with the BLENDER / GODOT / FFMPEG environment variables."""

import glob
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game")
BUILD = os.path.join(ROOT, "build")


def _first_existing(candidates):
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


def blender():
    env = os.environ.get("BLENDER")
    if env:
        return env
    home = os.path.expanduser("~")
    candidates = [shutil.which("blender")]
    candidates += sorted(glob.glob(r"C:\Program Files\Blender Foundation\Blender *\blender.exe"),
                         reverse=True)
    candidates += ["/Applications/Blender.app/Contents/MacOS/Blender",
                   os.path.join(home, "Applications/Blender.app/Contents/MacOS/Blender")]
    found = _first_existing(candidates)
    if not found:
        sys.exit("Blender not found. Set the BLENDER environment variable to blender(.exe).")
    return found


def godot():
    """Prefer the Windows *_console.exe build so stdout/stderr can be captured."""
    env = os.environ.get("GODOT")
    if env:
        return env
    home = os.path.expanduser("~")
    patterns = [
        os.path.join(home, "Downloads", "Godot_v4*", "Godot_v4*_console.exe"),
        os.path.join(home, "Documents", "Godot", "Godot_v4*", "Godot_v4*_console.exe"),
        os.path.join(home, "Downloads", "Godot_v4*_console.exe"),
        r"C:\Program Files\Godot\Godot_v4*_console.exe",
    ]
    candidates = []
    for pat in patterns:
        candidates += sorted(glob.glob(pat), reverse=True)
    candidates += [shutil.which("godot4"), shutil.which("godot"),
                   "/Applications/Godot.app/Contents/MacOS/Godot"]
    found = _first_existing(candidates)
    if not found:
        sys.exit("Godot 4 not found. Set the GODOT environment variable to the executable.")
    return found


def ffmpeg():
    """ffmpeg for the footage tools: FFMPEG, then the imageio-ffmpeg wheel, then PATH."""
    env = os.environ.get("FFMPEG")
    if env:
        return env
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    found = shutil.which("ffmpeg")
    if not found:
        sys.exit("ffmpeg not found. Run `pip install imageio-ffmpeg` or set the FFMPEG environment variable.")
    return found
