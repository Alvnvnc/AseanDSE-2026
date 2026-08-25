"""Impor CSV jadi DATASET baru di SAC lewat UI (Playwright).

Dipakai untuk 7 berkas di `ekspor-csv/perbaikan/` yang tipenya perlu dibetulkan.
Langkah pertama skrip ini adalah MEMETAKAN tombol impor di layar Files —
jalankan dengan `--intip` dulu untuk melihat kandidatnya.
"""
import sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from pathlib import Path
from playwright.sync_api import sync_playwright
import sac

SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"


def intip(page):
    """Cetak kandidat tombol/menu yang berhubungan dengan impor data."""
    hasil = page.evaluate("""() => {
      const out = [];
      document.querySelectorAll('button, [role=button], ui5-button, [title], [aria-label]')
        .forEach(el => {
          const t = [el.getAttribute('title'), el.getAttribute('aria-label'),
                     (el.textContent || '').trim().slice(0, 40)].filter(Boolean).join(' | ');
          if (!t) return;
          if (/import|upload|acquire|new model|dataset|\\+/i.test(t)) {
            const r = el.getBoundingClientRect();
            out.push({tag: el.tagName, id: el.id, t: t.slice(0, 90),
                      x: Math.round(r.x), y: Math.round(r.y),
                      w: Math.round(r.width), h: Math.round(r.height)});
          }
        });
      return out.slice(0, 40);
    }""")
    for h in hasil:
        print("  ", h)
    return hasil


with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
              timeout=120000)
    time.sleep(45)
    page.screenshot(path=f"{SHOT}/files-toolbar.png")
    print("kandidat tombol impor:")
    intip(page)
    print("tangkapan:", f"{SHOT}/files-toolbar.png")
