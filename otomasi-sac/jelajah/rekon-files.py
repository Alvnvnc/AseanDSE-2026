"""Buka layar Files (read-only) sambil merekam XHR -> dapat aksi daftar & daftar dataset."""
import json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
import sac

SINI = Path(__file__).resolve().parent
HOOK = (SINI / "hook.js").read_text()
SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
OUT = sys.argv[1]

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.add_init_script(HOOK)
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded", timeout=120000)
    time.sleep(45)
    page.screenshot(path=f"{SHOT}/files.png")
    log = page.evaluate("() => window.__log || []")

json.dump(log, open(OUT, "w"), indent=1)
for d in log:
    u = d.get("u", "")
    if any(k in u for k in ("contentlib", "objectmgr", "epm/")) and d.get("m") == "POST":
        body = d.get("body") or ""
        try:
            aksi = json.loads(body).get("action")
        except Exception:
            aksi = "?"
        print(f"{str(d.get('status')):4s} len={str(d.get('len')):8s} action={aksi!r:28s} {u.split('?')[0][-40:]}")
print("total:", len(log), "->", OUT)
