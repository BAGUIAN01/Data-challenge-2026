"""Cut a face-camera take into its speech segments (pauses removed): frames and clean voice, plus a timeline (JSON).

    python3 montage/decouper.py take.mov work_dir [--start 1.9]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

take, work = sys.argv[1], Path(sys.argv[2])
start = float(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 0.0
# --keep a-b,c-d: the ranges to keep, chosen on the word timings of the transcript (overrides the pauses)
keep = [tuple(map(float, r.split("-"))) for r in sys.argv[sys.argv.index("--keep") + 1].split(",")] if "--keep" in sys.argv else None
work.mkdir(parents=True, exist_ok=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", take], capture_output=True, text=True).stdout)
log = subprocess.run(["ffmpeg", "-nostats", "-i", take, "-af", "silencedetect=n=-42dB:d=0.45", "-f", "null", "-"], capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
# speech = the gaps between silences; keep pieces longer than 0.6 s, with a little air around them
speech, cur = [], 0.0
for s, e in zip(starts, ends + [dur] * (len(starts) - len(ends))):
    if s - cur > 0.6:
        speech.append((cur, s))
    cur = e
if dur - cur > 0.6:
    speech.append((cur, dur))
segs = [(max(start, a - 0.12), min(dur, b + 0.18)) for a, b in speech if b > start]
segs = [(a, b) for a, b in segs if b - a > 0.6]
if keep:
    segs = keep
# frames of each segment, upright, numbered on the output timeline; and the voice, cleaned
fr = work / "cam"
fr.mkdir(exist_ok=True)
for f in fr.glob("*.jpg"):
    f.unlink()
n0, parts = 0, []
for i, (a, b) in enumerate(segs):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{a}", "-t", f"{b - a}", "-i", take, "-vf", "fps=30,scale=1080:1920",
                    "-q:v", "3", "-start_number", str(n0), str(fr / "c%05d.jpg")], check=True)
    n = len(list(fr.glob("c*.jpg")))
    parts.append({"i": i, "src": [round(a, 3), round(b, 3)], "from": n0, "to": n})
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{a}", "-t", f"{b - a}", "-i", take, "-ac", "1", "-ar", "48000",
                    "-af", "afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse", str(work / f"v{i}.wav")], check=True)
    n0 = n
lst = work / "voix.txt"
lst.write_text("".join(f"file '{work / f'v{p['i']}.wav'}'\n" for p in parts))
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-af",
                "highpass=f=80,afftdn=nf=-50,acompressor=threshold=-24dB:ratio=3:attack=10:release=150,loudnorm=I=-16:TP=-1.5:LRA=9",
                "-ar", "48000", str(work / "voix.wav")], check=True)
json.dump({"fps": 30, "frames": n0, "segments": parts}, open(work / "decoupe.json", "w"), indent=1)
print(json.dumps(parts))
