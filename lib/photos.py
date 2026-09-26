#!/usr/bin/env python3
"""License-safe aircraft photos for cloud runs (CC0 / PDM / CC BY only — never ShareAlike, never NC).

Why: Wikimedia (commons.wikimedia.org AND upload.wikimedia.org) rate-limits the shared cloud egress IP
with HTTP 429 on essentially every request (verified 2026-09-26). So the cloud order is:
  1. Wikimedia Commons API (one quick attempt, in case the limit has lifted)
  2. Openverse API, source=flickr (live.staticflickr.com downloads work from the cloud)
Real aircraft photos only — never AI-generated backgrounds (feedback-real-visuals-only).

Usage:
  photos.py search "<query>" [n]                 -> list candidates (license | creator | title | size)
  photos.py fetch <slug> "<query>" <outdir> [k]  -> downloads k images to <outdir>/<slug>-<i>.jpg,
                                                   appends credits to <outdir>/credits.json
Tip: short literal queries work best ("Cirrus SR22T", "Piper Arrow", "Beechcraft Bonanza A36").
"""
import json
import os
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "NextPlaneMediaFetch/1.0 (https://nextplane.us; support@nextplane.us)"}
OV = "https://api.openverse.org/v1/images/"
LICENSES = "by,cc0,pdm"  # excludes by-sa, by-nc, by-nd, etc.


def _get(url, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)


def commons_try(query, n=10):
    """Single attempt at Commons. Returns [] on 429/any error."""
    params = {"action": "query", "generator": "search", "gsrsearch": query, "gsrnamespace": "6",
              "gsrlimit": str(n), "prop": "imageinfo", "iiprop": "extmetadata|url|size|mime",
              "iiurlwidth": "1600", "format": "json"}
    try:
        r = json.load(_get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params), 20))
    except Exception:
        return []
    out = []
    for p in r.get("query", {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata", {})
        lic = em.get("LicenseShortName", {}).get("value", "")
        if any(x in lic.upper() for x in ("SA", "NC", "ND", "GFDL")):
            continue
        if not (lic.upper().startswith(("CC0", "CC BY", "PUBLIC DOMAIN", "PD"))):
            continue
        out.append({"source": "wikimedia", "title": p["title"], "license": lic,
                    "creator": em.get("Artist", {}).get("value", ""), "url": ii.get("thumburl") or ii.get("url"),
                    "page": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(p["title"].replace(" ", "_")),
                    "width": ii.get("width", 0)})
    return out


def openverse(query, n=20):
    q = urllib.parse.urlencode({"q": query, "source": "flickr", "license": LICENSES, "page_size": str(n)})
    d = json.load(_get(f"{OV}?{q}"))
    out = []
    for r in d.get("results", []):
        lic = f"CC {r['license'].upper()} {r.get('license_version') or ''}".strip()
        if r["license"] in ("cc0", "pdm"):
            lic = "CC0" if r["license"] == "cc0" else "Public Domain Mark"
        out.append({"source": "flickr/openverse", "title": r.get("title", ""), "license": lic,
                    "creator": r.get("creator", ""), "url": r["url"], "page": r.get("foreign_landing_url", ""),
                    "width": r.get("width") or 0})
    return out


def candidates(query, n=20):
    return commons_try(query, n) + openverse(query, n)


def fetch(slug, query, outdir, k=1):
    os.makedirs(outdir, exist_ok=True)
    cred_path = os.path.join(outdir, "credits.json")
    creds = json.load(open(cred_path)) if os.path.exists(cred_path) else []
    got = 0
    for c in sorted(candidates(query), key=lambda c: -(c["width"] or 0)):
        if got >= k:
            break
        if (c["width"] or 0) < 800:
            continue
        try:
            data = _get(c["url"], 90).read()
        except Exception as e:
            print(slug, "download failed", c["source"], e)
            continue
        fn = os.path.join(outdir, f"{slug}-{got}.jpg")
        open(fn, "wb").write(data)
        creds.append(dict(c, slug=slug, local=fn))
        print(slug, got, c["license"], "|", c["creator"][:40], "|", c["title"][:50], len(data) // 1024, "KB")
        got += 1
    json.dump(creds, open(cred_path, "w"), indent=1)
    if got < k:
        print(slug, f"ONLY {got} of {k} — try a shorter/different query")
    return got


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        for c in candidates(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 15):
            print(c["source"], "|", c["license"], "|", c["creator"][:30], "|", c["title"][:50], "|", c["width"])
    elif len(sys.argv) >= 5 and sys.argv[1] == "fetch":
        fetch(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else 1)
    else:
        print(__doc__)
        sys.exit(2)
