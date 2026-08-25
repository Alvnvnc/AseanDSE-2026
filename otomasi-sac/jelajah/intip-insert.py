"""Petakan tombol grup Insert di editor story (untuk menemukan tombol Table)."""
import sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac

SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
SID = sys.argv[1] if len(sys.argv) > 1 else "8D68C286FA86EB3FB3B3D419CC1A8B38"

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{SID}/?mode=edit",
              wait_until="domcontentloaded", timeout=120000)
    time.sleep(50)
    page.screenshot(path=f"{SHOT}/toolbar-insert.png")
    for t in page.evaluate("""() => [...document.querySelectorAll('*')]
        .map(e => {const r = e.getBoundingClientRect();
                   return {id: e.id, tag: e.tagName,
                           t: (e.getAttribute('title') || e.getAttribute('aria-label') || '').slice(0,50),
                           x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2),
                           w: Math.round(r.width)};})
        .filter(o => o.t && o.y > 110 && o.y < 165 && o.w > 15)"""):
        print("  ", t)
