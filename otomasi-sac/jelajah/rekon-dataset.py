"""Coba beberapa aksi baca-saja untuk mendaftar dataset (CUBE) di tenant."""
import json, time
from playwright.sync_api import sync_playwright
import sac, api

AKSI = [
    ("getResources", {"resourceType": "CUBE", "metadata": {"name": True, "resourceType": True,
                                                           "modifiedTime": True}}),
    ("getResourceList", {"resourceType": "CUBE"}),
    ("listResources", {"resourceType": "CUBE"}),
    ("search", {"resourceType": "CUBE", "searchText": ""}),
    ("getChildren", {"resourceType": "CUBE"}),
]

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "story2" not in page.url:
        page.goto(sac.STORY_URL, wait_until="domcontentloaded", timeout=120000); time.sleep(45)
    print("hook aktif? __log =", page.evaluate("() => (window.__log||[]).length"))
    for aksi, data in AKSI:
        st, r = api.contentlib(page, aksi, data)
        teks = json.dumps(r)[:220] if not isinstance(r, str) else r[:220]
        print(f"--- {aksi:18s} status={st} {teks}")
