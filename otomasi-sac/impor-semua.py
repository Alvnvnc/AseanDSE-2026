"""Impor CSV perbaikan jadi DATASET baru di SAC, satu per satu, lewat UI.

Alur per berkas: buka layar buat dataset -> kartu CSV -> pasang berkas ->
Create -> dialog Save (nama sudah terisi dari nama berkas) -> Save.

Jalankan: .venv/bin/python otomasi-sac/impor-semua.py [pola-nama ...]
"""
import sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from pathlib import Path
from playwright.sync_api import sync_playwright
import sac

SUMBER = Path("/home/alvn/Documents/Riset/AseanDSE-2026/ekspor-csv/perbaikan")
SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
URL_BUAT = (f"{sac.TENANT}/sap/fpa/ui/app.html#/dataset&/ds/"
            f"?mode=create&defaultLocation=PRIVATE_SWALLOWGANK")

CARI_TEKS = """([teks, ymin]) => {
  const els = [...document.querySelectorAll('button, [role=button], ui5-button, .sapMBtn')];
  for (const el of els) {
    if ((el.textContent || '').trim() !== teks) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 20 || r.height < 8 || r.y < ymin) continue;
    return {x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2)};
  }
  return null;
}"""


def klik(page, teks, ymin=0):
    """Klik tombol berlabel `teks` dengan mouse sungguhan (klik JS sering diabaikan UI5)."""
    kotak = page.evaluate(CARI_TEKS, [teks, ymin])
    if not kotak:
        return False
    page.mouse.click(kotak["x"], kotak["y"])
    return True


def impor(page, berkas: Path) -> bool:
    page.goto("about:blank"); time.sleep(1)
    page.goto(URL_BUAT, wait_until="domcontentloaded", timeout=120000)
    time.sleep(32)

    page.mouse.click(186, 290)                       # kartu "From a CSV or Excel File"
    time.sleep(9)
    fu = page.locator("input[type=file]")
    if not fu.count():
        print("   ! kotak unggah tidak muncul"); return False
    fu.first.set_input_files(str(berkas))
    time.sleep(18)

    if not klik(page, "Create", ymin=300):
        print("   ! tombol Create tidak ketemu"); return False
    time.sleep(45)

    if not klik(page, "Save", ymin=400):
        page.screenshot(path=f"{SHOT}/impor-gagal-{berkas.stem[:20]}.png")
        print("   ! dialog Save tidak ketemu"); return False
    time.sleep(55)
    return True


pola = sys.argv[1:]
berkas = sorted(p for p in SUMBER.glob("*.csv")
                if not pola or any(x.lower() in p.name.lower() for x in pola))
print(f"{len(berkas)} berkas akan diimpor\n")

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    for i, f in enumerate(berkas, 1):
        print(f"[{i}/{len(berkas)}] {f.name}")
        ok = impor(page, f)
        print("   ->", "berhasil" if ok else "GAGAL")
