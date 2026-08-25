"""Bangkitkan widget grafik SAC dari satu widget template.

Template diambil dari grafik line yang sudah ada di story; seluruh referensi
cube diganti dengan string-replace, lalu bagian yang menentukan isi grafik
(bindings, ffQuery, sumbu, filter) disusun ulang dari resep.
"""
from __future__ import annotations
import copy, json, uuid

CUBE_TEMPLAT = "Cfck6l1nqg35g3qjqvbkeds4b6o"
uid = lambda: str(uuid.uuid4())
# SAC memakai string entity-id ini sebagai identitas tekstual -> tanpa spasi.
jdump = lambda o: json.dumps(o, separators=(",", ":"))


def ds_id(cube: str) -> str:
    return f"planning:[TENANT_O][][/t.O.{cube}/{cube}_qs]"


def entitas_dataset(cube: str) -> dict:
    return {"id": ds_id(cube), "type": "dataset",
            "data": {"id": ds_id(cube), "isRemote": False, "systemType": "ORCA_MAIN"},
            "bSuppressPromptDialog": False}


def entitas_alias(cube: str) -> dict:
    return {"datasetId": ds_id(cube), "alias": f'"{cube}_qs"', "type": "datasetAlias", "id": uid()}


def entitas_viz(cube: str, viz_id: str) -> dict:
    return {"type": "visualization.viz", "id": viz_id,
            "vendorId": "sap.epm.story.entity.viz.VizVendor",
            "data": {"isPlaceHolder": True,
                     "vizDefinition": {"properties": {},
                                       "datasetEntityId": jdump([{"datasetId": ds_id(cube)}]),
                                       "cacheHintEnabled": True}},
            "datasets": [ds_id(cube)]}


def _sumber(cube: str, jenis: str, nama: str) -> str:
    d = [{"datasetId": ds_id(cube)}]
    if jenis == "meas":
        d += [{"dimensionId": "CustomDimension1"}, {"measureId": nama}]
    else:
        d += [{"dimensionId": nama}]
    return jdump(d)


def _elemen_dim(templat_dim: dict, nama: str, axis: str) -> dict:
    e = copy.deepcopy(templat_dim)
    e["Name"] = nama
    e["Axis"] = axis
    e["ResultSetAttributeFields"] = [[{"Name": nama}]]
    e["ResultSetAttributeNodes"] = [nama]
    e["ResultSetFields"] = [{"Name": nama}]
    return e


def _elemen_measure(templat_meas: dict, measures: list[str]) -> dict:
    e = copy.deepcopy(templat_meas)
    e["MembersRepo"] = [{"CType": "BasicMeasure",
                         "KeyRef": {"GroupName": "CustomDimension1", "ObjectName": m,
                                    "StorageName": "main"}} for m in measures]
    e["OrderedStructureMemberNames"] = list(measures)
    return e


def _filter_cartesian(field: str, nilai: list[str], kecualikan=False) -> dict:
    """Satu FilterOperation per nilai — kalau digabung, SAC hanya memakai nilai pertama."""
    return {"CType": "FilterCartesianList", "ConvertToFlatSelection": False,
            "Elements": [{"CType": "FilterOperation", "Comparison": "=", "Exactness": 0,
                          "FieldName": field, "HasDepth": False, "HasLevelOffset": False,
                          "Id": uid(), "IsExcluding": kecualikan,
                          "Values": [{"Value": v, "ValueType": "String"}]}
                         for v in nilai],
            "FieldName": field, "Id": uid()}


def _elemen_sort(spec: dict) -> dict:
    """spec:
        {"jenis": "measure", "measure": "cases", "dimensi": "country", "arah": "Descending"}
        {"jenis": "urutan",  "dimensi": "month_name", "urutan": ["Jan", "Feb", ...]}
        {"jenis": "field",   "dimensi": "year", "arah": "Ascending"}
    """
    j = spec["jenis"]
    arah = {"asc": "Asc", "desc": "Desc"}[spec.get("arah", "asc").lower()]
    if j == "measure":
        e = {"SortType": "Measure", "Direction": arah, "MeasureName": spec["measure"]}
    elif j == "urutan":
        # urutan kustom: SortType Field + daftar CustomSort
        e = {"SortType": "Field", "Direction": arah, "FieldName": spec["dimensi"],
             "CustomSort": list(spec["urutan"])}
    else:
        e = {"SortType": "Field", "Direction": arah, "FieldName": spec["dimensi"]}
    if spec.get("dimensi"):
        e["Dimension"] = spec["dimensi"]
    return e


