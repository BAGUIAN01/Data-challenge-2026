"""The film's beat plan, in seconds: 120 BPM, one beat = 0.5 s, every cut on a beat. The picture (film.js) and the
score (son.py) both read it, so the sound cannot drift from the image."""
BEAT = 0.5
URL = "kalantigui-decrochage.vercel.app"

SCENES = {
    "ecoles": 0.0,      # schools light up, then switch off in the north and east
    "flip": 9.0,        # the calendar pages start turning
    "rapport": 10.75,   # the report arrives
    "stamp": 11.5,      # TOO LATE
    "tard": 7.0,        # the calendar scene
    "titre": 13.0,      # the logo
    "montre": 17.0,     # 1 · it shows
    "bulles": 21.5,     # the sudden drops
    "previent": 27.0,   # 2 · it warns
    "agir": 37.0,       # 3 · what to do
    "tags": 39.5,       # the four levers, one per beat pair
    "outil": 47.0,      # the tool
    "avion": 50.5,      # airplane mode
    "papier": 52.5,     # the printed sheet
    "fin": 55.0,        # before the school year, not after
    "logo": 57.5,       # the end card
    "end": 61.0,
}
