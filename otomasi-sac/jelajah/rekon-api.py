"""Rekam semua XHR saat story dimuat -> tahu endpoint internal SAC."""
import json, time, sys
from collections import Counter
from playwright.sync_api import sync_playwright
import sac

OUT = sys.argv[1]
catatan = []

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)

    def on_req(req):
        if req.resource_type in ("xhr", "fetch"):
            d = {"m": req.method, "u": req.url, "t": req.resource_type}
            try:
                pd = req.post_data
                if pd:
                    d["body"] = pd[:2000]
            except Exception:
                pass
            catatan.append(d)

    page.on("request", on_req)
    page.goto(sac.STORY_URL, wait_until="domcontentloaded", timeout=120000)
    time.sleep(45)
    page.reload(wait_until="domcontentloaded", timeout=120000)
    time.sleep(45)

json.dump(catatan, open(OUT, "w"), indent=1)
paths = Counter(c["m"] + " " + c["u"].split("?")[0].replace(sac.TENANT, "") for c in catatan)
for k, v in paths.most_common(60):
    print(f"{v:3d}  {k[:150]}")
print("total:", len(catatan), "->", OUT)
