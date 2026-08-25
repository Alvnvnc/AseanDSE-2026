"""23 resep grafik SAC, diterjemahkan dari `storyboard/storyboard.tex`.

Nama measure/dimensi memakai nama sebagaimana SAC mengimpornya
(lihat `otomasi-sac/dataset-sac.json`), bukan nama kolom CSV asli.
"""

TAHUN_2000_2024 = [str(t) for t in range(2000, 2025)]
BULAN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FASE_ENSO = ["Strong La Nina", "La Nina", "Neutral", "El Nino", "Strong El Nino"]
ENAM_PROVINSI = ["Bali", "Kalimantan Utara", "Kalimantan Timur", "Gorontalo",
                 "Dki Jakarta", "Jawa Barat"]

PROP_HEATMAP = {
    "legendGroup": {"layout": {"position": "bottom"}, "visible": True},
    # tanpa ini SAC tidak menggambar label sumbu kedua pada heat map
    "categoryAxis2": {"visible": True, "axisLine": {"size": 3},
                      "axisTick": {"visible": False}, "showLabelGrids": True,
                      "label": {"visible": True, "style": {"fontSize": "13px"}}},
}

# Warna dek (sama dengan palet.py) — dipakai untuk sorotan per anggota.
BIRU, ORANYE, MERAH, ABU = "#2A78D6", "#E8833A", "#C53232", "#8A8F98"
BIRU_TUA, BIRU_MUDA, ABU_MUDA = "#1B5E9E", "#6BA6E8", "#B9BDC2"

# Fase ENSO itu berurutan (dingin -> panas), jadi warnanya dibuat menyebar
# dari biru ke merah, bukan warna palet acak. Dipakai di h06 dan h07 sekaligus
# supaya bahasa warnanya sama di seluruh dek.
WARNA_ENSO = {
    "Strong La Nina": BIRU_TUA,
    "La Nina": BIRU_MUDA,
    "Neutral": ABU_MUDA,
    "El Nino": ORANYE,
    "Strong El Nino": MERAH,
}

# Sepuluh negara ASEAN: semuanya biru dek, Indonesia oranye.
NEGARA_ASEAN = ["Brunei Darussalam", "Cambodia", "Indonesia", "Laos", "Malaysia",
                "Myanmar", "Philippines", "Singapore", "Thailand", "Vietnam"]
WARNA_NEGARA = {n: (ORANYE if n == "Indonesia" else BIRU) for n in NEGARA_ASEAN}

# Dimensi yang sudah dilabeli sumbu kategori tidak perlu legenda lagi.
# `visible: False` saja tidak cukup: selama `responsive` masih True, SAC
# mengatur sendiri legendanya dan menimpa bendera itu. Harus dua-duanya.
TANPA_LEGENDA = {"legendGroup": {"visible": False, "responsive": False}}


def PENANDA(skala: float) -> dict:
    """Ukuran titik pencar (panel Styling -> Data Points -> Data Marker Size).
    1.0 = 100%. Sarangnya memang ganda — begitu SAC menuliskannya."""
    return {"general": {"pointScale": {"pointScale": skala}}}


