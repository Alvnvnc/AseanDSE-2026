"""Bangun story SAC berisi satu grafik per halaman, dari resep di resep.py.

Story dibuat sebagai SALINAN `swalloy-story` (supaya tema & template grafik ikut),
lalu seluruh halaman lama dibuang dan diganti halaman hasil generator.
`swalloy-story` sendiri tidak disentuh.
"""
import json, sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/storyboard")
import sac, sac_story, generator as G, resep, api
import alur as alur_mod
import palet
import sorot
import tabel as tabel_mod

# Halaman di sini tidak dibangun ulang — melindungi suntingan manual di SAC.
# Sejauh ini tidak terpakai: semua yang dibutuhkan sudah bisa lewat API.
JANGAN_BANGUN_ULANG: set[str] = set()
from panduan_sac import baca_slot

# Slot di dek berorientasi potret; kalau halaman SAC dibiarkan 16:9, grafiknya
# mengecil dan menyisakan ruang kosong. Ukuran halaman disamakan rasionya.
SLOT = {s["nama"]: (s["lebar"], s["tinggi"]) for s in baca_slot()}


def ukuran_halaman(berkas, sisi_panjang=1400):
    """Rasio halaman mengikuti slot dek, tapi dibatasi: kalau terlalu tinggi,
    SAC hanya menggambar grafik di bagian atas dan label sumbunya hilang."""
    lebar_bp, tinggi_bp = SLOT.get(berkas, (16, 9))
    rasio = max(1.0, min(3.0, lebar_bp / tinggi_bp))
    return sisi_panjang, max(300, round(sisi_panjang / rasio))

NAMA = "swalloy-grafik"
DS = json.load(open("/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/dataset-sac.json"))
PETA = "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/halaman.json"


def cari_story(page, nama):
    st, repo = api.contentlib(page, "getRepoView", {
        "resourceId": "PRIVATE_SWALLOWGANK", "filter": [], "bIncTemporary": True,
        "detail": False, "allowAuthOverride": False,
        "options": {"sort": {"key": "name", "descending": False},
                    "includeTotalResourceCount": True, "limit": 500, "offset": 0},
        "fetchAncestorNodes": True, "showContentSharedWithUser": True})

    def jelajah(o):
        if isinstance(o, dict):
            if o.get("resourceType") == "STORY" and o.get("name") == nama:
                yield o.get("resourceId")
            for v in o.values():
                yield from jelajah(v)
        elif isinstance(o, list):
            for v in o:
                yield from jelajah(v)
    for r in jelajah(repo):
        return r
    return None


