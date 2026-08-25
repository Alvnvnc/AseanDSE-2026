"""Sisipkan satu widget Table lewat UI, untuk dijadikan template generator."""
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
             {"width": 1900, "height": 1050, "deviceScaleFactor": 1, "mobile": False})
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{SID}/?mode=edit",
              wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    page.mouse.click(614, 141)          # ADD_TABLEId-1
    time.sleep(12)
    page.screenshot(path=f"{SHOT}/tabel-1.png")
    print("setelah klik Insert Table:")
    for t in page.evaluate("""() => [...document.querySelectorAll('button,[role=button],li,input,span')]
        .map(e => {const r = e.getBoundingClientRect();
                   return {t: (e.textContent||e.getAttribute('placeholder')||'').trim().slice(0,45),
                           x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2),
                           w: Math.round(r.width)};})
        .filter(o => o.t && o.w > 30 && o.y > 150)""")[:28]:
        print("  ", t)
