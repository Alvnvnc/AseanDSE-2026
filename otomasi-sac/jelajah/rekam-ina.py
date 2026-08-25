"""Buka halaman uji dengan hook, rekam permintaan/ jawaban InA GetResponse."""
import json, sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from pathlib import Path
from playwright.sync_api import sync_playwright
import sac, sac_story

SID = "8D68C286FA86EB3FB3B3D419CC1A8B38"
HOOK = Path("/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/hook.js").read_text()

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "app.html" not in page.url:
        page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
                  timeout=120000); time.sleep(40)
    meta, isi = sac_story.baca(page, SID)
    pid = [x for x in isi["entities"][0]["data"]["pages"] if x["title"] == "UJI-generator"][0]["id"]

    page.add_init_script(HOOK)
    galat = []
    page.on("console", lambda m: galat.append(m.text[:400]) if m.type == "error" else None)
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{SID}/?pageId={pid}&mode=view",
              wait_until="domcontentloaded", timeout=120000)
    time.sleep(70)
    log = page.evaluate("() => window.__log || []")

ina = [d for d in log if "GetResponse" in d.get("u", "")]
print("GetResponse:", len(ina))
for d in ina:
    resp = d.get("resp") or ""
    print("="*90)
    print("status", d.get("status"), "len", d.get("len"))
    if any(k in resp for k in ('"Messages"', '"error"', 'ERROR', 'Exception')):
        print("RESP:", resp[:2500])
    else:
        print("RESP(awal):", resp[:400])
print("\n--- console error ---")
for g in galat[:12]: print(" *", g[:300])
