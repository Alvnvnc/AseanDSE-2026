import json, sys, time
from playwright.sync_api import sync_playwright
import sac, api

OUT = sys.argv[1]
with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    if "story2" not in page.url:
        page.goto(sac.STORY_URL, wait_until="domcontentloaded", timeout=120000); time.sleep(45)

    st, story = api.contentlib(page, "getContent", {
        "resourceType": "STORY", "resourceId": sac.STORY_ID,
        "oOpt": {"fetchDefaultBookmark": True, "sTranslationLocale": "en_UK",
                 "propertyBag": True, "isStory": True, "isStory2": True,
                 "fetchTheme": True, "fetchComposite": True,
                 "fetchImportPageDetails": True, "optimized": True,
                 "dontFetchPersistedInfo": True},
        "bIncDependency": False})
    print("getContent status:", st, "tipe:", type(story).__name__)
    json.dump(story, open(OUT, "w"), indent=1)
    print("tersimpan:", OUT)
    if isinstance(story, dict):
        print("kunci utama:", list(story.keys())[:30])
