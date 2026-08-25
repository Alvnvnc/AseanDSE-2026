"""Tangkap bilah alat editor story dan daftarkan tombolnya."""
import sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac

SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
SID = sys.argv[1]

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    cdp = ctx.new_cdp_session(page)
    cdp.send("Emulation.setDeviceMetricsOverride",
             {"width": 1900, "height": 1000, "deviceScaleFactor": 1, "mobile": False})
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{SID}/?mode=edit",
              wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    page.screenshot(path=f"{SHOT}/toolbar.png", clip={"x": 0, "y": 100, "width": 1500, "height": 80})
    for t in page.evaluate("""() => [...document.querySelectorAll('[id]')]
        .map(e => {const r = e.getBoundingClientRect();
                   return {id: e.id, t: (e.getAttribute('title')||e.getAttribute('aria-label')||'').slice(0,40),
                           x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2),
                           w: Math.round(r.width), h: Math.round(r.height)};})
        .filter(o => o.y > 115 && o.y < 165 && o.w > 15 && o.w < 90)"""):
        print("  ", t)
