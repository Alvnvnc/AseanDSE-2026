"""Bangun halaman diagram alur h03 (Shapes + Text) langsung dari definisi.

Versi asli di `swalloy-story` bermasalah untuk dek:
  * seluruh isinya satu baris tipis (rasio 9:1) padahal slot dek 558x232bp (2,4:1),
    jadi gambarnya mengecil dan menyisakan ruang kosong besar;
  * "panah"-nya sebenarnya pictogram `<line>` yang menggambar garis di y=30,
    sementara widget-nya cuma 16 px tinggi -> garisnya tergunting dan tak terlihat.

Di sini kotak, panah, dan teks dibangun ulang dengan proporsi slot dek, panah SVG
sendiri (garis + kepala panah, ber-`viewBox` supaya ikut menyesuaikan kotaknya),
dan warna mengikuti palet dek.
"""
from __future__ import annotations
import json
import uuid

uid = lambda: str(uuid.uuid4())

# --- palet dek (lihat storyboard/gambar-sac/BACA-DULU.md) ---
BIRU = "#2A78D6"      # indeks iklim / kondisi normal
ABU = "#D5DADD"       # konteks (isian terang supaya teks gelap tetap terbaca)
MERAH = "#C53232"     # puncak / wabah
ORANYE = "#E8833A"    # alarm / aksi
GARIS = "#131E29"

ID_KOTAK = "alur-kotak-persegi"
ID_PANAH = "alur-panah-kanan"
ID_TEKS = "alur-teks"

SVG_KOTAK = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='100%' height='100%' "
    "viewBox='0 0 100 100' preserveAspectRatio='none'>"
    "<g class='infographic-pictogram shape' style='stroke-width:2'>"
    "<rect x='1' y='1' width='98' height='98' vector-effect='non-scaling-stroke' "
    "class='shape'></rect></g></svg>"
)

# garis + kepala panah; viewBox membuatnya ikut ukuran widget, tidak tergunting
SVG_PANAH = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='100%' height='100%' "
    "viewBox='0 0 60 20' preserveAspectRatio='none'>"
    "<g class='infographic-pictogram shape' style='stroke-width:3'>"
    "<line x1='0' y1='10' x2='48' y2='10' vector-effect='non-scaling-stroke' "
    "class='shape'></line>"
    "<polyline points='42,4 54,10 42,16' fill='none' vector-effect='non-scaling-stroke' "
    "class='shape'></polyline></g></svg>"
)

LANGKAH = [
    ("Climate index\n(ONI, monthly, public)", BIRU, "#FFFFFF"),
    ("3-4 month lag", ABU, GARIS),
    ("Dengue surge", MERAH, "#FFFFFF"),
    ("Action window:\nPSN/3M, larviciding,\nstockpiles", ORANYE, GARIS),
]


def entitas() -> list[dict]:
    """Entity pendukung: dua pictogram (kotak, panah) + satu entity teks."""
    return [
        {"type": "sap.lumira.story.entity.pictogram", "id": ID_KOTAK,
         "vendorId": "sap.lumira.story.entity.vendor.BasicPictogramVendor",
         "originatorId": "76",
         "data": {"originatorId": "76", "key": "76", "svg": SVG_KOTAK,
                  "initialStrokeWidth": 2, "excludedSettings": ["stroke width"],
                  "pictogramClass": "1"}},
        {"type": "sap.lumira.story.entity.pictogram", "id": ID_PANAH,
         "vendorId": "sap.lumira.story.entity.vendor.BasicPictogramVendor",
         "originatorId": "75",
         "data": {"originatorId": "75", "key": "75", "svg": SVG_PANAH,
                  "initialStrokeWidth": 3, "initialStrokeColor": GARIS,
                  "excludedSettings": ["fill color"], "pictogramClass": "1"}},
        {"type": "sap.lumira.story.entity.text", "id": ID_TEKS,
         "vendorId": "sap.epm.story.entity.text.TextWidgetVendor",
         "originatorId": "1", "data": {"text": "", "autoResize": False}},
    ]


def _kotak(isian: str, w: int, h: int) -> dict:
    return {
        "id": uid(), "class": "sap.lumira.story.entity.pictogram.PictogramShapeWidget",
        "definition": {
            "entityId": ID_KOTAK,
            "quickActionsSettings": {"visible": False, "settingsSeq": [], "commenting": False},
            "strokeWidth": 0, "fillColor": isian, "strokeColor": isian,
            "themeOverrideSettings": {
                "backgroundColor": "transparent",
                "border": {"format": "none", "style": "solid", "color": "transparent",
                           "thickness": 0, "radius": 0},
                "fillColor": isian, "strokeColor": isian, "strokeWidth": 0},
        },
        "themeClasses": [],
        "dimension": {"width": w, "height": h, "x": 0, "y": 0, "angle": 0,
                      "margin": {"disabled": False, "left": 0, "top": 0,
                                 "right": 0, "bottom": 0}},
        "serviceValidationHashes": {},
        "parentDimension": {"width": w, "height": h, "x": 0, "y": 0},
        "aCCDInfoForCopyPaste": [], "storeEntityType": "pictogramWidget",
    }


