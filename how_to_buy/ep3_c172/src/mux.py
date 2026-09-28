import os, sys, subprocess
sys.path.insert(0, "/tmp/htb_c172")
from timeline import OFFS, TOTAL
from beats import BEATS
R = "/tmp/htb_c172"; DUR = TOTAL
segs = sorted(f for f in os.listdir(f"{R}/segs") if f.endswith(".mp4") and "part" not in f)
open(f"{R}/segs/list.txt", "w").write("".join(f"file '{R}/segs/{s}'\n" for s in segs))
subprocess.run(f"ffmpeg -v error -y -f concat -safe 0 -i {R}/segs/list.txt -c copy {R}/video_nosound.mp4", shell=True, check=True)
BIDS = [b for b, _, _ in BEATS]; NB = len(BIDS)
vo_in = " ".join(f"-i {R}/vo/{b}.mp3" for b in BIDS)
fc = "".join(f"[{i}:a]adelay={int(OFFS[b]*1000)}|{int(OFFS[b]*1000)},apad=whole_dur={DUR}[v{i}];" for i, b in enumerate(BIDS))
fc += "".join(f"[v{i}]" for i in range(NB))
fc += f"amix=inputs={NB}:normalize=0,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,asplit=2[vo1][vo2];"
fc += (f"[{NB}:a]atrim=18:{DUR+18},asetpts=PTS-STARTPTS,volume=-12dB,afade=t=in:d=1.0,afade=t=out:st={DUR-3}:d=3,apad=whole_dur={DUR},"
       f"aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[mu];")
fc += "[mu][vo2]sidechaincompress=threshold=0.015:ratio=5:attack=25:release=450:makeup=1[mud];"
fc += "[vo1][mud]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11:linear=true,alimiter=limit=0.78:level=false[aout]"
cmd = (f"ffmpeg -v error -y {vo_in} -i {R}/music_full.wav -i {R}/video_nosound.mp4 "
       f'-filter_complex "{fc}" -map {NB+1}:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart {R}/ep3_how_to_buy_c172.mp4')
subprocess.run(cmd, shell=True, check=True)
os.system(f"ffprobe -v error -show_entries format=duration,size -of default=nw=1 {R}/ep3_how_to_buy_c172.mp4")
