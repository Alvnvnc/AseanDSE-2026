import json, sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac, sac_story

SID = "8D68C286FA86EB3FB3B3D419CC1A8B38"
SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "app.html" not in page.url:
        page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
                  timeout=120000); time.sleep(40)
    meta, isi = sac_story.baca(page, SID)
    hal = [p_ for p_ in isi["entities"][0]["data"]["pages"] if p_["title"] == "UJI-generator"][0]
    pid = hal["id"]
    print("pageId:", pid, "| widget:", len(hal["content"]["widgets"]))
    url = f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{SID}/?pageId={pid}&mode=view"
    page.goto("about:blank"); time.sleep(1)
    page.goto(url, wait_until="domcontentloaded", timeout=120000)
    time.sleep(70)
    page.screenshot(path=f"{SHOT}/pageid-view.png")
    print("->", f"{SHOT}/pageid-view.png")
