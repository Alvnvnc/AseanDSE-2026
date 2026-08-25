"""Ubah sedikit lalu Ctrl+S di story SALINAN, rekam payload updateContent asli."""
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
    page.keyboard.press("Escape"); time.sleep(1)
    # geser widget sedikit supaya story jadi "dirty"
    page.mouse.click(900, 600); time.sleep(2)
    for _ in range(3):
        page.keyboard.press("ArrowRight"); time.sleep(0.4)
    time.sleep(2)
    page.screenshot(path=f"{SHOT}/sebelum-ctrls.png")
    n0 = page.evaluate("() => (window.__log||[]).length")
    page.keyboard.press("Control+s")
    time.sleep(30)
    page.screenshot(path=f"{SHOT}/setelah-ctrls.png")
    log = page.evaluate("(n) => (window.__log||[]).slice(n)", n0)

json.dump(log, open(OUT, "w"), indent=1)
print("panggilan setelah Ctrl+S:", len(log))
for d in log:
    u = d.get("u", "")
    if "contentlib" in u or "objectmgr" in u:
        try:
            aksi = json.loads(d["body"]).get("action")
        except Exception:
            aksi = "?"
        print(f"  status={d.get('status')} action={aksi!r} bodylen={len(d.get('body') or '')} resp={str(d.get('resp'))[:150]}")
