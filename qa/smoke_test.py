#!/usr/bin/env python3
"""Zero-cost environment check for a cloud run: fonts + PIL + photo fetch + endcard + ffmpeg + loudness + QA gate.
Usage: python3 qa/smoke_test.py   (after `source setup.sh smoke`)"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
KIT = os.environ.get("KIT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("WORK", "/tmp/smoke"); os.makedirs(f"{WORK}/frames", exist_ok=True)
sys.path.insert(0, f"{KIT}/lib"); from endcard import draw_endcard; import photos
FD = f"{KIT}/fonts"; W, H, FPS = 1080, 1920, 30
bg = None
if photos.fetch("smoke", "Cirrus SR22", f"{WORK}/photos", 1):
    im = Image.open(f"{WORK}/photos/smoke-0.jpg").convert("RGB")
    s = max(W / im.width, H / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1))
    l, t = (im.width - W) // 2, (im.height - H) // 2
    bg = ImageEnhance.Brightness(im.crop((l, t, l + W, t + H))).enhance(0.45)
f = ImageFont.truetype(f"{FD}/BarlowCondensed-Bold.ttf", 120)
N = 11 * FPS
for i in range(N):
    t = i / FPS
    if t < 2:
        fr = (bg or Image.new("RGB", (W, H), (10, 22, 34))).copy()
        ImageDraw.Draw(fr).text((W // 2, H // 2), f"${int(10000 * min(t / 1.5, 1)):,}", font=f, fill=(37, 197, 203), anchor="mm")
    else:
        fr = draw_endcard(Image.new("RGB", (W, H), (10, 22, 34)), t - 2, FD, f"{KIT}/assets/logo_for_dark_800.png")
    fr.save(f"{WORK}/frames/f{i + 1:05d}.jpg", quality=90)
out = f"{WORK}/smoke.mp4"
subprocess.run(f"ffmpeg -v error -y -framerate 30 -i {WORK}/frames/f%05d.jpg -f lavfi -i sine=f=220:d=11 "
               f"-filter_complex \"[1:a]loudnorm=I=-14:TP=-2:linear=true,aformat=channel_layouts=stereo[a]\" -map 0:v -map \"[a]\" "
               f"-c:v libx264 -pix_fmt yuv420p -c:a aac -shortest {out}", shell=True, check=True)
r = subprocess.run([sys.executable, f"{KIT}/qa/check_render.py", out], capture_output=True, text=True)
print(r.stdout.strip())
print("SMOKE", "PASS" if "QA PASS" in r.stdout else "CHECK OUTPUT ABOVE", "-", out)
