"""Buka Files -> '+' -> Dataset, lalu laporkan apa yang muncul."""
import sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac

SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"


def tutup_popup(page):
    page.evaluate("""() => {
      document.querySelectorAll('[title="Close"], [aria-label="Close"]').forEach(e => {
        const r = e.getBoundingClientRect();
        if (r.width && r.y < 200) e.click();
      });
    }""")


def klik_teks(page, teks, xmin=0):
    return page.evaluate("""([teks, xmin]) => {
      const els = [...document.querySelectorAll('li, [role=menuitem], .sapMMenuItem, ui5-menu-item, span, div')];
      for (const el of els) {
        if ((el.textContent || '').trim() !== teks) continue;
        const r = el.getBoundingClientRect();
        if (r.width < 10 || r.height < 5 || r.x < xmin) continue;
        let n = el;
        for (let i = 0; n && i < 5; i++, n = n.parentElement) {
          const q = n.getBoundingClientRect();
          if (q.width > 30 && q.height > 10) { n.click(); return {ok: true, x: q.x, y: q.y}; }
        }
      }
      return {ok: false};
    }""", [teks, xmin])


with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
              timeout=120000)
    time.sleep(42)
    tutup_popup(page); time.sleep(2)

    page.mouse.click(1028, 156)   # tombol "+"
    time.sleep(4)
    page.screenshot(path=f"{SHOT}/impor-menu.png")
    hasil = klik_teks(page, "Dataset", xmin=1000)
    print("klik 'Dataset':", hasil)
    time.sleep(12)
    page.screenshot(path=f"{SHOT}/impor-dialog.png")
    print("URL:", page.url[:150])
    print("input file:", page.evaluate("""() => [...document.querySelectorAll('input[type=file]')]
          .map(e => ({id: e.id, accept: e.accept}))"""))
    for t in page.evaluate("""() => [...document.querySelectorAll('button, [role=button], ui5-button, li, .sapMBtn')]
          .map(e => {const r = e.getBoundingClientRect();
                     return {t: (e.textContent||e.getAttribute('title')||'').trim().slice(0,50),
                             x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2),
                             w: Math.round(r.width)};})
          .filter(o => o.t && o.w > 25 && o.y > 95)""")[:30]:
        print("  ", t)
