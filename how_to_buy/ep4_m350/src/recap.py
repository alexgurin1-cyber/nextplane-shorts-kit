import os, sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
    pg.goto("https://nextplane.us/signin", wait_until="networkidle", timeout=90000)
    pg.fill("input[type=email]", os.environ["NEXTPLANE_CAPTURE_EMAIL"]); pg.fill("input[type=password]", os.environ["NEXTPLANE_CAPTURE_PASSWORD"])
    pg.click("button[type=submit]"); pg.wait_for_timeout(5000)
    pg.goto("https://nextplane.us/aircraft-report/N333WR", wait_until="networkidle", timeout=120000); pg.wait_for_timeout(9000)
    if "UNLOCK IN REPORT" in pg.inner_text("body"): print("LOCKED"); sys.exit(3)
    pg.evaluate("""() => { const m=document.querySelector('main'); let n=m;
      while(n && n.parentElement){ for(const s of n.parentElement.children){ if(s!==n) s.style.display='none'; } n=n.parentElement; }
      m.style.marginLeft='0'; }""")
    pg.evaluate("""() => { const h=[...document.querySelectorAll('main h1, main h2, main h3, main h4')].find(e=>e.offsetParent && /^Replacement cost/.test(e.innerText.trim()));
      let c=h.parentElement; while(c && c.tagName!=='MAIN'){ const cs=getComputedStyle(c); const r=c.getBoundingClientRect(); if(parseFloat(cs.borderTopWidth)>0 && r.width>500) break; c=c.parentElement; } c.setAttribute('data-cap','1'); c.scrollIntoView({block:'end'}); }""")
    pg.wait_for_timeout(800); pg.mouse.move(5, 5); pg.wait_for_timeout(800)
    el = pg.locator("[data-cap='1']").first
    bb = el.bounding_box(); pg.screenshot(path="cap/replacement.png", clip=bb); print(bb)
    b.close()
