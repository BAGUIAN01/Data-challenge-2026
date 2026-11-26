"""The film's beat plan, in seconds: 120 BPM, one beat = 0.5 s, every cut on a beat. The picture (film.js) and the
score (audio/son.py) both read it, so the sound cannot drift from the image. Version 2: 52 s."""
BEAT = 0.5
URL = "kalantigui-decrochage.vercel.app"

SCENES = {
    "ecoles": 0.0,     # schools light up all over the country
    "off": 3.2,        # the camera closes in on the north and east, schools switch off
    "tard": 6.5,       # the calendar: September, a decision to make
    "flip": 8.0,       # pages turn (no month named: we do not know the report's exact date)
    "rapport": 9.5,    # "months later": the report
    "stamp": 10.25,    # TOO LATE
    "titre": 12.5,     # the logo
    "montre": 16.0,    # 1 · it shows: the regions drop in, slow decline
    "bulles": 18.6,    # the sudden drops
    "previent": 23.5,  # 2 · it warns
    "alertes": 25.0,   # the alert badges
    "sep": 27.0,       # September: alert
    "jan": 28.0,       # January: confirm
    "agir": 31.0,      # 3 · what to do
    "lift": 31.8,      # the priority regions rise
    "tags": 33.5,      # the four levers, one every 0.9 s
    "outil": 39.5,     # the tool
    "phone": 40.6,     # the phone arrives
    "avion": 42.0,     # airplane mode: the sound cuts
    "zoom": 42.3,      # the camera closes in on the offline banner
    "papier": 45.4,    # the printed sheet
    "fin": 47.0,       # before the school year, not after
    "logo": 49.3,      # the end card
    "end": 52.0,
}
