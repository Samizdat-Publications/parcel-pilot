"""Synthesize every sound in the game into game/assets/audio/*.wav.

  python tools/build_audio.py              # everything
  python tools/build_audio.py --only crash # one sound

Loops (engine, wind, music) get a RIFF 'smpl' chunk with their loop points, so Godot's
importer ("Detect From WAV") loops them with no extra settings.
"""

import argparse
import os
import struct
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synth import dsp, music, sfx  # noqa: E402
from toolpaths import GAME  # noqa: E402

OUT = os.path.join(GAME, "assets", "audio")


def write_wav(path, x, loop=False):
    x = np.clip(x, -1.0, 1.0)
    frames = len(x)
    channels = 1 if x.ndim == 1 else x.shape[1]
    data = (x * 32767).astype("<i2").tobytes()
    fmt = struct.pack("<HHIIHH", 1, channels, dsp.SR, dsp.SR * channels * 2, channels * 2, 16)
    chunks = [b"fmt " + struct.pack("<I", len(fmt)) + fmt,
              b"data" + struct.pack("<I", len(data)) + data + (b"\0" if len(data) % 2 else b"")]
    if loop:
        smpl = struct.pack("<9I", 0, 0, int(1e9 / dsp.SR), 60, 0, 0, 0, 1, 0)
        smpl += struct.pack("<6I", 0, 0, 0, frames - 1, 0, 0)
        chunks.append(b"smpl" + struct.pack("<I", len(smpl)) + smpl)
    body = b"WAVE" + b"".join(chunks)
    with open(path, "wb") as fh:
        fh.write(b"RIFF" + struct.pack("<I", len(body)) + body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    wanted = {s for s in args.only.split(",") if s}
    jobs = dict(sfx.ALL)
    jobs["music"] = music.render
    for name, fn in jobs.items():
        if wanted and name not in wanted:
            continue
        t0 = time.time()
        x = fn()
        loop = name in sfx.LOOPS or name == "music"
        # Remove DC: a plain mean for loops (keeps them periodic), a gentle 20 Hz
        # high-pass for one-shots.
        if loop:
            x = x - x.mean(axis=0)
        else:
            x = dsp.normalize(dsp.highpass(x, 20.0, order=1), float(np.max(np.abs(x))))
        path = os.path.join(OUT, f"{name}.wav")
        write_wav(path, x, loop)
        print(f"[audio] {name}: {len(x) / dsp.SR:.2f} s, {'stereo' if x.ndim == 2 else 'mono'}"
              f"{', loop' if loop else ''} ({time.time() - t0:.1f} s)")


if __name__ == "__main__":
    main()
