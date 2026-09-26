#!/usr/bin/env python3
"""Mux Buzzwords analyst: VO beats + music bed (sidechain-ducked) + frames -> nextplane_buzzwords.mp4
Usage: mux_bw.py [preview]"""
import os, sys
sys.path.insert(0, "/tmp/bw")
import render_bw as R
PREVIEW = "preview" in sys.argv
OUTNAME = "nextplane_buzzwords_PREVIEW_noVO.mp4" if PREVIEW else "nextplane_buzzwords.mp4"
TMP = "/tmp/bw"; DUR = R.TOTAL
MUSIC = f"{TMP}/music_el.mp3"
if not os.path.exists(f"{TMP}/video_nosound.mp4") or os.path.getsize(f"{TMP}/video_nosound.mp4") < 100000:
    os.system(f"ffmpeg -v error -framerate 30 -i {TMP}/frames/f%05d.jpg -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -movflags +faststart {TMP}/video_nosound.mp4 -y")
os.system(f"ffprobe -v error -show_entries format=duration -of default=nw=1 {TMP}/video_nosound.mp4")
if PREVIEW:
    fc = f"[0:a]volume=-9dB,apad=whole_dur={DUR},atrim=0:{DUR},loudnorm=I=-16:TP=-2.5[aout]"
    cmd = f'ffmpeg -v error -i {MUSIC} -i {TMP}/video_nosound.mp4 -filter_complex "{fc}" -map 1:v -map "[aout]" -c:v copy -c:a aac -b:a 160k -shortest {TMP}/{OUTNAME} -y'
else:
    BIDS = R.BEATS; NB = len(BIDS)
    delays = {b: int(R.OFFS[b]*1000) for b in BIDS}
    vo_in = " ".join(f"-i {TMP}/vo/{b}.mp3" for b in BIDS)
    fc = "".join(f"[{i}:a]adelay={delays[b]}|{delays[b]},apad=whole_dur={DUR}[v{i}];" for i, b in enumerate(BIDS))
    fc += "".join(f"[v{i}]" for i in range(NB))
    fc += f"amix=inputs={NB}:normalize=0,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,asplit=2[vo1][vo2];"
    fc += (f"[{NB}:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,volume=-11dB,afade=t=in:d=0.8,afade=t=out:st={DUR-1.6}:d=1.5,apad=whole_dur={DUR},"
           f"aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[mu];")
    fc += "[mu][vo2]sidechaincompress=threshold=0.015:ratio=5:attack=25:release=450:makeup=1[mud];"
    fc += "[vo1][mud]amix=inputs=2:normalize=0,"
    fc += "loudnorm=I=-13.5:TP=-2.5:linear=true,volume=0.7dB,alimiter=limit=0.75:level=false[aout]"
    cmd = (f"ffmpeg -v error {vo_in} -i {MUSIC} -i {TMP}/video_nosound.mp4 "
           f'-filter_complex "{fc}" -map {NB+1}:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -shortest {TMP}/{OUTNAME} -y')
print("music:", MUSIC); print(os.system(cmd))
os.system(f"ffprobe -v error -show_entries format=duration,size -of default=nw=1 {TMP}/{OUTNAME}")
