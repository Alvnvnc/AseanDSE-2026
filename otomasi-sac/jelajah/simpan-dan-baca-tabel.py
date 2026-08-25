"""Ctrl+S di editor, lalu baca definisi widget Table yang baru disisipkan."""
import json, sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac, sac_story

SID = sys.argv[1]
with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.keyboard.press("Escape"); time.sleep(1)
    page.keyboard.press("Control+s")
    time.sleep(35)
    meta, isi = sac_story.baca(page, SID)

tabel = None
for hal in isi["entities"][0]["data"]["pages"]:
    for w in hal["content"]["widgets"]:
        if isinstance(w, dict) and "table" in str(w.get("class", "")).lower():
            tabel = w
            print("ditemukan di halaman:", hal["title"], "| class:", w["class"])
            break
    if tabel: break

if tabel is None:
    print("belum ada widget Table di story")
else:
    json.dump(tabel, open("/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/templat-tabel.json", "w"), indent=1)
    print("ukuran definisi:", len(json.dumps(tabel)))
    print("kunci definition:", list(tabel["definition"].keys()))
