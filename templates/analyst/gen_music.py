#!/usr/bin/env python3
"""Music bed for the Buzzwords analyst short — ElevenLabs Music, exact length."""
import json, os, urllib.request, sys
KEY = os.environ["ELEVENLABS_API_KEY"]
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 93.92
body = json.dumps({"prompt": "confident mid-tempo analytical underscore, 94 BPM, workshop-groove feel: muted electric bass pulse, tight rimshot and shaker percussion, warm Rhodes chords, subtle typewriter-click texture, clean and modern, builds a notch at 30 seconds and again at 70 seconds, a small suspenseful dip around 55 seconds for a twist reveal, resolves warmly in the last 8 seconds, no vocals, no melody hooks", "music_length_ms": int(DUR*1000)}).encode()
req = urllib.request.Request("https://api.elevenlabs.io/v1/music", data=body, headers={"xi-api-key": KEY, "Content-Type": "application/json"})
data = urllib.request.urlopen(req, timeout=170).read()
open("/tmp/bw/music_el.mp3", "wb").write(data); print("EL music ok", len(data)//1024, "KB")
