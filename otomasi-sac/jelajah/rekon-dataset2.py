"""Ambil metadata satu DATASET: id cube + daftar dimensi/measure."""
import json, time
from playwright.sync_api import sync_playwright
import sac, api

DS = "DB086A86FA81B79A35CEF734CAE2FD4B"  # Monthly series IDN-THA

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "app.html" not in page.url:
        page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
                  timeout=120000); time.sleep(40)
    st, r = api.contentlib(page, "getContent", {"resourceType": "DATASET", "resourceId": DS})
    print("getContent DATASET:", st)
    json.dump(r, open("/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/ds.json", "w"), indent=1)
    cd = r.get("cdata") or {}
    print("cdata keys:", list(cd.keys()))
    for k, v in cd.items():
        if k != "datasources":
            print(f"  {k:26s} {json.dumps(v)[:160]}")
    print("subObjects:", json.dumps(r.get("subObjects"))[:600])
    print("objectId:", r.get("objectId"))
    kolom = cd.get("datasources", [{}])[0].get("columns", [])
    print("kolom:", [(c.get("columnName"), c.get("dataTypeName")) for c in kolom])
