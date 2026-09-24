"""Every sound effect in the game, as a recipe. Each returns a mono float array.

Musical effects use D major so they sit on top of the music track.
"""

import numpy as np

from synth import dsp
from synth.dsp import SR, midi_hz

D5, E5, FS5, G5, A5, B5, CS6, D6, E6, FS6, A6, D7 = 74, 76, 78, 79, 81, 83, 85, 86, 88, 90, 93, 98


# ----------------------------------------------------------------- loops
def engine_loop():
    """Small radial engine plus propeller wash. Built from whole cycles only, so it loops."""
    period = 1100                      # samples per firing pulse (40.09 Hz)
    pulses = 80
    n = period * pulses
    t = dsp.t_axis(n)
    f0 = SR / period
    rng = np.random.default_rng(3)
    train = np.zeros(n)
    train[::period] = rng.uniform(0.8, 1.2, pulses)
    burst_n = 420
    burst = dsp.noise(burst_n, "white", 5) * np.exp(-np.arange(burst_n) / 70.0)
    burst += np.sin(2 * np.pi * 95 * np.arange(burst_n) / SR) * np.exp(-np.arange(burst_n) / 160.0) * 1.6
    firing = dsp.circular_convolve(train, burst)
    hum = sum(np.sin(2 * np.pi * f0 * k * t + k * 0.7) / k ** 1.25 for k in range(1, 14))
    wobble_hz = 20 / (n / SR)          # whole cycles per loop
    wobble = 0.78 + 0.22 * np.sin(2 * np.pi * wobble_hz * t)
    sound = (firing * 0.9 + hum * 0.45) * wobble
    sound = dsp.circular_band(sound, 30, 1600)
    return dsp.normalize(sound, 0.8)


def wind_loop():
    n = SR * 4
    t = dsp.t_axis(n)
    w = dsp.circular_band(dsp.noise(n, "white", 21), 260, 2400, soft=1.0)
    gust = 0.72 + 0.2 * np.sin(2 * np.pi * 0.25 * t) + 0.08 * np.sin(2 * np.pi * 1.5 * t + 1.0)
    return dsp.normalize(w * gust, 0.8)


# ------------------------------------------------------------ one-shots
def _chord(notes, seconds, bell=True, pluck=True, spread=0.0):
    out = np.zeros(dsp.n_samples(seconds))
    for k, note in enumerate(notes):
        tone = np.zeros(1)
        if pluck:
            tone = dsp.pluck(midi_hz(note), seconds - k * spread, 0.997, 0.7, seed=note)
        if bell:
            b = dsp.fm_bell(midi_hz(note + 12), seconds - k * spread, 3.5, 1.6, 0.6) * 0.4
            tone = dsp.mix(tone, b)
        out = dsp.place(out, tone, k * spread)
    return out


def deliver():
    """Hoop threaded: a bright rising arpeggio that lands on a sparkling chord."""
    out = _chord([D5, FS5, A5, D6], 1.6, spread=0.07)
    sparkle = dsp.highpass(dsp.noise(dsp.n_samples(0.9), "white", 8), 6000) * dsp.exp_decay(dsp.n_samples(0.9), 0.25)
    out = dsp.place(out, sparkle * 0.25, 0.22)
    whoosh = _whoosh(0.5, 300, 3000, 12)
    out = dsp.place(out, whoosh * 0.5, 0.0)
    return dsp.normalize(dsp.reverb(out, 1.4, 0.2))


def express():
    """Express delivery: the same fanfare, one step higher and with a bell on top."""
    out = _chord([FS5, A5, D6, FS6], 1.8, spread=0.06)
    out = dsp.place(out, dsp.fm_bell(midi_hz(A6), 1.2, 3.5, 2.0, 0.5) * 0.5, 0.3)
    out = dsp.place(out, dsp.fm_bell(midi_hz(D7), 1.0, 3.5, 2.0, 0.45) * 0.35, 0.38)
    out = dsp.place(out, _whoosh(0.5, 300, 3500, 13) * 0.5, 0.0)
    return dsp.normalize(dsp.reverb(out, 1.6, 0.24))


