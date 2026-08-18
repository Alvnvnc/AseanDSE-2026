#!/usr/bin/env python3
"""Kamus istilah Indonesia -> Inggris untuk keluaran Excel.

Data kerja (CSV di `data/siap-sac/` dan `analisis/keluaran/`) tetap berbahasa
Indonesia; penerjemahan hanya terjadi di lapisan ekspor, supaya notebook dan
skrip penyiapan tidak perlu ikut berubah. Yang diterjemahkan:

* `KOLOM`   — nama kolom (jadi label sumbu & dimensi di SAP Analytics Cloud);
* `NILAI`   — isi sel kategori (fase ENSO, status, nama bulan, ...);
* `POLA`    — sisa pola angka/satuan yang tidak praktis didaftar satu per satu;
* `FRASA`   — prosa lembar "Key figures" (dari `angka_kunci_storyboard.md`).

Nama diri (provinsi, kabupaten/kota, kota, nama TPA) sengaja TIDAK diterjemahkan
supaya penjodohan geografis di SAC tidak pecah.
"""

from __future__ import annotations

import re

import pandas as pd

# --------------------------------------------------------------------------
# 1. Nama kolom
# --------------------------------------------------------------------------

KOLOM: dict[str, str] = {
    # --- kunci wilayah & waktu ---
    "negara": "country",
    "iso3": "iso3",
    "provinsi": "province",
    "kode_provinsi": "province_code",
    "provinsi_setara_dengue": "province_dengue_match",
    "kab_kota": "district_city",
    "kode_kab_kota": "district_city_code",
    "kota": "city",
    "wilayah": "area",
    "lingkup": "setting",
    "tahun": "year",
    "bulan": "month",
    "nama_bulan": "month_name",
    "periode": "period",
    "tanggal": "date",
    "tanggal_mulai": "start_date",
    "tanggal_akhir": "end_date",
    "jendela": "window",
    # --- dengue & iklim ---
    "kasus": "cases",
    "definisi_kasus": "case_definition",
    "resolusi_spasial": "spatial_resolution",
    "resolusi_waktu": "temporal_resolution",
    "sumber_resolusi": "source_resolution",
    "lengkap": "complete",
    "suhu_c": "temp_c",
    "hujan_mm": "rain_mm",
    "suhu_jeda0": "temp_c_lag0",
    "suhu_jeda1": "temp_c_lag1",
    "suhu_jeda2": "temp_c_lag2",
    "suhu_jeda3": "temp_c_lag3",
    "hujan_jeda0": "rain_mm_lag0",
    "hujan_jeda1": "rain_mm_lag1",
    "hujan_jeda2": "rain_mm_lag2",
    "hujan_jeda3": "rain_mm_lag3",
    "oni": "oni",
    "oni_jeda0": "oni_lag0",
    "oni_jeda3": "oni_lag3",
    "oni_jeda4": "oni_lag4",
    "fase": "enso_phase",
    "fase_jeda4": "enso_phase_lag4",
    "fase_enso_jeda4": "enso_phase_lag4",
    "penduduk": "population",
    "populasi_ribu": "population_thousand",
    "insidens_per_100rb": "incidence_per_100k",
    # --- lembar hasil hitung ---
    "kasus_anomali_z": "cases_anomaly_z",
    "ambang_P75": "threshold_p75",
    "bulan_puncak_kasus": "peak_case_month",
    "alarm_aturan_D": "alarm_rule_d",
    "alarm_El_Nino": "alarm_el_nino",
    "kasus_rerata": "mean_cases",
    "hujan_rerata_mm": "mean_rain_mm",
    "suhu_rerata_c": "mean_temp_c",
    "jendela_tahun_lengkap": "complete_years_window",
    "urutan": "order",
    "rerata_kasus_per_bulan": "mean_cases_per_month",
    "n_bulan": "n_months",
    "rasio_thd_netral": "ratio_vs_neutral",
    "cukup_data": "enough_data",
    "rasio_nino_vs_lain": "ratio_nino_vs_other",
    "n_bulan_nino": "n_months_nino",
    "arah": "direction",
    # --- kalender risiko & insidens ---
    "share_persen": "share_percent",
    "status": "status",
    "status_kode": "status_code",
    "rata2": "mean",
    "bulan_puncak": "peak_month",
    # --- korelasi & aturan pemicu ---
    "prediktor": "predictor",
    "jeda": "lag",
    "aturan": "rule",
    "keterangan": "item",
    "cakupan_alarm_%": "alarm_coverage_%",
    "cakupan_%": "coverage_%",
    "sensitivitas": "sensitivity",
    "sensitivitas_%": "sensitivity_%",
    "spesifisitas": "specificity",
    "spesifisitas_%": "specificity_%",
    "presisi": "precision",
    "presisi_%": "precision_%",
    "presisi/PPV": "precision/PPV",
    "sistem": "system",
    "sumber": "source",
    # --- episode El Nino & dampak ---
    "oni_puncak": "oni_peak",
    "alarm_menyala": "alarm_fires",
    "kasus_lewat_P75": "cases_cross_p75",
    "tenggang_bulan": "lead_time_months",
    "kasus_tertinggi_12bln": "peak_cases_12m",
    "skenario": "scenario",
    "kasus/tahun": "cases/year",
    "konservatif (rerata episode, US$90)": "conservative (avg episode, US$90)",
    "rawat inap bawah (US$316)": "hospitalisation low (US$316)",
    "rawat inap atas (US$791)": "hospitalisation high (US$791)",
    "Rp/tahun (jangkar rawat inap)": "Rp/year (hospitalisation anchor)",
    # --- bencana/banjir vs dengue (uji nol halaman 14) ---
    "uji": "test",
    "penyebut": "denominator",
    "nilai_p": "p_value",
    "kesimpulan": "verdict",
    "rumah_terendam": "houses_flooded",
    "kejadian_bencana": "disaster_events",
    "terendam_per_100rb": "houses_flooded_per_100k",
    "kejadian_per_100rb": "disaster_events_per_100k",
    # --- kekeringan x akses air ---
    "r_kering": "r_drought",
    "jeda_kering": "lag_drought",
    "r_oni4": "r_oni_lag4",
    "pengganda_nino": "nino_multiplier",
    "perpipaan_%": "piped_water_%",
    "tahun_pipa": "piped_water_year",
    # --- kerentanan banjir & WASH ---
    "penduduk_kota_2025": "city_population_2025",
    "terpapar_2020": "exposed_2020",
    "terpapar_2030": "exposed_2030",
    "persen_2020": "percent_2020",
    "pertumbuhan_2020_2030_%": "growth_2020_2030_%",
    "tahun_data": "data_year",
    "air_perpipaan_%": "piped_water_%",
    "air_minimal_dasar_%": "at_least_basic_water_%",
    "air_dikelola_aman_%": "safely_managed_water_%",
    "sanitasi_minimal_dasar_%": "at_least_basic_sanitation_%",
    "layanan": "service",
    "tingkat": "service_level",
    "indikator": "indicator",
    "persen": "percent",
    "nilai": "value",
    "satuan": "unit",
    # --- udara & sampah ---
    "polutan": "pollutant",
    "konsentrasi_ug_m3": "concentration_ug_m3",
    "cakupan_waktu_persen": "temporal_coverage_percent",
    "jenis_stasiun": "station_type",
    "jenis_tpa": "landfill_type",
    "nama_tpa": "landfill_name",
    "kelompok": "group",
    "bsu_aktif": "waste_bank_unit_active",
    "bsu_tidak_aktif": "waste_bank_unit_inactive",
    "sampah_terkelola_bsu_ton": "waste_managed_unit_bank_ton",
    "bsi_aktif": "waste_bank_central_active",
    "bsi_tidak_aktif": "waste_bank_central_inactive",
    "sampah_terkelola_bsi_ton": "waste_managed_central_bank_ton",
    "status_rips": "waste_master_plan_status",
    "verifikasi_lapangan": "field_verification",
    "nilai_kinerja_ps": "waste_performance_score",
    "progress_sa": "self_assessment_progress",
    "timbulan_ton_per_hari": "waste_generated_ton_per_day",
    "persen_terkelola": "percent_managed",
    "persen_belum_terkelola": "percent_unmanaged",
    # --- lembar "Key figures" ---
    "bagian": "section",
    "poin": "point",
}

