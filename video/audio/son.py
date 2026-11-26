#!/usr/bin/env python3
"""son.py — the soundtrack of the animated part: a 120 BPM score (balafon, pad, bass, light drums) and the sound of
every gesture, placed on the film's own plan (film/plan.py), so the sound cannot drift from the picture.
Built with the synthesiser of the Kalantigui films (synth.py); the balafon voice is the one of make_music.py.

    python3 audio/son.py        # → audio/son.wav
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "film"))
import synth  # noqa: E402
from plan import BEAT, SCENES as S  # noqa: E402
from synth import SR, add, clap, env, hat, highpass, hz, impact, kick, lowpass, pad, pluck, riser, sub  # noqa: E402

rng = np.random.default_rng(11)
END = S["end"]


def balafon(m, d=0.9):
    """Wooden bar: fundamental and inharmonic partials, a short gourd buzz, the mallet's click."""
    t = np.arange(int(SR * d)) / SR
    f = hz(m)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.45 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 22)
         + 0.18 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 40))
    buzz = np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t * 30) * 0.06
    mallet = highpass(rng.standard_normal(len(t)), 2500) * np.exp(-t * 400) * 0.25
    return (x + lowpass(buzz, 3000) + mallet) * np.clip(t / 0.001, 0, 1) * 0.3


def tok():
    """A muted, dull knock: a school switching off."""
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 40) + lowpass(rng.standard_normal(n), 600) * np.exp(-t * 60) * 0.4
    return s * 0.35


def flip():
    """A calendar page torn off."""
    n = int(0.16 * SR)
    s = highpass(rng.standard_normal(n), 1800) * env(n, 0.005, 0.05)
    return lowpass(s, 7000) * 0.35


def whoosh(dur=0.45, lo=300, hi=3000):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    for k in range(10):
        a, b = k * n // 10, (k + 1) * n // 10
        out[a:b] = lowpass(highpass(noise[a:b], 120), lo + (hi - lo) * k / 9)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out * e * 0.25


def ping(m):
    return pluck(m, 0.35, 5200) * 1.4


# ── harmony: Am F C G, a balafon riff on the C pentatonic (as in the Kalantigui films)
CHORDS = [(45, [57, 60, 64]), (41, [53, 57, 60]), (48, [55, 60, 64]), (43, [55, 59, 62])]
RIFF = [[76, 72, 69, 72, 74, 72, 69, 67], [72, 69, 65, 69, 72, 74, 72, 69],
        [76, 72, 67, 72, 79, 76, 72, 74], [74, 71, 67, 71, 74, 76, 74, 71]]


def energy(t):
    """0 pad alone · 1 pad, bass, hats, sparse balafon · 2 full groove · -1 silence."""
    if t < S["tard"]:
        return 0
    if t < S["stamp"]:
        return 1
    if t < S["titre"]:
        return -1
    if t < S["montre"]:
        return 1
    if t < S["previent"]:
        return 2
    if t < S["agir"]:
        return 1
    if t < S["fin"]:
        return 2
    return 0


def score():
    bars = int(END / (4 * BEAT)) + 1
    for b in range(bars):
        tb = b * 4 * BEAT
        root, ch = CHORDS[b % 4]
        e0 = energy(tb)
        if tb < S["logo"] and e0 >= 0:
            add(tb, pad([m + 12 for m in ch], 4 * BEAT), 1.0 if e0 < 2 else 0.75)
        for beat in range(4):
            t = tb + beat * BEAT
            e = energy(t)
            if e < 0 or t >= S["logo"]:
                continue
            if e >= 1:
                add(t, sub(root - 12, BEAT * 0.9), 0.55 if e == 1 else 0.8)
                add(t + BEAT / 2, hat(), 0.7, 0.25)
            if e == 2:
                add(t, kick(0.9))
                if beat % 2 == 1:
                    add(t, clap(), 0.8)
                add(t + BEAT / 4, hat(0.02), 0.45, -0.25)
                add(t + 3 * BEAT / 4, hat(0.02), 0.45, -0.25)
            for k in range(2):
                note = RIFF[b % 4][beat * 2 + k]
                if e == 2 or (e == 1 and k == 0):
                    add(t + k * BEAT / 2, balafon(note), 0.9 if e == 2 else 0.7, -0.3 if k else 0.3)


