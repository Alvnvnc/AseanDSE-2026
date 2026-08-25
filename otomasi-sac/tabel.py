"""Bangkitkan widget Table SAC dari satu tabel template.

Polanya sama dengan `generator.py` untuk grafik: satu tabel dibuat sekali lewat
UI, lalu diperbanyak dengan mengganti id cube dan menyusun ulang `ffQuery`.

Bedanya, tabel menyimpan kueri di entity `analyticgrid.table`
(`data.content.segments[1].dataRegion.ffQuery`, berupa string JSON), bukan di
widget-nya.
"""
from __future__ import annotations
import copy
import json

import generator as G

CUBE_TEMPLAT = "Cpco6l1nqg1ocm2b2fo5qqjeg33"
RELASI_TEMPLAT = "sap.dataset.conf_5B171050DF500D001A0032069967D971_view"
uid = G.uid
jdump = G.jdump


def _dataregion(entity: dict) -> dict:
    for seg in entity["data"]["content"]["segments"]:
        if "dataRegion" in seg:
            return seg["dataRegion"]
    raise RuntimeError("dataRegion tidak ditemukan di template tabel")


def buat_tabel(templat_widget: dict, templat_entity: dict, *, cube: str,
               relasi: str, nama_dataset: str, judul: str,
               dims: list[str], measures: list[str],
               filter_dim: dict | None = None,
               sort: list[dict] | None = None) -> tuple[dict, dict]:
    """-> (widget, entity) siap dimasukkan ke halaman & daftar entity."""
    teks = json.dumps([templat_widget, templat_entity])
    teks = teks.replace(CUBE_TEMPLAT, cube)
    if relasi:
        teks = teks.replace(RELASI_TEMPLAT, relasi)
    w, e = json.loads(teks)

    entity_id = uid()
    w["id"] = uid()
    w["definition"]["entityId"] = entity_id
    e["id"] = entity_id
    e["datasets"] = [G.ds_id(cube)]
    e["data"]["title"] = judul
    e["data"]["tileId"] = w["id"]

    # nama dataset yang tampil di panel builder
    ds = e["data"]["content"].get("dataSource", {})
    if isinstance(ds, dict):
        ds["shortDescription"] = nama_dataset

    dr = _dataregion(e)
    dr["title"] = judul
    dr["titleChunks"] = [{"type": "text", "value": judul}]
    dr["titleDom"] = f"<span>{judul}</span>"
    dr["showTitle"] = True
    if isinstance(dr.get("dataSource"), dict):
        dr["dataSource"]["shortDescription"] = nama_dataset

    ff = json.loads(dr["ffQuery"])
    el_lama = ff["DimensionsRepo"]["Elements"]
    t_meas = [x for x in el_lama if x["Name"] == "CustomDimension1"][0]
    t_dim = [x for x in el_lama if x["Name"] == "Version"][0]

    elemen = [G._elemen_dim(t_dim, d, "Rows") for d in dims]
    elemen.append(G._elemen_measure(t_meas, measures))
    elemen.append(copy.deepcopy(t_dim))          # Version tetap ada
    ff["DimensionsRepo"]["Elements"] = elemen

    bebas = ["Version", "CustomDimension2", "$$Unit$$", "$$Version$$"]
    ff["Query"]["AxesLayout"] = [
        {"Axis": "Free", "OrderedDimensionNames": bebas},
        {"Axis": "Columns", "OrderedDimensionNames": ["CustomDimension1"]},
        {"Axis": "Rows", "OrderedDimensionNames": list(dims)},
        {"Axis": "Technical", "OrderedDimensionNames": ["$$Cells$$"]},
    ]
    if isinstance(ff["Query"].get("AxesRepo"), dict):
        ff["Query"]["AxesRepo"]["Elements"] = [
            {"Axis": "Columns", "CType": "Axis", "Layout": ["CustomDimension1"],
             "ResultStructureRepo": {"CType": "Totals", "ResultAlignment": "Default",
                                     "Visibility": "Default"}, "Type": 2,
             "ZeroSuppressionType": 0},
            {"Axis": "Rows", "CType": "Axis", "Layout": list(dims),
             "ResultStructureRepo": {"CType": "Totals", "ResultAlignment": "Default",
                                     "Visibility": "Default"}, "Type": 1,
             "ZeroSuppressionType": 0},
        ]

    sub = [G._filter_cartesian("[Measures].[Measures]", measures)]
    for d, nilai in (filter_dim or {}).items():
        sub.append(G._filter_cartesian(d, nilai if isinstance(nilai, list) else [nilai]))
    ff["FilterRepo"] = {"CType": "Filter", "DynamicFilter": {
        "CType": "FilterExpression", "CellValueOperand": [],
        "FilterRoot": {"CType": "FilterAlgebra", "Code": "And", "Id": uid(),
                       "SubSelections": sub},
        "Id": uid(), "IsSuppressingNulls": False}}
    ff["SortRepo"] = {"CType": "Sorting",
                      "Elements": [G._elemen_sort(x) for x in (sort or [])]}
    dr["ffQuery"] = json.dumps(ff)

    ent = lambda d: jdump([{"datasetId": G.ds_id(cube)}, {"dimensionId": d}])
    ent_meas = lambda m: jdump([{"datasetId": G.ds_id(cube)},
                                {"dimensionId": "CustomDimension1"}, {"measureId": m}])
    st = dr.get("initialUQMExternalState") or {}
    st["hierarchyOptions"] = [{"entityId": ent(d), "showLeavesOnly": False}
                              for d in list(dims) + ["CustomDimension1", "Version"]]
    st["totals"] = [{"entityId": ent(d), "enabled": False, "useAlways": False} for d in dims]
    st["usedMeasures"] = [ent_meas(m) for m in measures]
    st["usedSecondaryMeasures"] = []
    st["usedDimensions"] = {
        "rowAxis": [ent(d) for d in dims],
        "columnAxis": [ent("CustomDimension1")],
        "filterDimensions": [ent("CustomDimension1"), ent("Version")]
                            + [ent(d) for d in dims]
                            + [ent(d) for d in (filter_dim or {}) if d not in dims],
    }
    st["drills"] = []; st["hierarchyLevels"] = []; st["ranks"] = []; st["sorts"] = []
    st["topEntries"] = []
    dr["initialUQMExternalState"] = st

    w["definition"]["tableDefinition"]["allPrimaryMembersSelected"] = {
        jdump([{"datasetId": G.ds_id(cube)}]): False}
    w["definition"]["tableDefinition"]["entityFormatInfos"] = [
        {"entityId": ent("CustomDimension1"), "format": "description"}]
    return w, e
