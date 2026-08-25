"""Buka story, pindah ke halaman berjudul X, tangkap layar."""
import sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac

SID, JUDUL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
MODE = sys.argv[4] if len(sys.argv) > 4 else "edit"

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.goto("about:blank"); time.sleep(1)
    # buang cache lokal SAC supaya isi terbaru yang dimuat
    try:
        page.goto(sac.TENANT + "/sap/fpa/ui/app.html", wait_until="domcontentloaded", timeout=90000)
        page.evaluate("""async () => {
            if (window.caches) { for (const k of await caches.keys()) await caches.delete(k); }
            if (navigator.serviceWorker) {
              for (const r of await navigator.serviceWorker.getRegistrations()) await r.unregister();
            }
            if (window.indexedDB && indexedDB.databases) {
              for (const d of await indexedDB.databases()) { try { indexedDB.deleteDatabase(d.name); } catch(e){} }
            }
        }""")
        time.sleep(3)
    except Exception as e:
        print("bersih cache gagal:", str(e)[:120])
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{SID}/?mode={MODE}",
              wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    if JUDUL != "-":
        ok = page.evaluate("""(judul) => {
            const els = [...document.querySelectorAll('[title]')]
              .filter(e => e.getAttribute('title') === judul);
            for (const el of els) {
              let n = el;
              for (let i = 0; n && i < 6; i++, n = n.parentElement) {
                const r = n.getBoundingClientRect();
                if (r.width > 10 && r.height > 5) { n.click(); return true; }
              }
            }
            return false;
        }""", JUDUL)
        print("klik tab", JUDUL, "->", ok)
        time.sleep(35)
    page.screenshot(path=OUT)
    print("->", OUT)
