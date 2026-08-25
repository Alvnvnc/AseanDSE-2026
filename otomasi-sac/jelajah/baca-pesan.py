"""Buka satu halaman, baca teks pesan/peringatan di dalam widget."""
import json, sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac

PETA = json.load(open("/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/halaman.json"))
target = sys.argv[1]
h = [x for x in PETA["halaman"] if x["berkas"] == target][0]

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{PETA['storyId']}"
              f"/?pageId={h['pageId']}&mode=view", wait_until="domcontentloaded", timeout=120000)
    time.sleep(50)
    teks = page.evaluate("""() => {
      const out = new Set();
      document.querySelectorAll('*').forEach(el => {
        if (el.children.length) return;
        const t = (el.textContent || '').trim();
        if (t.length > 10 && t.length < 400 &&
            /unavailable|invalid|error|cannot|not supported|required|feed|missing|add /i.test(t))
          out.add(t);
      });
      return [...out];
    }""")
    print("pesan di halaman:")
    for t in teks: print("  *", t)
    page.screenshot(path="/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad/pesan.png")
