"""A dynamic edit of the face-camera part: opening sting, jump cuts with punch-ins, animated banners, key words,
a moving branded background. Writes work/dyn.html, whose window.render(t) draws frame t (async: it waits for the
camera frame to decode).

    python3 montage/dynamique.py work_dir habillage.json
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
work, cfg = Path(sys.argv[1]), json.load(open(sys.argv[2], encoding="utf-8"))
cut = json.load(open(work / "decoupe.json"))
# events are given in the take's own time (from the transcript); place them on the edited timeline
def place(t):
    for s in cut["segments"]:
        a, b = s["src"]
        if a <= t <= b:
            return cfg["intro"] + s["from"] / cut["fps"] + (t - a)
    return None
cfg["ev"] = {k: place(v) for k, v in cfg.get("events", {}).items()}
for ph in cfg.get("phrases", []):
    ph["ev"] = [place(t) for t in ph["at"]]
    ph["evEnd"] = place(ph["until"]) if "until" in ph else None
D = json.load(open(HERE.parents[1] / "preparation_jury/deck/donnees.json", encoding="utf-8"))
MAP = D["carte"]
outline = "".join(f'<path d="{g["d"]}"/>' for g in MAP["regions"].values())
VB = f'-10 -10 {float(MAP["largeur"]) + 20} {float(MAP["hauteur"]) + 20}'
fonts = (HERE.parent / "maquettes/fonts").resolve()
img = (HERE.parent / "maquettes/img").resolve()
ICON = {
    "map": '<path d="M14.1 5.1 9.9 3 3 6v15l6.9-3 4.2 2.1L21 17V2z"/><path d="M9.9 3v15"/><path d="M14.1 5.1v15"/>',
    "radar": '<path d="M19.1 4.9A10 10 0 1 1 4.9 19.1"/><path d="M16.2 7.8a6 6 0 1 1-8.5 8.5"/><circle cx="12" cy="12" r="2"/><path d="m13.4 10.6 5.7-5.7"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
}
chips = "".join(f'<div class="chip" data-k="{k}"><i><svg viewBox="0 0 24 24" fill="none" stroke="#13294B" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{ICON[ic]}</svg></i>{w}</div>'
                for k, (w, ic) in enumerate([("Cartographier", "map"), ("Prédire", "radar"), ("Agir", "target")]))
page = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
@font-face {{ font-family: Jakarta; src: url(file://{fonts}/PlusJakartaSans.woff2); font-weight: 200 700; }}
@font-face {{ font-family: Jakarta; src: url(file://{fonts}/PlusJakartaSans-800.woff2); font-weight: 800 900; }}
@font-face {{ font-family: Inter; src: url(file://{fonts}/Inter.woff2); font-weight: 100 900; }}
html, body {{ margin: 0; background: #000; }}
#f {{ width: 1920px; height: 1080px; position: relative; overflow: hidden; background: #13294B; font-family: Inter; color: #fff; }}
#grid {{ position: absolute; inset: -80px; background-image: radial-gradient(rgba(255,255,255,.09) 2px, transparent 2.5px); background-size: 44px 44px; }}
#bf {{ position: absolute; left: 900px; top: 120px; width: 1250px; opacity: .07; }}
#bf path {{ fill: none; stroke: #fff; stroke-width: 2.4; }}
#sting {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; gap: 40px; }}
.badge {{ width: 200px; height: 200px; border-radius: 48px; background: #fff; display: flex; align-items: center; justify-content: center; }}
.badge img {{ width: 80%; }}
#sting b {{ font: 800 110px Jakarta; letter-spacing: -.02em; }} #sting em {{ font-style: normal; color: #FDCD2F; }}
#bug {{ position: absolute; right: 70px; top: 56px; display: flex; align-items: center; gap: 16px; font: 800 24px Jakarta; letter-spacing: .14em; }}
#bug .badge {{ width: 62px; height: 62px; border-radius: 16px; }}
#cam {{ position: absolute; left: 150px; top: 50px; width: 551px; height: 980px; border-radius: 40px; overflow: hidden; box-shadow: 16px 16px 0 #FDCD2F; background: #222; }}
#cam img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform-origin: 50% 32%; }}
#flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; }}
.panel {{ position: absolute; left: 820px; top: 0; width: 1040px; height: 1080px; }}
.hello {{ position: absolute; left: 0; top: 330px; font: 800 150px Jakarta; letter-spacing: -.03em; }}
.card {{ position: absolute; left: 0; top: 560px; }}
.card .bar {{ height: 14px; width: 0; background: #FDCD2F; border-radius: 7px; margin-bottom: 18px; }}
.card .box {{ background: #fff; color: #13294B; border-radius: 28px; padding: 32px 44px; clip-path: inset(0 100% 0 0 round 28px); box-shadow: 0 12px 0 #FDCD2F; display: inline-block; }}
.card small {{ display: block; font: 800 22px Jakarta; letter-spacing: .14em; color: #1f4f8f; margin-bottom: 8px; }}
.card b {{ display: block; font: 800 64px Jakarta; letter-spacing: -.01em; }}
.card p {{ margin: 12px 0 0; font: 600 32px Inter; opacity: .8; }}
.big {{ position: absolute; left: 0; top: 250px; font: 800 120px/1.02 Jakarta; letter-spacing: -.02em; }} .big em {{ font-style: normal; color: #FDCD2F; }}
.chips {{ position: absolute; left: 0; top: 560px; display: flex; flex-direction: column; gap: 22px; }}
.chip {{ display: flex; align-items: center; gap: 22px; font: 800 60px Jakarta; background: #fff; color: #13294B; border-radius: 26px; padding: 18px 36px 18px 20px; box-shadow: 0 10px 0 #FDCD2F; align-self: flex-start; }}
.chip i {{ width: 76px; height: 76px; border-radius: 20px; background: #FDCD2F; display: flex; align-items: center; justify-content: center; }} .chip svg {{ width: 48px; height: 48px; }}
#chap {{ position: absolute; left: 150px; bottom: 0; height: 0; }}
.p3 {{ padding-top: 250px; }} .p3 .ln {{ overflow: hidden; padding-bottom: 30px; margin-bottom: -18px; }}
.p3 .lw {{ display: inline-block; font: 800 104px/1.02 Jakarta; letter-spacing: -.02em; }} .p3 .lw em {{ font-style: normal; color: #FDCD2F; }}
#prog {{ position: absolute; left: 0; bottom: 0; height: 8px; background: #FDCD2F; }}
</style></head><body><div id="f">
<div id="grid"></div><svg id="bf" viewBox="{VB}">{outline}</svg>
<div id="cam"><img id="ci"><div id="flash"></div></div>
<div class="panel" id="p0"><div class="hello">Bonjour.</div>
  <div class="card" id="c0"><div class="bar"></div><div class="box"><small>JE ME PRÉSENTE</small><b>{cfg["moi"]["nom"]}</b><p id="t0">{cfg["moi"]["titre"]}</p></div></div></div>
<div class="panel" id="p1"><div class="card" id="c1" style="top:400px"><div class="bar"></div><div class="box"><small>MON COÉQUIPIER</small><b id="n1">{cfg["equipier"]["nom"]}</b><p id="t1">{cfg["equipier"]["titre"]}</p></div></div></div>
<div class="panel" id="p2"><div class="big" id="b2">Équipe <em>Biiga</em></div><div class="chips">{chips}</div></div>
{"".join(f'<div class="panel p3" data-k="{k}">' + "".join(f'<div class="ln"><span class="lw" data-i="{i}">{l}</span></div>' for i, l in enumerate(ph["lines"])) + "</div>" for k, ph in enumerate(cfg.get("phrases", [])))}
<div id="bug"><div class="badge"><img src="file://{img}/logo-mark.png"></div>ÉQUIPE BIIGA</div>
<div id="sting"><div class="badge" id="sb"><img src="file://{img}/logo-mark.png"></div><b id="st">Équipe <em>Biiga</em></b></div>
<div id="prog"></div>
</div>
<script>const CUT = {json.dumps(cut)}; const CFG = {json.dumps(cfg)}; const CAM = "file://{(work / 'cam').resolve()}/";</script>
<script>{(HERE / "dynamique.js").read_text()}</script></body></html>'''
(work / "dyn.html").write_text(page, encoding="utf-8")
print(work / "dyn.html")
