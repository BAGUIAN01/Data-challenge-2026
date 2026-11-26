"""
synth.py — the small synthesiser behind the SaaS-style scores
(compose_proto.py, compose_vie2.py): sine kick, filtered noise hats and
claps, sub bass, saw plucks, a soft pad, risers and impacts, mixed into one
stereo buffer. 120 BPM.
"""
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
BPM = 120
BEAT = 60 / BPM
rng = np.random.default_rng(7)
mix = np.zeros((int(SR * 120), 2))  # long enough for any film; master() trims


def add(t, sig, gain=1.0, pan=0.0):
    i = int(t * SR)
    sig = sig[: max(0, len(mix) - i)]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[i : i + len(sig), 0] += sig * gain * l * 1.41
    mix[i : i + len(sig), 1] += sig * gain * r * 1.41


def env(n, a, d):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    att = int(a * SR)
    if att:
        e[:att] *= np.linspace(0, 1, att)
    return e


def lowpass(x, fc, order=2):
    b, a = butter(order, min(fc / (SR / 2), 0.99), "low")
    return lfilter(b, a, x)


def highpass(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2), "high")
    return lfilter(b, a, x)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def kick(gain=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / 0.035)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.16)
    click = highpass(rng.standard_normal(n), 2000) * env(n, 0, 0.004) * 0.3
    return (s + click) * gain


def hat(dur=0.05):
    n = int(0.2 * SR)
    return highpass(rng.standard_normal(n), 7000) * env(n, 0, dur) * 0.35


def clap():
    n = int(0.3 * SR)
    b, a = butter(2, [900 / (SR / 2), 2400 / (SR / 2)], "band")
    s = lfilter(b, a, rng.standard_normal(n))
    e = env(n, 0, 0.09)
    for k in (0.0, 0.011, 0.022):
        j = int(k * SR)
        e[j : j + 200] += 0.6
    return s * e * 0.5


def saw(freq, n, detune=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for d in ((-detune, 0, detune) if detune else (0,)):
        ph = (t * freq * (1 + d)) % 1.0
        out += 2 * ph - 1
    return out / (3 if detune else 1)


def pluck(m, dur=0.22, bright=3200):
    n = int(0.5 * SR)
    s = saw(hz(m), n, 0.004)
    return lowpass(s, bright) * env(n, 0.002, dur) * 0.22


def sub(m, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * hz(m) * t) + 0.25 * np.sin(4 * np.pi * hz(m) * t)
    e = np.minimum(1, t / 0.005) * np.exp(-t / (length * 0.9))
    return s * e * 0.42


def pad(ms, length):
    n = int(length * SR)
    s = sum(saw(hz(m), n, 0.006) for m in ms) / len(ms)
    t = np.arange(n) / SR
    e = np.minimum(1, t / 0.4) * np.minimum(1, (length - t) / 0.5)
    return lowpass(s, 1400) * e * 0.16


def riser(t_end, dur):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    for k in range(8):  # stepped filter sweep
        a, b = k * n // 8, (k + 1) * n // 8
        out[a:b] = highpass(noise[a:b], 300 + k * 900)
    add(t_end - dur, out * np.linspace(0, 1, n) ** 2 * 0.22)


def impact(t, gain=1.0):
    add(t, kick(1.3 * gain))
    n = int(1.6 * SR)
    add(t, lowpass(rng.standard_normal(n), 900) * env(n, 0, 0.35) * 0.35 * gain)




def scratch():
    """A record scratch: noise through a resonance swept up and down, twice, in a third of a second."""
    n = int(0.34 * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    # the stroke: the pitch of the resonance follows the hand, forward then back, forward again
    f = 500 + 2600 * np.abs(np.sin(np.pi * t / 0.17)) ** 0.7
    y = np.zeros(n)
    s1 = s2 = 0.0
    for i in range(n):
        w = 2 * np.pi * f[i] / SR
        r = 0.985
        s1, s2 = 2 * r * np.cos(w) * s1 - r * r * s2 + x[i], s1
        y[i] = s1
    y /= np.max(np.abs(y)) + 1e-9
    y *= np.minimum(1, t / 0.01) * np.exp(-t / 0.22)
    return np.stack([y, y], axis=1) * 0.8


def master(end, out):
    """Glue, limit, fade out, write a 16-bit WAV of `end` seconds."""
    x = mix[: int(SR * end)].copy()
    x = np.tanh(x * 1.2) / np.tanh(1.2)
    x /= np.max(np.abs(x)) + 1e-9
    x *= 0.89
    fade = int(0.4 * SR)
    x[-fade:] *= np.linspace(1, 0, fade)[:, None]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    wavfile.write(out, SR, (x * 32767).astype(np.int16))


CHORDS = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]  # Am F C G
ARP = [0, 1, 2, 1, 0, 2, 1, 2]


def saas_score(shots, out, accents=()):
    """The score of a SaaS-style module film. shots: [(id, frames, energy)]
    with energy 0 (pad and plucks), 1 (hats, soft pulse) or 2 (full groove);
    a riser and an impact on each id in `accents`; the shared intro accent
    and the end chord."""
    FPS = 30
    T, E = {}, []
    acc = 0
    for sid, n, e in shots:
        T[sid] = acc / FPS
        E.append((acc / FPS, (acc + n) / FPS, e))
        acc += n
    END = acc / FPS

    def energy(t):
        for a, b, e in E:
            if a <= t < b:
                return e
        return 0

    for b in range(int(END / BEAT)):
        tb = b * BEAT
        root, ch = CHORDS[(b // 4) % 4]
        e = energy(tb)
        if b % 4 == 0:
            add(tb, pad([m + 12 for m in ch], 4 * BEAT), 1.0 if e < 2 else 0.7)
        for i in range(4):
            step = (b % 2) * 4 + i
            add(tb + i * BEAT / 4, pluck(ch[ARP[step]] + 12 + (12 if step == 7 else 0), 0.16 if e == 2 else 0.24, 4200 if e == 2 else 2600), 0.85, -0.35 if i % 2 else 0.35)
        if e >= 1:
            add(tb + BEAT / 2, hat(), 0.9, 0.2)
            add(tb + BEAT / 2, sub(root - 24, BEAT / 2), 0.5 if e == 1 else 1.0)
            if b % 4 == 0 and e == 1:
                add(tb, kick(0.6))
        if e == 2:
            add(tb, kick())
            add(tb + BEAT / 4, hat(0.02), 0.5, -0.2)
            add(tb + 3 * BEAT / 4, hat(0.02), 0.5, -0.2)
            if b % 2 == 1:
                add(tb, clap(), 1.0)
            add(tb, sub(root - 24, BEAT / 2), 0.55)

    riser(58 / FPS, 1.2)
    impact(58 / FPS, 0.9)  # the dot becomes the logo
    for sid in accents:
        riser(T[sid], 0.9)
        impact(T[sid], 0.9)
    impact(T["end"] + 12 / FPS, 1.2)
    add(T["end"] + 12 / FPS, pad([60, 64, 67, 72], END - T["end"]), 1.6)
    add(T["end"] + 12 / FPS, sub(36, 3.0), 0.8)
    master(END, out)
    return END
