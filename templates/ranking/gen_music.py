#!/usr/bin/env python3
"""Music bed (ElevenLabs Music), exact length = render TOTAL."""
import json, os, urllib.request, sys, time
KEY = os.environ["ELEVENLABS_API_KEY"]; ROOT = os.environ["WORK"]
DUR = float(sys.argv[1])
P = ("confident mid-tempo analytical underscore, 96 BPM, clean modern feel: muted electric bass pulse, tight rimshot and shaker percussion, "
     "warm electric piano chords, light ticking clock texture, a steady five-step build between 12 and 50 seconds with a soft accent on each step, "
     "a suspenseful dip around 55 seconds, a warm resolve in the last 8 seconds, no vocals, no melody hooks")
body = json.dumps({"prompt": P, "music_length_ms": int(DUR*1000)}).encode()
for k in range(5):
    try:
        data = urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io/v1/music", data=body, headers={"xi-api-key": KEY, "Content-Type": "application/json"}), timeout=200).read(); break
    except Exception as e:
        print("retry", k, e); time.sleep(20)
open(f"{ROOT}/music_el.mp3", "wb").write(data); print("EL music ok", len(data)//1024, "KB")
