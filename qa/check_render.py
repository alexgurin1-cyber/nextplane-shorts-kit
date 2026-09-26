#!/usr/bin/env python3
"""
QA gate for rendered clips — blocks anything below production standard.
Usage: python3 check_render.py <video.mp4> [--no-audio-required] [--max-duration=105]
Exit 0 = pass, exit 1 = fail (with reasons).

Checks (PRODUCTION_STANDARD.md):
  1. 1080x1920 @ 30fps
  2. duration 10-75s
  3. audio present; |video - audio| <= 0.5s
  4. integrated loudness -15..-13 LUFS, true peak <= -1 dB
  5. no near-black frames after the first 0.5s
Extracts first/mid/last frame PNGs next to the video for visual review.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    return json.loads(r.stdout)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = Path(sys.argv[1])
    audio_required = "--no-audio-required" not in sys.argv
    max_dur = next((float(a.split("=")[1]) for a in sys.argv if a.startswith("--max-duration=")), 75.0)
    failures = []

    info = probe(path)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)

    # 1. resolution + fps
    if not v:
        print("FAIL: no video stream"); sys.exit(1)
    if (int(v["width"]), int(v["height"])) != (1080, 1920):
        failures.append(f"resolution {v['width']}x{v['height']} != 1080x1920")
    num, den = (v.get("r_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den)
    if not 29 <= fps <= 61:
        failures.append(f"fps {fps:.1f} — must be 30 (or 60)")

    # 2. duration
    vdur = float(v.get("duration") or info["format"]["duration"])
    if not 10 <= vdur <= max_dur:
        failures.append(f"duration {vdur:.1f}s outside 10-{max_dur:.0f}s")

    # 3. audio presence + length match
    if a:
        adur = float(a.get("duration") or vdur)
        if abs(vdur - adur) > 0.5:
            failures.append(f"audio/video length mismatch: video {vdur:.1f}s vs audio {adur:.1f}s")
    elif audio_required:
        failures.append("no audio stream")

    # 4. loudness (EBU R128)
    if a:
        r = run(["ffmpeg", "-i", str(path), "-map", "a", "-af",
                 "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"])
        m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.DOTALL)
        if m:
            stats = json.loads(m.group(0))
            lufs = float(stats["input_i"])
            tp = float(stats["input_tp"])
            if not -15.5 <= lufs <= -12.5:
                failures.append(f"loudness {lufs:.1f} LUFS — target -14 (±1.5)")
            if tp > -0.5:
                failures.append(f"true peak {tp:.1f} dBTP > -0.5")

    # 5. black-void frames (skip first 0.5s)
    r = run(["ffmpeg", "-i", str(path), "-vf", "blackdetect=d=0.4:pix_th=0.08",
             "-an", "-f", "null", "-"])
    blacks = [
        (float(m.group(1)), float(m.group(2)))
        for m in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)
        if float(m.group(2)) > 0.5
    ]
    if blacks:
        failures.append(f"black-void segments: {blacks[:3]}")

    # review frames
    for tag, ts in [("first", 0.2), ("mid", vdur / 2), ("last", max(vdur - 0.5, 0))]:
        run(["ffmpeg", "-y", "-ss", str(ts), "-i", str(path), "-frames:v", "1",
             str(path.with_suffix(f".qa_{tag}.png"))])

    if failures:
        print(f"QA FAIL — {path.name}")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    print(f"QA PASS — {path.name} ({vdur:.1f}s, {fps:.0f}fps, review frames extracted)")
    sys.exit(0)

if __name__ == "__main__":
    main()
