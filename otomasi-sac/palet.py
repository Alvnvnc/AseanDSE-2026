"""Terapkan palet warna dek ke seluruh grafik dalam story.

SAC memilih warna seri dari palet yang ditunjuk
`story.data.namedColorStates.defaultPalettes`, dan definisi paletnya ada di
`storyWideSettings["theme.color.palettes"]`. Dengan menimpa isi palet yang
sedang ditunjuk, semua grafik ikut berubah sekaligus — tanpa perlu menyetel
warna per widget.

Palet dek (lihat `storyboard/gambar-sac/BACA-DULU.md`):
    #2A78D6 kasus / kondisi normal      #E8833A alarm / El Nino
    #C53232 puncak / wabah              #8A8F98 konteks, garis ambang
"""
from __future__ import annotations

BIRU, ORANYE, MERAH, ABU = "#2A78D6", "#E8833A", "#C53232", "#8A8F98"

# Empat warna dek dulu, lalu turunannya untuk seri ke-5 dan seterusnya.
DERET = [BIRU, ORANYE, MERAH, ABU,
         "#1B5E9E", "#B35C1E", "#8E2020", "#5F646B",
         "#6BA6E8", "#F2B075", "#DB7B7B", "#B9BDC2"]

# Heat map memakai palet gradasi. Naskah meminta sekuensial putih -> merah untuk
# kalender risiko (h08, h10): nilai rendah nyaris putih sehingga puncaknya
# menonjol. Heat map korelasi (h06, h07) ikut membacanya sebagai intensitas.
# Perhatikan: kunci "0" memetakan nilai TERTINGGI dan "100" nilai terendah
# (terbalik dari dugaan), jadi merah ada di "0".
PUTIH_HANGAT = "#FDF3EF"
GRADASI = {"0": MERAH, "100": PUTIH_HANGAT}


def terapkan(isi: dict) -> list[str]:
    """Timpa palet yang sedang aktif. -> daftar palet yang diubah."""
    data = isi["entities"][0]["data"]
    palet = data.get("storyWideSettings", {}).get("theme.color.palettes") or []
    aktif = (data.get("namedColorStates") or {}).get("defaultPalettes") or {}
    peta = {p.get("id"): p for p in palet}
    diubah = []

    ref = aktif.get("standardPalette", {}).get("id")
    p = peta.get(ref)
    if p and isinstance(p.get("colors"), list):
        n = len(p["colors"])
        p["colors"] = [DERET[i % len(DERET)] for i in range(n)]
        diubah.append("standardPalette")

    ref = aktif.get("gradientPalette", {}).get("id")
    p = peta.get(ref)
    if p and isinstance(p.get("gradient"), dict):
        p["gradient"] = dict(GRADASI)
        diubah.append("gradientPalette")

    # bar bertingkat/waterfall memakai palet sendiri
    ref = aktif.get("waterfallStandardPalette", {}).get("id")
    p = peta.get(ref)
    if p and isinstance(p.get("colors"), list):
        n = len(p["colors"])
        p["colors"] = [DERET[i % len(DERET)] for i in range(n)]
        diubah.append("waterfallStandardPalette")

    return diubah
