"""Baca/tulis isi story SAC lewat REST internal contentlib."""
from __future__ import annotations
import json
import api

OOPT = {"fetchDefaultBookmark": True, "sTranslationLocale": "en_UK", "propertyBag": True,
        "isStory": True, "isStory2": True, "fetchTheme": True, "fetchComposite": True,
        "fetchImportPageDetails": True, "optimized": True, "dontFetchPersistedInfo": True}


def baca(page, resource_id: str):
    """-> (meta_resource, isi_konten_dict)"""
    st, r = api.contentlib(page, "getContent", {
        "resourceType": "STORY", "resourceId": resource_id, "oOpt": OOPT,
        "bIncDependency": False})
    if st != 200:
        raise RuntimeError(f"getContent gagal {st}: {str(r)[:300]}")
    return r, json.loads(r["cdata"]["content"])


def tulis(page, meta: dict, isi: dict, local_ver: int | None = None,
          abaikan_versi: bool = False):
    """Simpan kembali isi story. `meta` dari baca()."""
    cdata = json.dumps(isi)
    opt = {"dataChangeInsightsSupport": {"value": 0},
           "enhancedProperties": {"STORY_OPTIMIZED_INFO": "VIEW_EDIT_STORY2",
                                  "DEFAULT_VIEW_MODE": "view",
                                  "CONTENT_SIZE": str(len(cdata))},
           "contentOnly": True, "ignoreVersion": abaikan_versi,
           "localVer": local_ver if local_ver is not None else meta.get("updateCounter", 0) + 1,
           "importPageDetails": [], "fetchImportPageDetails": True,
           "ignoreSizeLimit": True, "propertyBag": True,
           "videoDataStorySupport": {"value": 0}}
    st, r = api.contentlib(page, "updateContent", {
        "resourceId": meta["resourceId"], "name": meta["name"],
        "description": meta.get("description", ""), "cdata": cdata,
        "mobileSupport": 0, "updateOpt": opt,
        "fetchOpt": {"bIncDependency": False, "bIncSubItems": False}})
    return st, r


def mulai_edit(page, resource_id):
    return api.contentlib(page, "startEdit", {"resourceId": resource_id})


def selesai_edit(page, resource_id):
    return api.contentlib(page, "stopEdit", {"resourceId": resource_id})
