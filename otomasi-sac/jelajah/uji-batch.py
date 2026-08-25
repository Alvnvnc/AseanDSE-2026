"""Uji generator: 4 tipe grafik berbeda di story SALINAN, satu halaman 2x2."""
import json, sys, time
sys.path.insert(0, "/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac")
from playwright.sync_api import sync_playwright
import sac, sac_story, generator as G

SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
UJI = "8D68C286FA86EB3FB3B3D419CC1A8B38"
DS = json.load(open("/home/alvn/Documents/Riset/AseanDSE-2026/otomasi-sac/dataset-sac.json"))
cube = lambda n: DS[n]["cube"]

C = cube("Drought x water access")
BULAN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
D = cube("Dengue national annual")
S = cube("Seasonality IDN-THA")
R = cube("Risk calendar IDN")
RESEP = [
    dict(nama="U1", cube=D, tipe="barcolumn", judul="U1 measure Desc",
         feeds={"valueAxis": [("meas", "cases")], "categoryAxis": [("dim", "country")]},
         sort=[dict(jenis="measure", measure="cases", dimensi="country", arah="desc")]),
    dict(nama="U2", cube=S, tipe="barcolumn", judul="U2 urutan bulan kustom",
         feeds={"valueAxis": [("meas", "mean_cases")], "categoryAxis": [("dim", "month_name")]},
         filter_dim={"country": ["Indonesia"]},
         sort=[dict(jenis="urutan", dimensi="month_name", urutan=BULAN)]),
    dict(nama="U3", cube=R, tipe="heatmap", judul="U3 heatmap bulan terurut",
         feeds={"categoryAxis": [("dim", "province")], "categoryAxis2": [("dim", "month_name")],
                "color": [("meas", "share_percent")]},
         sort=[dict(jenis="urutan", dimensi="month_name", urutan=BULAN)]),
    dict(nama="U4", cube=S, tipe="combstackedbcl", judul="U4 kombinasi bulan terurut",
         feeds={"valueAxis": [("meas", "mean_cases")], "valueAxis2": [("meas", "mean_rain_mm")],
                "categoryAxis": [("dim", "month_name")]},
         filter_dim={"country": ["Indonesia"]},
         sort=[dict(jenis="urutan", dimensi="month_name", urutan=BULAN)]),
]

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "app.html" not in page.url:
        page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
                  timeout=120000); time.sleep(40)

    meta, isi = sac_story.baca(page, UJI)
    ents = isi["entities"]
    story = ents[0]["data"]

    G.buang_halaman(isi, "UJI-generator")
    for k in ("storyFilters", "uqmStoryFilters", "uqmFieldSelectionFilters", "uqmStoryLAFilters"):
        if isinstance(story.get(k), list):
            story[k] = []
    print("filter story dilepas")
    templat = [w for w in story["pages"][0]["content"]["widgets"]
               if isinstance(w, dict) and w.get("class") == "sap.lumira.story.viz.VizWidget"][0]

    hal = G.halaman_baru("UJI-generator", "x")
    seksi_templat = hal["content"]["layouts"][0]["definition"]["page"]["sections"][0]
    hal["content"]["layouts"][0]["definition"]["page"]["sections"] = []
    kotak = [(8, 8), (756, 8), (8, 425), (756, 425)]

    cube_ada = {e["id"] for e in ents if e.get("type") == "dataset"}
    for (x, y), r in zip(kotak, RESEP):
        w, viz_id = G.buat_widget(templat, cube=r["cube"], tipe=r["tipe"], judul=r["judul"],
                                  feeds=r["feeds"], filter_dim=r.get("filter_dim"), sort=r.get("sort"))
        hal["content"]["widgets"].append(w)
        ents.append(G.entitas_viz(r["cube"], viz_id))
        if G.ds_id(r["cube"]) not in cube_ada:
            ents.append(G.entitas_dataset(r["cube"]))
            ents.append(G.entitas_alias(r["cube"]))
            cube_ada.add(G.ds_id(r["cube"]))
        hal["content"]["layouts"][0]["definition"]["page"]["sections"].append({
            "sectionId": G.uid(),
            "definition": {"x": x, "y": y, "width": 732, "height": 400, "title": r["nama"]},
            "widgets": [{"widgetId": w["id"],
                         "definition": {"removeable": True, "x": 0, "y": 0, "width": 732,
                                        "height": 400, "border": {},
                                        "backgroundColorSwatchId": "BackgroundColor_2"}}]})

    story["pages"].append(hal)
    G.daftarkan_halaman(ents, hal["id"], "UJI-generator",
                        [w["id"] for w in hal["content"]["widgets"]])

    sac_story.mulai_edit(page, UJI)
    st, r = sac_story.tulis(page, meta, isi, local_ver=meta["metadata"]["version"])
    print("simpan:", st, (json.dumps(r)[:200] if not isinstance(r, str) else r[:200]))
    sac_story.selesai_edit(page, UJI)

    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{UJI}/?mode=edit",
              wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    try:
        page.get_by_text("UJI-generator", exact=True).first.click(timeout=10000)
    except Exception as e:
        print("gagal klik tab halaman:", str(e)[:200])
    time.sleep(30)
    page.screenshot(path=f"{SHOT}/uji-batch.png")
    print("tangkapan:", f"{SHOT}/uji-batch.png")
