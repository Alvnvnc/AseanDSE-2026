"""Simpan JSON story apa adanya ke berkas (untuk dibandingkan sebelum/sesudah)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from playwright.sync_api import sync_playwright
import sac, sac_story

PETA = json.load(open(Path(__file__).resolve().parent.parent / "halaman.json"))
out = sys.argv[1]
with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    meta, isi = sac_story.baca(page, PETA["storyId"])
json.dump(isi, open(out, "w"), indent=1, sort_keys=True)
print("versi:", meta["metadata"]["version"], "->", out)
