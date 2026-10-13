import json, subprocess, sys, os
v=sys.argv[1]
i=json.loads(subprocess.check_output(["python3","render15.py",v,"info"]))
DUR=i["total"]; B=[f"{v}_b{k}" for k in (1,2,3)]
subprocess.run(f"ffmpeg -v error -y -framerate 30 -i frames_{v}/f%05d.jpg -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart vid_{v}.mp4",shell=True,check=True)
fc="".join(f"[{k}:a]adelay={int(i['offs'][b]*1000)}|{int(i['offs'][b]*1000)},apad=whole_dur={DUR}[v{k}];" for k,b in enumerate(B))
fc+="[v0][v1][v2]amix=inputs=3:normalize=0,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,asplit=2[vo1][vo2];"
fc+=f"[3:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,volume=-8dB,afade=t=out:st={DUR-0.9}:d=0.85,apad=whole_dur={DUR},aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[mu];"
fc+="[mu][vo2]sidechaincompress=threshold=0.015:ratio=4:attack=20:release=350:makeup=1[mud];[vo1][mud]amix=inputs=2:normalize=0,loudnorm=I=-13.5:TP=-2.5:linear=true,volume=0.7dB,alimiter=limit=0.75:level=false[aout]"
ins=" ".join(f"-i vo/{b}.mp3" for b in B)
subprocess.run(f'ffmpeg -v error -y {ins} -i music_{v}.mp3 -i vid_{v}.mp4 -filter_complex "{fc}" -map 4:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -ar 48000 -t {DUR} -movflags +faststart nextplane15_{v}.mp4',shell=True,check=True)
