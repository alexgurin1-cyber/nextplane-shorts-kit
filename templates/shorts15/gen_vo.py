import base64, json, os, sys, urllib.request
KEY=os.environ["ELEVENLABS_API_KEY"]; VOICE="5DB4wgykoKoCu98YaGe6"
URL=f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps"
OUT=os.environ["WORK"]+"/vo"; os.makedirs(OUT, exist_ok=True)
CTA="Before you call the broker, check the data at NextPlane dot U S."
S={
 # 2026-11-11 daily run: SAME PRICE TWINS, Beechcraft A36 Bonanza at $349,000: N8088J (1990, E-2502, 1,844 h since new on the
 # original engine per both ads, dealer NC, $369,000 Oct 6 -> $349,000 Nov 7) vs N85BB (1973, E-508, 7,315 h, IO-550-B 30 h since
 # RAM overhaul, dealer NE, $349,000 unchanged since Jul 2). No federal accident record on either (N-number and serial).
 "a36eng":["Two Bonanza A thirty-sixes. Both three hundred forty-nine thousand dollars.",
           "One is seventeen years newer, on its original engine. The other has a fresh overhaul.", CTA],
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
 # 2026-10-30 daily run (replaces withdrawn liqlj45): WHAT THE AD LEFT OUT, 2020 Cessna 172S Skyhawk SP N20818, dealer ad 257843429 $599,000
 # ("Zero SMOH, Zero Since New Prop, New Paint"); NTSB CEN23LA394, Sep 2 2023, Englewood CO, substantial damage, 2 minor injuries, serial 172S12579 matched
 "c172s":["About six hundred thousand dollars for this twenty twenty Skyhawk. New engine, new paint.",
          "What it leaves out: a twenty twenty-three federal accident record. Substantial damage.", CTA],
 # 2026-11-02 daily run: SAME PRICE TWINS, Piper Turbo Arrow III at $134,000: N41GF (1977, cut four times $159,000 -> $134,000,
 # engine 1,155 h) vs N6089H (1978, unchanged since Apr 18, engine 511 h). No federal accident record on either airframe.
 "arrow3":["Two Piper Turbo Arrows. Both one hundred thirty-four thousand dollars.",
           "One was cut four times. The other has under half the engine hours and hasn't moved since April.", CTA],
 # 2026-11-03 daily run: WHAT THE AD LEFT OUT, 2023 Cirrus SR20 G6 N190BM, dealer ad 261520569 (Provo UT) $499,900 since Oct 21,
 # b1 v1 with "Cirrus" ran 15.23 s (make stays on screen). "beautifully equipped", 395 h since new; NTSB WPR23LA358, Sep 27 2023, Salt Lake City UT, substantial damage, instructional, no injuries, serial 9381 matched
 "sr20bm":["About five hundred thousand dollars, for a beautifully equipped S R twenty, says the ad.",
           "What it leaves out: a twenty twenty-three federal accident record. Substantial damage.", CTA],
 # 2026-11-04 daily run: SAME PRICE TWINS, Cessna 182N Skylane at $175,000: N9051G (1970, dealer MO, engine 134 h since overhaul;
 # NTSB MIA88LA275 Sep 29 1988 Belleview FL, substantial damage, 1 minor injury, serial 18260591 matched; ad damage field false, text silent)
 # vs N9164G (1971, dealer CA, engine 950 h since overhaul, no federal accident record by N-number or serial). Neither price has moved.
 # v1 ("Two Cessna one eighty-two Skylanes" / "The other has no record.") ran ~16.3 s, and "...The other doesn't." still 16.2 s; 182 and B's clean record stay on screen.
 "c182n":["Two Cessna Skylanes. Both one hundred seventy-five thousand dollars.",
          "One has a fresh engine overhaul, and a federal accident record from nineteen eighty-eight.", CTA],
 # 2026-11-09 daily run: WHAT THE AD LEFT OUT, 1975 Cessna 182P Skylane N9802E, dealer ad tap_2456163 (Livermore CA) $169,950
 # ("factory brand new engine and factory brand new propeller with only 58 hours since new"); NTSB WPR22LA252, Jul 14 2022,
 # San Martin CA, substantial damage, 2 aboard, no injuries, Part 91 personal, serial 18263916 matched; ad damage field false, text silent
 "c182p":["A hundred seventy thousand dollars for this Skylane. Brand-new engine and prop.",
          "What it leaves out: a twenty twenty-two federal accident record. Substantial damage.", CTA],
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
 # 2026-10-29 liquidity campaign Format A (A12): Cessna 414/414A (family "Cessna 414/414A"), n=59 sold, 11 model years (1971-85),
 # 50 d typical (#3 of 13 twin families), 7 of 59 cut (12%, 2nd-fewest of 13 twins after Navajo/Chieftain 9%), 4.7%/yr value lost
 # (re-verified on scratch.scratch_sold_listings_20261018). Campaign line "The twin that sells at the asking price." voiced as the plain fraction.
 "liq414":["Is a Cessna four fourteen liquid?",
           "About seven weeks to sell. Nearly nine in ten never get cut. It loses about five percent a year.",   # 21-word v1 ran 15.73 s (limit 15.0)
           "Check yours. "+CTA],
 # 2026-10-30 liquidity campaign Format A (A19): Learjet 45/45XR (family "Learjet 45/45XR"), n=16 sold, 9 model years (1999-2012),
 # 27 d typical = fastest of all jet families with >=12 sold (next: CJ1 44 d), 1 of 16 cut (6%); lost/yr omitted per campaign table ("—").
 # Re-verified on scratch.scratch_sold_listings_20261018. No prices voiced (jet).
 "liqlj45":["Is a Learjet forty-five liquid?",
            "Twenty-seven days, the fastest jet in our sold data. Fifteen of sixteen sell without a price cut.",
            "Check yours. "+CTA],
 "a36cut":["Two hundred twenty-nine thousand dollars for this Beechcraft Bonanza A36.",
           "In August, the same ad asked three hundred ten thousand. It's been cut three times.", CTA],
 # 2026-10-31 daily run: PRICE JUMP (down, same ad), 1978 Beechcraft F33A Bonanza N22099, dealer ad 260580053 (Raleigh NC),
 # $345,000 first recorded Sep 25 -> $299,500 Oct 1 -> $279,900 Oct 15 -> $250,000 Oct 21 (three cuts in 26 days, -$95,000)
 # b1 v1 "...for this Beechcraft Bonanza F thirty-three A." ran 15.24 s total; "Beechcraft" dropped (on screen instead)
 "f33a":["Two hundred fifty thousand dollars for this Bonanza F thirty-three A.",
         "In September, the same ad asked three hundred forty-five thousand. Three cuts in under four weeks.", CTA],
 # 2026-10-30 first-of-the-month PRICE CUTS set (Alex): one clip per category; counts = distinct US airplanes with a >=1% cut that month
 "cuts_single":["So you want to buy a single-engine airplane?",
                "Five hundred seventy-five got a price cut in September. Six hundred fifteen in October. Is yours one of them?", CTA],
 "cuts_twin":["So you want to buy a twin?",
              "Seventy-six got a price cut in September. Eighty-nine in October. Is yours one of them?", CTA],
 "cuts_turboprop":["So you want to buy a turboprop?",
                   "Thirty-one got a price cut in September. Forty-eight in October. The cuts are rising. Is yours next?", CTA],
 # 2026-11-03 NUMBER clip pilot (Alex: alternate single-airplane clips with market numbers). DAMAGE HISTORY, US piston singles
 # for sale with an N-number: 479 of 3,001 (16.0% -> "one in six") = 366 ads that disclose damage + 113 with a serial-matched
 # federal substantial-damage record whose ad damage field is false. campaign/numbers/DATA_20261103.md
 "num_dmg_single":["Shopping for a single-engine airplane?",
                   "One in six for sale has a damage history. A hundred thirteen ads don't mention it. Is yours one of them?", CTA],
 # 2026-11-05 TRAINING HISTORY, Cirrus SR20: 37 of 116 (31.9% -> "nearly one in three"); 35 of the 37 ("most") averaged >250 airframe hours/yr.
 # campaign/numbers/DATA_20261105.md
 "num_trn_sr20":["Shopping for a Cirrus S R twenty?",
                 "Nearly one in three shows signs of a training past. Most averaged over two hundred fifty hours a year. Is yours one of them?", CTA],
 # 2026-11-06 PRICE HISTORY (up): 2007 Beechcraft G36 Bonanza N6980B, serial E-3780, same dealer (Lexington KY) relisted it five times:
 # $624,900 May 23 -> $599,900 Jul 7 -> $579,900 Jul 29 -> $549,900 Aug 29 (last seen Sep 19) -> $699,900 Oct 15 with a zero-time engine
 # (earlier ads: 1,727 h engine, "discuss options of including a Zero time engine"). Up $150,000 from the September ask.
 # 2026-11-07 SELLER OWNERSHIP, US single-engine pistons (builds <= 2024, seen in the last 7 days): 603 of 2,687 with a valid FAA
 # certificate date were registered to the seller under 2 years ago (22.4% -> "more than one in five"); 238 under 1 year.
 # campaign/numbers/DATA_20261107.md
 "num_own_single":["Shopping for a single-engine airplane?",
                   "More than one in five sellers has owned it under two years. Two hundred thirty-eight, under one year. Is yours one of them?", CTA],
 # 2026-11-14 SELLER OWNERSHIP, Beechcraft Bonanza (US, N-number, builds <= 2024, seen in the last 7 days, listing serial =
 # FAA serial): 35 of 257 registered to the seller under 2 years ago (13.6% -> "nearly one in seven"); 12 under 1 year.
 # campaign/numbers/DATA_20261114.md
 "num_own_bonanza":["Shopping for a Beechcraft Bonanza?",
                    "Nearly one in seven sellers has owned it under two years. Twelve, under one year. Is yours one of them?", CTA],
 # 2026-11-08 PRICED HIGHER, US single-engine pistons seen in the last 7 days: 64 of 2,374 (2.7% -> "almost three in a hundred")
 # are priced above their own first ask or above an earlier closed ad for the same tail; 34 above an earlier ad (53% -> "about half").
 # Strict count after row check (history-based first ask, 3-day glitch rule, price sanity screen). campaign/numbers/DATA_20261108.md
 # 2026-11-15 PRICED HIGHER, US Piper single-engine pistons seen in the last 7 days: 13 of 485 (2.7% -> "almost three in a
 # hundred") after row check (4 dropped: N12345 placeholder, N31920 glitch first ask, N478MD serial mismatch, N5889V serial
 # mismatch +59%); largest: Malibu Mirage s/n 4636508 ad closed Jun 16 at $659,000 -> new ad Aug 5 at $789,000 (+$130,000).
 # campaign/numbers/DATA_20261115.md
 "num_up_piper":["Shopping for a single-engine Piper?",
                 "Almost three in a hundred ask more than before. One Malibu came back a hundred thirty thousand dollars higher. Is yours one of them?", CTA],
 # 2026-11-16 ONE DOLLAR FIGURE, Cessna 182 family (US, N-number, seen in the last 7 days): 89 of 227 (39.2% -> "almost four
 # in ten") ask less than their first recorded ask; median cut $15,000 (cuts > 35% dropped). campaign/numbers/DATA_20261116.md
 # 2026-11-17 daily run: REPORT DEMO (post day Fri 2026-11-20), 2004 Cirrus SR22 G2 N656CD, serial 1006, dealer UT, 930 h.
 # Two live ads, same dealer, both seen 2026-11-17: tap_2456749 $360,000 unchanged since Jul 4; 256792343 $299,000 after three cuts
 # ($360,000 Jun 2 -> $349,000 Jul 9 -> $329,000 Sep 5 -> $299,000 Oct 31). Report: "Live ads disagree on price"; est. value $325,000.
 "demo_sr22n656":["You found this S R twenty-two at three hundred sixty thousand. Is that the right price?",
                  "The report: a second live ad, same airplane, two hundred ninety-nine thousand.", CTA],
 # 2026-11-18 daily run: REPORT DEMO (post day Fri 2026-11-20), 2024 Cirrus SR22T G7 N772RG, serial 10037, dealer TN, 261 h.
 # One ad, first seen Apr 13 at $1,139,900; cuts May 6, Jul 29, Oct 9 -> $1,084,900. Report: "More than 6 months", 3 cuts, -$55,000.
 "demo_sr22tn772":["You found this S R twenty-two Turbo at one million eighty-five thousand. How long has it been for sale?",
                   "The report: over six months, three cuts, fifty-five thousand off.", CTA],
 # 2026-11-19 daily run: ONE DOLLAR FIGURE (post day Sun 2026-11-22), Beechcraft Bonanza G36, model year 2008 (US, N-number,
 # seen in the last 7 days, one row per tail, FAA year + serial checked): 6 for sale, $519,000 to $764,900 -> $245,900 apart.
 # campaign/numbers/DATA_20261119.md
 # 2026-11-21 daily run: REPORT DEMO (post day Mon 2026-11-23), 2023 Cirrus SR20 G6 N264HS (serial 9385, dealer), ad 260289165:
 # first seen Sep 11 2026 at $599,000, cut Oct 15 -> $579,000, Nov 11 -> $499,900 (-$99,100, -16.5%). Report captured 2026-11-21:
 # priced at the 74th percentile of 48 comparable G6 listings; estimated value $489,450. campaign/demo/DATA_20261121_N264HS.md
 "demo_sr20n264":["You found this S R twenty at about five hundred thousand. Is it a bargain?",
                  "The report: cut almost a hundred thousand, and still above most S R twenties like it.", CTA],
 # 2026-11-23 daily run: REPORT DEMO (post day Thu 2026-11-26), 2006 Cirrus SR22 G2 N25HW (serial 2021, dealer), ad 262675585
 # first seen 2026-11-23 at $309,900. Federal accident record CEN23LA017, 2022-10-23, serial 2021 (exact registration + serial match).
 # Report captured 2026-11-23: header "Report (Oct 23, 2022)", 46th percentile of 80 G2 comps, est. value $317,750.
 # campaign/demo/DATA_20261123_N25HW.md
 "demo_sr22n25":["You found this S R twenty-two at about three hundred ten thousand. Has it ever been in an accident?",
                 "The report: yes, a federal accident record, October twenty twenty-two. Still priced mid-market.", CTA],
 # 2026-11-24 daily run: REPORT DEMO (post day Fri 2026-11-27), 2014 Cirrus SR22T G5 N378WT (dealer), ad 254812715 first seen
 # Apr 16 2026 at $599,900; cuts Aug 5 -> $579,900, Sep 7 -> $569,900, Sep 17 -> $559,900. Report captured 2026-11-24: "This listing
 # vs. their usual": time on market 222 days, dealer's typical sale (all aircraft) 55 days, 6.4 pts below their usual (-6.6% vs
 # market, expected ~$599,450, 46 comps). Doubt: SELLER. campaign/demo/DATA_20261124_N378WT.md
 "demo_sr22tn378":["You found this S R twenty-two Turbo. Do you know how this seller negotiates?",
                   "The report: this dealer usually sells in fifty-five days. This one: over seven months, three cuts.", CTA],
 # 2026-11-26 daily run: REPORT DEMO (post day Mon 2026-11-30), 2020 Cirrus SR20 G6 N643LV (serial 2632). Two live ads for the
 # same airplane: tap_2452200 $419,000 since Jul 4 2026, and dealer ad 252568413 first seen Apr 18 2026 at $419,000, cut Jul 9 to
 # $375,000 (-$44,000). Report captured 2026-11-26: Listing history "Live ads disagree on price". Doubt: PRICE.
 # campaign/demo/DATA_20261126_N643LV.md
 "demo_sr20n643":["You found this S R twenty at four hundred nineteen thousand dollars. Is that the right price?",
                  "The report: the same airplane has a second live ad, forty-four thousand dollars lower.", CTA],
 # 2026-11-25 daily run: ONE DOLLAR FIGURE (post day Sun 2026-11-29), 1978 Cessna 182Q: eight for sale, $139,900 to $379,000,
 # gap $239,100. campaign/numbers/DATA_20261125.md
 "num_dol_c182qgap":["Buying a nineteen seventy-eight Cessna one eighty-two Q? What should it cost?",
                     "Eight are for sale, priced almost two hundred forty thousand dollars apart. See what's behind yours.", CTA],
 "num_dol_g36gap":["Buying a two thousand eight Bonanza G thirty-six? What should it cost?",
                   "Six are for sale, priced almost two hundred fifty thousand dollars apart. See what's behind yours.", CTA],
 # 2026-11-20 daily run: ONE DOLLAR FIGURE (post day Sat 2026-11-21, Director slot empty and tomorrow), Piper PA-46 piston
 # (Malibu, Mirage, Matrix, M350; US, N-number, seen in the last 7 days, parts plane N504EZ dropped): 17 of 57 ask less than their
 # first recorded ask; median cut $52,000. campaign/numbers/DATA_20261120.md
 # 2026-11-27 daily run: ONE DOLLAR FIGURE (post day Sat 2026-11-28, Director slot empty and tomorrow), Beechcraft A36 Bonanza
 # (US, N-number, seen in the last 7 days): 38 of 77 ask less than their first recorded ask; median cut $25,000. DATA_20261127.md
 "num_dol_a36cut":["Shopping for a Bonanza A thirty-six? How much do sellers cut?",
                   "About half have cut the price. The typical cut: twenty-five thousand dollars. See every cut on yours.", CTA],
 "num_dol_pa46cut":["Shopping for a Piper Malibu? How much do sellers cut?",
                    "Almost three in ten have cut the price. The typical cut: fifty-two thousand dollars. See every cut on yours.", CTA],
 "num_dol_c182cut":["Shopping for a Cessna one eighty-two? How much do sellers cut?",
                    "Almost four in ten have cut the price. The typical cut: fifteen thousand dollars. See every cut on yours.", CTA],
 "num_up_single":["Shopping for a single-engine airplane?",
                  "Almost three in a hundred ask more than before. About half were relisted higher. Is yours one of them?", CTA],
 # 2026-11-10 DAMAGE HISTORY, Cirrus SR22/SR22T (US, N-number, seen in the last 7 days): 15 of 309 (4.9% -> "about one in
 # twenty") = 14 ads that disclose damage + 1 serial-matched federal substantial-damage record the ad doesn't mention. Disclosed:
 # 5 prop strikes, 3 hail, 1 parachute (CAPS) pull. campaign/numbers/DATA_20261110.md
 # 2026-11-12 TRAINING HISTORY, Cessna 172 family (US, N-number, seen in the last 7 days): 38 of 202 (18.8% -> "nearly one in
 # five"), strict after row check; 16 currently FAA-registered to a flight school, academy, university or flying club.
 # campaign/numbers/DATA_20261112.md
 "num_trn_c172":["Shopping for a Cessna one seventy-two?",
                 "Nearly one in five shows signs of a training past. Sixteen are still registered to a flight school or club. Is yours one of them?", CTA],
 "num_dmg_sr22":["Shopping for a Cirrus S R twenty-two?",
                 "About one in twenty for sale has a damage history. Prop strikes, hail, even a parachute pull. Is yours one of them?", CTA],
 # 2026-11-13 PRICE HISTORY (up, relisted higher): N784RJ 2014 SR22T G5, same dealer, $518,900 (Apr 18 - Jun 27) ->
 # $664,900 since Sep 3 with a September 2026 engine overhaul (+$146,000). No federal accident record.
 "sr22tup":["About six hundred sixty-five thousand dollars for this S R twenty-two T.",
            "In June, same dealer: five hundred nineteen thousand. Now with an overhauled engine.", CTA],
 "g36up":["About seven hundred thousand dollars for this Bonanza G thirty-six.",
          "In September, same dealer: five hundred fifty thousand. Now with a zero-hour engine.", CTA],
}
S["seldlr182"]=["This Cessna Skylane has been for sale seven months. Not one price cut.",
 "Its dealer usually asks about a quarter above the market, and cuts only one airplane in seven.", CTA]
