"""A small DSP toolkit: oscillators, noise, envelopes, filters, reverb, and the two
instruments the music leans on (Karplus-Strong pluck and FM bell).

Everything is numpy arrays of float64 at SR. Looping sounds are built from periodic
parts only (whole cycles, circular filtering, circular convolution) so they loop
without a click.
"""

import wave

import numpy as np
from scipy import signal

SR = 44100


def n_samples(seconds):
    return int(round(seconds * SR))


def t_axis(n):
    return np.arange(n) / SR


# ------------------------------------------------------------------ sources
def osc(freq, n, shape="sine", phase=0.0):
    """Oscillator. `freq` may be a scalar or a per-sample array (sweeps)."""
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,))
    ph = phase + np.cumsum(f) / SR
    ph -= ph[0] - phase
    frac = ph % 1.0
    if shape == "sine":
        return np.sin(2 * np.pi * ph)
    if shape == "saw":
        return 2.0 * frac - 1.0
    if shape == "square":
        return np.where(frac < 0.5, 1.0, -1.0)
    if shape == "triangle":
        return 4.0 * np.abs(frac - 0.5) - 1.0
    raise ValueError(shape)


def noise(n, color="white", seed=0):
    rng = np.random.default_rng(seed)
    w = rng.standard_normal(n)
    if color == "white":
        return w
    spec = np.fft.rfft(w)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1]
    spec *= (1 / np.sqrt(f)) if color == "pink" else (1 / f)
    out = np.fft.irfft(spec, n)
    return out / (np.max(np.abs(out)) + 1e-9)


# ---------------------------------------------------------------- envelopes
def adsr(n, attack=0.005, decay=0.1, sustain=0.0, release=0.05):
    a, d, r = n_samples(attack), n_samples(decay), n_samples(release)
    s_len = max(n - a - d - r, 0)
    env = np.concatenate([np.linspace(0, 1, max(a, 1), endpoint=False),
                          np.linspace(1, sustain, max(d, 1), endpoint=False),
                          np.full(s_len, sustain),
                          np.linspace(sustain, 0, max(r, 1))])
    return _fit(env, n)


def exp_decay(n, tau, attack=0.002):
    t = t_axis(n)
    env = np.exp(-t / tau)
    a = n_samples(attack)
    if a > 1:
        env[:a] *= np.linspace(0, 1, a)
    return env


def _fit(x, n):
    return x[:n] if len(x) >= n else np.concatenate([x, np.zeros(n - len(x))])


