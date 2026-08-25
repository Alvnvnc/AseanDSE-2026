"""Uji klon grafik di story SALINAN dengan payload simpan yang benar."""
import json, time, uuid
from playwright.sync_api import sync_playwright
import sac, sac_story

SHOT = "/tmp/claude-1000/-home-alvn-Documents-Riset-AseanDSE-2026/17376010-2635-488d-97da-095ba251cbf7/scratchpad"
UJI = "8D68C286FA86EB3FB3B3D419CC1A8B38"
uid = lambda: str(uuid.uuid4())

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "app.html" not in page.url:
        page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/files", wait_until="domcontentloaded",
                  timeout=120000); time.sleep(40)

    meta, isi = sac_story.baca(page, UJI)
    print("updateCounter:", meta.get("updateCounter"), "| metadata.version:",
      (meta.get("metadata") or {}).get("version"), "| nama:", meta["name"])

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

    viz_asli = [e for e in isi["entities"] if e.get("type") == "visualization.viz"
                and e.get("id") == asli["definition"]["entityId"]][0]
    ve = json.loads(json.dumps(viz_asli)); ve["id"] = viz_baru
    isi["entities"].append(ve)

    lay = hal["content"]["layouts"][0]["definition"]["page"]
    lay["sections"].append({
        "sectionId": uid(),
        "definition": {"x": 1160, "y": 0, "width": 300, "height": 731, "title": "Section Klon"},
        "widgets": [{"widgetId": klon["id"],
                     "definition": {"removeable": True, "x": 0, "y": 0, "height": 731,
                                    "width": 300, "border": {},
                                    "backgroundColorSwatchId": "BackgroundColor_2"}}]})

    sac_story.mulai_edit(page, UJI)
    st, r = sac_story.tulis(page, meta, isi, abaikan_versi=True)
    print("updateContent:", st, json.dumps(r)[:300] if not isinstance(r, str) else r[:300])
    sac_story.selesai_edit(page, UJI)

    page.goto("about:blank"); time.sleep(1)
    page.goto(f"{sac.TENANT}/sap/fpa/ui/app.html#/story2&/s2/{UJI}/?mode=edit",
              wait_until="domcontentloaded", timeout=120000)
    time.sleep(55)
    page.screenshot(path=f"{SHOT}/uji-klon2.png")
    print("tangkapan:", f"{SHOT}/uji-klon2.png")