def buat_widget(templat: dict, *, cube: str, tipe: str, judul: str, subjudul: str = "",
                feeds: dict[str, list[tuple[str, str]]], filter_dim: dict | None = None,
                garis_acuan: list | None = None,
                sort: list[dict] | None = None,
                top: dict[str, int] | None = None,
                properti: dict | None = None,
                rentang_sumbu: dict[str, tuple] | None = None,
                bendera: dict | None = None) -> tuple[dict, str]:
    """-> (widget, viz_entity_id)"""
    teks = json.dumps(templat).replace(CUBE_TEMPLAT, cube)
    w = json.loads(teks)
    w["id"] = uid()
    viz_id = uid()
    w["definition"]["entityId"] = viz_id
    vd = w["definition"]["vizDefinition"]

    vd["type"] = tipe
    vd["title"] = judul
    vd["htmlTitle"] = f"<p><span>{judul}</span></p>"
    vd["headerProperties"] = {"isTitleExpanded": True, "hasUserModifiedTitle": True,
                              "hasUserModifiedSubtitle": bool(subjudul)}
    vd["subtitle"] = subjudul
    vd["htmlSubtitle"] = f"<p><span>{subjudul}</span></p>" if subjudul else ""
    vd["referenceLines"] = garis_acuan or []

    # Rentang sumbu nilai manual (SAC menyebutnya "Edit Axis").
    # Tanpa ini SAC selalu menskalakan otomatis -- untuk pencar suhu 24-27 C
    # sumbu X-nya dimulai dari nol sehingga titiknya menggumpal.
    if rentang_sumbu:
        vd["axisRange"] = [{"feed": f, "min": mn, "max": mx,
                            "dynamicAxisEnabled": False}
                           for f, (mn, mx) in rentang_sumbu.items()]
        vd.setdefault("properties", {})["axisSync"] = False

    def gabung(tujuan, tambahan):
        for k, v in tambahan.items():
            if isinstance(v, dict) and isinstance(tujuan.get(k), dict):
                gabung(tujuan[k], v)
            else:
                tujuan[k] = v

    if properti:
        gabung(vd.setdefault("properties", {}), properti)
    for k, v in (bendera or {}).items():
        vd[k] = v
    vd["datasetEntityId"] = jdump([{"datasetId": ds_id(cube)}])

    # --- bindings
    vd["bindings"] = [{"feed": f, "source": [_sumber(cube, j, n) for j, n in isi]}
                      for f, isi in feeds.items() if isi]

    # --- kumpulkan dimensi & measure
    dims_baris, dims_kolom, measures, meas_sekunder = [], [], [], []
    for f, isi in feeds.items():
        for jenis, nama in isi:
            if jenis == "meas":
                if nama not in measures:
                    measures.append(nama)
                if f == "valueAxis2" and nama not in meas_sekunder:
                    meas_sekunder.append(nama)
            else:
                target = dims_baris if f in ("categoryAxis",) else dims_kolom
                if nama not in dims_baris and nama not in dims_kolom:
                    target.append(nama)

    ff = vd["ffQuery"]
    el_lama = ff["DimensionsRepo"]["Elements"]
    t_dim = [e for e in el_lama if e["Name"] != "CustomDimension1"][0]
    t_meas = [e for e in el_lama if e["Name"] == "CustomDimension1"][0]

    elemen = [_elemen_dim(t_dim, d, "Rows") for d in dims_baris]
    elemen += [_elemen_dim(t_dim, d, "Columns") for d in dims_kolom]
    for e in elemen:                       # batasi jumlah anggota (Top-N)
        if (top or {}).get(e["Name"]):
            e["Top"] = int(top[e["Name"]])
    elemen.append(_elemen_measure(t_meas, measures))
    ff["DimensionsRepo"]["Elements"] = elemen

    ff["Query"]["AxesLayout"] = [
        {"Axis": "Free", "OrderedDimensionNames": ["CustomDimension2", "Version"]},
        {"Axis": "Columns", "OrderedDimensionNames": dims_kolom + ["CustomDimension1"]},
        {"Axis": "Rows", "OrderedDimensionNames": dims_baris},
        {"Axis": "Technical", "OrderedDimensionNames": ["$$Cells$$"]},
    ]
    ff["Query"]["AxesRepo"]["Elements"] = [
        {"Axis": "Columns", "CType": "Axis", "Layout": dims_kolom + ["CustomDimension1"],
         "ResultStructureRepo": {"CType": "Totals", "ResultAlignment": "Default",
                                 "Visibility": "Default"}, "Type": 2, "ZeroSuppressionType": 0},
        {"Axis": "Rows", "CType": "Axis", "Layout": dims_baris,
         "ResultStructureRepo": {"CType": "Totals", "ResultAlignment": "Default",
                                 "Visibility": "Default"}, "Type": 1, "ZeroSuppressionType": 0},
    ]

    # --- filter: measure + dimensi
    sub = [_filter_cartesian("[Measures].[Measures]", measures)]
    for d, nilai in (filter_dim or {}).items():
        sub.append(_filter_cartesian(d, nilai if isinstance(nilai, list) else [nilai]))
    ff["FilterRepo"] = {"CType": "Filter", "DynamicFilter": {
        "CType": "FilterExpression", "CellValueOperand": [],
        "FilterRoot": {"CType": "FilterAlgebra", "Code": "And", "Id": uid(),
                       "SubSelections": sub},
        "Id": uid(), "IsSuppressingNulls": False}}

    ff["SortRepo"] = {"CType": "Sorting",
                      "Elements": [_elemen_sort(x) for x in (sort or [])]}

    # --- state awal UQM (harus konsisten dengan bindings, kalau tidak grafik ditolak)
    ent = lambda d: jdump([{"datasetId": ds_id(cube)}, {"dimensionId": d}])
    ent_meas = lambda m: jdump([{"datasetId": ds_id(cube)},
                                {"dimensionId": "CustomDimension1"}, {"measureId": m}])
    dipakai = dims_baris + dims_kolom + ["CustomDimension1", "Version"]
    st = vd.get("initialUQMExternalState") or {}
    st["hierarchyOptions"] = [{"entityId": ent(d), "showLeavesOnly": False} for d in dipakai]
    st["totals"] = [{"entityId": ent(d), "enabled": False, "useAlways": False}
                    for d in dims_baris + dims_kolom]
    st["usedMeasures"] = [ent_meas(m) for m in measures]
    st["usedSecondaryMeasures"] = [ent_meas(m) for m in meas_sekunder]
    st["usedDimensions"] = {
        "rowAxis": [ent(d) for d in dims_baris],
        "columnAxis": [ent(d) for d in dims_kolom] + [ent("CustomDimension1")],
        "filterDimensions": [ent("CustomDimension1"), ent("Version")]
                            + [ent(d) for d in dims_baris + dims_kolom]
                            + [ent(d) for d in (filter_dim or {}) 
                               if d not in dims_baris + dims_kolom],
    }
    st["drills"] = []; st["hierarchyLevels"] = []; st["ranks"] = []; st["sorts"] = []
    st["topEntries"] = []
    vd["initialUQMExternalState"] = st

    return w, viz_id


