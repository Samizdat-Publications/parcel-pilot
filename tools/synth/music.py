"""The music loop: an easygoing 104 BPM tune in D major.

Plucked ukulele-ish arpeggios (Karplus-Strong), a glockenspiel melody (FM bells),
a round sine bass, a soft detuned pad, and light percussion. Rendered with a tail
that is folded back onto the start, so the loop point is seamless.
"""

import numpy as np

from synth import dsp
from synth.dsp import SR, midi_hz

BPM = 104
BEAT = 60.0 / BPM
BAR = 4 * BEAT

CHORDS = {"D": (62, 66, 69), "A": (61, 64, 69), "Bm": (62, 66, 71), "G": (62, 67, 71)}
BASS = {"D": 50, "A": 45, "Bm": 47, "G": 43}
PROGRESSION = ["D", "A", "Bm", "G", "D", "A", "G", "A",
               "Bm", "G", "D", "A", "Bm", "G", "A", "D"]

# (bar, beat, midi note, length in beats)
MELODY = [
    (0, 0, 78, 1), (0, 1, 81, 1), (0, 2, 86, 1.5), (0, 3.5, 85, 0.5),
    (1, 0, 83, 1), (1, 1, 81, 1), (1, 2, 76, 2),
    (2, 0, 78, 1), (2, 1, 83, 1), (2, 2, 86, 1), (2, 3, 85, 1),
    (3, 0, 83, 1.5), (3, 1.5, 81, 0.5), (3, 2, 79, 2),
    (4, 0, 78, 1), (4, 1, 81, 1), (4, 2, 86, 1), (4, 3, 90, 1),
    (5, 0, 88, 1.5), (5, 1.5, 86, 0.5), (5, 2, 85, 1), (5, 3, 81, 1),
    (6, 0, 83, 1), (6, 1, 86, 1), (6, 2, 85, 1), (6, 3, 88, 1),
    (7, 0, 85, 2), (7, 2, 88, 2),
    (8, 0, 86, 1), (8, 1, 83, 1), (8, 2, 78, 2),
    (9, 0, 79, 1), (9, 1, 83, 1), (9, 2, 86, 1.5), (9, 3.5, 83, 0.5),
    (10, 0, 81, 1), (10, 1, 78, 1), (10, 2, 81, 1), (10, 3, 86, 1),
    (11, 0, 85, 2), (11, 2, 88, 2),
    (12, 0, 90, 1.5), (12, 1.5, 88, 0.5), (12, 2, 86, 1), (12, 3, 83, 1),
    (13, 0, 86, 1.5), (13, 1.5, 83, 0.5), (13, 2, 79, 2),
    (14, 0, 81, 1), (14, 1, 85, 1), (14, 2, 88, 1), (14, 3, 85, 1),
    (15, 0, 86, 4),
]
ARPEGGIO = (0, 1, 2, 3, 2, 1, 2, 3)   # index into chord tones; 3 = root an octave up


def _kick():
    n = dsp.n_samples(0.3)
    return dsp.osc(np.geomspace(115, 42, n), n) * dsp.exp_decay(n, 0.09, 0.002)


def _snare():
    n = dsp.n_samples(0.18)
    body = dsp.bandpass(dsp.noise(n, "white", 7), 900, 5000) * dsp.exp_decay(n, 0.05)
    return body + dsp.osc(190, n) * dsp.exp_decay(n, 0.03) * 0.4


def _shaker(seed):
    n = dsp.n_samples(0.06)
    return dsp.highpass(dsp.noise(n, "white", seed), 6000) * dsp.adsr(n, 0.01, 0.04, 0.0, 0.01)


def _pad(notes, seconds):
    n = dsp.n_samples(seconds)
    voice = np.zeros(n)
    for note in notes:
        for detune in (-0.12, 0.12):
            voice += dsp.osc(midi_hz(note + detune), n, "saw")
    voice = dsp.lowpass(voice, 1400)
    return voice * dsp.adsr(n, 0.35, 0.2, 0.8, 0.6)


def render():
    loop_len = dsp.n_samples(BAR * len(PROGRESSION))
    total = loop_len + dsp.n_samples(3.0)
    pluck_l = np.zeros(total)
    bells = np.zeros(total)
    bass = np.zeros(total)
    pad = np.zeros(total)
    drums = np.zeros(total)
    shaker = np.zeros(total)

    plucks = {}
    for bar, chord in enumerate(PROGRESSION):
        tones = list(CHORDS[chord]) + [CHORDS[chord][0] + 12]
        start = bar * BAR
        for k, idx in enumerate(ARPEGGIO):
            note = tones[idx] + 12
            if note not in plucks:
                plucks[note] = dsp.pluck(midi_hz(note), 1.4, 0.996, 0.5, seed=note)
            accent = 1.0 if k % 2 == 0 else 0.7
            pluck_l = dsp.place(pluck_l, plucks[note], start + k * BEAT * 0.5, 0.55 * accent)
        root = BASS[chord]
        for beat, length in ((0, 1.5), (1.5, 0.5), (2, 1.0), (3, 1.0)):
            n = dsp.n_samples(length * BEAT * 0.95)
            tone = dsp.osc(midi_hz(root if beat != 3 else root + 7), n, "sine")
            tone += dsp.osc(midi_hz(root), n, "triangle") * 0.3
            bass = dsp.place(bass, tone * dsp.adsr(n, 0.01, 0.1, 0.7, 0.08), start + beat * BEAT, 0.7)
        pad = dsp.place(pad, _pad(CHORDS[chord], BAR * 1.05), start, 0.12)
        for beat in range(4):
            if beat in (0, 2):
                drums = dsp.place(drums, _kick(), start + beat * BEAT, 0.9)
            else:
                drums = dsp.place(drums, _snare(), start + beat * BEAT, 0.3)
        for eighth in range(8):
            shaker = dsp.place(shaker, _shaker(bar * 8 + eighth), start + eighth * BEAT * 0.5,
                               0.12 if eighth % 2 else 0.07)

    for (bar, beat, note, length) in MELODY:
        seconds = length * BEAT + 0.8
        tone = dsp.fm_bell(midi_hz(note), seconds, 3.5, 1.1, 0.55) * 0.8
        tone += dsp.fm_bell(midi_hz(note + 12), seconds, 7.0, 0.5, 0.3) * 0.15
        bells = dsp.place(bells, tone, bar * BAR + beat * BEAT, 0.42)

    left = pluck_l * 0.8 + bells * 0.45 + pad * 0.6 + shaker * 0.4
    right = pluck_l * 0.45 + bells * 0.8 + pad * 0.6 + shaker * 0.9
    center = bass + drums
    stereo = np.stack([left + center, right + center], axis=1)
    wet = np.stack([dsp.reverb(stereo[:, 0], 2.2, 0.3, seed=3), dsp.reverb(stereo[:, 1], 2.2, 0.3, seed=4)], axis=1)
    looped = np.stack([dsp.fold_tail(wet[:, 0], loop_len), dsp.fold_tail(wet[:, 1], loop_len)], axis=1)
    return dsp.normalize(dsp.soft_clip(looped / np.max(np.abs(looped)), 1.2), 0.82)
