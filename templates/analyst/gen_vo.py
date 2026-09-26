#!/usr/bin/env python3
"""Tyler Cash VO for the "Buzzwords" CLASSIC ANALYST short (ElevenLabs with-timestamps)."""
import base64, json, os, sys, urllib.request
KEY = os.environ["ELEVENLABS_API_KEY"]
VOICE = "5DB4wgykoKoCu98YaGe6"
URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps"
OUT = "/tmp/bw/vo"
os.makedirs(OUT, exist_ok=True)
BEATS = {
"b1": "An ad says, complete logs. Nice words. Across four hundred forty nine ads that use them, they add exactly zero dollars.",
"b2": "NextPlane matched each one against the same model, the same few years, listings that don't say it. Six phrases. One question: which ones are worth real money?",
"b3": "Meticulously maintained: plus ten thousand dollars. Always hangared: plus fifty three hundred. One owner: plus three thousand. No damage history: plus one thousand, basically noise. And complete logs: zero.",
"b4": "The phrase built to reassure you the most costs the seller money. No accident, no corrosion: minus ninety nine hundred dollars. It shows up more on older airplanes. The plane that doesn't need to say it, usually doesn't.",
"b5": "A nineteen sixty eight Cherokee, forty three thousand dollars: complete logbooks, no damage history. A twenty twenty three Cirrus turbo, nine hundred fifty thousand dollars: meticulously maintained. Same script. Different stakes.",
"b6": "This is what buyers pay next to the words, not proof the words caused it. Asking prices, not sold prices. And meticulous ads skew newer and better equipped: the adjective and the airplane travel together.",
"b7": "Don't buy the story. Buy the data. Before you call the broker, check the data at NextPlane dot U S.",
}
def gen(bid, text):
    body = json.dumps({"text": text, "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.62, "similarity_boost": 0.85, "style": 0.25, "use_speaker_boost": True}}).encode()
    req = urllib.request.Request(URL, data=body, headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=180))
    open(f"{OUT}/{bid}.mp3", "wb").write(base64.b64decode(r["audio_base64"]))
    al = r["alignment"]
    chars, starts, ends = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    words, cur, ws = [], "", None
    for c, s, e in zip(chars, starts, ends):
        if c.strip() == "":
            if cur: words.append({"w": cur, "s": ws, "e": e}); cur, ws = "", None
        else:
            if ws is None: ws = s
            cur += c
    if cur: words.append({"w": cur, "s": ws, "e": ends[-1]})
    json.dump({"dur": ends[-1], "words": words}, open(f"{OUT}/{bid}.json", "w"))
    bad = [(w["w"], round(w["e"]-w["s"],2)) for w in words[:-1] if w["e"]-w["s"] > 1.8]
    print(bid, round(ends[-1],2), "s,", len(words), "words", ("SMEAR:"+str(bad)) if bad else "OK")
for bid in (sys.argv[1:] or list(BEATS)):
    if os.path.exists(f"{OUT}/{bid}.json"):
        print(bid, "exists, skip"); continue
    gen(bid, BEATS[bid])