def halaman_baru(judul: str, widget_id: str, lebar: int = 1496,
                 tinggi: int = 834) -> dict:
    """Halaman kanvas berisi satu grafik penuh."""
    seksi = {
        "sectionId": uid(),
        "definition": {"x": 8, "y": 8, "width": lebar - 16, "height": tinggi - 16,
                       "title": "Section"},
        "widgets": [{
            "widgetId": widget_id,
            "definition": {"removeable": True, "x": 0, "y": 0, "width": lebar - 16,
                           "height": tinggi - 16, "border": {},
                           "backgroundColorSwatchId": "BackgroundColor_2"},
        }],
    }
    layout = {
        "id": "boxlayout",
        "definition": {
            "type": "sap.lumira.story.layout.unified",
            "page": {
                "sections": [seksi],
                "definition": {"backgroundColor": "#FFFFFF", "type": "CANVAS",
                               "height": tinggi, "width": lebar,
                               "backgroundColorSwatchId": "BackgroundColor_2"},
            },
        },
    }
    return {
        "title": judul,
        "hidden": False,
        "definition": {"type": "CANVAS", "snapToGrid": True, "snapToObject": True,
                       "layoutId": "boxlayout", "fitPageToDevice": False,
                       "enableDevicePreview": False,
                       "devicePreviewSize": {"width": 0, "height": 0}},
        "id": uid(),
        "content": {"version": "1.0", "filters": [], "uqmPageFilters": [],
                    "uqmLAPageGroups": [], "uqmLAPageFilters": [],
                    "uqmScopedPageGroups": [], "uqmCascadeGroupings": [],
                    "uqmLAPageFilterFFQueries": {},
                    "widgets": [], "layouts": [layout]},
    }


def _entity_app(ents: list) -> dict:
    """Entity ':application' — daftar halaman & nama widget yang dipakai UI."""
    for e in ents:
        if isinstance(e, dict) and str(e.get("id", "")).endswith(":application"):
            return e
    raise RuntimeError("entity :application tidak ditemukan")


def daftarkan_halaman(ents: list, page_id: str, nama: str, widget_ids: list[str]) -> None:
    """Tanpa ini halaman tidak muncul di tab bar SAC."""
    app = _entity_app(ents)
    inst = jdump([{"appPage": page_id}])
    app.setdefault("appPages", [])
    if not any(a.get("payload", {}).get("pageId") == page_id for a in app["appPages"]):
        app["appPages"].append({"instanceId": inst, "payload": {
            "pageId": page_id, "behaviorMode": "CANVAS",
            "referencedWidgetInstanceIds": [], "allReferencedWidgetIdsForInit": {},
            "allReferencedWidgetIds": []}})
    app.setdefault("app", {}).setdefault("names", {})[inst] = nama
    for i, wid in enumerate(widget_ids, 1):
        kunci = jdump([{"story": "storyID"}, {"viz2": wid}])
        app["app"]["names"][kunci] = f"{nama}_Chart{i}"


def buang_halaman(isi: dict, judul: str) -> None:
    """Hapus halaman berjudul `judul` beserta pendaftarannya."""
    ents = isi["entities"]
    story = ents[0]["data"]
    buang = [p for p in story["pages"] if p.get("title") == judul]
    ids = {p["id"] for p in buang}
    story["pages"] = [p for p in story["pages"] if p.get("title") != judul]
    app = _entity_app(ents)
    app["appPages"] = [a for a in app.get("appPages", [])
                       if a.get("payload", {}).get("pageId") not in ids]
    for pid in ids:
        app.get("app", {}).get("names", {}).pop(jdump([{"appPage": pid}]), None)
