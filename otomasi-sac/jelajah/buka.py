import sys, time
from playwright.sync_api import sync_playwright
import sac

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/sac.png"
with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.set_viewport_size({"width": 1900, "height": 1050})
    page.goto(sac.STORY_URL, wait_until="domcontentloaded", timeout=120000)
    for i in range(12):
        time.sleep(5)
        try:
            t = page.title(); u = page.url
        except Exception as e:
            print("target hilang:", e); break
        print(f"[{5*(i+1):3d}s] {t[:60]!r} :: {u[:100]}")
        try:
            page.screenshot(path=OUT)
        except Exception:
            pass
    print("selesai ->", OUT)
