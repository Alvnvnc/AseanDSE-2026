"""Utilitas bersama: sambung ke Edge ber-CDP dan buka story SAC."""
from __future__ import annotations
import time
from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"
TENANT = "https://aseandse.ap11.hcs.cloud.sap"
STORY_ID = "1B584A86FA86219FFA6406E73D4A5C3C"
STORY_URL = f"{TENANT}/sap/fpa/ui/app.html#/story2&/s2/{STORY_ID}/?mode=edit"


def sambung(p):
    b = p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    return b, ctx, page


def tunggu_diam(page, detik=30, jeda=2.0):
    """Tunggu sampai jumlah request mereda (SAC lambat memuat)."""
    batas = time.time() + detik
    while time.time() < batas:
        time.sleep(jeda)
        try:
            siap = page.evaluate("() => document.readyState")
        except Exception:
            siap = "?"
        if siap == "complete":
            time.sleep(3)
            return True
    return False
