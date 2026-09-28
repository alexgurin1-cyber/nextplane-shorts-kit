import json, os, sys, urllib.request
KEY = os.environ["ELEVENLABS_API_KEY"]
BASE = "confident mid-tempo analytical underscore for an aviation buyer's guide, 92 BPM, warm and optimistic: muted electric bass pulse, tight rimshot and shaker, warm Rhodes chords, soft plucked guitar arpeggio, clean modern documentary feel, steady energy with gentle lifts, no vocals, no prominent melody hook, key of D major"
PARTS = {"m1": BASE + ", opens with a light intro then settles into the groove",
         "m2": BASE + ", slightly fuller arrangement with added light pads, same tempo and key",
         "m3": BASE + ", same groove building a notch, then resolves warmly and ends cleanly in the final 10 seconds"}
for k in sys.argv[1:]:
    if os.path.exists(f"{k}.mp3"): continue
    body = json.dumps({"prompt": PARTS[k], "music_length_ms": 175000}).encode()
    data = urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io/v1/music", data=body, headers={"xi-api-key": KEY, "Content-Type": "application/json"}), timeout=590).read()
    open(f"{k}.mp3", "wb").write(data); print(k, len(data)//1024, "KB", flush=True)
