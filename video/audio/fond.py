#!/usr/bin/env python3
"""fond.py — the music under the voice of the complete video: an opening sting, then a light balafon groove
(pad, bass, hats, the riff on one note in two) for as long as the voice lasts. Same harmony and voice as son.py.

    python3 audio/fond.py seconds out.wav
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "film"))
import synth  # noqa: E402
from son import CHORDS, RIFF, balafon  # noqa: E402
from synth import BEAT, add, hat, impact, pad, riser, sub  # noqa: E402

D, OUT = float(sys.argv[1]), sys.argv[2]
synth.mix = np.zeros((int(synth.SR * (D + 4)), 2))
# opening sting: the logo pops at 0.15 s, a bright balafon note follows
impact(0.15, 0.9)
add(0.5, balafon(84, 1.2), 0.9)
for b in range(int(D / (4 * BEAT)) + 1):
    tb = b * 4 * BEAT
    root, ch = CHORDS[b % 4]
    add(tb, pad([m + 12 for m in ch], 4 * BEAT), 0.9)
    for beat in range(4):
        t = tb + beat * BEAT
        add(t, sub(root - 12, BEAT * 0.9), 0.5)
        add(t + BEAT / 2, hat(), 0.5, 0.25)
        add(t, balafon(RIFF[b % 4][beat * 2]), 0.6, 0.3)
synth.master(D, OUT)
print(OUT, D)
