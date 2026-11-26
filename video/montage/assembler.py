"""The complete video: the face-camera take, cut on its words, with the animation shots over the voice.

    python3 montage/assembler.py take.mov work_dir montage/final.json

Shots come from final.json: each keeps a range of the take (in seconds); a face shot shows the camera page
(montage/dynamique.*), a film shot shows the animation (film/), its own time mapped onto the voice by keyframes
[take time, film time]. After the last word, the tail of the animation plays (the tool, the end card).
Writes work/plan.json (one entry per frame), then renders and assembles with ffmpeg."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
take, work, cfgp = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
cfg = json.load(open(cfgp, encoding="utf-8"))
FPS = 30
keep = ",".join(f"{a}-{b}" for a, b in (s["src"] for s in cfg["shots"]))
subprocess.run(["python3", str(HERE / "decouper.py"), take, str(work), "--keep", keep], check=True, stdout=subprocess.DEVNULL)
subprocess.run(["python3", str(HERE / "dynamique.py"), str(work), cfgp], check=True, stdout=subprocess.DEVNULL)
cut = json.load(open(work / "decoupe.json"))


def interp(kf, x):
    for (a, fa), (b, fb) in zip(kf, kf[1:]):
        if x <= b:
            return fa + (fb - fa) * (x - a) / (b - a)
    return kf[-1][1]


I = cfg["intro"]
plan = [["dyn", n / FPS] for n in range(round(I * FPS))]
for shot, seg in zip(cfg["shots"], cut["segments"]):
    for n in range(seg["from"], seg["to"]):
        t_out = I + n / FPS
        if shot.get("face"):
            plan.append(["dyn", t_out])
        else:
            src = seg["src"][0] + (n - seg["from"]) / FPS
            plan.append(["film", interp(shot["film"], src), t_out])
talk = len(plan) / FPS
tail = cfg["tail"] if isinstance(cfg["tail"], list) and isinstance(cfg["tail"][0], dict) else [{"film": cfg["tail"]}]
pieces = []  # the tail's sound, piece by piece
for piece in tail:
    if "film" in piece:
        a, b = piece["film"]
        base = len(plan) / FPS
        plan += [["film", a + n / FPS, base + n / FPS] for n in range(round((b - a) * FPS))]
        pieces.append(["son", a, b - a])
    else:
        n = piece["n"]
        plan += [["img", f"{piece['img']}/f{k:05d}.jpg"] for k in range(n)]
        pieces.append(["fond", 0, n / FPS])
# the tail's sound: the animation's own sound for its pieces, the music bed for the frames
parts = []
for i, (kind, a, d) in enumerate(pieces):
    out = work / f"tail{i}.wav"
    if kind == "son":
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(a), "-t", str(d), "-i", str(HERE.parent / "audio/son.wav"),
                        "-ar", "48000", "-ac", "2", str(out)], check=True)
    else:
        subprocess.run(["python3", str(HERE.parent / "audio/fond.py"), str(d + 0.05), str(out) + ".raw.wav"], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(out) + ".raw.wav", "-af", "volume=-3dB", "-t", str(d),
                        "-ar", "48000", "-ac", "2", str(out)], check=True)
    parts.append(out)
(work / "tail.txt").write_text("".join(f"file '{x}'\n" for x in parts))
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "tail.txt"), str(work / "tail.wav")], check=True)


def place(t):
    for s in cut["segments"]:
        x, y = s["src"]
        if x - 0.05 <= t <= y + 0.05:
            return I + s["from"] / FPS + (t - x)
    raise SystemExit(f"caption time {t} is in no kept range")


caps = [{"small": c["small"], "smallAt": place(c["smallAt"]), "lines": c["lines"], "at": [place(t) for t in c["at"]],
         "until": place(c["until"]), "night": c.get("night", False)} for c in cfg.get("captions", [])]
json.dump({"frames": plan, "caps": caps}, open(work / "plan.json", "w"))
print(f"{len(plan)} frames, voice ends at {talk:.2f} s, total {len(plan) / FPS:.2f} s")
json.dump({"talk": talk, "total": len(plan) / FPS}, open(work / "durees.json", "w"))
