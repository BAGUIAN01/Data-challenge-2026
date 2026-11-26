#!/bin/bash
# Assemble the complete video: frames, voice over the music bed, then the tail of the animation with its own sound.
#   bash montage/encoder.sh work_dir out.mp4
set -e
W=$1; OUT=$2; CFG=${3:-$(dirname "$0")/final.json}; CFG=$(cd "$(dirname "$CFG")" && pwd)/$(basename "$CFG"); V=$(cd "$(dirname "$0")/.." && pwd)
TALK=$(python3 -c "import json;print(round(json.load(open('$W/durees.json'))['talk'],3))")
TAIL=$(python3 -c "import json;c=json.load(open('$CFG'));print(c['tail'][1]-c['tail'][0])")
TAIL0=$(python3 -c "import json;c=json.load(open('$CFG'));print(c['tail'][0])")
INTRO_MS=$(python3 -c "import json;c=json.load(open('$CFG'));print(int(c['intro']*1000))")
ffmpeg -y -loglevel error -framerate 30 -i "$W/final/f%05d.jpg" -i "$W/fond.wav" -i "$W/voix.wav" -ss "$TAIL0" -t "$TAIL" -i "$V/audio/son.wav" -filter_complex "
[1:a]aresample=48000,volume='if(lt(t,1.25),1,if(lt(t,1.6),1-(t-1.25)/0.35*0.82,0.18))':eval=frame,atrim=duration=$TALK[bed];
[2:a]aresample=48000,adelay=$INTRO_MS|$INTRO_MS,apad,atrim=duration=$TALK[vo];
[bed][vo]amix=inputs=2:normalize=0,afade=t=out:st=$(python3 -c "print($TALK-0.25)"):d=0.25[talk];
[3:a]aresample=48000,afade=t=in:d=0.15[tail];
[talk][tail]concat=n=2:v=0:a=1,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -map_metadata -1 -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest "$OUT"
ffprobe -v error -show_entries format=duration,size -of compact "$OUT"
