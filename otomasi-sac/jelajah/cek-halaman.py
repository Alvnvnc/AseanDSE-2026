import json, sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac, sac_story

SID = sys.argv[1]
with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "app.html" not in page.url:
        page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
                  timeout=120000); time.sleep(40)
    meta, isi = sac_story.baca(page, SID)
d = isi["entities"][0]["data"]
print("pages:", [p_["title"] for p_ in d["pages"]])
for k in ("presentationModel", "topics", "queryDefinitions", "storyWideSettings"):
    v = d.get(k)
    print(f"{k:22s} {type(v).__name__} {json.dumps(v)[:260]}")
