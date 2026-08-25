"""Pilih widget grafik lalu telusuri panel Styling untuk menemukan setelan sumbu."""
import json, sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac

SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
PETA = json.load(open("/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/halaman.json"))
h = [x for x in PETA["halaman"] if x["berkas"] == "h06-scatter-suhu"][0]

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    cdp = ctx.new_cdp_session(page)
    cdp.send("Emulation.setDeviceMetricsOverride",
             {"width": 1900, "height": 1050, "deviceScaleFactor": 1, "mobile": False})
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{PETA['storyId']}"
              f"/?pageId={h['pageId']}&mode=edit", wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    page.mouse.click(700, 600)          # klik badan grafik -> pilih widget
    time.sleep(8)
    page.screenshot(path=f"{SHOT}/styling-1.png")
    print("panel kanan:")
    for t in page.evaluate("""() => [...document.querySelectorAll('*')]
        .map(e => {const r = e.getBoundingClientRect();
                   return {t: (e.textContent||'').trim().slice(0,38), id: e.id,
                           x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2),
                           w: Math.round(r.width)};})
        .filter(o => o.t && o.x > 1380 && o.w > 40 && o.w < 400)""")[:35]:
        print("  ", t)