# --------------------------------------------------------------------------
# 2. Isi sel kategori
# --------------------------------------------------------------------------

NILAI: dict[str, str] = {
    # --- negara ---
    "Kamboja": "Cambodia",
    "Filipina": "Philippines",
    "Singapura": "Singapore",
    # --- fase ENSO (tanpa diakritik supaya aman jadi kunci gabung di SAC) ---
    "El Nino kuat": "Strong El Nino",
    "El Nino": "El Nino",
    "Netral": "Neutral",
    "La Nina": "La Nina",
    "La Nina kuat": "Strong La Nina",
    # --- nama bulan ---
    "Mei": "May",
    "Agu": "Aug",
    "Okt": "Oct",
    "Des": "Dec",
    # --- label ya/tidak & status ---
    "Ya": "Yes",
    "Tidak": "No",
    "Puncak": "Peak",
    "Siaga": "Watch",  # samakan dengan teks slide "Peak - Watch - Normal"
    "Normal": "Normal",
    "Naik saat El Nino": "Higher during El Nino",
    "Tidak naik": "Not higher",
    # --- prediktor korelasi ---
    "Suhu": "Temperature",
    "Hujan": "Rainfall",
    # --- aturan pemicu ---
    "A. Musim (Jan/Feb/Mar/Apr)": "A. Season (Jan/Feb/Mar/Apr)",
    "B. El Niño: ONI jeda-4 ≥ 0,5": "B. El Nino: ONI lag-4 >= 0.5",
    "C. Musim ATAU El Niño": "C. Season OR El Nino",
    "D. Musim DAN El Niño (eskalasi)": "D. Season AND El Nino (escalation)",
    "A. Musim (Jan-Apr)": "A. Season (Jan-Apr)",
    "B. El Nino: ONI jeda-4 >= 0,5": "B. El Nino: ONI lag-4 >= 0.5",
    "C. A atau B": "C. A or B",
    "D. A dan B (eskalasi)": "D. A and B (escalation)",
    "latih 2010-2016": "train 2010-2016",
    "UJI 2017-2024": "TEST 2017-2024",
    "UJI 2017-2022": "TEST 2017-2022",
    # --- tolok ukur EWS ---
    "Aturan kami D vs P75 (uji luar-sampel 2017-2024)":
        "Our rule D vs P75 (out-of-sample test 2017-2024)",
    "Aturan kami D vs kanal endemis (2010-2024)":
        "Our rule D vs endemic channel (2010-2024)",
    "Rentang 17 EWS dengue (tinjauan sistematis)":
        "Range across 17 dengue EWS (systematic review)",
    "WHO-TDR EWARS, Meksiko (dengue)": "WHO-TDR EWARS, Mexico (dengue)",
    "EWARS-csd, 11 kota Kolombia (median)": "EWARS-csd, 11 Colombian cities (median)",
    "notebook ini": "this notebook",
    # --- uji nol bencana/banjir vs dengue (halaman 14) ---
    "Mentah": "Raw (no denominator)",
    "Per 100 rb penduduk": "Per 100k population",
    "Menyesatkan: artefak penduduk": "Misleading: population artefact",
    "Tidak ada hubungan": "No relationship",
    "Berlawanan arah": "Opposite direction",
    "Penyebab artefak": "Source of the artefact",
    "Jumlah kejadian bencana vs kasus dengue": "Disaster events vs dengue cases",
    "Rumah terendam vs kasus dengue": "Houses flooded vs dengue cases",
    "Rumah terendam vs insidens dengue": "Houses flooded vs dengue incidence",
    "Jumlah kejadian vs insidens dengue": "Disaster events vs dengue incidence",
    "Rumah terendam tahun T vs insidens tahun T+1":
        "Houses flooded in year T vs incidence in year T+1",
    "Perubahan antar-tahun dalam provinsi sama (rumah terendam)":
        "Year-on-year change within the same province (houses flooded)",
    "Perubahan antar-tahun dalam provinsi sama (kejadian)":
        "Year-on-year change within the same province (events)",
    "Penduduk vs kasus dengue": "Population vs dengue cases",
    "Penduduk vs jumlah kejadian bencana": "Population vs disaster events",
    # --- indikator bencana (BNPB) ---
    "Jumlah kejadian": "Number of events",
    "Korban meninggal": "Deaths",
    "Korban hilang": "Missing",
    "Korban terluka": "Injured",
    "Korban menderita": "Affected",
    "Korban mengungsi": "Displaced",
    "Rumah rusak berat": "Houses severely damaged",
    "Rumah rusak sedang": "Houses moderately damaged",
    "Rumah rusak ringan": "Houses lightly damaged",
    "Rumah terendam": "Houses flooded",
    "Fasilitas pendidikan rusak": "Education facilities damaged",
    "Fasilitas kesehatan rusak": "Health facilities damaged",
    "Fasilitas peribadatan rusak": "Places of worship damaged",
    "Fasilitas umum rusak": "Public facilities damaged",
    # --- paparan banjir (GHSL) ---
    "Penduduk terpapar banjir 10 tahunan": "Population exposed to 10-year flood",
    "Penduduk terpapar banjir 100 tahunan": "Population exposed to 100-year flood",
    "Persen penduduk terpapar banjir 100 tahunan":
        "Percent of population exposed to 100-year flood",
    "jiwa": "people",
    "persen": "percent",
    # --- WASH (JMP) ---
    "Air minum": "Drinking water",
    "Sanitasi": "Sanitation",
    "Higiene tangan": "Hand hygiene",
    "Higiene (CTPS)": "Hygiene (handwashing)",
    "Pengelolaan limbah medis": "Health-care waste management",
    "Kebersihan lingkungan": "Environmental cleaning",
    "Tanpa layanan": "No service",
    "Dasar": "Basic",
    "Terbatas": "Limited",
    "Minimal dasar": "At least basic",
    "Tidak layak": "Unimproved",
    "Air permukaan": "Surface water",
    "Perpipaan": "Piped",
    "Dikelola aman": "Safely managed",
    "BAB terbuka": "Open defecation",
    "Tersambung selokan": "Sewer connection",
    "Tanpa fasilitas": "No facility",
    "Nasional": "National",
    "Rumah sakit": "Hospitals",
    "Non-rumah sakit": "Non-hospitals",
    "Perkotaan": "Urban",
    "Perdesaan": "Rural",
    "Total": "Total",
    # --- sampah (SIPSN) ---
    "Tidak memiliki TPA": "No landfill",
    "343 TPA (353 Kota/Kab)": "343 landfills (353 cities/regencies)",
    "Diluar 343 TPA (171 Kota/Kab)": "Outside the 343 landfills (171 cities/regencies)",
    "Ada (Draft) tapi Belum Disahkan": "Draft, not yet ratified",
    "Ada tapi Belum Disahkan": "Exists, not yet ratified",
    "Ada dan Sudah Disahkan": "Exists and ratified",
    "Ada tapi Tidak Lengkap": "Exists but incomplete",
    "Ada tapi File Belum Terlampir": "Exists but file not attached",
    "Dalam Perencanaan": "Being planned",
    "Belum ada informasi": "No information yet",
    "Tidak Sesuai": "Not compliant",
    "Tidak Ada": "None",
    "Sudah": "Done",
    "Belum": "Not yet",
    # --- sumber penduduk (BPS) ---
    "BPS proyeksi SP2010 (WebAPI)": "BPS SP2010 projection (WebAPI)",
}

