import base64, json, os, sys, urllib.request
sys.path.insert(0, "/tmp/htb_m350"); from beats import BEATS
KEY = os.environ["ELEVENLABS_API_KEY"]; VOICE = "5DB4wgykoKoCu98YaGe6"
URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps"
OUT = "/tmp/htb_m350/vo"; os.makedirs(OUT, exist_ok=True)
def gen(bid, text):
    body = json.dumps({"text": text, "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.62, "similarity_boost": 0.85, "style": 0.25, "use_speaker_boost": True}}).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request(URL, data=body, headers={"xi-api-key": KEY, "Content-Type": "application/json"}), timeout=300))
    open(f"{OUT}/{bid}.mp3", "wb").write(base64.b64decode(r["audio_base64"]))
    al = r["alignment"]; words, cur, ws = [], "", None
    for c, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if c.strip() == "":
            if cur: words.append({"w": cur, "s": ws, "e": e}); cur, ws = "", None
        else:
            if ws is None: ws = s
            cur += c
    if cur: words.append({"w": cur, "s": ws, "e": al["character_end_times_seconds"][-1]})
    dur = al["character_end_times_seconds"][-1]
    json.dump({"dur": dur, "words": words}, open(f"{OUT}/{bid}.json", "w"))
    bad = [(w["w"], round(w["e"]-w["s"],2)) for w in words[:-1] if w["e"]-w["s"] > 1.8]
    print(bid, round(dur,1), "s", len(words), "w", ("SMEAR:"+str(bad)) if bad else "OK", flush=True)
for bid, _, text in BEATS:
    if len(sys.argv) > 1 and bid not in sys.argv[1:]: continue
    if os.path.exists(f"{OUT}/{bid}.json") and len(sys.argv) == 1: continue
    gen(bid, text)
