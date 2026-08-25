"""Daftar URL skrip yang dimuat SAC (untuk digrep di luar browser)."""
import json, sys, time
from playwright.sync_api import sync_playwright
import sac

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    urls = page.evaluate("""() => performance.getEntriesByType('resource')
        .filter(e => /\\.js(\\?|$)/.test(e.name))
        .map(e => [e.name, Math.round(e.transferSize||0)])""")
urls.sort(key=lambda x: -x[1])
for u, s in urls[:40]:
    print(f"{s:9d}  {u[:150]}")
print("total js:", len(urls))
json.dump([u for u, _ in urls], open(sys.argv[1], "w"), indent=1)