RESEP = [
    dict(berkas="h02-tren-tahunan", dataset="Dengue national annual", tipe="line",
         judul="ASEAN dengue cases, 2000-2024",
         feeds={"valueAxis": [("meas", "cases")], "categoryAxis": [("dim", "year")]},
         filter={"complete": ["True"], "year": TAHUN_2000_2024},
         sort=[dict(jenis="field", dimensi="year", arah="asc")], status="siap"),

    dict(berkas="h02-per-negara", dataset="Dengue national annual", tipe="barcolumn",
         judul="Cases by country, latest complete year",
         # `country` juga ditaruh di feed `color` — tanpa itu sorotan per anggota
         # tidak berlaku. Legendanya disembunyikan karena sumbu kategori sudah
         # menuliskan nama negaranya.
         feeds={"valueAxis": [("meas", "cases")], "categoryAxis": [("dim", "country")],
                "color": [("dim", "country")]},
         filter={"complete": ["True"], "year": ["2023"]},
         sort=[dict(jenis="measure", measure="cases", dimensi="country", arah="desc")],
         properti=TANPA_LEGENDA,
         sorot={"dimensi": "country", "warna": WARNA_NEGARA},
         status="siap"),

    dict(berkas="h03-alur", dataset=None, tipe=None,
         judul="From public index to public action",
         feeds={}, filter={},
         status="diambil apa adanya dari Page_3 `swalloy-story` (Shapes + Text)"),

    dict(berkas="h05-musiman-idn", dataset="Seasonality IDN-THA", tipe="combstackedbcl",
         judul="Indonesia - cases vs rainfall by month",
         feeds={"valueAxis": [("meas", "mean_cases")],
                "valueAxis2": [("meas", "mean_rain_mm")],
                "categoryAxis": [("dim", "month_name")]},
         filter={"country": ["Indonesia"]},
         sort=[dict(jenis="urutan", dimensi="month_name", urutan=BULAN)], status="siap"),

    dict(berkas="h05-musiman-tha", dataset="Seasonality IDN-THA", tipe="combstackedbcl",
         judul="Thailand - cases vs rainfall by month",
         feeds={"valueAxis": [("meas", "mean_cases")],
                "valueAxis2": [("meas", "mean_rain_mm")],
                "categoryAxis": [("dim", "month_name")]},
         filter={"country": ["Thailand"]},
         sort=[dict(jenis="urutan", dimensi="month_name", urutan=BULAN)], status="siap"),

    dict(berkas="h06-heatmap-jeda", dataset="Lag correlation - national FIX", tipe="heatmap",
         judul="Correlation by predictor and lag",
         feeds={"categoryAxis": [("dim", "lag_label")], "categoryAxis2": [("dim", "predictor")],
                "color": [("meas", "r")]},
         filter={"iso3": ["IDN"]},
         sort=[dict(jenis="field", dimensi="lag_label", arah="asc")],
         properti=PROP_HEATMAP,
         status="siap"),

    dict(berkas="h06-scatter-suhu", dataset="Monthly series IDN-THA", tipe="scatterplot",
         judul="Temperature (lag 2) vs cases, Indonesia",
         # satu titik = satu bulan (dimensi `period`), diwarnai menurut fase ENSO
         feeds={"valueAxis": [("meas", "temp_c_lag2")], "valueAxis2": [("meas", "cases")],
                "color": [("dim", "enso_phase_lag4")], "shape": [("dim", "period")]},
         filter={"country": ["Indonesia"]},
         # Tanpa rentang manual SAC memulai sumbu X dari nol, padahal suhunya
         # 24,6-26,5 C -> semua titik menggumpal di tepi kanan.
         rentang_sumbu={"valueAxis": (24, 27), "valueAxis2": (0, "auto")},
         properti=PENANDA(2.0),
         sorot={"dimensi": "enso_phase_lag4", "warna": WARNA_ENSO},
         status="siap"),

    dict(berkas="h07-fase-enso", dataset="ENSO phase - averages", tipe="barcolumn",
         judul="Mean monthly cases by ENSO phase (lag 4)",
         feeds={"valueAxis": [("meas", "mean_cases_per_month")],
                "categoryAxis": [("dim", "enso_phase_lag4")],
                "color": [("dim", "enso_phase_lag4")]},
         filter={},
         sort=[dict(jenis="urutan", dimensi="enso_phase_lag4", urutan=FASE_ENSO)],
         properti=TANPA_LEGENDA,
         sorot={"dimensi": "enso_phase_lag4", "warna": WARNA_ENSO},
         status="siap"),

    dict(berkas="h07-anomali", dataset="Lag correlation - anomaly FIX", tipe="heatmap",
         judul="Same signal, seasonality removed",
         feeds={"categoryAxis": [("dim", "lag_label")], "categoryAxis2": [("dim", "predictor")],
                "color": [("meas", "r")]},
         filter={"iso3": ["IDN"]},
         sort=[dict(jenis="field", dimensi="lag_label", arah="asc")],
         properti=PROP_HEATMAP,
         status="siap"),

    dict(berkas="h08-kalender-idn", dataset="Risk calendar IDN", tipe="heatmap",
         judul="Indonesia - share of annual cases by month",
         feeds={"categoryAxis": [("dim", "province")], "categoryAxis2": [("dim", "month_name")],
                "color": [("meas", "share_percent")]},
         filter={},
         sort=[dict(jenis="urutan", dimensi="month_name", urutan=BULAN)],
         properti=PROP_HEATMAP, status="siap"),

    dict(berkas="h08-kalender-tha", dataset="Risk calendar THA", tipe="heatmap",
         judul="Thailand - share of annual cases by month",
         feeds={"categoryAxis": [("dim", "province")], "categoryAxis2": [("dim", "month_name")],
                "color": [("meas", "share_percent")]},
         filter={},
         sort=[dict(jenis="urutan", dimensi="month_name", urutan=BULAN)],
         properti=PROP_HEATMAP, status="siap"),

    dict(berkas="h09-insidens", dataset="Province incidence 18-20", tipe="barcolumn",
         judul="Incidence per 100k, 2018-2020",
         feeds={"valueAxis": [("meas", "mean")], "categoryAxis": [("dim", "province")]},
         filter={},
         sort=[dict(jenis="measure", measure="mean", dimensi="province", arah="desc")],
         top={"province": 12}, status="siap (12 provinsi teratas)"),

    dict(berkas="h09-wash", dataset="WASH by country", tipe="barcolumn",
         judul="Piped water access, ASEAN",
         feeds={"valueAxis": [("meas", "piped_water_")],
                "categoryAxis": [("dim", "country")]},
         filter={},
         sort=[dict(jenis="measure", measure="piped_water_", dimensi="country", arah="asc")],
         status="siap"),

    dict(berkas="h09-banjir", dataset="City flood vulnerability", tipe="barcolumn",
         judul="Flood-zone population",
         feeds={"valueAxis": [("meas", "exposed_2020")], "categoryAxis": [("dim", "city")]},
         filter={},
         sort=[dict(jenis="measure", measure="exposed_2020", dimensi="city", arah="desc")],
         top={"city": 8}, status="siap (8 kota teratas)"),

    dict(berkas="h10-kalender-prioritas", dataset="Risk calendar IDN", tipe="heatmap",
         judul="Risk calendar, six priority provinces",
         feeds={"categoryAxis": [("dim", "province")], "categoryAxis2": [("dim", "month_name")],
                "color": [("meas", "status_code")]},
         filter={"province": ENAM_PROVINSI},
         sort=[dict(jenis="urutan", dimensi="month_name", urutan=BULAN)],
         properti=PROP_HEATMAP, status="siap"),

    dict(berkas="h10-deret-alarm", dataset="Monthly series IDN-THA", tipe="line",
         judul="Cases vs the P75 outbreak threshold",
         feeds={"valueAxis": [("meas", "cases"), ("meas", "threshold_p75")],
                "categoryAxis": [("dim", "period")]},
         filter={"country": ["Indonesia"]},
         sort=[dict(jenis="field", dimensi="period", arah="asc")], status="siap"),

    dict(berkas="h11-deret-aturan", dataset="Monthly series IDN-THA", tipe="line",
         judul="When the rule fired, 2010-2024",
         feeds={"valueAxis": [("meas", "cases"), ("meas", "threshold_p75")],
                "categoryAxis": [("dim", "period")], "color": [("dim", "alarm_rule_d")]},
         filter={"country": ["Indonesia"]},
         sort=[dict(jenis="field", dimensi="period", arah="asc")], status="siap"),

    dict(berkas="h11-aturan", dataset="Trigger rules - evaluation LONG", tipe="barcolumn",
         judul="Precision vs alert frequency, four rules",
         feeds={"valueAxis": [("meas", "value")], "categoryAxis": [("dim", "rule")],
                "color": [("dim", "metric")]},
         filter={"metric": ["precision_%", "alarm_coverage_%"]},
         sort=[dict(jenis="field", dimensi="rule", arah="asc")], status="siap"),

    dict(berkas="h12-luar-sampel", dataset="Trigger rules - out of sample LONG",
         tipe="barcolumn",
         judul="Train vs blind test, Indonesia and Thailand",
         feeds={"valueAxis": [("meas", "value")],
                "categoryAxis": [("dim", "country"), ("dim", "period")],
                "color": [("dim", "metric")]},
         filter={"metric": ["precision_%", "sensitivity_%"]},
         sort=[dict(jenis="field", dimensi="country", arah="asc")], status="siap"),

    dict(berkas="h12-tolok-ukur", dataset="EWS benchmark TABLE", tipe="tabel",
         judul="How we compare to published EWS",
         # kolom teks aslinya berupa rentang ("50-100%"), jadi dipecah jadi
         # batas bawah & atas supaya bisa tampil sebagai angka
         dims=["system", "source"],
         measures=["sensitivity_low", "sensitivity_high",
                   "precision_low", "precision_high"],
         feeds={}, filter={},
         sort=[dict(jenis="field", dimensi="system", arah="asc")], status="siap"),

    dict(berkas="h13-dampak", dataset="Monetary impact STACK", tipe="stackedbar",
         judul="Avoided hospitalisation cost by scenario (US$ thousand)",
         # bertingkat: batas bawah sebagai dasar + selisih ke batas atas,
         # sehingga tinggi total = batas atas (bukan penjumlahan dua perkiraan)
         feeds={"valueAxis": [("meas", "usd_thousand")],
                "categoryAxis": [("dim", "scenario")], "color": [("dim", "metric")]},
         filter={"metric": ["hospitalisation low", "extra up to high"]},
         sort=[dict(jenis="field", dimensi="scenario", arah="asc")],
         status="siap (bar bertingkat: batas bawah + selisih ke batas atas)"),

    dict(berkas="h13-tenggang", dataset="El Nino lead time TABLE", tipe="tabel",
         judul="Lead time, every El Nino episode since 2009",
         dims=["episode", "alarm", "cases_cross"],
         measures=["lead_time_months"],
         feeds={}, filter={},
         sort=[dict(jenis="field", dimensi="episode", arah="asc")], status="siap"),

    dict(berkas="h14-kekeringan", dataset="Drought x water access", tipe="scatterplot",
         judul="No relationship (rho = +0.34, p = 0.46, n = 7)",
         feeds={"valueAxis": [("meas", "piped_water_")], "valueAxis2": [("meas", "r_drought")],
                "color": [("dim", "country")]},
         filter={},
         # akses air ledeng maksimum 100% -> sumbu otomatis 0-120 menyisakan
         # seperlima lebar kosong di kanan
         rentang_sumbu={"valueAxis": (0, 105)},
         # cuma 7 titik: penanda bawaan terlalu kecil untuk dibaca di dek
         properti=PENANDA(3.0),
         status="siap"),
]

SIAP = [r for r in RESEP if r["tipe"] and not r["status"].startswith("TERHALANG")]