S["selllc"]=["Three hundred thirty-nine thousand dollars for this Bonanza. The seller is an LLC with just this one airplane.",
 "Listed in April at three hundred eighty-five thousand. Five price cuts since.", CTA]
S["dlr182"]=["This Skylane has been for sale seven months. No price cut.",
 "Its dealer usually asks a quarter above market, and cuts one airplane in seven.", CTA]
S["llcf33"]=["This Bonanza is sold by an LLC that owns just this one airplane.",
 "Listed in April at three hundred eighty-five thousand dollars. Five cuts since.", CTA]
S["dlr2"]=["This dealer has listed twenty-nine airplanes since April. Fifteen sold.",
 "They usually ask a quarter above market and rarely cut. This Skylane: seven months, no cut.", CTA]
S["llc2"]=["This seller listed just one airplane this year. An LLC selling its own Skylane.",
 "One hundred fifty-five thousand dollars in June. Three cuts later: one hundred twenty-five thousand.", CTA]
S["dlr3"]=["This dealer listed twenty-nine airplanes since April.",
 "They usually ask a quarter above market. This Skylane: seven months, no cut.", CTA]
S["llc3"]=["One airplane listed all year. Just an LLC selling its Skylane.",
 "Three price cuts since June. Thirty thousand dollars off.", CTA]
