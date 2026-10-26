import os
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = b.new_page(viewport={"width":1600,"height":1000})
    pg.goto("https://nextplane.us/signin", wait_until="networkidle", timeout=90000)
    pg.fill("input[type=email]", os.environ["NEXTPLANE_CAPTURE_EMAIL"]); pg.fill("input[type=password]", os.environ["NEXTPLANE_CAPTURE_PASSWORD"])
    pg.click("button[type=submit]"); pg.wait_for_timeout(5000)
    pg.goto("https://nextplane.us/aircraft-report/N8395H", wait_until="networkidle", timeout=120000); pg.wait_for_timeout(9000)
    h = pg.evaluate("() => document.documentElement.scrollHeight")
    for y in range(0, h, 700): pg.evaluate(f"() => window.scrollTo(0,{y})"); pg.wait_for_timeout(200)
    open("cap2_main_text.txt","w").write(pg.inner_text("main")); b.close()
