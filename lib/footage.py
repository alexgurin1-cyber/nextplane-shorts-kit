#!/usr/bin/env python3
"""NextPlane real-footage library: find and fetch screened stock b-roll for Shorts.

The index (footage/index.json) lists clips from Pexels and Pixabay that were screened frame by frame
for general-aviation relevance. Each entry records the topic, whether an aircraft is in the shot,
the best identification of that aircraft, shot type, orientation, licence and credit.
Real footage only: AI-generated clips are excluded at collection time (feedback-real-visuals-only).

Clips are not stored in this public repository (the stock licences do not allow redistributing
the files on their own). `get` downloads from the source and normalises to a silent H.264 clip.
If a private footage checkout is present (env NP_FOOTAGE_DIR, or ../nextplane-footage), the
normalised copy there is used and nothing is downloaded.

Usage:
  footage.py topics
  footage.py find [--topic T] [--aircraft TEXT] [--orient V|H] [--min-quality N] [--text TEXT] [--n N]
  footage.py get <key> <outdir> [--seconds S] [--full]     # --full keeps the source resolution
  footage.py credits <key> [<key> ...]                     # rows for *_FOOTAGE_CREDITS.md

Rule for use in a Short: if `aircraft_in_shot` is true, the clip may only illustrate that aircraft
type or a generic statement. Never show an identifiable model under narration about another model.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "..", "footage", "index.json")
UA = {"User-Agent": "curl/8.5.0"}


def load():
    return json.load(open(INDEX))["clips"]


def local_dir():
    for d in (os.environ.get("NP_FOOTAGE_DIR"), os.path.join(HERE, "..", "..", "nextplane-footage")):
        if d and os.path.isdir(d):
            return d
    return None


def find(a):
    out = []
    for c in load():
        if a.topic and c["topic"] != a.topic:
            continue
        if a.orient and c["orientation"] != a.orient:
            continue
        if c["quality"] < a.min_quality:
            continue
        if a.aircraft and a.aircraft.lower() not in c["aircraft"].lower():
            continue
        if a.text and a.text.lower() not in (c["shot"] + " " + c["description"] + " " + c["aircraft"]).lower():
            continue
        out.append(c)
    out.sort(key=lambda c: (-c["quality"], c["key"]))
    return out[: a.n]


def get(key, outdir, seconds=10, full=False):
    c = next((c for c in load() if c["key"] == key), None)
    if not c:
        sys.exit(f"unknown key {key}")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, key + ".mp4")
    d = local_dir()
    if d and not full:
        p = os.path.join(d, c["file"])
        if os.path.exists(p):
            open(out, "wb").write(open(p, "rb").read())
            return out
    raw = out + ".src"
    open(raw, "wb").write(urllib.request.urlopen(urllib.request.Request(c["download_url"], headers=UA), timeout=180).read())
    vf = "fps=30,format=yuv420p" if full else \
        "scale='if(gt(iw,ih),-2,1080)':'if(gt(iw,ih),1080,-2)':flags=lanczos,fps=30,format=yuv420p"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(c["start"]), "-i", raw, "-t", str(seconds), "-an",
                    "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", out], check=True)
    os.remove(raw)
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("topics")
    f = sub.add_parser("find")
    f.add_argument("--topic")
    f.add_argument("--aircraft")
    f.add_argument("--orient", choices=["V", "H"])
    f.add_argument("--min-quality", type=int, default=2)
    f.add_argument("--text")
    f.add_argument("--n", type=int, default=20)
    g = sub.add_parser("get")
    g.add_argument("key")
    g.add_argument("outdir")
    g.add_argument("--seconds", type=float, default=10)
    g.add_argument("--full", action="store_true")
    cr = sub.add_parser("credits")
    cr.add_argument("keys", nargs="+")
    a = ap.parse_args()
    if a.cmd == "topics":
        n = {}
        for c in load():
            n.setdefault(c["topic"], [0, 0])
            n[c["topic"]][0] += 1
            n[c["topic"]][1] += c["orientation"] == "V"
        for t, (k, v) in sorted(n.items()):
            print(f"{t:18s}{k:4d} clips ({v} vertical)")
    elif a.cmd == "find":
        for c in find(a):
            print(f'{c["key"]:20s} q{c["quality"]} {c["orientation"]} {c["topic"]:16s} | '
                  f'{c["aircraft"] or "no aircraft"} | {c["shot"]}')
    elif a.cmd == "get":
        print(get(a.key, a.outdir, a.seconds, a.full))
    elif a.cmd == "credits":
        idx = {c["key"]: c for c in load()}
        print("| Key | Licence | Creator | Source |\n|---|---|---|---|")
        for k in a.keys:
            c = idx[k]
            print(f'| {k} | {c["license"]} | {c["creator"]} | {c["source_page"]} |')


if __name__ == "__main__":
    main()
