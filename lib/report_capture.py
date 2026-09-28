#!/usr/bin/env python3
"""Capture the live NextPlane single-aircraft report for one tail number, section by section, in the cloud.

Headless Chromium (Playwright, /opt/pw-browsers/chromium) reaches nextplane.us from Claude cloud sessions
(verified 2026-09-26). The unlocked report needs a signed-in account with report access:
  NEXTPLANE_CAPTURE_EMAIL, NEXTPLANE_CAPTURE_PASSWORD   (from memory reference-nextplane-capture-login)

Usage:
  report_capture.py <N-number> <out_dir>
Writes <out_dir>/full.png, one PNG per report section (sec_XX_<slug>.png, 1600x900, header/sidebar hidden),
and <out_dir>/sections.json with each section's heading and visible text (for the accuracy cross-check).
Exit code 3 = not signed in / report still locked (blurred "UNLOCK IN REPORT" placeholders present).
"""
import json
import os
import re
import sys

from playwright.sync_api import sync_playwright

BASE = "https://nextplane.us"
W, H = 1600, 900


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40] or "section"


def main(tail, out):
    os.makedirs(out, exist_ok=True)
    email, pw = os.environ.get("NEXTPLANE_CAPTURE_EMAIL"), os.environ.get("NEXTPLANE_CAPTURE_PASSWORD")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        if email and pw:
            pg.goto(f"{BASE}/signin", wait_until="networkidle", timeout=90000)
            pg.fill("input[type=email]", email)
            pg.fill("input[type=password]", pw)
            pg.click("button[type=submit]")
            pg.wait_for_timeout(5000)
        pg.goto(f"{BASE}/aircraft-report/{tail}", wait_until="networkidle", timeout=120000)
        pg.wait_for_timeout(6000)
        body = pg.inner_text("body")
        if "UNLOCK IN REPORT" in body:
            pg.screenshot(path=f"{out}/locked.png")
            print("LOCKED: report is not unlocked for this session (sign-in missing or no report access)")
            sys.exit(3)
        pg.screenshot(path=f"{out}/full.png", full_page=True)
        # Frame recipe from Episode 1: keep scrollY=0, hide fixed chrome, widen container, translate main per section.
        # 2026-09-28: the old CSS rule `[class*=sidebar]{display:none}` also matched the layout wrapper that
        # contains <main>, hid the whole report and produced 0 sections. Hide only the siblings of main's ancestors.
        pg.evaluate("""() => { const m=document.querySelector('main'); let n=m;
          while(n && n.parentElement){ for(const s of n.parentElement.children){ if(s!==n) s.style.display='none'; } n=n.parentElement; }
          if(m) m.style.marginLeft='0'; }""")
        pg.add_style_tag(content=".max-w-6xl{max-width:1600px!important}")
        secs = pg.evaluate("""() => {
          const hs=[...document.querySelectorAll('main h2, main h3')].filter(h=>h.offsetParent);
          return hs.map(h=>{const r=h.getBoundingClientRect(); const box=h.closest('section')||h.parentElement;
            return {title:h.innerText.trim(), y:r.top+window.scrollY, text:(box?box.innerText:'').slice(0,4000)};});
        }""")
        meta = []
        for i, s in enumerate(secs):
            y = max(0, int(s["y"]) - 24)
            pg.evaluate(f"() => {{window.scrollTo(0,0); const m=document.querySelector('main'); if(m) m.style.transform='translateY(-{y}px)';}}")
            pg.wait_for_timeout(700)
            fn = f"sec_{i:02d}_{slug(s['title'])}.png"
            pg.screenshot(path=f"{out}/{fn}")
            meta.append({"file": fn, "title": s["title"], "text": s["text"]})
        json.dump(meta, open(f"{out}/sections.json", "w"), indent=1)
        print(f"OK {len(meta)} sections -> {out}")
        b.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1].upper(), sys.argv[2])
