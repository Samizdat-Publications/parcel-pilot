"""Audio QA without ears: levels, clipping, DC, loop-seam continuity, and spectrograms.

  python tools/audio_report.py      # prints a table, writes build/audio_report.png

A loop is seamless when the jump from its last sample back to its first is no bigger
than an ordinary sample-to-sample step inside the file.
"""

import glob
import os
import struct
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from toolpaths import BUILD, GAME

AUDIO = os.path.join(GAME, "assets", "audio")


def read_wav(path):
    with wave.open(path, "rb") as w:
        ch, sr, n = w.getnchannels(), w.getframerate(), w.getnframes()
        x = np.frombuffer(w.readframes(n), dtype="<i2").astype(float) / 32767.0
    x = x.reshape(-1, ch).mean(axis=1) if ch > 1 else x
    with open(path, "rb") as fh:
        loops = b"smpl" in fh.read()
    return x, sr, ch, loops


def spectrogram(x, sr, width=560, height=140):
    win = 1024
    hop = max(win // 4, len(x) // width)
    frames = [x[i:i + win] * np.hanning(win) for i in range(0, max(len(x) - win, 1), hop)]
    if not frames:
        return Image.new("RGB", (width, height))
    mag = np.abs(np.fft.rfft(np.array(frames), axis=1))
    db = 20 * np.log10(mag + 1e-6)
    db = np.clip((db - db.max() + 80) / 80, 0, 1)
    freqs = np.fft.rfftfreq(win, 1 / sr)
    rows = np.geomspace(40, sr / 2, height)  # log frequency axis
    idx = np.searchsorted(freqs, rows).clip(0, len(freqs) - 1)
    img = db[:, idx].T[::-1]
    r = (np.clip(img * 1.6, 0, 1) * 255).astype(np.uint8)
    g = (np.clip(img * 1.6 - 0.5, 0, 1) * 255).astype(np.uint8)
    b = (np.clip(0.3 + img * 0.6, 0, 1) * 255 * (1 - img * 0.5)).astype(np.uint8)
    return Image.fromarray(np.stack([r, g, b], axis=2)).resize((width, height))


def main():
    rows = []
    tiles = []
    for path in sorted(glob.glob(os.path.join(AUDIO, "*.wav"))):
        name = os.path.splitext(os.path.basename(path))[0]
        x, sr, ch, loops = read_wav(path)
        peak = np.max(np.abs(x))
        rms = np.sqrt(np.mean(x ** 2))
        clipped = int(np.sum(np.abs(x) > 0.999))
        steps = np.abs(np.diff(x))
        seam = abs(x[0] - x[-1]) / (np.percentile(steps, 99) + 1e-9) if loops else 0.0
        verdict = "ok"
        if clipped > 10 or np.isnan(x).any() or abs(np.mean(x)) > 0.01:
            verdict = "CHECK"
        if loops and seam > 1.5:
            verdict = "SEAM"
        rows.append((name, len(x) / sr, ch, peak, 20 * np.log10(rms + 1e-9), clipped, seam, loops, verdict))
        tiles.append((name, spectrogram(x, sr)))
    print(f"{'sound':<12} {'sec':>6} {'ch':>2} {'peak':>5} {'rms dB':>7} {'clip':>5} {'seam':>5}  verdict")
    for (name, sec, ch, peak, rms, clipped, seam, loops, verdict) in rows:
        seam_s = f"{seam:5.2f}" if loops else "   - "
        print(f"{name:<12} {sec:6.2f} {ch:>2} {peak:5.2f} {rms:7.1f} {clipped:5d} {seam_s}  {verdict}")
    cols = 2
    w, h = 560, 140
    sheet = Image.new("RGB", (cols * (w + 10), ((len(tiles) + 1) // cols) * (h + 26)), (18, 18, 22))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default(size=14)
    except TypeError:
        font = ImageFont.load_default()
    for i, (name, img) in enumerate(tiles):
        x0, y0 = (i % cols) * (w + 10), (i // cols) * (h + 26)
        draw.text((x0 + 4, y0 + 4), name, fill=(230, 225, 210), font=font)
        sheet.paste(img, (x0, y0 + 22))
    os.makedirs(BUILD, exist_ok=True)
    sheet.save(os.path.join(BUILD, "audio_report.png"))
    print("[audio_report] build/audio_report.png")


if __name__ == "__main__":
    main()