# Sisa pola yang tidak praktis didaftar satu per satu (angka ikut berubah bila
# notebook dijalankan ulang, jadi harus berbasis pola).
POLA: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^Tidak \(n=(\d+)\)$"), r"No (n=\1)"),
    (re.compile(r"^(\d+)% kasus musim puncak tercegah$"),
     r"\1% of peak-season cases averted"),
    (re.compile(r"(?<=\d)\s*\bjt\b"), "M"),
    (re.compile(r"\bmiliar\b"), "billion"),
    (re.compile(r"\bjuta\b"), "million"),
    (re.compile(r"\bdkk\."), "et al."),
]


def kolom(nama: object) -> object:
    """Terjemahkan satu nama kolom; yang tak dikenal dibiarkan apa adanya."""
    return KOLOM.get(str(nama), nama)


def nilai(v: str) -> str:
    """Terjemahkan satu isi sel teks."""
    if v in NILAI:
        return NILAI[v]
    hasil = v
    for pola, ganti in POLA:
        hasil = pola.sub(ganti, hasil)
    return hasil


def terjemahkan(df: pd.DataFrame) -> pd.DataFrame:
    """Salinan `df` dengan nama kolom dan isi sel teks berbahasa Inggris."""
    df = df.rename(columns=kolom)
    for kol in df.columns:
        if df[kol].dtype == "object" or pd.api.types.is_string_dtype(df[kol]):
            unik = df[kol].dropna().unique()
            peta = {v: nilai(v) for v in unik if isinstance(v, str)}
            if any(k != n for k, n in peta.items()):
                df[kol] = df[kol].map(lambda v: peta.get(v, v))
    return df


