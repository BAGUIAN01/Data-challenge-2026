# Vidéo de la dernière étape : la partie animée

Une minute, sans voix, en musique, qui suit la partie face caméra. Aucun chiffre à l'écran : des cartes et des mots.
Chaque état de la carte vient des données de l'analyse (écoles par région et part fermée, taux d'achèvement, pires
baisses, risque 2026/27, régions prioritaires et leviers).

| Dossier | Ce que c'est |
| --- | --- |
| `maquettes/` | les six images clés validées avant l'animation, les polices, les images de l'outil |
| `film/` | le film : `plan.py` (les temps, sur une pulsation de 0,5 s), `construire.py` (la page), `film.css`, `film.js` (`render(t)`) |
| `audio/` | la bande-son : `son.py` (musique au balafon et bruitages, sur le même plan), `synth.py` (le synthétiseur des films Kalantigui) |
| `out/` | `biiga-animation.mp4` : 1920 × 1080, 30 i/s, H.264, AAC, −14 LUFS |

## Refaire la vidéo

```bash
python3 film/construire.py                                   # → film/film.html
node film/stills.cjs /tmp/stills 2,20,44                     # quelques images pour relire
node film/rendre.cjs /tmp/frames                             # toutes les images (30 par seconde)
python3 audio/son.py                                         # → audio/son.wav
ffmpeg -framerate 30 -i /tmp/frames/f%05d.jpg -i audio/son.wav -c:v libx264 -crf 17 -pix_fmt yuv420p \
  -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 256k -shortest out/biiga-animation.mp4
```

`rendre.cjs` et `stills.cjs` utilisent Playwright (Chromium). `construire.py` demande `qrcode`.