def _panah(w: int, h: int) -> dict:
    return {
        "id": uid(), "class": "sap.lumira.story.entity.pictogram.PictogramShapeWidget",
        "definition": {
            "entityId": ID_PANAH,
            "quickActionsSettings": {"visible": False, "settingsSeq": [], "commenting": False},
            "strokeWidth": 3, "strokeColor": GARIS,
        },
        "themeClasses": [],
        "dimension": {"width": w, "height": h, "x": 0, "y": 0, "angle": 0,
                      "margin": {"disabled": False, "left": 0, "top": 0,
                                 "right": 0, "bottom": 0}},
        "serviceValidationHashes": {},
        "parentDimension": {"width": w, "height": h, "x": 0, "y": 0},
        "aCCDInfoForCopyPaste": [], "storeEntityType": "pictogramWidget",
    }


def _teks(isi: str, warna: str, w: int, h: int, ukuran: int) -> dict:
    baris = "".join(
        f"<p style=\"text-align: center\"><span style=\"color: {warna}; "
        f"font-size: {ukuran}px; font-weight: bold\">{b}</span></p>"
        for b in isi.split("\n"))
    return {
        "id": uid(), "class": "sap.fpa.ui.story.entity.text.TextWidget",
        "definition": {
            "entityId": ID_TEKS, "text": baris, "autoResize": False,
            "defaultFont": {"color": warna, "font-family": "'72-Web'",
                            "isThemingDefault": False},
            "isPlaceholder": False, "placeholderMetatype": "",
            "dtExcludeFormatting": True, "dtMaxMembers": 10,
        },
        "themeClasses": [],
        "dimension": {"width": w, "height": h, "x": 0, "y": 0, "angle": 0,
                      "margin": {"disabled": False, "left": 0, "top": 0,
                                 "right": 0, "bottom": 0}},
        "serviceValidationHashes": {},
        "parentDimension": {"width": w, "height": h, "x": 0, "y": 0},
        "aCCDInfoForCopyPaste": [], "storeEntityType": "textWidget",
    }


def buat_halaman(judul: str = "h03-alur", lebar: int = 1400,
                 rasio_slot: float = 558 / 232) -> dict:
    """Empat kotak berurutan dengan panah di antaranya.

    Tinggi kotak dihitung supaya kotak pembatas seluruh isi berbanding sama
    dengan slot di dek (default 558x232 bp) — tanpa ini gambarnya mengambang
    di tengah slot dengan ruang kosong di atas-bawah.
    """
    tepi = 26
    tepi_atas = 30
    lebar_panah = 66
    n = len(LANGKAH)
    isi_lebar = lebar - 2 * tepi
    lebar_kotak = (isi_lebar - (n - 1) * lebar_panah) // n
    # kotak dibuat proporsional (bukan dipanjangkan mengikuti slot); sisa tinggi
    # diisi ruang putih supaya kotak pembatasnya tetap sebanding dengan slot dek
    tinggi_kotak = round(lebar_kotak * 1.05)
    tinggi = max(round(isi_lebar / rasio_slot), tinggi_kotak) + 2 * tepi_atas
    atas = (tinggi - tinggi_kotak) // 2

    widgets, seksi = [], []

    def tambah(w, x, y, lb, tg):
        widgets.append(w)
        seksi.append({
            "sectionId": uid(),
            "definition": {"x": x, "y": y, "width": lb, "height": tg, "title": "Section"},
            "widgets": [{"widgetId": w["id"],
                         "definition": {"removeable": True, "x": 0, "y": 0,
                                        "width": lb, "height": tg, "border": {}}}],
        })

    for i, (isi, isian, warna_teks) in enumerate(LANGKAH):
        x = tepi + i * (lebar_kotak + lebar_panah)
        tambah(_kotak(isian, lebar_kotak, tinggi_kotak), x, atas, lebar_kotak, tinggi_kotak)
        if i < n - 1:
            tinggi_panah = 40
            tambah(_panah(lebar_panah, tinggi_panah),
                   x + lebar_kotak, atas + (tinggi_kotak - tinggi_panah) // 2,
                   lebar_panah, tinggi_panah)

    # teks diletakkan di atas kotak (urutan belakangan = lapisan atas)
    for i, (isi, isian, warna_teks) in enumerate(LANGKAH):
        x = tepi + i * (lebar_kotak + lebar_panah)
        lb = lebar_kotak - 32
        baris = len(isi.split("\n"))
        tg = 52 * baris
        tambah(_teks(isi, warna_teks, lb, tg, 30),
               x + 16, atas + (tinggi_kotak - tg) // 2, lb, tg)

    layout = {"id": "boxlayout", "definition": {
        "type": "sap.lumira.story.layout.unified",
        "page": {"sections": seksi,
                 "definition": {"backgroundColor": "#FFFFFF", "type": "CANVAS",
                                "height": tinggi, "width": lebar}}}}
    return {
        "title": judul, "hidden": False,
        "definition": {"type": "CANVAS", "snapToGrid": True, "snapToObject": True,
                       "layoutId": "boxlayout", "fitPageToDevice": False,
                       "enableDevicePreview": False,
                       "devicePreviewSize": {"width": 0, "height": 0}},
        "id": uid(),
        "content": {"version": "1.0", "filters": [], "uqmPageFilters": [],
                    "uqmLAPageGroups": [], "uqmLAPageFilters": [],
                    "uqmScopedPageGroups": [], "uqmCascadeGroupings": [],
                    "uqmLAPageFilterFFQueries": {},
                    "widgets": widgets, "layouts": [layout]},
    }
