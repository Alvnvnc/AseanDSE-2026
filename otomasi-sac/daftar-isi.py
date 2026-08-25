"""Daftar seluruh isi folder pribadi SAC: story, dataset (CUBE), dll."""
import json, sys, time
from playwright.sync_api import sync_playwright
import sac, api

OUT = sys.argv[1]
BODY = {"resourceId": "PRIVATE_SWALLOWGANK", "filter": [], "bIncTemporary": True, "detail": False,
        "allowAuthOverride": False,
        "options": {"metadata": {"epmObjectDataToFetch": {"CUBE": ["mode", "isRemote",
                                                                  "capability.simpleColumnNames"]},
                                 "fetchEpmObjectTypes": ["CUBE"], "fetchEpmObjectMetadata": False},
                    "fetchEnhancedProperties": ["SIMPLE_COLUMN_NAMES", "MODE", "IS_REMOTE",
                                                "DATA_ANALYZER_INFO", "STORY_OPTIMIZED_INFO",
                                                "DEFAULT_VIEW_MODE"],
                    "sort": {"key": "name", "descending": False},
                    "includeTotalResourceCount": True, "limit": 500, "offset": 0},
        "fetchAncestorNodes": True, "showContentSharedWithUser": True}

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "app.html" not in page.url:
        page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
                  timeout=120000); time.sleep(40)
    st, r = api.contentlib(page, "getRepoView", BODY)

json.dump(r, open(OUT, "w"), indent=1)
print("status", st, "->", OUT)


def jelajah(o, jalur=""):
    if isinstance(o, dict):
        if "resourceType" in o and "name" in o:
            yield (o.get("resourceType"), o.get("name"), o.get("resourceId") or o.get("id"))
        for k, v in o.items():
            yield from jelajah(v, jalur + "/" + k)
    elif isinstance(o, list):
        for v in o:
            yield from jelajah(v, jalur)


baris = list(jelajah(r))
tipe = {}
for t, n, i in baris:
    tipe.setdefault(t, []).append((n, i))
for t, v in sorted(tipe.items()):
    print(f"\n### {t} ({len(v)})")
    for n, i in sorted(v):
        print(f"   {n[:60]:62s} {str(i)[:60]}")
