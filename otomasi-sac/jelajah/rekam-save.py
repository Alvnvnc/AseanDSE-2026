"""Buka story SALINAN, klik Save, rekam payload updateContent yang asli."""
import json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
import sac

SINI = Path(__file__).resolve().parent
HOOK = (SINI / "hook.js").read_text()
SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
UJI = "8D68C286FA86EB3FB3B3D419CC1A8B38"
OUT = sys.argv[1]

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.add_init_script(HOOK)
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{UJI}/?mode=edit",
              wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)

    info = page.evaluate("""() => {
      const el = document.elementFromPoint(136, 141);
      const rantai = [];
      let e = el;
      for (let i = 0; e && i < 6; i++, e = e.parentElement) {
        rantai.push({tag: e.tagName, id: e.id, cls: (e.className && e.className.baseVal !== undefined
                     ? e.className.baseVal : String(e.className||'')).slice(0,120),
                     title: e.getAttribute('title'), aria: e.getAttribute('aria-label'),
                     icon: e.getAttribute('data-sap-ui-icon-content')});
      }
      return rantai;
    }""")
    for x in info: print("  ", x)
json.dump(info, open(OUT, "w"), indent=1)
