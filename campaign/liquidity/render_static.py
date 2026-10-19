#!/usr/bin/env python3
"""Render liquidity-campaign static assets: carousels (1080x1350), stat cards (1080x1350), poll cards (1080x1920)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from campaign_data import CAROUSELS, STAT_CARDS, POLLS

KIT = os.environ["KIT"]; OUT = os.environ.get("OUT", "out"); os.makedirs(OUT, exist_ok=True)
FD = f"{KIT}/fonts"; LOGO = Image.open(f"{KIT}/assets/logo_for_dark_800.png").convert("RGBA")
NAVY = (15, 42, 63); CYAN = (37, 197, 203); OFF = (246, 249, 250); WHITE = (255, 255, 255); GREY = (160, 172, 182)
DEEP = (8, 20, 31)
_F = {}
def F(n, s):
    if (n, s) not in _F: _F[(n, s)] = ImageFont.truetype(f"{FD}/{n}", s)
    return _F[(n, s)]
BCB = lambda s: F("BarlowCondensed-Bold.ttf", s); BCS = lambda s: F("BarlowCondensed-SemiBold.ttf", s)
SMB = lambda s: F("SpaceMono-Bold.ttf", s); SMR = lambda s: F("SpaceMono-Regular.ttf", s)

def wrap(d, txt, font, maxw):
    lines, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur); return lines

def canvas(W, H):
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    # subtle top band
    d.rectangle([0, 0, W, 6], fill=CYAN)
    return im, d

def brand(im, d, W, H, tag="nextplane.us"):
    lg = LOGO.resize((88, 88)); im.paste(lg, (64, H - 64 - 88), lg)
    d.text((64 + 88 + 22, H - 64 - 44), "NEXTPLANE", font=BCB(54), fill=OFF, anchor="lm")
    d.text((W - 64, H - 64 - 44), tag, font=SMR(30), fill=GREY, anchor="rm")

def text_block(d, x, y, lines, font, fill, lh):
    for ln in lines: d.text((x, y), ln, font=font, fill=fill); y += lh
    return y

# ---------- carousel ----------
def carousel(c):
    W, H = 1080, 1350; slug = c["id"].lower(); files = []
    # slide 1: question card
    im, d = canvas(W, H)
    d.text((64, 170), c["cat"].upper() + "  ·  " + c["metric"].upper(), font=SMB(30), fill=CYAN)
    y = text_block(d, 64, 250, wrap(d, c["q"], BCB(118), 950), BCB(118), OFF, 118)
    d.text((64, y + 30), "Swipe for the five.", font=BCS(48), fill=GREY)
    d.text((64, H - 260), "Is your airplane liquid?", font=BCS(54), fill=CYAN)
    brand(im, d, W, H); p = f"{OUT}/{slug}_01.png"; im.save(p); files.append(p)
    # slides 2-6: countdown 5 -> 1
    rows = c["rows"]
    for i, (model, num, why) in enumerate(rows):
        rank = 5 - i
        im, d = canvas(W, H)
        d.text((64, 150), f"#{rank}", font=BCB(170), fill=CYAN)
        d.text((64, 340), c["sub"], font=SMR(28), fill=GREY)
        y = text_block(d, 64, 420, wrap(d, model, BCB(96), 950), BCB(96), OFF, 100)
        d.text((64, y + 60), num, font=SMB(150), fill=WHITE)
        d.text((64, y + 60 + 170), c["unit"], font=BCS(44), fill=CYAN)
        y2 = text_block(d, 64, y + 60 + 260, wrap(d, why, BCS(46), 950), BCS(46), OFF, 54)
        brand(im, d, W, H); p = f"{OUT}/{slug}_{i+2:02d}.png"; im.save(p); files.append(p)
    # slide 7: the catch
    im, d = canvas(W, H)
    d.text((64, 170), "THE CATCH", font=SMB(30), fill=CYAN)
    y = text_block(d, 64, 250, wrap(d, c["catch"], BCB(84), 950), BCB(84), OFF, 92)
    d.text((64, y + 60), "The list tells you the model.", font=BCS(52), fill=GREY)
    d.text((64, y + 120), "The report tells you the airplane.", font=BCS(52), fill=CYAN)
    brand(im, d, W, H); p = f"{OUT}/{slug}_07.png"; im.save(p); files.append(p)
    # slide 8: CTA
    im, d = canvas(W, H)
    d.text((64, 200), "Plug in the N-number.", font=BCB(110), fill=OFF)
    d.rounded_rectangle([64, 420, W - 64, 560], radius=18, fill=DEEP, outline=CYAN, width=3)
    d.text((100, 490), "N", font=SMB(60), fill=CYAN, anchor="lm")
    d.text((160, 490), "_ _ _ _ _", font=SMB(60), fill=GREY, anchor="lm")
    d.text((W - 100, 490), "→", font=SMB(60), fill=CYAN, anchor="rm")
    y = text_block(d, 64, 640, wrap(d, "Price-cut history on this tail. Days listed. Owners in the last five years. The federal accident record. Whether it behaves like its model.", BCS(48), 950), BCS(48), OFF, 58)
    d.text((64, H - 300), "nextplane.us", font=BCB(96), fill=CYAN)
    brand(im, d, W, H); p = f"{OUT}/{slug}_08.png"; im.save(p); files.append(p)
    return files

# ---------- stat card ----------
def stat_card(cid, big, line, date):
    W, H = 1080, 1350; im, d = canvas(W, H)
    d.text((64, 170), "IS YOUR AIRPLANE LIQUID?", font=SMB(30), fill=CYAN)
    size = 200 if len(big) <= 8 else (150 if len(big) <= 12 else 96)
    y = text_block(d, 64, 330, wrap(d, big, SMB(size), 950), SMB(size), WHITE, size + 10)
    text_block(d, 64, y + 50, wrap(d, line, BCS(60), 950), BCS(60), OFF, 70)
    d.text((64, H - 280), "Source: NextPlane sold-listing data", font=SMR(28), fill=GREY)
    brand(im, d, W, H); p = f"{OUT}/{cid.lower()}.png"; im.save(p); return p

# ---------- poll card (Stories) ----------
def poll_card(cid, q, a, b, reveal):
    W, H = 1080, 1920; im, d = canvas(W, H)
    d.text((64, 300), "IS YOUR AIRPLANE LIQUID?", font=SMB(30), fill=CYAN)
    y = text_block(d, 64, 380, wrap(d, q, BCB(104), 950), BCB(104), OFF, 110)
    for i, opt in enumerate((a, b)):
        yy = y + 80 + i * 170
        d.rounded_rectangle([64, yy, W - 64, yy + 130], radius=22, fill=DEEP, outline=CYAN, width=3)
        d.text((W / 2, yy + 65), opt, font=BCS(58), fill=OFF, anchor="mm")
    d.text((64, 1500), "Answer, then swipe for the number.", font=SMR(30), fill=GREY)
    brand(im, d, W, H); p = f"{OUT}/{cid.lower()}_q.png"; im.save(p)
    im, d = canvas(W, H)
    d.text((64, 300), "THE ANSWER", font=SMB(30), fill=CYAN)
    y = text_block(d, 64, 380, wrap(d, reveal, BCB(110), 950), BCB(110), WHITE, 116)
    text_block(d, 64, y + 60, wrap(d, q, BCS(52), 950), BCS(52), GREY, 60)
    d.text((64, 1440), "Source: NextPlane sold-listing data", font=SMR(28), fill=GREY)
    d.text((64, 1500), "Check your own tail: nextplane.us", font=BCS(48), fill=CYAN)
    brand(im, d, W, H); p2 = f"{OUT}/{cid.lower()}_a.png"; im.save(p2); return [p, p2]

if __name__ == "__main__":
    n = 0
    for c in CAROUSELS: n += len(carousel(c))
    for s in STAT_CARDS: stat_card(*s); n += 1
    for p in POLLS: n += len(poll_card(*p))
    print("rendered", n)
