import json, os, sys, subprocess, urllib.request, urllib.error, threading
KEY=os.environ["ELEVENLABS_API_KEY"]
P={
"sr20":"punchy modern electronic pulse for a 12-second social video, 112 BPM, starts immediately on a hard downbeat with a sub bass hit, tight hi-hats and plucked synth, a quick riser into a bigger hit at about 3.4 seconds where the reveal lands, confident and curious, clean resolve in the final 3 seconds, no vocals, no samba",
"a36":"tense minimal electronic groove for a 13-second social video, 104 BPM, starts on beat one with a deep kick and ticking clock-like percussion, muted synth bass, builds at about 3 seconds, small lift at 7 seconds, clean resolving chord in the final 3 seconds, no vocals",
"mirage":"investigative modern underscore for a 14-second social video, 96 BPM, opens instantly with a punchy kick and dark synth stab, pulsing bass, suspense rises at about 4.4 seconds for a reveal, decisive hit at 8 seconds, warm resolve in the final 3 seconds, no vocals, not monotone",
"pa32":"bright driving modern electronic groove for a 14-second social video, 108 BPM, starts instantly on a hard downbeat with a punchy kick, plucked synth and tight claps, a falling synth sweep into a heavier drop at about 3.4 seconds where the old price is revealed, a lift at 7 seconds, confident clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"m20k":"tense, curious modern electronic groove for a 15-second social video, 100 BPM, starts instantly on a hard downbeat with a deep kick and a two-note synth motif that answers itself like a comparison, tight hats and muted bass, a dark stab at about 4.5 seconds and a lift at about 6.5 seconds where the reveal lands, confident clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"sr22t":"sleek investigative modern electronic groove for a 15-second social video, 98 BPM, starts instantly on a hard downbeat with a punchy kick and a glossy synth pluck, confident at first, then a dark filtered stab and a tense rise at about 5.6 seconds where the reveal starts, a heavy decisive hit at about 8.5 seconds, warm clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"a36cut":"confident modern electronic groove for a 15-second social video, 104 BPM, starts instantly on a hard downbeat with a punchy kick, warm plucked synth and tight claps, a descending three-step synth figure around 4 to 7 seconds like a price stepping down, a heavier hit at about 7.5 seconds, bright clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"sr20g6":"curious, upbeat modern electronic groove for a 15-second social video, 106 BPM, starts instantly on a hard downbeat with a punchy kick and a bright two-note synth call-and-response like a side-by-side comparison, tight hats and rolling bass, a two-step descending figure around 5 to 7 seconds, a lift at about 8 seconds where the second fact lands, clean confident resolve in the final 3 seconds, no vocals, not monotone, no samba",
"liq172m":"bright, curious modern electronic groove for a 15-second social video, 108 BPM, starts instantly on a hard downbeat with a punchy kick and a questioning two-note synth pluck, tight hats and rolling bass, two short percussive drops at about 3 and 4.5 seconds as numbers land, a confident lift with a bigger hit at about 5.7 seconds for the verdict, clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"liqttx":"sleek, driving modern electronic groove for a 15-second social video, 112 BPM, starts instantly on a hard downbeat with a punchy kick and a sharp two-note synth question, tight hats and a pulsing bass line, three short percussive drops at about 3, 4.5 and 7 seconds as numbers land, a confident lift with a bigger hit at about 8.5 seconds for the verdict, clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"liqwarrior":"steady, upbeat modern electronic groove for a 15-second social video, 110 BPM, starts instantly on a hard downbeat with a punchy kick and a bright two-note synth question, crisp hats and a warm walking bass line, three short percussive drops at about 3, 4.5 and 6 seconds as numbers land, a confident lift with a bigger hit at about 7.5 seconds for the verdict, clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"liqdakota":"patient, warm modern electronic groove for a 15-second social video, 100 BPM, starts instantly on a hard downbeat with a punchy kick and a thoughtful two-note synth question, tight hats and a deep rolling bass line, three short percussive drops at about 3, 5 and 8 seconds as numbers land, a measured lift with a bigger hit at about 9.5 seconds for the verdict, clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"liqduke":"bold, propulsive modern electronic groove for a 15-second social video, 114 BPM, starts instantly on a hard downbeat with a punchy kick and a confident two-note brass-like synth question, crisp hats and a driving twin-pulse bass line, a sharp percussive drop at about 3 seconds and another at about 6.5 seconds as numbers land, a bright lift with a bigger hit at about 8.5 seconds for the verdict, clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"liq152":"quick, upbeat modern electronic groove for a 15-second social video, 116 BPM, starts instantly on a hard downbeat with a punchy kick and a playful two-note synth question, crisp hats and a bouncing bass line, a sharp percussive drop at about 3 seconds and another at about 6 seconds as numbers land, a bright lift with a bigger hit at about 8 seconds for the verdict, clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
"liq182p":"warm, confident modern electronic groove for a 15-second social video, 104 BPM, starts instantly on a hard downbeat with a punchy kick and a rising two-note synth question, tight hats and a rolling bass line, a short percussive drop at about 3 seconds and another at about 4.5 seconds as numbers land, a bright lift with a bigger hit at about 6.2 seconds for the verdict, clean resolve in the final 3 seconds, no vocals, not monotone, no samba",
}
# usage: gen_music.py [slug]  -> only that slug
if len(sys.argv) > 1: P = {sys.argv[1]: P[sys.argv[1]]}
def go(v):
    i=json.loads(subprocess.check_output(["python3","render15.py",v,"info"]))
    out=f"music_{v}.mp3"
    if os.path.exists(out): return
    body=json.dumps({"prompt":P[v],"music_length_ms":int(i["total"]*1000)}).encode()
    import time
    for k in range(5):  # music endpoint often 429s on the first call (seen 2026-10-17); back off and retry
        try:
            r=urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io/v1/music",data=body,headers={"xi-api-key":KEY,"Content-Type":"application/json"}),timeout=300).read(); break
        except urllib.error.HTTPError as e:
            if e.code!=429 or k==4: raise
            print(v,"429, retrying in",45*(k+1),"s"); time.sleep(45*(k+1))
    open(out,"wb").write(r); print(v,len(r))
ts=[threading.Thread(target=go,args=(v,)) for v in P]
[t.start() for t in ts]; [t.join() for t in ts]
