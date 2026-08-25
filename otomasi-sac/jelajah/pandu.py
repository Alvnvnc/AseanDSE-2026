"""Pandu UI SAC langkah demi langkah. Edge tetap hidup antar pemanggilan,
jadi tiap perintah bekerja pada halaman yang sama.

  pandu.py buka  <berkas-halaman> [mode]   buka halaman story
  pandu.py foto  [nama]                    tangkap layar
  pandu.py klik  <x> <y>                   klik mouse sungguhan
  pandu.py teks  <teks> [ymin] [xmin]      klik elemen daun bertuliskan <teks>
  pandu.py lihat [xmin] [ymin]             daftar teks daun + koordinatnya
  pandu.py ketik <teks>                    ketik di elemen yang sedang fokus
  pandu.py tombol <key>                    tekan tombol (Enter, Escape, ...)
  pandu.py js    <ekspresi>                jalankan JS, cetak hasilnya
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from playwright.sync_api import sync_playwright
import sac

SHOT = Path("/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/"
            "17376010-2635-488d-97da-095ba251cbf7/scratchpad")
PETA = json.load(open(Path(__file__).resolve().parent.parent / "halaman.json"))


def daun(page, xmin=0, ymin=0):
    return page.evaluate("""([xmin, ymin]) => [...document.querySelectorAll('*')]
        .filter(e => !e.children.length)
        .map(e => {const r = e.getBoundingClientRect();
                   return {t: (e.textContent||'').trim().slice(0,40),
                           x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2),
                           w: Math.round(r.width), h: Math.round(r.height)};})
        .filter(o => o.t && o.w > 2 && o.x >= xmin && o.y >= ymin)""", [xmin, ymin])


def main():
    perintah = sys.argv[1]
    with sync_playwright() as p:
        b, ctx, page = sac.sambung(p)

        if perintah == "buka":
            berkas = sys.argv[2]
            mode = sys.argv[3] if len(sys.argv) > 3 else "edit"
            h = [x for x in PETA["halaman"] if x["berkas"] == berkas][0]
            cdp = ctx.new_cdp_session(page)
            cdp.send("Emulation.setDeviceMetricsOverride",
                     {"width": 1920, "height": 1200, "deviceScaleFactor": 1, "mobile": False})
            page.goto("about:blank"); time.sleep(1)
            page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{PETA['storyId']}"
                      f"/?pageId={h['pageId']}&mode={mode}",
                      wait_until="domcontentloaded", timeout=120000)
            time.sleep(60)
            page.evaluate("""() => {const b = document.getElementById(
                'browser-language-popup-close-button'); if (b) b.click();}""")
            time.sleep(2)
            page.screenshot(path=str(SHOT / "pandu.png"))
            print("terbuka:", berkas, h["pageId"])

        elif perintah == "foto":
            nama = sys.argv[2] if len(sys.argv) > 2 else "pandu"
            page.screenshot(path=str(SHOT / f"{nama}.png"))
            print("foto:", nama)

        elif perintah == "klik":
            x, y = int(sys.argv[2]), int(sys.argv[3])
            page.mouse.click(x, y)
            time.sleep(float(sys.argv[4]) if len(sys.argv) > 4 else 4)
            page.screenshot(path=str(SHOT / "pandu.png"))
            print("klik", x, y)

        elif perintah == "teks":
            t = sys.argv[2]
            ymin = int(sys.argv[3]) if len(sys.argv) > 3 else 0
            xmin = int(sys.argv[4]) if len(sys.argv) > 4 else 0
            cocok = [o for o in daun(page, xmin, ymin) if o["t"] == t]
            if not cocok:
                cocok = [o for o in daun(page, xmin, ymin) if t.lower() in o["t"].lower()]
            print("kandidat:", cocok[:6])
            if cocok:
                page.mouse.click(cocok[0]["x"], cocok[0]["y"])
                time.sleep(5)
                page.screenshot(path=str(SHOT / "pandu.png"))

        elif perintah == "lihat":
            xmin = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            ymin = int(sys.argv[3]) if len(sys.argv) > 3 else 0
            for o in daun(page, xmin, ymin):
                print(f"  ({o['x']:4d},{o['y']:4d}) {o['w']:4d}x{o['h']:<3d} {o['t']}")

        elif perintah == "ketik":
            page.keyboard.type(sys.argv[2], delay=60)
            time.sleep(1)
            page.screenshot(path=str(SHOT / "pandu.png"))
            print("ketik:", sys.argv[2])

        elif perintah == "tombol":
            page.keyboard.press(sys.argv[2])
            time.sleep(float(sys.argv[3]) if len(sys.argv) > 3 else 3)
            page.screenshot(path=str(SHOT / "pandu.png"))
            print("tombol:", sys.argv[2])

        elif perintah == "kanan":
            x, y = int(sys.argv[2]), int(sys.argv[3])
            page.mouse.click(x, y, button="right")
            time.sleep(float(sys.argv[4]) if len(sys.argv) > 4 else 4)
            page.screenshot(path=str(SHOT / "pandu.png"))
            print("klik kanan", x, y)

        elif perintah == "gulir":
            x, y, dy = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
            page.mouse.move(x, y)
            page.mouse.wheel(0, dy)
            time.sleep(3)
            page.screenshot(path=str(SHOT / "pandu.png"))
            print("gulir", dy)

        elif perintah == "ukuran":
            w, h = int(sys.argv[2]), int(sys.argv[3])
            cdp = ctx.new_cdp_session(page)
            cdp.send("Emulation.setDeviceMetricsOverride",
                     {"width": w, "height": h, "deviceScaleFactor": 1, "mobile": False})
            time.sleep(4)
            page.screenshot(path=str(SHOT / "pandu.png"))
            print("ukuran", w, h)

        elif perintah == "js":
            print(json.dumps(page.evaluate(sys.argv[2]), indent=1, default=str)[:6000])


main()
