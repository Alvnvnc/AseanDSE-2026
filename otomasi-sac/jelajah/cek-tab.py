import sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac

SID = sys.argv[1]
with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{SID}/?mode=edit",
              wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    info = page.evaluate("""() => {
      const out = [];
      document.querySelectorAll('.sapEpmUiTabContainerTabTitle, [class*=TabTitle]').forEach(el => {
        const r = el.getBoundingClientRect();
        out.push({t: el.getAttribute('title') || el.textContent, w: Math.round(r.width),
                  h: Math.round(r.height), x: Math.round(r.x), y: Math.round(r.y)});
      });
      return out;
    }""")
    for i in info: print(" ", i)