S["dlr4"]=[None, None, "Before you call, check the dealer's selling strategy at NextPlane dot U S."]
S["llc4"]=[None, None, "Before you call, check the seller's strategy at NextPlane dot U S."]
S["dlr5"]=["Do you know the selling strategy of the dealer behind this airplane?",
 "This one asks a quarter above market and rarely cuts. This Skylane: seven months, no cut.",
 "Before you call the broker, find out their strategy at NextPlane dot U S."]
S["llc5"]=["Do you know the selling strategy of the owner behind this airplane?",
 "One LLC, one airplane, one ad all year. Three price cuts since June, thirty thousand dollars off.",
 "Before you call the seller, find out their strategy at NextPlane dot U S."]
S["llc6"]=[None, "One LLC, one airplane, one ad all year. Three cuts, thirty thousand dollars off.", None]
S["sdl_f33a"]=["Do you know the selling strategy of the dealer behind this airplane?",
 "This one asks sixteen percent over market, then cuts half. This Bonanza: five months, two cuts.",
 "Before you call the broker, find out their strategy at NextPlane dot U S."]
# usage: gen_vo.py [slug]  -> only that slug (no need to delete the pilot entries)
if len(sys.argv) > 1: S = {sys.argv[1]: S[sys.argv[1]]}
# optional per-slug delivery speed (ElevenLabs voice_settings.speed, 0.7-1.2) when a clip runs over 15.0 s at the default pace
SPEED={"demo_sr20n643":1.1, "demo_sr22tn378":1.1, "demo_sr22n25":1.1, "sdl_f33a":1.1, "num_dol_g36gap":1.1, "num_dol_pa46cut":1.1, "num_dol_c182qgap":1.1, "num_dol_a36cut":1.1}
def gen(bid,text):
    if os.path.exists(f"{OUT}/{bid}.json"): return
    vs={"stability":0.62,"similarity_boost":0.85,"style":0.25,"use_speaker_boost":True}
    sp=SPEED.get(bid.rsplit("_b",1)[0])
    if sp: vs["speed"]=sp
    body=json.dumps({"text":text,"model_id":"eleven_turbo_v2_5","voice_settings":vs}).encode()
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
        bid=f"{v}_b{i+1}"
        if t: gen(bid,t)
        d=json.load(open(f"{OUT}/{bid}.json")); bad=[w["w"] for w in d["words"][:-1] if w["e"]-w["s"]>1.8]
        print(bid, round(d["dur"],2), len(d["words"]), "SMEAR "+str(bad) if bad else "ok")