with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "app.html" not in page.url:
        page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
                  timeout=120000); time.sleep(40)

    sid = cari_story(page, NAMA)
    if sid:
        print("pakai story yang sudah ada:", sid)
    else:
        st, r = api.contentlib(page, "copyResource", {
            "resourceIds": [sac.STORY_ID], "targetParentResId": "PRIVATE_SWALLOWGANK",
            "options": {"mode": "2", "details": {sac.STORY_ID: {
                "name": NAMA, "description": "23 grafik SAC untuk dek ASEAN DSE - dibangun otomatis"}}}})
        sid = r["resourceMappings"][sac.STORY_ID]["targetResourceId"]
        print("story baru dibuat:", sid)

    meta, isi = sac_story.baca(page, sid)
    ents = isi["entities"]
    story = ents[0]["data"]

    # template grafik: widget viz pertama yang ketemu di halaman mana pun
    TPL_TABEL = "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/templat-tabel.json"
    TPL_TABEL_ENT = "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/templat-tabel-entity.json"

    templat = None
    for hal in story["pages"]:
        for w in hal["content"]["widgets"]:
            if isinstance(w, dict) and w.get("class") == "sap.lumira.story.viz.VizWidget":
                templat = w; break
        if templat: break
    if templat is None:
        templat = json.load(open("/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/templat-widget.json"))
    else:
        json.dump(templat, open("/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/templat-widget.json", "w"))

    # Halaman yang disunting manual di SAC: dipertahankan apa adanya, tidak
    # dibangun ulang. Isi dengan nama berkas, mis. {"h06-scatter-suhu"}.
    disimpan = {h["title"]: h for h in story["pages"]
                if h.get("title") in JANGAN_BANGUN_ULANG}
    if disimpan:
        print("  = dipertahankan apa adanya:", ", ".join(sorted(disimpan)))

    # Diagram alur h03 dibangun ulang dengan proporsi slot dek (lihat alur.py).
    if "h03-alur" in disimpan:
        alur, entitas_alur = disimpan.pop("h03-alur"), []
    else:
        lebar_bp, tinggi_bp = SLOT.get("h03-alur", (558, 232))
        alur = alur_mod.buat_halaman("h03-alur", 1400, lebar_bp / tinggi_bp)
        entitas_alur = alur_mod.entitas()

    # bersihkan: halaman, filter story, entity dataset/viz lama
    story["pages"] = []
    for k in ("storyFilters", "uqmStoryFilters", "uqmFieldSelectionFilters", "uqmStoryLAFilters"):
        if isinstance(story.get(k), list):
            story[k] = []
    app = G._entity_app(ents)
    app["appPages"] = []
    app.setdefault("app", {})["names"] = {
        k: v for k, v in app.get("app", {}).get("names", {}).items()
        if '"appPage"' not in k and '"viz2"' not in k}
    sisa = [e for e in ents if e.get("type") not in ("dataset", "datasetAlias",
                                                     "visualization.viz")]
    ents[:] = sisa

    cube_ada = set()
    dibangun = []

    if alur is not None:
        ada = {e.get("id") for e in ents}
        for e in entitas_alur:
            if e.get("id") not in ada:
                ents.append(e)
        story["pages"].append(alur)
        G.daftarkan_halaman(ents, alur["id"], "h03-alur", [])
        dibangun.append({"berkas": "h03-alur", "pageId": alur["id"],
                         "widgetId": alur["content"]["widgets"][0]["id"],
                         "widgetIds": [x["id"] for x in alur["content"]["widgets"]],
                         "lebar": alur["content"]["layouts"][0]["definition"]["page"]
                                      ["definition"]["width"],
                         "tinggi": alur["content"]["layouts"][0]["definition"]["page"]
                                       ["definition"]["height"],
                         "rasio": SLOT.get("h03-alur", (558, 232))[0]
                                  / SLOT.get("h03-alur", (558, 232))[1],
                         "dataset": None, "tipe": "shapes+text"})
        print("  + h03-alur                 (diagram Shapes+Text dari story asli)")
    permintaan_sorot: list[dict] = []
    for r in resep.SIAP:
        if r["berkas"] in disimpan:
            hal = disimpan[r["berkas"]]
            story["pages"].append(hal)
            G.daftarkan_halaman(ents, hal["id"], r["berkas"],
                                [w["id"] for w in hal["content"]["widgets"]
                                 if isinstance(w, dict)])
            dibangun.append({"berkas": r["berkas"], "pageId": hal["id"],
                             "widgetId": hal["content"]["widgets"][0]["id"],
                             "widgetIds": [w["id"] for w in hal["content"]["widgets"]
                                           if isinstance(w, dict)],
                             "dataset": r["dataset"], "tipe": r["tipe"]})
            continue
        cube = DS[r["dataset"]]["cube"]
        if r.get("sorot"):
            permintaan_sorot.append({"cube": cube, **r["sorot"]})
        if r["tipe"] == "tabel":
            tw, te = tabel_mod.buat_tabel(
                json.load(open(TPL_TABEL)), json.load(open(TPL_TABEL_ENT)),
                cube=cube, relasi=DS[r["dataset"]].get("relationName") or "",
                nama_dataset=r["dataset"], judul=r["judul"],
                dims=r["dims"], measures=r["measures"],
                filter_dim=r["filter"], sort=r.get("sort"))
            # tabel melebar mengikuti lebar halaman; slot dek untuk kedua tabel
            # berorientasi potret, jadi halamannya sengaja dibuat sempit
            lebar_hal, tinggi_hal = 820, 1000
            hal = G.halaman_baru(r["berkas"], tw["id"], lebar_hal, tinggi_hal)
            hal["content"]["widgets"] = [tw]
            story["pages"].append(hal)
            G.daftarkan_halaman(ents, hal["id"], r["berkas"], [tw["id"]])
            ents.append(te)
            if cube not in cube_ada:
                ents.append(G.entitas_dataset(cube)); ents.append(G.entitas_alias(cube))
                cube_ada.add(cube)
            dibangun.append({"berkas": r["berkas"], "pageId": hal["id"],
                             "widgetId": tw["id"], "widgetIds": [tw["id"]],
                             "lebar": lebar_hal, "tinggi": tinggi_hal,
                             "dataset": r["dataset"], "tipe": r["tipe"]})
            print(f"  + {r['berkas']:24s} {'tabel':16s} {r['dataset']}")
            continue
        w, viz_id = G.buat_widget(templat, cube=cube, tipe=r["tipe"], judul=r["judul"],
                                  feeds=r["feeds"], filter_dim=r["filter"],
                                  sort=r.get("sort"), top=r.get("top"),
                                  properti=r.get("properti"),
                                  rentang_sumbu=r.get("rentang_sumbu"),
                                  bendera=r.get("bendera"))
        lebar_hal, tinggi_hal = ukuran_halaman(r["berkas"])
        hal = G.halaman_baru(r["berkas"], w["id"], lebar_hal, tinggi_hal)
        hal["content"]["widgets"] = [w]
        story["pages"].append(hal)
        G.daftarkan_halaman(ents, hal["id"], r["berkas"], [w["id"]])
        ents.append(G.entitas_viz(cube, viz_id))
        if cube not in cube_ada:
            ents.append(G.entitas_dataset(cube))
            ents.append(G.entitas_alias(cube))
            cube_ada.add(cube)
        dibangun.append({"berkas": r["berkas"], "pageId": hal["id"], "widgetId": w["id"],
                         "widgetIds": [w["id"]],
                         "lebar": lebar_hal, "tinggi": tinggi_hal,
                         "dataset": r["dataset"], "tipe": r["tipe"]})
        print(f"  + {r['berkas']:24s} {r['tipe']:16s} {r['dataset']}")

    diubah = palet.terapkan(isi)
    print("  palet dek diterapkan:", ", ".join(diubah) or "(tidak ada yang cocok)")
    disorot = sorot.terapkan(isi, permintaan_sorot)
    print("  sorotan per anggota:", ", ".join(disorot) or "(tidak ada)")

    sac_story.mulai_edit(page, sid)
    st, res = sac_story.tulis(page, meta, isi, local_ver=meta["metadata"]["version"])
    print("simpan:", st, "" if st == 200 else json.dumps(res)[:300])
    sac_story.selesai_edit(page, sid)

json.dump({"storyId": sid, "halaman": dibangun}, open(PETA, "w"), indent=1)
print(f"\n{len(dibangun)} halaman -> {PETA}")
print("URL:", f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{sid}/?mode=view")
