"""Buka panel Styling grafik dan cari setelan rentang sumbu."""
import json, sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac

SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
PETA = json.load(open("/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/halaman.json"))
h = [x for x in PETA["halaman"] if x["berkas"] == "h06-scatter-suhu"][0]


def daftar(page, xmin=1500):
    return page.evaluate("""(xmin) => [...document.querySelectorAll('*')]
        .filter(e => !e.children.length)
        .map(e => {const r = e.getBoundingClientRect();
                   return {t: (e.textContent||'').trim().slice(0,34),
                           x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)};})
        .filter(o => o.t && o.x > xmin)""", xmin)


with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    cdp = ctx.new_cdp_session(page)
    cdp.send("Emulation.setDeviceMetricsOverride",
             {"width": 2000, "height": 1100, "deviceScaleFactor": 1, "mobile": False})
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{PETA['storyId']}"
              f"/?pageId={h['pageId']}&mode=edit", wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    # tutup popup bahasa
    page.evaluate("""() => {const b = document.getElementById('browser-language-popup-close-button');
                            if (b) b.click();}""")
    time.sleep(2)
    page.mouse.click(700, 600)          # pilih widget
    time.sleep(6)
    time.sleep(8)
    # UI5 mengabaikan klik JavaScript -> pakai mouse sungguhan
    def klik_teks(t):
        pos = page.evaluate("""(teks) => {
          for (const e of document.querySelectorAll('*')) {
            if (e.children.length) continue;
            if ((e.textContent||'').trim() !== teks) continue;
            const r = e.getBoundingClientRect();
            return {x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)};
          }
          return null;
        }""", t)
        if pos:
            page.mouse.click(pos["x"], pos["y"])
        return pos

    print("klik Builder:", klik_teks("Builder"))
    time.sleep(7)
    print("klik Styling:", klik_teks("Styling"))
    time.sleep(7)
    page.screenshot(path=f"{SHOT}/styling-2.png")
    print("isi panel kanan:")
    for t in daftar(page)[:40]:
        print("  ", t)
