"""Lanjutkan alur: klik kartu CSV, unggah berkas, laporkan layar berikutnya."""
import sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac

SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
BERKAS = sys.argv[1]
URL_BUAT = (f"{sac.TENANT}/sap/fpa/ui/app.html#/dataset&/ds/"
            f"?mode=create&defaultLocation=PRIVATE_SWALLOWGANK")


def lapor(page, tahap):
    page.screenshot(path=f"{SHOT}/impor-{tahap}.png")
    print(f"--- {tahap} | {page.url[:120]}")
    print("   input file:", page.evaluate(
        "() => [...document.querySelectorAll('input[type=file]')].map(e => e.id || '(tanpa id)')"))
    for t in page.evaluate("""() => [...document.querySelectorAll('button, [role=button], ui5-button, input')]
          .map(e => {const r = e.getBoundingClientRect();
                     return {t: (e.textContent||e.getAttribute('title')||e.getAttribute('placeholder')||'').trim().slice(0,45),
                             x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2),
                             w: Math.round(r.width)};})
          .filter(o => o.t && o.w > 25 && o.y > 95 && o.x > 60)""")[:22]:
        print("   ", t)


with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.goto("about:blank"); time.sleep(1)
    page.goto(URL_BUAT, wait_until="domcontentloaded", timeout=120000)
    time.sleep(35)
    page.mouse.click(186, 290)      # kartu "Bring in data from CSV or Excel files."
    time.sleep(10)
    lapor(page, "kartu-csv")

    inputs = page.locator("input[type=file]")
    if inputs.count():
        inputs.first.set_input_files(BERKAS)
        print(">> berkas dipasang:", BERKAS)
        time.sleep(25)
        lapor(page, "setelah-unggah")
        page.mouse.click(978, 619)      # tombol Create
        print(">> Create diklik, menunggu wrangler...")
        time.sleep(60)
        lapor(page, "wrangler")
    else:
        print(">> tidak ada input[type=file]; mungkin lewat dialog pemilih berkas")
