"""Element-level capture of the N333WR report: one PNG per card (2x) + DOM boxes of every leaf text for callouts/blurs."""
import os, json, sys
from playwright.sync_api import sync_playwright
TAIL = "N333WR"; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
TARGETS = {
 "header": r"^N333WR$", "verdict": r"^CURRENT OWNERSHIP PERIOD$", "gradestrip": r"^NEXTPLANE INVESTMENT GRADE", "valuation": r"^Estimated Market Value$", "cpm": r"^True Cost per Mile", "msrp": r"^Original new price",
 "replacement": r"^Replacement cost", "flight": r"^Flight Activity$", "fl_period": r"^Flight Hours by Period$",
 "fl_monthly": r"^Monthly Flight Activity", "fl_map": r"^Route Map$", "fl_ops": r"^Operational Summary$", "fl_routes": r"^Top Routes$",
 "reg": r"^Registration & Transfer Timeline", "opcost": r"^Estimated Annual Operating Cost", "ads": r"^Airworthiness & Maintenance Program",
 "sdr": r"^Service Difficulty Reports", "seller": r"^Who's Selling This Aircraft$", "pricehist": r"^Price history$",
 "grade": r"^Composite valuation score$", "pricepos": r"^Price position vs. market$", "mktcomp": r"^Market comparison$",
 "complist": r"^Aircraft this buyer is also seeing$", "perf": r"^Performance vs. Competing Models$", "dynamics": r"^Time to Sell",
 "velocity": r"^Market velocity$", "specs": r"^Original specifications$", "deprec": r"^Your aircraft's value over time",
}
JS = r"""([re_src, minw]) => {
  const re = new RegExp(re_src);
  let h = [...document.querySelectorAll('main h1, main h2, main h3, main h4')].find(e => e.offsetParent && re.test(e.innerText.trim()));
  if (!h) h = [...document.querySelectorAll('main *')].find(e => e.offsetParent && e.children.length===0 && re.test((e.innerText||'').trim()));
  if (!h) return null;
  let c = h.parentElement;
  while (c && c.tagName !== 'MAIN') {
    const cs = getComputedStyle(c); const r = c.getBoundingClientRect();
    if (parseFloat(cs.borderTopWidth) > 0 && r.width > minw) break;
    c = c.parentElement;
  }
  if (!c || c.tagName === 'MAIN') c = h.parentElement;
  c.setAttribute('data-cap', '1');
  const cb = c.getBoundingClientRect(); const boxes = [];
  for (const e of c.querySelectorAll('*')) {
    if (!e.offsetParent || e.children.length) continue;
    const t = (e.innerText || e.textContent || '').trim(); if (!t) continue;
    const r = e.getBoundingClientRect(); boxes.push({t: t.slice(0,120), x: r.left-cb.left, y: r.top-cb.top, w: r.width, h: r.height});
  }
  return {w: cb.width, h: cb.height, boxes};
}"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
    pg.goto("https://nextplane.us/signin", wait_until="networkidle", timeout=90000)
    pg.fill("input[type=email]", os.environ["NEXTPLANE_CAPTURE_EMAIL"]); pg.fill("input[type=password]", os.environ["NEXTPLANE_CAPTURE_PASSWORD"])
    pg.click("button[type=submit]"); pg.wait_for_timeout(5000)
    pg.goto(f"https://nextplane.us/aircraft-report/{TAIL}", wait_until="networkidle", timeout=120000); pg.wait_for_timeout(9000)
    if "UNLOCK IN REPORT" in pg.inner_text("body"): print("LOCKED"); sys.exit(3)
    # scroll through once so lazy sections mount
    hgt = pg.evaluate("() => document.documentElement.scrollHeight")
    for y in range(0, hgt, 700): pg.evaluate(f"() => window.scrollTo(0,{y})"); pg.wait_for_timeout(250)
    pg.evaluate("() => window.scrollTo(0,0)"); pg.wait_for_timeout(1500)
    pg.evaluate("""() => { const m=document.querySelector('main'); let n=m;
      while(n && n.parentElement){ for(const s of n.parentElement.children){ if(s!==n) s.style.display='none'; } n=n.parentElement; }
      m.style.marginLeft='0'; }""")
    pg.wait_for_timeout(1500)
    open(f"{OUT}/main_text.txt", "w").write(pg.inner_text("main"))
    meta = {}
    for k, rx in TARGETS.items():
        pg.evaluate("() => document.querySelectorAll('[data-cap]').forEach(e=>e.removeAttribute('data-cap'))")
        r = pg.evaluate(JS, [rx, 300 if k.startswith("fl_") else 500])
        if not r: print("MISS", k); continue
        el = pg.locator("[data-cap='1']").first
        el.scroll_into_view_if_needed(); pg.wait_for_timeout(900)
        try: el.screenshot(path=f"{OUT}/{k}.png")
        except Exception as ex: print("SHOTFAIL", k, ex); continue
        r["text"] = el.inner_text()[:6000]; meta[k] = r
        print(k, int(r["w"]), int(r["h"]), len(r["boxes"]))
    json.dump(meta, open(f"{OUT}/sections.json", "w"), indent=1)
    b.close()
