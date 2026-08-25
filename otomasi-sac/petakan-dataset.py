"""Petakan seluruh DATASET di SAC: id cube, kolom, mana dimensi mana measure."""
import json, sys, time
from playwright.sync_api import sync_playwright
import sac, api

OUT = sys.argv[1]

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "app.html" not in page.url:
        page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
                  timeout=120000); time.sleep(40)

    st, repo = api.contentlib(page, "getRepoView", {
        "resourceId": "PRIVATE_SWALLOWGANK", "filter": [], "bIncTemporary": True, "detail": False,
        "allowAuthOverride": False,
        "options": {"sort": {"key": "name", "descending": False},
                    "includeTotalResourceCount": True, "limit": 500, "offset": 0},
        "fetchAncestorNodes": True, "showContentSharedWithUser": True})

    def jelajah(o):
        if isinstance(o, dict):
            if o.get("resourceType") == "DATASET" and o.get("name"):
                yield o["name"], o.get("resourceId")
            for v in o.values():
                yield from jelajah(v)
        elif isinstance(o, list):
            for v in o:
                yield from jelajah(v)

    ds = sorted(set(jelajah(repo)))
    print("dataset ditemukan:", len(ds))

    hasil = {}
    for nama, rid in ds:
        st, r = api.contentlib(page, "getContent", {"resourceType": "DATASET", "resourceId": rid})
        if st != 200:
            print(f"  ! {nama}: {st}"); continue
        cd = r["cdata"]
        olap = cd.get("olapMetadata") or {}
        hasil[nama] = {
            "resourceId": rid,
            "cube": (cd.get("cube") or {}).get("name"),
            # dibutuhkan widget Table pada content.dataSource
            "relationName": cd.get("relationName"),
            "relationSchema": cd.get("relationSchema"),
            "datasetId": cd.get("datasetId"),
            "kolom": [{"nama": c.get("name"), "tipe": c.get("dataType"),
                       "storage": c.get("storageType")} for c in (cd.get("columns") or [])],
            "olap_dimensi": [d.get("dimensionId") for d in (olap.get("dimensions") or [])],
            "olap_measure": [m.get("columnName") for m in (olap.get("measures") or [])],
            "agregasi": {m.get("columnName"): m.get("aggregationType")
                         for m in (olap.get("measures") or [])},
            "olap_keys": list(olap.keys()),
        }
        print(f"  {nama[:34]:36s} cube={hasil[nama]['cube']}  "
              f"dim={len(hasil[nama]['olap_dimensi'])} meas={len(hasil[nama]['olap_measure'])}")

json.dump(hasil, open(OUT, "w"), indent=1)
print("->", OUT)