def gestures():
    # schools light up: a rising balafon run; then switch off one by one, north and east first
    for i, m in enumerate([67, 69, 72, 74, 76, 79, 81, 84, 86]):
        add(0.4 + i * 0.2, balafon(m, 0.6), 0.55, -0.4 + i * 0.09)
    for i in range(10):
        add(S["off"] + i * 0.22, tok(), 0.95 - i * 0.05, 0.3 - i * 0.06)
    impact(S["off"] + 0.1, 0.5)
    # the calendar
    add(S["tard"] - 0.15, whoosh(), 1.0)
    for k in range(6):
        add(S["flip"] + k * 0.25, flip(), 1.0, (-1) ** k * 0.3)
    add(S["rapport"], ping(76), 1.0)
    impact(S["stamp"], 1.4)
    riser(S["titre"], 1.4)
    impact(S["titre"], 0.9)
    add(S["titre"] + 0.4, balafon(84, 1.2), 0.9)
    # it shows: one balafon note per sudden drop
    add(S["montre"] - 0.15, whoosh(), 0.9)
    for i, m in enumerate([72, 74, 76, 79, 81, 84, 86, 88]):
        add(S["bulles"] + i * 0.25, balafon(m, 0.7), 0.85, -0.4 + i * 0.1)
    # it warns: a high ping per alert
    add(S["previent"] - 0.1, whoosh(0.5, 200, 1800), 1.0)
    for i in range(5):
        add(S["alertes"] + i * 0.2, ping(81 + (i % 2) * 3), 0.8, -0.3 + i * 0.15)
    add(S["sep"], ping(76), 0.9)
    add(S["jan"], ping(79), 0.9)
    # what to do: the regions rise, then one chord per lever
    add(S["agir"] - 0.1, whoosh(), 0.9)
    add(S["lift"], whoosh(0.8, 150, 900), 0.8)
    for i, (r, ch) in enumerate(CHORDS):
        for m in ch:
            add(S["tags"] + i * 0.9, balafon(m + 12, 0.9), 0.55)
    # the tool
    add(S["outil"] - 0.15, whoosh(), 1.0)
    add(S["phone"], whoosh(0.4, 400, 2500), 0.7)
    add(S["zoom"], whoosh(1.0, 150, 1200), 0.7)
    add(S["zoom"] + 1.0, ping(84), 0.8)
    add(S["papier"], whoosh(0.5, 300, 2200), 0.8)
    # the end
    add(S["fin"] - 0.1, whoosh(0.6, 200, 1500), 1.0)
    impact(S["fin"] + 1.0, 1.1)
    for i, m in enumerate([57, 60, 64, 69, 72, 76]):
        add(S["logo"] + i * 0.09, balafon(m, 2.5), 0.7)
    add(S["logo"], pad([57, 60, 64, 69], 3.5), 1.6)
    add(S["logo"], sub(33, 3.0), 0.9)


def main():
    score()
    # airplane mode: everything cuts for half a second, then comes back
    a, b = int(S["avion"] * SR), int((S["avion"] + 0.5) * SR)
    synth.mix[a:b] = 0.0
    gestures()
    click = highpass(rng.standard_normal(int(0.03 * SR)), 3000) * env(int(0.03 * SR), 0, 0.006) * 0.8
    add(S["avion"], click, 1.0)
    impact(S["avion"] + 0.5, 0.9)
    synth.master(END, str(HERE / "son.wav"))
    print("son.wav", END, "s")


if __name__ == "__main__":
    main()
