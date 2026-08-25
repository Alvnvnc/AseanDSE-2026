"""Sisipkan properti percobaan ke vizDefinition satu halaman, lalu simpan.

  uji-skala.py <berkas-halaman> '<json-tambalan-properties>'

Tambalan digabung secara rekursif ke `vizDefinition.properties`.
Nilai `null` menghapus kunci.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from playwright.sync_api import sync_playwright
import sac, sac_story

PETA = json.load(open(Path(__file__).resolve().parent.parent / "halaman.json"))
berkas, tambalan = sys.argv[1], json.loads(sys.argv[2])


def gabung(dst, src):
    for k, v in src.items():
        if v is None:
            dst.pop(k, None)
        elif isinstance(v, dict) and isinstance(dst.get(k), dict):
            gabung(dst[k], v)
        else:
            dst[k] = v


with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    meta, isi = sac_story.baca(page, PETA["storyId"])
    hal = [x for x in isi["entities"][0]["data"]["pages"] if x["title"] == berkas][0]
    n = 0
    for w in hal["content"]["widgets"]:
        vd = w.get("definition", {}).get("vizDefinition")
        if not vd:
            continue
        gabung(vd.setdefault("properties", {}), tambalan)
        n += 1
    print("widget ditambal:", n)
    st, r = sac_story.tulis(page, meta, isi, local_ver=meta["metadata"]["version"])
    print("simpan:", st, str(r)[:200])
