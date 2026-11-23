"""Clip captures between two text markers (for seller blocks without bordered containers). Boxes in CSS px relative to clip."""
import os, json, sys
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
CLIPS = {"sellerusual": ("THIS LISTING VS. THEIR USUAL", "Dealer stats as of"),
         "sellertop": ("Who's Selling This Aircraft", "NEXTPLANE DEALER SCORE")}
FIND = r"""([a, b]) => {
  const leaf = t => [...document.querySelectorAll('main *')].find(e => e.offsetParent && e.children.length===0 && (e.innerText||'').trim().startsWith(t));
  const A = leaf(a), B = leaf(b); if (!A || !B) return null;
  const m = document.querySelector('main').getBoundingClientRect();
  const ra = A.getBoundingClientRect(), rb = B.getBoundingClientRect();
  const y0 = ra.top + window.scrollY - 24, y1 = rb.bottom + window.scrollY + 16;
  const boxes = [];
  for (const e of document.querySelectorAll('main *')) {
    if (!e.offsetParent || e.children.length) continue; const t = (e.innerText||e.textContent||'').trim(); if (!t) continue;
    const r = e.getBoundingClientRect(); const yy = r.top + window.scrollY;
    if (yy >= y0 && yy + r.height <= y1) boxes.push({t: t.slice(0,120), x: r.left - m.left, y: yy - y0, w: r.width, h: r.height});
  }
  return {x: m.left, y: y0, w: m.width, h: y1 - y0, boxes};
}"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
    pg.goto("https://nextplane.us/signin", wait_until="networkidle", timeout=90000)
    pg.fill("input[type=email]", os.environ["NEXTPLANE_CAPTURE_EMAIL"]); pg.fill("input[type=password]", os.environ["NEXTPLANE_CAPTURE_PASSWORD"])
    pg.click("button[type=submit]"); pg.wait_for_timeout(5000)
    pg.goto("https://nextplane.us/aircraft-report/N814LT", wait_until="networkidle", timeout=120000); pg.wait_for_timeout(9000)
    hgt = pg.evaluate("() => document.documentElement.scrollHeight")
    for y in range(0, hgt, 700): pg.evaluate(f"() => window.scrollTo(0,{y})"); pg.wait_for_timeout(250)
    pg.evaluate("""() => { const m=document.querySelector('main'); let n=m;
      while(n && n.parentElement){ for(const s of n.parentElement.children){ if(s!==n) s.style.display='none'; } n=n.parentElement; }
      m.style.marginLeft='0'; }"""); pg.wait_for_timeout(1500)
    meta = {}
    for k, (a, z) in CLIPS.items():
        r = pg.evaluate(FIND, [a, z])
        if not r: print("MISS", k); continue
        pg.screenshot(path=f"{OUT}/{k}.png", full_page=True, clip={"x": r["x"], "y": r["y"], "width": r["w"], "height": r["h"]})
        meta[k] = {"w": r["w"], "h": r["h"], "boxes": r["boxes"]}; print(k, int(r["w"]), int(r["h"]), len(r["boxes"]))
    json.dump(meta, open(f"{OUT}/sections.json", "w"), indent=1); b.close()
