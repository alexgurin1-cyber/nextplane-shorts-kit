"""Click 'Update valuation' on the N814LT report (hours prefilled 1678/1678) and capture the valuation card after."""
import os, sys, json, re
JS = re.search(r'JS = r"""(.*?)"""', open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"capture.py")).read(), re.S).group(1)
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
    pg.goto("https://nextplane.us/signin", wait_until="networkidle", timeout=90000)
    pg.fill("input[type=email]", os.environ["NEXTPLANE_CAPTURE_EMAIL"]); pg.fill("input[type=password]", os.environ["NEXTPLANE_CAPTURE_PASSWORD"])
    pg.click("button[type=submit]"); pg.wait_for_timeout(5000)
    pg.goto("https://nextplane.us/aircraft-report/N814LT", wait_until="networkidle", timeout=120000); pg.wait_for_timeout(9000)
    pg.evaluate("""() => { const m=document.querySelector('main'); let n=m;
      while(n && n.parentElement){ for(const s of n.parentElement.children){ if(s!==n) s.style.display='none'; } n=n.parentElement; }
      m.style.marginLeft='0'; }""")
    btn = pg.get_by_role("button", name="Update valuation")
    btn.scroll_into_view_if_needed(); pg.wait_for_timeout(800)
    pg.evaluate(JS, ["^Estimated Market Value$", 500]); card = pg.locator("[data-cap='1']").first
    card.screenshot(path=f"{OUT}/val_before.png")
    btn.click(); pg.wait_for_timeout(5000)
    pg.evaluate("() => document.querySelectorAll('[data-cap]').forEach(e=>e.removeAttribute('data-cap'))")
    r = pg.evaluate(JS, ["^Estimated Market Value$", 500]); card = pg.locator("[data-cap='1']").first
    card.screenshot(path=f"{OUT}/val_after.png"); json.dump(r, open(f"{OUT}/val_after.json","w"))
    open(f"{OUT}/val_after.txt","w").write(card.inner_text())
    print(card.inner_text()[:1500])
    b.close()
