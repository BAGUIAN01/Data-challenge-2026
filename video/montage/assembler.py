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
            plan.append(["film", interp(shot["film"], src)])
talk = len(plan) / FPS
a, b = cfg["tail"]
plan += [["film", a + n / FPS] for n in range(round((b - a) * FPS))]
json.dump(plan, open(work / "plan.json", "w"))
print(f"{len(plan)} frames, voice ends at {talk:.2f} s, total {len(plan) / FPS:.2f} s")
json.dump({"talk": talk, "total": len(plan) / FPS}, open(work / "durees.json", "w"))
