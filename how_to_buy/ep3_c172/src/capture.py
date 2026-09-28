"""Section-by-section capture of the N733JE report (element screenshots + callout boxes)."""
import os, json, re, sys
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
TARGETS = {  # key: (heading text regex, [callout texts])
 "header": (r"^N733JE$", ["Hagerstown", "Nov 2019", "$129,900", "None", "6.9 yrs", "No security conveyance indexed"]),
 "verdict": (r"^CURRENT OWNERSHIP PERIOD$", ["6.9 yrs", "No security conveyance indexed", "HAGERSTOWN FLIGHT SCHOOL", "trade-a-plane"]),
 "cpm": (r"^True Cost per Mile", ["THIS AIRCRAFT", "MARKET AVERAGE", "1,500 hr SMOH", "1,024 hr avg SMOH"]),
 "flight": (r"^Recent activity from ADS-B", ["HGR → SBY"]),
 "reg": (r"^Registration & Transfer Timeline", ["HAGERSTOWN FLIGHT SCHOOL", "No security conveyance indexed", "No ownership transfer observed since May 9, 2026."]),
 "ads": (r"^Airworthiness & Maintenance Program", ["HAGERSTOWN", "trade-a-plane", "2011-10-09", "2020-18-01", "12 ADs", "O-320-H2AD"]),
 "sdr": (r"^Service Difficulty Reports", ["No Service Difficulty Report has been filed under this N-number since 1995."]),
 "pricehist": (r"^Price history$", []),
 "valuation": (r"^Estimated Market Value$", []),
 "seller": (r"^Who's Selling This Aircraft$", []),
}
JS = r"""([re_src, callouts]) => {
  const re = new RegExp(re_src);
  let h = [...document.querySelectorAll('main h1, main h2, main h3')].find(e => e.offsetParent && re.test(e.innerText.trim()));
  if (!h) h = [...document.querySelectorAll('main *')].find(e => e.offsetParent && e.children.length===0 && re.test((e.innerText||'').trim()));
  if (!h) return null;
  // climb to the card: first ancestor with a border and >= 500px wide
  let c = h.parentElement;
  while (c && c.tagName !== 'MAIN') {
    const cs = getComputedStyle(c); const r = c.getBoundingClientRect();
    if (parseFloat(cs.borderTopWidth) > 0 && r.width > 500) break;
    c = c.parentElement;
  }
  if (!c || c.tagName === 'MAIN') c = h.parentElement;
  c.setAttribute('data-cap', '1');
  const cb = c.getBoundingClientRect();
  const boxes = [];
  for (const t of callouts) {
    const els = [...c.querySelectorAll('*')].filter(e=>e.offsetParent).filter(e => e.children.length === 0 && e.innerText && e.innerText.trim().includes(t));
    for (const e of els) { const r = e.getBoundingClientRect(); boxes.push({t, x: r.left - cb.left, y: r.top - cb.top, w: r.width, h: r.height}); }
  }
  return {w: cb.width, h: cb.height, boxes};
}"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
    pg.goto("https://nextplane.us/signin", wait_until="networkidle", timeout=90000)
    pg.fill("input[type=email]", os.environ["NEXTPLANE_CAPTURE_EMAIL"]); pg.fill("input[type=password]", os.environ["NEXTPLANE_CAPTURE_PASSWORD"])
    pg.click("button[type=submit]"); pg.wait_for_timeout(5000)
    pg.goto("https://nextplane.us/aircraft-report/N733JE", wait_until="networkidle", timeout=120000); pg.wait_for_timeout(8000)
    if "UNLOCK IN REPORT" in pg.inner_text("body"): print("LOCKED"); sys.exit(3)
    # hide everything outside <main> (sidebar, top bar)
    pg.evaluate("""() => { const m=document.querySelector('main'); let n=m;
      while(n && n.parentElement){ for(const s of n.parentElement.children){ if(s!==n) s.style.display='none'; } n=n.parentElement; }
      m.style.marginLeft='0'; }""")
    pg.wait_for_timeout(1500)
    meta = {}
    for k, (rx, co) in TARGETS.items():
        pg.evaluate("() => document.querySelectorAll('[data-cap]').forEach(e=>e.removeAttribute('data-cap'))")
        r = pg.evaluate(JS, [rx, co])
        if not r: print("MISS", k); continue
        el = pg.locator("[data-cap='1']").first
        el.scroll_into_view_if_needed(); pg.wait_for_timeout(600)
        el.screenshot(path=f"{OUT}/{k}.png")
        r["text"] = el.inner_text()[:3000]; meta[k] = r
        print(k, int(r["w"]), int(r["h"]), [x["t"] for x in r["boxes"]])
    json.dump(meta, open(f"{OUT}/sections.json", "w"), indent=1)
    b.close()
