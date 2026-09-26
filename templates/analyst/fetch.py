#!/usr/bin/env python3
"""Fetch license-safe (CC0/PD/CC-BY, no SA) photos from Wikimedia Commons for the Buzzwords short."""
import json, os, re, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "NextPlaneMediaFetch/1.0 (alex.gurin1@gmail.com)"}
API = "https://commons.wikimedia.org/w/api.php"
OUT = "/tmp/bw/photos"; os.makedirs(OUT, exist_ok=True)
def api(params):
    params = dict(params, format="json")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    for attempt in range(5):
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                time.sleep(8 * (attempt + 1)); continue
            raise
def lic_ok(em):
    short = em.get("LicenseShortName", {}).get("value", "")
    if re.search(r"share.?alike|GFDL|-SA", short, re.I): return None
    if re.match(r"^(CC0|Public domain|PD|CC BY)", short, re.I): return short
    return None
creds = []
def fetch(slug, query, want=1, listonly=False):
    r = api({"action": "query", "generator": "search", "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": "40",
             "prop": "imageinfo", "iiprop": "extmetadata|url|size|mime", "iiurlwidth": "1600"})
    pages = sorted(r.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    got = 0
    for p in pages:
        if got >= want: break
        ii = (p.get("imageinfo") or [{}])[0]; em = ii.get("extmetadata", {})
        if ii.get("mime") not in ("image/jpeg", "image/png") or ii.get("width", 0) < 1000: continue
        short = lic_ok(em)
        if listonly:
            print("  ", short or "(no)", "|", p["title"][:70]); continue
        if not short: continue
        artist = re.sub(r"<[^>]+>", "", em.get("Artist", {}).get("value", "unknown")).strip()
        url = ii.get("thumburl") or ii.get("url")
        try: data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
        except Exception as e: print(slug, "DL fail", e); continue
        fn = f"{OUT}/{slug}-{got}.jpg"; open(fn, "wb").write(data)
        creds.append({"slug": slug, "file": p["title"], "license": short, "artist": artist,
                      "url": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(p["title"].replace(" ", "_")), "local": fn})
        print(slug, got, short, "|", artist[:40], "|", p["title"][:60], len(data) // 1024, "KB"); got += 1
    if got < want and not listonly: print(slug, "ONLY", got, "of", want)
jobs = [
    ("chero", "Piper pa-28-140 cherokee g-atoo arp"),
    ("chero2", "Piper PA-28-140 Cherokee Cruiser D-ELAU"),
    ("sr22t", "Cirrus SR22 GTS G3 Turbo D-EGHX"),
    ("sr22t2", "Cirrus SR22-GTSx G3 Turbo HB-KHR"),
]
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "fetch"
    for slug, q in jobs:
        if mode == "list": print(slug, q); fetch(slug, q, listonly=True); time.sleep(3); continue
        if os.path.exists(f"{OUT}/{slug}-0.jpg"): print(slug, "exists"); continue
        try: fetch(slug, q)
        except Exception as e: print(slug, "ERR", e)
        time.sleep(3)
    old = json.load(open(f"{OUT}/credits.json")) if os.path.exists(f"{OUT}/credits.json") else []
    seen = {c["local"] for c in old}; old += [c for c in creds if c["local"] not in seen]
    json.dump(old, open(f"{OUT}/credits.json", "w"), indent=1); print("credits:", len(old))