# ------------------------------------------------------------------ filters
def lowpass(x, cutoff, order=2):
    sos = signal.butter(order, min(cutoff, SR * 0.45), "low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def highpass(x, cutoff, order=2):
    sos = signal.butter(order, cutoff, "high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def bandpass(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, min(hi, SR * 0.45)], "band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def sweep_lowpass(x, cutoffs, block=256):
    """Time-varying low-pass: `cutoffs` is one value per sample, applied per block."""
    out = np.zeros_like(x)
    zi = None
    for start in range(0, len(x), block):
        c = float(np.clip(cutoffs[min(start, len(cutoffs) - 1)], 30.0, SR * 0.45))
        sos = signal.butter(2, c, "low", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[start:start + block], zi = signal.sosfilt(sos, x[start:start + block], zi=zi)
    return out


def circular_band(x, lo, hi, soft=1.3):
    """Band-limit a periodic signal in the frequency domain (keeps loops seamless)."""
    n = len(x)
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    gain = np.ones_like(f)
    if lo > 0:
        gain *= 1 / (1 + (lo / np.maximum(f, 1e-6)) ** (2 * soft))
    if hi > 0:
        gain *= 1 / (1 + (f / hi) ** (2 * soft))
    return np.fft.irfft(spec * gain, n)


def circular_convolve(x, kernel):
    n = len(x)
    k = np.zeros(n)
    k[:len(kernel)] = kernel
    return np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(k), n)


# ------------------------------------------------------------------- effects
def reverb(x, seconds=1.8, wet=0.22, damp=3500.0, seed=11, predelay=0.012):
    """Convolution reverb with a synthetic, damped noise impulse response."""
    n = n_samples(seconds)
    ir = noise(n, "white", seed) * np.exp(-t_axis(n) / (seconds / 5.5))
    ir = lowpass(ir, damp)
    ir = np.concatenate([np.zeros(n_samples(predelay)), ir])
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    tail = signal.fftconvolve(x, ir)
    out = np.concatenate([x, np.zeros(len(tail) - len(x))])
    return out + wet * tail


def soft_clip(x, drive=1.5):
    return np.tanh(x * drive) / np.tanh(drive)


def pan(x, position):
    """Mono to stereo, position -1 (left) .. +1 (right), constant power."""
    a = (position + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1)


def mix(*tracks):
    n = max(len(t) for t in tracks)
    shape = (n, 2) if any(t.ndim == 2 for t in tracks) else (n,)
    out = np.zeros(shape)
    for t in tracks:
        if out.ndim == 2 and t.ndim == 1:
            t = np.stack([t, t], axis=1) * 0.7071
        out[:len(t)] += t
    return out


def place(buffer, sound, at_seconds, gain=1.0):
    """Add `sound` into `buffer` starting at a time, growing the buffer if needed."""
    start = n_samples(at_seconds)
    end = start + len(sound)
    if end > len(buffer):
        pad_shape = (end - len(buffer),) + buffer.shape[1:]
        buffer = np.concatenate([buffer, np.zeros(pad_shape)])
    if buffer.ndim == 2 and sound.ndim == 1:
        sound = np.stack([sound, sound], axis=1) * 0.7071
    buffer[start:end] += sound * gain
    return buffer


def normalize(x, peak=0.89):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def fade(x, fade_in=0.0, fade_out=0.0):
    x = x.copy()
    a, b = n_samples(fade_in), n_samples(fade_out)
    if a > 0:
        ramp = np.linspace(0, 1, a)
        x[:a] *= ramp if x.ndim == 1 else ramp[:, None]
    if b > 0:
        ramp = np.linspace(1, 0, b)
        x[-b:] *= ramp if x.ndim == 1 else ramp[:, None]
    return x


def fold_tail(x, loop_len):
    """Wrap everything past loop_len back onto the start, so reverb tails and ringing
    notes carry over the loop point seamlessly."""
    out = x[:loop_len].copy()
    rest = x[loop_len:]
    while len(rest):
        k = min(len(rest), loop_len)
        out[:k] += rest[:k]
        rest = rest[k:]
    return out


# --------------------------------------------------------------- instruments
def midi_hz(note):
    return 440.0 * 2 ** ((note - 69) / 12)


def pluck(freq, seconds, damping=0.996, brightness=0.55, seed=0):
    """Karplus-Strong string, vectorized one delay-line period at a time."""
    n = n_samples(seconds)
    period = max(2, int(round(SR / freq)))
    rng = np.random.default_rng(seed)
    burst = rng.uniform(-1, 1, period)
    burst = lowpass(burst, 1200 + brightness * 7000)
    burst -= burst.mean()  # the string's averaging filter would carry any DC forever
    # y[n] = damping * (y[n-N] + y[n-N-1]) / 2, one period per numpy step. Index 0 is a
    # silent lead-in so every read stays strictly behind the samples being written.
    out = np.zeros(n + period + 2)
    out[1:period + 1] = burst
    pos = period + 1
    while pos < n + 1:
        block = min(period, n + 1 - pos)
        prev = out[pos - period - 1:pos - period + block]
        out[pos:pos + block] = damping * 0.5 * (prev[:block] + prev[1:block + 1])
        pos += block
    return out[1:n + 1] * exp_decay(n, seconds * 0.9, 0.001)


def fm_bell(freq, seconds, ratio=3.5, index=2.4, tau=0.9):
    n = n_samples(seconds)
    t = t_axis(n)
    env = np.exp(-t / tau)
    mod = np.sin(2 * np.pi * freq * ratio * t) * index * np.exp(-t / (tau * 0.5))
    return np.sin(2 * np.pi * freq * t + mod) * env * adsr(n, 0.002, 0.0, 1.0, 0.02)


def write_wav(path, x):
    x = np.clip(x, -1.0, 1.0)
    data = (x * 32767).astype("<i2")
    channels = 1 if x.ndim == 1 else x.shape[1]
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
