import time
from playwright.sync_api import sync_playwright
import sac

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    print("pages di context:", len(ctx.pages))
    for pg in ctx.pages:
        print("  page:", pg.url[:120])
    print("frames:")
    for f in page.frames:
        print("  -", (f.name or "(no-name)")[:30], "::", f.url[:130])
    print("iframe di DOM:", page.eval_on_selector_all("iframe", "els => els.map(e => e.src)"))
    print("global sap?", page.evaluate("() => typeof sap"))
    print("sap.fpa?", page.evaluate("() => typeof (window.sap && sap.fpa)"))
    print("keys window mirip sac:", page.evaluate(
        "() => Object.keys(window).filter(k => /fpa|sac|story|analytic/i.test(k)).slice(0,40)"))
