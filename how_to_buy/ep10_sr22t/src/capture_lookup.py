"""Product demo frames: nextplane.us home -> type N657CB into #hero-nnumber -> submit -> report opens (signed in)."""
import os, sys
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=1.2)
    pg.goto("https://nextplane.us/signin", wait_until="networkidle", timeout=90000)
    pg.fill("input[type=email]", os.environ["NEXTPLANE_CAPTURE_EMAIL"]); pg.fill("input[type=password]", os.environ["NEXTPLANE_CAPTURE_PASSWORD"])
    pg.click("button[type=submit]"); pg.wait_for_timeout(5000)
    pg.goto("https://nextplane.us/", wait_until="networkidle", timeout=90000); pg.wait_for_timeout(4000)
    pg.screenshot(path=f"{OUT}/l0_home.png")
    box = pg.locator("#hero-nnumber"); box.scroll_into_view_if_needed(); box.click()
    for i, ch in enumerate("N657CB"):
        box.type(ch, delay=120); pg.screenshot(path=f"{OUT}/l1_type_{i}.png")
    pg.wait_for_timeout(800); pg.screenshot(path=f"{OUT}/l2_typed.png")
    box.press("Enter"); pg.wait_for_timeout(2500); pg.screenshot(path=f"{OUT}/l3_loading.png")
    pg.wait_for_load_state("networkidle", timeout=120000); pg.wait_for_timeout(8000)
    print("URL", pg.url); pg.screenshot(path=f"{OUT}/l4_report.png")
    pg.mouse.wheel(0, 700); pg.wait_for_timeout(1500); pg.screenshot(path=f"{OUT}/l5_report_scroll.png")
    b.close()
