"""Rekam XHR lewat CDP (termasuk worker) saat story dimuat."""
import json, sys, time
from collections import Counter
from playwright.sync_api import sync_playwright
import sac

OUT = sys.argv[1]
req = {}

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    cdp = ctx.new_cdp_session(page)
    cdp.send("Network.enable")
    cdp.send("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": False,
                                      "flatten": True})

    def on_send(e):
        r = e["request"]
        if True:
            req[e["requestId"]] = {"m": r["method"], "u": r["url"], "type": e.get("type"),
                                   "body": (r.get("postData") or "")[:1500]}

    def on_resp(e):
        if e["requestId"] in req:
            req[e["requestId"]]["status"] = e["response"]["status"]

    cdp.on("Network.requestWillBeSent", on_send)
    cdp.on("Network.responseReceived", on_resp)

    page.goto("about:blank")
    time.sleep(1)
    page.goto(sac.STORY_URL, wait_until="domcontentloaded", timeout=120000)
    time.sleep(60)
    print("workers:", [w.url[:80] for w in page.workers])

data = list(req.values())
json.dump(data, open(OUT, "w"), indent=1)
c = Counter(d["m"] + " " + d["u"].split("?")[0].replace(sac.TENANT, "") for d in data
            if "sapanalytics.cloud" not in d["u"])
for k, v in c.most_common(50):
    print(f"{v:3d}  {k[:160]}")
print("total:", len(data), "->", OUT)
