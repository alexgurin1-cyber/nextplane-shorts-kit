#!/usr/bin/env python3
"""VO beats + ducked music + frames -> $WORK/nextplane_<slug>.mp4"""
import os, sys, json
ROOT = os.environ["WORK"]; sys.path.insert(0, ROOT)
import render as R
slug = json.load(open(f"{ROOT}/spec.json"))["slug"]; OUT = f"{ROOT}/nextplane_{slug}.mp4"
DUR = R.TOTAL; MUSIC = f"{ROOT}/music_el.mp3"
if not os.path.exists(f"{ROOT}/video_nosound.mp4") or os.path.getsize(f"{ROOT}/video_nosound.mp4") < 100000:
    os.system(f"ffmpeg -v error -framerate 30 -i {ROOT}/frames/f%05d.jpg -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -movflags +faststart {ROOT}/video_nosound.mp4 -y")
BIDS = R.BEATS; NB = len(BIDS); delays = {b: int(R.OFFS[b]*1000) for b in BIDS}
vo_in = " ".join(f"-i {ROOT}/vo/{b}.mp3" for b in BIDS)
fc = "".join(f"[{i}:a]adelay={delays[b]}|{delays[b]},apad=whole_dur={DUR}[v{i}];" for i, b in enumerate(BIDS))
fc += "".join(f"[v{i}]" for i in range(NB))
fc += f"amix=inputs={NB}:normalize=0,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,asplit=2[vo1][vo2];"
fc += (f"[{NB}:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,volume=-11dB,afade=t=in:d=0.8,afade=t=out:st={DUR-1.6}:d=1.5,apad=whole_dur={DUR},"
       f"aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[mu];")
fc += "[mu][vo2]sidechaincompress=threshold=0.015:ratio=5:attack=25:release=450:makeup=1[mud];"
fc += "[vo1][mud]amix=inputs=2:normalize=0,loudnorm=I=-13.5:TP=-2.5:linear=true,volume=0.7dB,alimiter=limit=0.75:level=false[aout]"
cmd = f'ffmpeg -v error {vo_in} -i {MUSIC} -i {ROOT}/video_nosound.mp4 -filter_complex "{fc}" -map {NB+1}:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -shortest {OUT} -y'
print(os.system(cmd)); os.system(f"ffprobe -v error -show_entries format=duration,size -of default=nw=1 {OUT}")
