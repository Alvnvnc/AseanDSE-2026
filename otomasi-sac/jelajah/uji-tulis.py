"""UJI AMAN: salin story, gandakan satu grafik lewat API, simpan, buka, tangkap layar.

Tidak menyentuh `swalloy-story` sama sekali.
"""
import json, time, uuid
from playwright.sync_api import sync_playwright
import sac, api

SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
NAMA_SALINAN = "UJI-otomasi-hapus-saja"


def uid():
    return str(uuid.uuid4())


with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "app.html" not in page.url:
        page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
                  timeout=120000); time.sleep(40)

    # 1. salin story
    st, r = api.contentlib(page, "copyResource", {
        "resourceIds": [sac.STORY_ID],
        "targetParentResId": "PRIVATE_SWALLOWGANK",
        "options": {"mode": "2", "details": {sac.STORY_ID: {"name": NAMA_SALINAN,
                                                            "description": "uji otomasi"}}}})
    print("copyResource:", st, json.dumps(r)[:300])
    baru = (r.get("resourceMappings", {}).get(sac.STORY_ID, {}) or {}).get("targetResourceId")
    print("story salinan:", baru)
    assert baru, "gagal menyalin"

    # 2. baca isi salinan
    st, sal = api.contentlib(page, "getContent", {
        "resourceType": "STORY", "resourceId": baru,
        "oOpt": {"fetchDefaultBookmark": True, "sTranslationLocale": "en_UK", "propertyBag": True,
                 "isStory": True, "isStory2": True, "fetchTheme": True, "fetchComposite": True,
                 "fetchImportPageDetails": True, "optimized": True, "dontFetchPersistedInfo": True},
        "bIncDependency": False})
    print("getContent salinan:", st)
    cdata = sal["cdata"]
    isi = json.loads(cdata["content"])

    # 3. gandakan widget grafik pertama
    hal = isi["entities"][0]["data"]["pages"][0]
    ws = hal["content"]["widgets"]
    asli = [w for w in ws if isinstance(w, dict) and w.get("class") == "sap.lumira.story.viz.VizWidget"][0]

    klon = json.loads(json.dumps(asli))
    klon["id"] = uid()
    viz_baru = uid()
    klon["definition"]["entityId"] = viz_baru
    klon["definition"]["vizDefinition"]["title"] = "KLON UJI"
    klon["definition"]["vizDefinition"]["htmlTitle"] = "KLON UJI"
    ws.append(klon)

    # entity visualization.viz pendamping
    viz_asli = [e for e in isi["entities"]
                if e.get("type") == "visualization.viz"
                and e.get("id") == asli["definition"]["entityId"]][0]
    ve = json.loads(json.dumps(viz_asli))
    ve["id"] = viz_baru
    isi["entities"].append(ve)

    # tata letak: sisipkan section baru di kanan
    lay = hal["content"]["layouts"][0]["definition"]["page"]
    lay["sections"].append({
        "sectionId": uid(),
        "definition": {"x": 1160, "y": 0, "width": 300, "height": 731, "title": "Section Klon"},
        "widgets": [{"widgetId": klon["id"],
                     "definition": {"removeable": True, "x": 0, "y": 0, "height": 731,
                                    "width": 300, "border": {},
                                    "backgroundColorSwatchId": "BackgroundColor_2"}}]})

    cdata["content"] = json.dumps(isi)

    # 4. simpan
    api.contentlib(page, "startEdit", {"resourceId": baru})
    st, r2 = api.contentlib(page, "updateContent", {
        "resourceId": baru, "name": NAMA_SALINAN, "description": "uji otomasi",
        "cdata": json.dumps(cdata), "updateOpt": {}})
    print("updateContent:", st, json.dumps(r2)[:400])
    api.contentlib(page, "stopEdit", {"resourceId": baru})

    # 5. buka hasilnya
    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{baru}/?mode=edit",
              wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    page.screenshot(path=f"{SHOT}/uji-klon.png")
    print("tangkapan:", f"{SHOT}/uji-klon.png")
    print("STORY_UJI_ID =", baru)
