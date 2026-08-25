"""Centang 'Do not ask me again' pada popup bahasa lalu tutup — sekali saja."""
import sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    cdp = ctx.new_cdp_session(page)
    cdp.send("Emulation.setDeviceMetricsOverride",
             {"width": 1700, "height": 1050, "deviceScaleFactor": 1, "mobile": False})
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
              timeout=120000)
    time.sleep(45)
    for nama, sel in [("checkbox", "browser-language-popup-checkbox"),
                      ("tutup", "browser-language-popup-close-button")]:
        pos = page.evaluate("""(id) => {const e = document.getElementById(id);
            if (!e) return null; const r = e.getBoundingClientRect();
            return {x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)};}""", sel)
        print(nama, "->", pos)
        if pos:
            page.mouse.click(pos["x"], pos["y"])
            time.sleep(3)
    time.sleep(3)
    print("popup masih ada?", page.evaluate(
        "() => !!document.getElementById('browser-language-popup-close-button')"))
