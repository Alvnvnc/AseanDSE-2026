"""Sorotan warna per anggota dimensi (SAC menyebutnya *Assign Colours*).

Palet biasa memberi warna berurutan: anggota ke-1 dapat warna ke-1, dan
seterusnya. Untuk menyorot satu anggota tertentu — Indonesia di antara sepuluh
negara ASEAN — warnanya harus dipatok ke nama anggotanya.

SAC menyimpannya di **tingkat story**, bukan di widget: `story.data.colorSync`,
berkunci ganda (dataset, lalu dataset+dimensi):

    colorSync = {
      "version": "1.0.0",
      '[{"datasetId":"<ds>"}]': {
        '[{"datasetId":"<ds>"},{"dimensionId":"country"}]': {
           "colors": [...12 warna palet...],
           "explicitColorAssignments":       {"Indonesia": "#e8833a"},
           "explicitColorSwatchAssignments": {"Indonesia": ""},
           "id": "<id standardPalette>",
           "mappingPaletteId": "sapColorfulPalette",
           "preferredMappingPaletteId": "sapColorfulPalette"
        }
      }
    }

Karena berkunci dataset+dimensi, satu penetapan berlaku untuk **semua** grafik
yang memakai dataset dan dimensi itu — itulah gunanya nama "colour sync".

Syarat dari SAC sendiri (pesan `ASSIGNED_COLORS_DISABLED`): tidak berlaku kalau
"Unsync Colours" dipasang, kalau grafiknya punya lebih dari satu measure, atau
kalau feed Colour berisi lebih dari satu dimensi. Dan yang terpenting:
**dimensinya harus ada di feed `color`** — kalau cuma di `categoryAxis`,
penetapan ini tidak dipakai.

Di UI: chip dimensi pada bagian Colour -> **•••** -> **Colour Sync** ->
**Assign Colours...**
"""
from __future__ import annotations
import json

jdump = lambda o: json.dumps(o, separators=(",", ":"))


def terapkan(isi: dict, daftar: list[dict]) -> list[str]:
    """`daftar`: [{"cube": ..., "dimensi": ..., "warna": {anggota: "#rrggbb"}}, ...]

    -> daftar keterangan yang bisa dicetak.
    """
    from generator import ds_id
    import palet

    data = isi["entities"][0]["data"]
    aktif = (data.get("namedColorStates") or {}).get("defaultPalettes") or {}
    std = aktif.get("standardPalette") or {}
    palet_id = std.get("id")
    palet_map = std.get("mappingPaletteId", "sapColorfulPalette")

    # Ditulis ulang dari nol supaya hasil bangun selalu sama — sisa percobaan
    # lewat UI tidak ikut terbawa.
    versi = (data.get("colorSync") or {}).get("version", "1.0.0")
    cs = {"version": versi}
    data["colorSync"] = cs
    catatan = []

    for s in daftar:
        ds = ds_id(s["cube"])
        kunci_ds = jdump([{"datasetId": ds}])
        kunci_dim = jdump([{"datasetId": ds}, {"dimensionId": s["dimensi"]}])
        cs.setdefault(kunci_ds, {})[kunci_dim] = {
            "colors": list(palet.DERET),
            # SAC menuliskan warnanya huruf kecil; ditiru supaya tidak ada
            # selisih semu saat membandingkan JSON sebelum/sesudah.
            "explicitColorAssignments": {k: v.lower() for k, v in s["warna"].items()},
            "explicitColorSwatchAssignments": {k: "" for k in s["warna"]},
            "id": palet_id,
            "mappingPaletteId": palet_map,
            "preferredMappingPaletteId": palet_map,
        }
        catatan.append(f"{s['dimensi']} ({len(s['warna'])} anggota)")
    return catatan