# --------------------------------------------------------------------------
# 3. Prosa lembar "Key figures"
# --------------------------------------------------------------------------

RE_HALAMAN = re.compile(r"\(halaman ([^)]+)\)")


def _halaman(m: re.Match[str]) -> str:
    isi = m.group(1)
    kata = "pages" if re.search(r"\d\s*[,–-]\s*\d", isi) else "page"
    return f"({kata} {isi})"


# Urutan penting: frasa panjang lebih dulu, kata umum paling akhir.
FRASA_MENTAH: list[tuple[str, str]] = [
    # --- angka & satuan ---
    ("≥", ">="),
    ("≤", "<="),
    (r"(\d),(\d+)\s*\bjt\b", r"\1.\2M"),
    (r"(\d),(\d)(?!\d)", r"\1.\2"),
    (r"(?<=\d)\s*\brb\b", "k"),
    (r"(?<=\d)\s*\bjt\b", "M"),
    (r"/100rb\b", "/100k"),
    # --- judul bagian ---
    ("Sudut inovasi: kekeringan x akses air", "Innovation angle: drought x water access"),
    (r"\beksploratif\b", "exploratory"),
    (r"/ inovasi", "/ innovation"),
    ("Dampak dalam dolar", "Impact in dollars"),
    ("Kepala cerita", "Headline"),
    ("Aturan alarm", "Alarm rules"),
    ("Tenggang waktu nyata", "Real-world lead time"),
    ("Prioritas wilayah", "Geographic priorities"),
    ("Standar & tolok ukur", "Standards & benchmarks"),
    ("Kejujuran data", "Data honesty"),
    (r"^Dampak\b", "Impact"),  # "Dampak dalam dolar" sudah tergantikan di atas
    # --- kepala cerita ---
    ("kasusnya lebih tinggi pada bulan El Niño", "record higher cases in El Nino months"),
    ("Efek konsisten antar provinsi", "The effect is consistent across provinces"),
    ("Sinyal BUKAN musim semata", "The signal is NOT seasonality alone"),
    ("korelasi ONI jeda 3-4 terhadap", "the correlation between ONI at lag 3-4 and"),
    ("anomali kasus", "case anomalies"),
    (r"\(musim sudah dibuang\)", "(seasonality removed)"),
    ("uji tanda", "sign test"),
    ("provinsi Indonesia", "Indonesian provinces"),
    ("provinsi Thailand", "Thai provinces"),
    ("El Niño kuat", "Strong El Nino"),
    ("El Niño biasa", "moderate El Nino"),
    ("vs netral", "vs neutral"),
    # --- aturan alarm ---
    ("Musim puncak", "Peak season"),
    ("pada data penuh", "on full data for"),
    ("menyala hanya", "fires in only"),
    (r"([\d.]+)% bulan\b", r"\1% of months"),
    ("Uji luar-sampel", "Out-of-sample test"),
    ("aturan dari", "rule built on"),
    ("diuji buta", "blind-tested on"),
    ("Replikasi Thailand", "Thailand replication"),
    ("suhu 2 bulan lalu di atas normal", "temperature two months earlier above normal"),
    ("lift uji", "test lift"),
    # --- tenggang waktu ---
    ("Episode El Niño", "El Nino episode"),
    ("alarm menyala", "alarm fires"),
    ("kasus melewati P75 pada", "cases crossed P75 in"),
    (r"tenggang (\d+) bulan", r"\1 months of lead time"),
    (r"\bpuncaknya\b", "peaking at"),
    ("Seluruh episode sejak", "All episodes since"),
    ("tercatat di", "are listed in"),
    ("pakai ramalan ONI", "use forecast ONI"),
    (r"\(bukan teramati\)", "(not observed)"),
    ("untuk tenggang lebih panjang lagi", "for even longer lead time"),
    # --- prioritas wilayah ---
    ("Insidens tertinggi", "Highest incidence"),
    ("Bulan puncak tersering", "Most common peak month"),
    (r"dari (\d+) provinsi", r"of \1 provinces"),
    # --- dampak ---
    ("Rata-rata", "Average"),
    ("tahun lengkap", "complete years"),
    ("jatuh di", "falls in"),
    ("Skenario:", "Scenarios:"),
    ("kasus musim puncak tercegah", "of peak-season cases averted"),
    # --- sudut inovasi ---
    ("Efek kekeringan per negara", "Drought effect by country"),
    ("r anomali paling negatif", "most negative anomaly r"),
    ("Moderasi akses perpipaan", "Moderation by piped-water access"),
    ("pengganda El Nino", "El Nino multiplier"),
    ("n kecil", "Small n"),
    ("laporkan sebagai ARAH", "report as a DIRECTION only"),
    ("efek kekeringan", "drought effect at"),
    ("setelah dikontrol ONI", "after controlling for ONI"),
    ("tersisa r parsial", "the partial r is"),
    (r"\bpipa\b", "piped"),
    # --- standar & tolok ukur ---
    ("Ambang ONI", "ONI threshold"),
    ("di aturan kami", "in our rule"),
    ("definisi resmi El Nino NOAA/CPC", "the official NOAA/CPC El Nino definition"),
    ("bukan ambang karangan", "not an invented threshold"),
    ("Terhadap definisi wabah STANDAR", "Against the STANDARD outbreak definition"),
    ("kanal endemis WHO/PAHO", "WHO/PAHO endemic channel"),
    ("kanal endemis", "endemic channel"),
    (r"mean\+2SD 5 tahun", "5-year mean+2SD"),
    (r"(\d+) bulan\s+wabah di 2010\+", r"\1 outbreak months since 2010"),
    ("aturan D:", "rule D:"),
    ("Tolok ukur EWS terpublikasi", "Published EWS benchmarks"),
    ("utk konteks, bukan tandingan langsung", "for context, not a like-for-like contest"),
    ("tinjauan 17 EWS", "review of 17 EWS"),
    ("Rincian:", "Details:"),
    # --- dampak dalam dolar ---
    ("jangkar biaya rawat inap", "hospitalisation cost anchor"),
    ("Jangkar paling konservatif", "Most conservative anchor"),
    ("Pembanding beban nasional dengue", "For comparison, national dengue burden"),
    ("juta/tahun", "million/year"),
    (r"\bmiliar\b", "billion"),
    ("per tahun", "per year"),
    # --- kejujuran data ---
    ("Rekor dalam data", "Record in the data"),
    (r"total (\S+) tak bisa dibandingkan", r"the \1 totals are not comparable"),
    ("lengkap hanya s.d.", "complete only through"),
    ("Insidens hanya", "Incidence only for"),
    ("penyebut resmi BPS", "official BPS denominator"),
    ("di luar itu kasus mentah", "outside that window the numbers are raw cases"),
    ("jangan memeringkat antar wilayah", "do not rank regions"),
    ("Korelasi bukan kausalitas", "Correlation is not causation"),
    ("bingkai sebagai", "frame as"),
    ("mekanisme dari literatur", "mechanism from the literature"),
    # --- kata umum ---
    ("kasus/bulan", "cases/month"),
    ("kasus/tahun", "cases/year"),
    ("El Niño", "El Nino"),
    ("Meksiko", "Mexico"),
    ("Kolombia", "Colombia"),
    ("Kamboja", "Cambodia"),
    ("Singapura", "Singapore"),
    ("Filipina", "Philippines"),
    (r"\bAgu\b", "Aug"),
    (r"\bMei\b", "May"),
    (r"\bOkt\b", "Oct"),
    (r"\bDes\b", "Dec"),
    (r"\bDAN\b", "AND"),
    (r"\bATAU\b", "OR"),
    (r"\bdkk\.", "et al."),
    (r"\bsitasi\b", "cite"),
    (r"\bkorelasi\b", "correlation"),
    (r"\bpresisi\b", "precision"),
    (r"\bsensitivitas\b", "sensitivity"),
    (r"\bspesifisitas\b", "specificity"),
    (r"\bjeda\b", "lag"),
    (r"\bnegara\b", "countries"),
    (r"\bprovinsi\b", "provinces"),
    (r"\bkasus\b", "cases"),
    (r"\bsuhu\b", "temperature"),
    (r"\btetap\b", "is still"),
    (r"\bterhadap\b", "vs"),
    (r"\bbulan\b", "months"),
    (r"\bdan\b", "and"),
    (r"\buntuk\b", "for"),
    (r"\bdi\b", "in"),
]

FRASA: list[tuple[re.Pattern[str], str]] = [
    (re.compile(p), g) for p, g in FRASA_MENTAH
]


def prosa(teks: str) -> str:
    """Terjemahkan satu baris prosa angka kunci (judul bagian atau butir)."""
    teks = RE_HALAMAN.sub(_halaman, teks)
    for pola, ganti in FRASA:
        teks = pola.sub(ganti, teks)
    return teks
