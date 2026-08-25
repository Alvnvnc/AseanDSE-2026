"""Muat story dengan hook, cari tombol Save."""
import json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
import sac

SINI = Path(__file__).resolve().parent
HOOK = (SINI / "hook.js").read_text()
SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.add_init_script(HOOK)
    page.goto("about:blank"); time.sleep(1)
    page.goto(sac.STORY_URL, wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    page.screenshot(path=f"{SHOT}/pre-save.png")
    kandidat = page.evaluate("""() => {
      const out = [];
      document.querySelectorAll('[title],[aria-label],[data-help-id],[data-sap-fpa-elem-id]').forEach(el => {
        const t = [el.getAttribute('title'), el.getAttribute('aria-label'),
                   el.getAttribute('data-help-id'), el.getAttribute('data-sap-fpa-elem-id')]
                  .filter(Boolean).join(' | ');
        if (/save/i.test(t)) out.push({tag: el.tagName, id: el.id, t: t.slice(0,140)});
      });
      return out.slice(0, 30);
    }""")
    for k in kandidat: print(" ", k)
    print("jumlah kandidat:", len(kandidat))
