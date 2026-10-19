import base64, json, os, sys, urllib.request
KEY=os.environ["ELEVENLABS_API_KEY"]; VOICE="5DB4wgykoKoCu98YaGe6"
URL=f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps"
OUT=os.environ["WORK"]+"/vo"; os.makedirs(OUT, exist_ok=True)
CTA="Before you call the broker, check the data at NextPlane dot U S."
S={
 "sr20":["Three fifty-four nine for this Cirrus S R twenty.",
         "Twelve days ago, same airplane, same hours: two seventy-nine nine.", CTA],
 "a36":["Two A36 Bonanzas. Both two ninety-nine.",
        "One hasn't moved since April. The other was two ninety in August, then went up.", CTA],
 "mirage":["Five fifty, for the lowest-time Malibu Mirage on the market, says the ad.",
           "What it leaves out: a twenty twenty N T S B report. Substantial damage.", CTA],
 # 2026-10-14 daily run (plain-dollar standard: speak prices in full words, exact figures on screen)
 "pa32":["One hundred forty-two thousand dollars for this Piper Cherokee Six.",
         "In July, same seller, same hours: one hundred ninety-two thousand. The new ad doesn't say.", CTA],
 # 2026-10-15 daily run: SAME PRICE TWINS, Mooney M20K 231 (N3594H unchanged + 1984 accident record; N231HB cut twice)
 "m20k":["Two Mooney two thirty-ones. Both one hundred forty-nine thousand dollars.",
         "One was cut twice. The other has a federal accident record from nineteen eighty-four.", CTA],
 # 2026-10-16 daily run: WHAT THE AD LEFT OUT, 2021 Cirrus SR22T N236CB ("meticulously maintained"; NTSB CEN24LA309 Aug 6 2024, serial 2336)
 "sr22t":["About eight hundred thousand dollars, for a meticulously maintained Cirrus S R twenty-two, says the ad.",
          "What it leaves out: a twenty twenty-four federal accident record. Substantial damage.", CTA],
 # 2026-10-17 daily run: PRICE JUMP (down, same ad), 1980 Beechcraft A36 Bonanza N614MM, $310,000 (Aug 5) -> $229,000 (Oct 15), three cuts
 # 2026-10-18 daily run: SAME PRICE TWINS, Cirrus SR20 G6 at $489,900: N665M (2022, 740 h, cut twice from $534,900) vs N34AS (2021, 1,785 h, unchanged since Apr 13)
 "sr20g6":["Two Cirrus S R twenties. Both about four hundred ninety thousand dollars.",
           "The newer one has less than half the hours and was cut twice. The other hasn't moved since April.", CTA],
 # 2026-10-19 liquidity campaign Format A "Liquidity check" (model-level, no tail): Cessna 172M Skyhawk, 29 d typical, 14% cut, n=66 sold
 # b3 = "Check yours." + verbatim CTA (campaign spec); slug prefix "liq" selects scene_liq() in render15.py
 "liq172m":["Is a Cessna one seventy-two M liquid?",
            "A month on the market, and most sellers never touch the price. Every flight school wants one.",
            "Check yours. "+CTA],
 "a36cut":["Two hundred twenty-nine thousand dollars for this Beechcraft Bonanza A36.",
           "In August, the same ad asked three hundred ten thousand. It's been cut three times.", CTA],
}
# usage: gen_vo.py [slug]  -> only that slug (no need to delete the pilot entries)
if len(sys.argv) > 1: S = {sys.argv[1]: S[sys.argv[1]]}
def gen(bid,text):
    if os.path.exists(f"{OUT}/{bid}.json"): return
    body=json.dumps({"text":text,"model_id":"eleven_turbo_v2_5","voice_settings":{"stability":0.62,"similarity_boost":0.85,"style":0.25,"use_speaker_boost":True}}).encode()
    r=json.load(urllib.request.urlopen(urllib.request.Request(URL,data=body,headers={"xi-api-key":KEY,"Content-Type":"application/json"}),timeout=180))
    open(f"{OUT}/{bid}.mp3","wb").write(base64.b64decode(r["audio_base64"]))
    al=r["alignment"]; words=[]; cur=""; ws=None
    for c,s,e in zip(al["characters"],al["character_start_times_seconds"],al["character_end_times_seconds"]):
        if c.strip()=="":
            if cur: words.append({"w":cur,"s":ws,"e":pe}); cur="";ws=None
        else:
            if ws is None: ws=s
            cur+=c; pe=e
    if cur: words.append({"w":cur,"s":ws,"e":pe})
    json.dump({"dur":al["character_end_times_seconds"][-1],"words":words},open(f"{OUT}/{bid}.json","w"))
for v,beats in S.items():
    for i,t in enumerate(beats):
        bid=f"{v}_b{i+1}"; gen(bid,t)
        d=json.load(open(f"{OUT}/{bid}.json")); bad=[w["w"] for w in d["words"][:-1] if w["e"]-w["s"]>1.8]
        print(bid, round(d["dur"],2), len(d["words"]), "SMEAR "+str(bad) if bad else "ok")
