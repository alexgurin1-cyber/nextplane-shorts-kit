import json, os, sys, subprocess, urllib.request, threading
KEY=os.environ["ELEVENLABS_API_KEY"]
P={
"sr20":"punchy modern electronic pulse for a 12-second social video, 112 BPM, starts immediately on a hard downbeat with a sub bass hit, tight hi-hats and plucked synth, a quick riser into a bigger hit at about 3.4 seconds where the reveal lands, confident and curious, clean resolve in the final 3 seconds, no vocals, no samba",
"a36":"tense minimal electronic groove for a 13-second social video, 104 BPM, starts on beat one with a deep kick and ticking clock-like percussion, muted synth bass, builds at about 3 seconds, small lift at 7 seconds, clean resolving chord in the final 3 seconds, no vocals",
"mirage":"investigative modern underscore for a 14-second social video, 96 BPM, opens instantly with a punchy kick and dark synth stab, pulsing bass, suspense rises at about 4.4 seconds for a reveal, decisive hit at 8 seconds, warm resolve in the final 3 seconds, no vocals, not monotone",
"pa32":"bright driving modern electronic groove for a 14-second social video, 108 BPM, starts instantly on a hard downbeat with a punchy kick, plucked synth and tight claps, a falling synth sweep into a heavier drop at about 3.4 seconds where the old price is revealed, a lift at 7 seconds, confident clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"m20k":"tense, curious modern electronic groove for a 15-second social video, 100 BPM, starts instantly on a hard downbeat with a deep kick and a two-note synth motif that answers itself like a comparison, tight hats and muted bass, a dark stab at about 4.5 seconds and a lift at about 6.5 seconds where the reveal lands, confident clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"sr22t":"sleek investigative modern electronic groove for a 15-second social video, 98 BPM, starts instantly on a hard downbeat with a punchy kick and a glossy synth pluck, confident at first, then a dark filtered stab and a tense rise at about 5.6 seconds where the reveal starts, a heavy decisive hit at about 8.5 seconds, warm clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
}
# usage: gen_music.py [slug]  -> only that slug
if len(sys.argv) > 1: P = {sys.argv[1]: P[sys.argv[1]]}
def go(v):
    i=json.loads(subprocess.check_output(["python3","render15.py",v,"info"]))
    out=f"music_{v}.mp3"
    if os.path.exists(out): return
    body=json.dumps({"prompt":P[v],"music_length_ms":int(i["total"]*1000)}).encode()
    r=urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io/v1/music",data=body,headers={"xi-api-key":KEY,"Content-Type":"application/json"}),timeout=300).read()
    open(out,"wb").write(r); print(v,len(r))
ts=[threading.Thread(target=go,args=(v,)) for v in P]
[t.start() for t in ts]; [t.join() for t in ts]