def new_parcel():
    """A fresh destination: a soft two-note doorbell."""
    out = dsp.fm_bell(midi_hz(A5), 0.9, 2.0, 1.2, 0.35)
    out = dsp.place(out, dsp.fm_bell(midi_hz(D6), 0.9, 2.0, 1.2, 0.4), 0.14)
    return dsp.normalize(dsp.reverb(out, 1.0, 0.18), 0.7)


def _whoosh(seconds, lo, hi, seed):
    n = dsp.n_samples(seconds)
    sweep = np.geomspace(lo, hi, n)
    w = dsp.sweep_lowpass(dsp.noise(n, "white", seed), sweep)
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return w * env


def ring():
    """Boost ring: a rushing swell with a glassy shimmer."""
    out = _whoosh(0.7, 200, 5000, 31)
    for k, note in enumerate((A6, D7, FS6)):
        out = dsp.place(out, dsp.fm_bell(midi_hz(note), 0.6, 5.0, 1.0, 0.25) * 0.25, 0.1 + k * 0.05)
    return dsp.normalize(dsp.reverb(out, 1.0, 0.2))


def boost():
    """Throttle up: the engine revs while air rushes past."""
    n = dsp.n_samples(1.0)
    rev = dsp.osc(np.linspace(70, 190, n), n, "saw") * dsp.adsr(n, 0.05, 0.3, 0.6, 0.5)
    rev = dsp.lowpass(rev, 900)
    air = _whoosh(1.0, 400, 6000, 41)
    return dsp.normalize(dsp.mix(rev * 0.6, air * 0.8))


def crash():
    """A wooden thump, a crack and a little clatter."""
    n = dsp.n_samples(0.9)
    thump = dsp.osc(np.geomspace(90, 32, n), n) * dsp.exp_decay(n, 0.18, 0.001)
    crack_n = dsp.n_samples(0.08)
    crack = dsp.highpass(dsp.noise(crack_n, "white", 51), 900) * dsp.exp_decay(crack_n, 0.02)
    out = thump * 1.2
    out = dsp.place(out, crack * 0.9, 0.0)
    rng = np.random.default_rng(52)
    for k in range(6):
        tick_n = dsp.n_samples(0.05)
        tick = dsp.bandpass(dsp.noise(tick_n, "white", 60 + k), 1200, 3800) * dsp.exp_decay(tick_n, 0.012)
        out = dsp.place(out, tick * rng.uniform(0.25, 0.5), 0.08 + k * rng.uniform(0.04, 0.09))
    return dsp.normalize(dsp.soft_clip(out, 1.8))


def stamp():
    """Stamp collected: two quick bright dings."""
    out = dsp.fm_bell(midi_hz(D6 + 12), 0.5, 3.0, 1.5, 0.18)
    out = dsp.place(out, dsp.fm_bell(midi_hz(A6 + 12), 0.6, 3.0, 1.5, 0.22), 0.08)
    return dsp.normalize(dsp.reverb(out, 0.8, 0.15), 0.75)


def thunder():
    n = dsp.n_samples(3.2)
    rumble = dsp.lowpass(dsp.noise(n, "brown", 71), 260)
    rng = np.random.default_rng(72)
    swells = np.zeros(n)
    for _ in range(5):
        c = rng.uniform(0.0, 2.2)
        w = rng.uniform(0.2, 0.6)
        swells += np.exp(-((dsp.t_axis(n) - c) / w) ** 2) * rng.uniform(0.5, 1.0)
    env = dsp.exp_decay(n, 1.1, 0.01) * 0.6 + swells * dsp.exp_decay(n, 1.6) * 0.6
    crack_n = dsp.n_samples(0.25)
    crack = dsp.highpass(dsp.noise(crack_n, "white", 73), 1500) * dsp.exp_decay(crack_n, 0.05)
    out = dsp.place(rumble * env, crack * 0.6, 0.0)
    return dsp.normalize(dsp.reverb(out, 2.5, 0.3), 0.85)


