#!/usr/bin/env python3
"""Tyler Cash VO from $WORK/spec.json beats (ElevenLabs with-timestamps)."""
import base64, json, os, sys, urllib.request, time
KEY = os.environ["ELEVENLABS_API_KEY"]; VOICE = "5DB4wgykoKoCu98YaGe6"
URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps"
ROOT = os.environ["WORK"]; OUT = f"{ROOT}/vo"; os.makedirs(OUT, exist_ok=True)
BEATS = json.load(open(f"{ROOT}/spec.json"))["vo"]
def gen(bid, text):
    body = json.dumps({"text": text, "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.62, "similarity_boost": 0.85, "style": 0.25, "use_speaker_boost": True}}).encode()
    for k in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(URL, data=body, headers={"xi-api-key": KEY, "Content-Type": "application/json"}), timeout=180)); break
        except Exception as e:
            if k == 3: raise
            time.sleep(8)
    open(f"{OUT}/{bid}.mp3", "wb").write(base64.b64decode(r["audio_base64"]))
    al = r["alignment"]; chars, starts, ends = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    words, cur, ws = [], "", None
    for c, s, e in zip(chars, starts, ends):
        if c.strip() == "":
            if cur: words.append({"w": cur, "s": ws, "e": e}); cur, ws = "", None
        else:
            if ws is None: ws = s
            cur += c
    if cur: words.append({"w": cur, "s": ws, "e": ends[-1]})
    json.dump({"dur": ends[-1], "words": words}, open(f"{OUT}/{bid}.json", "w"))
    bad = [(w["w"], round(w["e"]-w["s"], 2)) for w in words[:-1] if w["e"]-w["s"] > 1.8]
    print(bid, round(ends[-1], 2), "s,", len(words), "words", ("SMEAR:"+str(bad)) if bad else "OK")
for bid in (sys.argv[1:] or list(BEATS)):
    if os.path.exists(f"{OUT}/{bid}.json"): print(bid, "exists"); continue
    gen(bid, BEATS[bid])
