"""Buka menu titik-tiga pada widget grafik dan daftarkan isinya."""
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
             {"width": 1700, "height": 1050, "deviceScaleFactor": 1, "mobile": False})
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{PETA['storyId']}"
              f"/?pageId={h['pageId']}&mode=edit", wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    page.evaluate("""() => {const b=document.getElementById('browser-language-popup-close-button');
                            if (b) b.click();}""")
    time.sleep(2)
    page.mouse.click(700, 600)
    time.sleep(6)
    # tombol ⋮ widget: cari lewat atribut
    pos = page.evaluate("""() => {
      for (const e of document.querySelectorAll('[title],[aria-label],[id]')) {
        const t = (e.getAttribute('title')||e.getAttribute('aria-label')||e.id||'');
        if (!/more|menu|overflow|option/i.test(t)) continue;
        const r = e.getBoundingClientRect();
        if (r.width > 15 && r.width < 60 && r.y > 190 && r.y < 320)
          return {t: t.slice(0,40), x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)};
      }
      return null;
    }""")
    print("tombol menu widget:", pos)
    if pos:
        page.mouse.click(pos["x"], pos["y"])
        time.sleep(6)
    page.screenshot(path=f"{SHOT}/menu-widget.png")
    print("isi menu:")
    for t in page.evaluate("""() => [...document.querySelectorAll('li,[role=menuitem],ui5-menu-item')]
        .map(e => {const r = e.getBoundingClientRect();
                   return {t: (e.textContent||'').trim().slice(0,40),
                           x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)};})
        .filter(o => o.t && o.y > 180)""")[:30]:
        print("  ", t)
