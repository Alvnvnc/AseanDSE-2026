"""Buka tiap halaman story di mode view, tangkap elemen grafiknya jadi PNG.

Hasil disimpan ke `storyboard/gambar-sac/<nama-berkas>.png` dengan nama persis
seperti yang ditunggu `storyboard.tex`.
"""
import base64, json, subprocess, sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from pathlib import Path
from playwright.sync_api import sync_playwright
import sac

PETA = json.load(open("/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/halaman.json"))
KELUAR = Path("/home/alvn/Documents/Riset/AseanDSE-2026/storyboard/gambar-sac")
SKALA_MIN = 2          # perbesaran minimum
LEBAR_TARGET = 1750    # lebar PNG yang dituju (syarat panitia >= 1600 px)
TUNGGU = 45
hanya = sys.argv[1:] or None

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    cdp = ctx.new_cdp_session(page)
    def pasang_viewport(h):
        """SAC hanya menggambar bagian yang terlihat -> viewport harus memuat
        seluruh kanvas halaman, kalau tidak separuh grafik keluar kosong."""
        lebar = max(1280, int(h.get("lebar", 1500)) + 140)
        tinggi = max(900, int(h.get("tinggi", 850)) + 220)
        cdp.send("Emulation.setDeviceMetricsOverride",
                 {"width": lebar, "height": tinggi, "deviceScaleFactor": 1,
                  "mobile": False})

    def skala_untuk(kotak):
        """Slot dek yang sempit butuh perbesaran lebih supaya tetap >= 1600 px."""
        if not kotak:
            return SKALA_MIN
        return max(SKALA_MIN, min(4, -(-LEBAR_TARGET // int(kotak["w"]))))

    def potret(berkas, kotak, skala):
        """Tangkap lewat CDP: hanya di sini parameter `scale` benar-benar dipakai.
        page.screenshot() milik Playwright mengabaikan deviceScaleFactor CDP."""
        param = {"format": "png", "captureBeyondViewport": True}
        if kotak:
            param["clip"] = {"x": kotak["x"], "y": kotak["y"], "width": kotak["w"],
                             "height": kotak["h"], "scale": skala}
        hasil = cdp.send("Page.captureScreenshot", param)
        Path(berkas).write_bytes(base64.b64decode(hasil["data"]))

    for h in PETA["halaman"]:
        if hanya and h["berkas"] not in hanya:
            continue
        pasang_viewport(h)
        url = (f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{PETA['storyId']}"
               f"/?pageId={h['pageId']}&mode=view")
        page.goto("about:blank"); time.sleep(1)
        page.goto(url, wait_until="domcontentloaded", timeout=120000)
        time.sleep(TUNGGU)

        # gabungkan kotak semua widget di halaman (h03-alur terdiri dari banyak bentuk)
        kotak = page.evaluate("""(ids) => {
            let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9, ketemu = false;
            for (const wid of ids) {
              const cari = [...document.querySelectorAll('[id],[data-widget-id]')]
                .filter(e => (e.id && e.id.includes(wid)) ||
                             e.getAttribute('data-widget-id') === wid);
              let best = null;
              for (const e of cari) {
                const r = e.getBoundingClientRect();
                if (r.width > 20 && r.height > 12 &&
                    (!best || r.width * r.height > best.width * best.height)) best = r;
              }
              if (best) {
                ketemu = true;
                x0 = Math.min(x0, best.x); y0 = Math.min(y0, best.y);
                x1 = Math.max(x1, best.x + best.width); y1 = Math.max(y1, best.y + best.height);
              }
            }
            if (!ketemu) return null;
            const m = 12;   // sedikit ruang tepi
            return {x: Math.max(0, x0 - m), y: Math.max(0, y0 - m),
                    w: (x1 - x0) + 2 * m, h: (y1 - y0) + 2 * m};
        }""", h.get("widgetIds") or [h["widgetId"]])

        # samakan dengan rasio slot dek: ruang putih ditambahkan seimbang,
        # gambarnya sendiri tidak diregangkan
        if kotak and h.get("rasio"):
            target = float(h["rasio"])
            sekarang = kotak["w"] / kotak["h"]
            if sekarang > target:                     # terlalu lebar -> tambah tinggi
                baru_h = kotak["w"] / target
                kotak["y"] -= (baru_h - kotak["h"]) / 2
                kotak["h"] = baru_h
            elif sekarang < target:                   # terlalu tinggi -> tambah lebar
                baru_w = kotak["h"] * target
                kotak["x"] -= (baru_w - kotak["w"]) / 2
                kotak["w"] = baru_w
            kotak["x"] = max(0, kotak["x"])
            kotak["y"] = max(0, kotak["y"])

        tujuan = KELUAR / f"{h['berkas']}.png"
        # grafik padat (ratusan titik) kadang butuh lebih dari 30 detik default
        for percobaan in (1, 2):
            try:
                skala = skala_untuk(kotak)
                potret(tujuan, kotak, skala)
                info = (f"{int(kotak['w']*skala)}x{int(kotak['h']*skala)}px @{skala}x" if kotak
                        else "SELURUH LAYAR (elemen widget tidak ketemu)")
                break
            except Exception as e:
                if percobaan == 2:
                    print(f"  {h['berkas']:24s} GAGAL: {str(e)[:90]}")
                    info = None
                    break
                time.sleep(20)
        if info is None:
            continue
        # tabel memakai sebagian kecil kanvas; sisanya putih -> dipangkas
        if h.get("tipe") == "tabel":
            subprocess.run(["magick", str(tujuan), "-bordercolor", "white",
                            "-border", "24", "-trim", "+repage", str(tujuan)],
                           check=False)
            info = subprocess.run(["magick", "identify", "-format", "%wx%h",
                                   str(tujuan)], capture_output=True,
                                  text=True).stdout + "px (dipangkas)"

        kb = tujuan.stat().st_size // 1024
        print(f"  {h['berkas']:24s} {info:34s} {kb} KB")