def zap():
    """Flying into the storm: an electric buzz."""
    n = dsp.n_samples(0.6)
    buzz = dsp.osc(60 + 8 * np.sin(2 * np.pi * 7 * dsp.t_axis(n)), n, "square")
    buzz = dsp.bandpass(buzz + dsp.noise(n, "white", 81) * 0.6, 200, 4000)
    return dsp.normalize(buzz * dsp.adsr(n, 0.005, 0.2, 0.4, 0.3))


def tick():
    n = dsp.n_samples(0.12)
    return dsp.normalize(dsp.osc(1046.5, n) * dsp.exp_decay(n, 0.03), 0.7)


def go():
    out = np.zeros(dsp.n_samples(0.8))
    for note in (D6, FS6, A6):
        out = dsp.mix(out, dsp.fm_bell(midi_hz(note), 0.8, 2.0, 1.4, 0.3))
    return dsp.normalize(dsp.reverb(out, 1.0, 0.2), 0.8)


def clock_tick():
    """The last ten seconds: a soft woodblock."""
    n = dsp.n_samples(0.09)
    wood = dsp.bandpass(dsp.noise(n, "white", 91), 800, 2500) * dsp.exp_decay(n, 0.012)
    wood += dsp.osc(880, n) * dsp.exp_decay(n, 0.02) * 0.6
    return dsp.normalize(wood, 0.6)


def ui_click():
    n = dsp.n_samples(0.08)
    wood = dsp.bandpass(dsp.noise(n, "white", 95), 1500, 5000) * dsp.exp_decay(n, 0.008)
    wood += dsp.osc(1320, n) * dsp.exp_decay(n, 0.015) * 0.5
    return dsp.normalize(wood, 0.55)


def ui_move():
    n = dsp.n_samples(0.06)
    return dsp.normalize(dsp.osc(1760, n) * dsp.exp_decay(n, 0.01), 0.35)


def parachute():
    """The parcel's chute pops open."""
    n = dsp.n_samples(0.45)
    fwump = dsp.lowpass(dsp.noise(n, "white", 99), 700) * dsp.adsr(n, 0.01, 0.12, 0.2, 0.25)
    fwump += dsp.osc(np.geomspace(220, 120, n), n) * dsp.exp_decay(n, 0.08) * 0.5
    return dsp.normalize(fwump, 0.7)


def results():
    """Shift over: a little melody that resolves."""
    melody = [(D5, 0.0), (FS5, 0.16), (A5, 0.32), (B5, 0.48), (A5, 0.72), (FS5, 0.88), (E5, 1.04), (D5, 1.28)]
    out = np.zeros(dsp.n_samples(3.0))
    for note, at in melody:
        out = dsp.place(out, dsp.pluck(midi_hz(note), 1.2, 0.997, 0.6, seed=note), at)
        out = dsp.place(out, dsp.fm_bell(midi_hz(note + 12), 0.8, 3.5, 1.2, 0.4) * 0.3, at)
    out = dsp.place(out, _chord([D5, FS5, A5, D6], 1.6, spread=0.0) * 0.6, 1.28)
    return dsp.normalize(dsp.reverb(out, 1.8, 0.25))


def new_best():
    out = _chord([A5, D6, FS6, A6], 1.6, spread=0.09)
    sparkle = dsp.highpass(dsp.noise(dsp.n_samples(1.2), "white", 110), 7000) * dsp.exp_decay(dsp.n_samples(1.2), 0.4)
    out = dsp.place(out, sparkle * 0.3, 0.3)
    return dsp.normalize(dsp.reverb(out, 1.8, 0.26))


ALL = {
    "engine_loop": engine_loop, "wind_loop": wind_loop, "deliver": deliver, "express": express,
    "new_parcel": new_parcel, "ring": ring, "boost": boost, "crash": crash, "stamp": stamp,
    "thunder": thunder, "zap": zap, "tick": tick, "go": go, "clock_tick": clock_tick,
    "ui_click": ui_click, "ui_move": ui_move, "parachute": parachute, "results": results,
    "new_best": new_best,
}
LOOPS = {"engine_loop", "wind_loop"}
