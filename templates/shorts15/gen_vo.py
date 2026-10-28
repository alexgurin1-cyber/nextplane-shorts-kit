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
 # 2026-10-20 liquidity campaign Format A (A3): Cessna 182P Skylane, 46 d typical, 11% cut, n=73 sold (6 model years -> no value-lost number)
 "liq182p":["Is a Cessna one eighty-two P Skylane liquid?",
            "About six and a half weeks to sell. Nine in ten sell without a price cut.",
            "Check yours. "+CTA],
 # 2026-10-21 liquidity campaign Format A (A5): Cessna 400 / TTx (incl. Columbia 400, Corvalis TT/TTx), 53 d typical, 10% cut (lowest of piston
 # singles with >=20 sold), 5.6%/yr value lost (11 model years), n=39 sold
 "liqttx":["Is a Cessna T T X liquid?",
           "Fewer price cuts than any other piston single. But it loses about six percent a year.",
           "Check yours. "+CTA],
 # 2026-10-22 liquidity campaign Format A (A2): Cessna 152, 20 d typical (fastest of every family with >=12 sold in the 2026-10-18 snapshot),
 # 17% cut, n=24 sold (6 model years -> no value-lost number). Table line said "in the country"; spoken as "in our sold data" (no extrapolation).
 "liq152":["Is a Cessna one fifty-two liquid?",
           "Twenty days, the fastest in our sold data. Over four in five sell without a price cut.",
           "Check yours. "+CTA],
 # 2026-10-23 liquidity campaign Format A (A6): Piper Warrior (PA-28-161 family), 39 d typical, 14% cut (avg cut 1.0%), 0.9%/yr value lost
 # (13 model years, 1973-2007), n=49 sold. Table line "the trainer that never gets cheaper" dropped (overclaims 0.9%/yr); spoken as "holds its value".
 "liqwarrior":["Is a Piper Warrior liquid?",
           "About six weeks to sell. Most sellers never cut the price. And it holds its value.",
           "Check yours. "+CTA],
 # 2026-10-24 liquidity campaign Format A (A11): Piper Dakota family (NextPlane model_family PA28-DAKOTA = Dakota 18, Turbo Dakota 6,
 # Cherokee 235 8), n=32 sold, 57 d typical, 41% cut (Dakota-only 46%, so "four in ten" holds either way), 3.6%/yr value lost (9 model years).
 "liqdakota":["Is a Piper Dakota liquid?",
           "About eight weeks to sell. Four in ten sellers cut the price. Know that before you list.",
           "Check yours. "+CTA],
 # 2026-10-25 liquidity campaign Format A (A14): Beechcraft Duke (60/A60/B60 piston, family "Beech Duke"), n=12 sold, 8 model years,
 # 41 d typical (fastest piston-twin family with >=12 sold; Navajo 45, 414 50), 17% cut (2 of 12) -> third number omitted ("—")
 "liqduke":["Is a Beechcraft Duke liquid?",
           "Forty-one days, the fastest twin in our sold data. Over four in five sell without a price cut.",
           "Check yours. "+CTA],
 # 2026-10-26 liquidity campaign Format A (A15): Diamond DA62 (family "Diamond DA62"), n=25 sold, 8 model years (2016-2024),
 # 116 d typical, 44% cut (11 of 25), 3.9%/yr value lost (re-verified on scratch_sold_listings_20261018)
 "liqda62":["Is a Diamond DA62 liquid?",
           # v2 2026-10-26 (Alex: "the most non-liquid airplane we have so far" -> voice it as such). 116 d = slowest family of all
           # four categories in the 2026-10-18 snapshot (next: Learjet 60 101 d, TBM 850 97 d); 44% cut ties Cessna 310 for highest.
           "No. One hundred sixteen days to sell, slowest in our data. Almost half get a price cut.",   # 22-word draft ran 16.6 s, 18-word 16.2 s, 18-word v3 15.13 s (limit 15.0)
           "Check yours. "+CTA],
 # 2026-10-27 liquidity campaign Format A (A17): Pilatus PC-12 NG/NGX (family "PC-12 NG/NGX"), n=26 sold, 11 model years (2008-2024),
 # 69 d typical, 0 of 26 cut (0%) -> third number omitted ("—" in the campaign table; re-verified on scratch_sold_listings_20261018)
 "liqpc12":["Is a Pilatus PC twelve N G liquid?",
           # v2 (Alex 2026-10-27: say where it ranks): 0% cut is 1 of 4 zero-cut families among all 104 with >=12 sold (top 5%);
           # #1 of 13 turboprop families. Days to sell (69) is mid-pack, so the rank is voiced for price cuts only.
           # v1: "Zero. Not one seller in our data cut the price. About ten weeks to sell."
           "Zero price cuts. Top five percent of all models in our data. About ten weeks to sell.",
           "Check yours. "+CTA],
 # 2026-10-28 liquidity campaign Format A (A18): Daher TBM 850 (family "TBM 850", turboprop), n=14 sold, 7 model years (2006-2013)
 # -> value-lost-per-year omitted ("—"); 97 d typical = slowest of 13 turboprop families (#3 of all 104); 5 of 14 cut (36%, highest
 # turboprop, tied Caravan 208B). Campaign line "Three months, and a one-in-three chance of a cut." extended with the rank (Alex 2026-10-27).
 "liqtbm850":["Is a Daher T B M eight fifty liquid?",
           "About three months to sell, the slowest turboprop in our data. One in three get a price cut.",
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
