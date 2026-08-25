"""Buka Edit Styling widget grafik dan daftarkan setelan yang tersedia."""
import json, sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac

SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
PETA = json.load(open("/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/halaman.json"))
h = [x for x in PETA["halaman"] if x["berkas"] == "h06-scatter-suhu"][0]


def klik_teks(page, teks, ymin=180):
    pos = page.evaluate("""([t, ymin]) => {
      for (const e of document.querySelectorAll('li,[role=menuitem],ui5-menu-item,span,div,button')) {
        if (e.children.length) continue;
        if ((e.textContent||'').trim() !== t) continue;
        const r = e.getBoundingClientRect();
        if (r.width < 10 || r.y < ymin) continue;
        return {x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)};
      }
      return null;
    }""", [teks, ymin])
    if pos:
        page.mouse.click(pos["x"], pos["y"])
    return pos


with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    cdp = ctx.new_cdp_session(page)
    cdp.send("Emulation.setDeviceMetricsOverride",
             {"width": 1700, "height": 1500, "deviceScaleFactor": 1, "mobile": False})
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{PETA['storyId']}"
              f"/?pageId={h['pageId']}&mode=edit", wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    page.mouse.click(700, 600); time.sleep(6)
    page.mouse.click(1480, 236); time.sleep(6)          # ⋮ More Actions
    print("Edit Styling:", klik_teks(page, "Edit Styling..."))
    time.sleep(10)
    # panel terbuka -> pindah ke tab Builder yang memuat setelan grafik
    print("tab Builder:", klik_teks(page, "Builder", ymin=200))
    time.sleep(8)
    # klik akordeon "Chart Properties" di posisi terkini
    pos = page.evaluate("""() => {
      for (const e of document.querySelectorAll('*')) {
        if (e.children.length) continue;
        if ((e.textContent||'').trim() !== 'Chart Properties') continue;
        const r = e.getBoundingClientRect();
        return {x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)};
      }
      return null;
    }""")
    print("Chart Properties di:", pos)
    if pos:
        page.mouse.click(pos["x"], pos["y"])
    time.sleep(9)

    pos2 = page.evaluate("""() => {
      for (const e of document.querySelectorAll('*')) {
        if (e.children.length) continue;
        if ((e.textContent||'').trim() !== 'Value Settings') continue;
        const r = e.getBoundingClientRect();
        if (r.y < 400) continue;
        return {x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)};
      }
      return null;
    }""")
    print("Value Settings di:", pos2)
    if pos2:
        page.mouse.click(pos2["x"], pos2["y"])
    time.sleep(9)
    page.screenshot(path=f"{SHOT}/edit-styling.png")
    print("isi panel:")
    for t in page.evaluate("""() => [...document.querySelectorAll('*')]
        .filter(e => !e.children.length)
        .map(e => {const r = e.getBoundingClientRect();
                   return {t: (e.textContent||'').trim().slice(0,32),
                           x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)};})
        .filter(o => o.t && o.x > 1150 && o.y > 1050)""")[:40]:
        print("  ", t)
