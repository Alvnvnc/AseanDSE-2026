#!/usr/bin/env python3
"""Ekspor semua data proyek ke CSV berbahasa Inggris, satu berkas per dataset SAC.

SAP Analytics Cloud mengimpor **satu dataset per berkas**, jadi buku kerja
`ekspor-xlsx/ASEAN_DSE_hasil_analisis.xlsx` (21 lembar) tidak bisa dipakai
langsung — lembarnya harus dipecah dulu. Skrip ini memecahnya:

1. `ekspor-csv/<Nama dataset>.csv` — 19 tabel siap grafik. **Nama berkas sengaja
   sama persis dengan nama dataset di `NASKAH-STORYBOARD.md`**, supaya kolom
   *Name* di layar impor SAC terisi otomatis dan resep grafik di naskah langsung
   cocok tanpa diterjemahkan lagi.
2. `ekspor-csv/sumber/<Nama>.csv` — 11 himpunan data sumber (isi sama dengan
   `data/siap-sac/*.csv` tapi berbahasa Inggris), untuk eksplorasi sendiri di SAC.
3. `ekspor-csv/IMPOR-SAC.md` — daftar siap salin: urutan impor, nama dataset,
   grafik mana memakai dataset mana, dan tipe kolom yang harus dibetulkan di layar
   impor. Berkas ini **dihasilkan skrip** — jangan disunting manual.

Definisi tabel, penerjemahan, dan urutan halaman dipakai ulang dari
`ekspor_xlsx.py`, jadi CSV dan XLSX tidak mungkin berbeda isi.

Jalankan: .venv/bin/python analisis/ekspor_csv.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ekspor_xlsx as xl  # noqa: E402
import istilah_en as en  # noqa: E402

AKAR = xl.AKAR
TUJUAN = AKAR / "ekspor-csv"
SUMBER = TUJUAN / "sumber"

# --------------------------------------------------------------------------
# Urutan impor — delapan pertama sudah menutup 15 halaman (NASKAH-STORYBOARD.md)
# --------------------------------------------------------------------------
URUTAN_IMPOR: list[str] = [
    # wajib
    "Monthly series IDN-THA",
    "ENSO phase - averages",
    "Risk calendar IDN",
    "Dengue national annual",
    "Seasonality IDN-THA",
    "Province incidence 18-20",
    "Trigger rules - evaluation",
    "Monetary impact",
    # opsional / cadangan pertanyaan juri
    "Lag correlation - national",
    "Lag correlation - anomaly",
    "Province consistency IDN",
    "Risk calendar THA",
    "City flood vulnerability",
    "WASH by country",
    "Trigger rules - out of sample",
    "Rules vs endemic channel",
    "EWS benchmark",
    "El Nino episodes - lead time",
    "Drought x water access",
    "Flood vs dengue tests",
    "Flood vs dengue panel",
]
WAJIB = 8

# Slot PNG di storyboard/gambar-sac/ -> dataset yang memberinya angka.
GRAFIK: list[tuple[str, str, str, str]] = [
    ("2", "h02-tren-tahunan.png", "Dengue national annual", "Line — cases per year, filter complete = True"),
    ("2", "h02-per-negara.png", "Dengue national annual", "Bar horizontal — cases per country, latest complete year"),
    ("3", "h03-alur.png", "—", "Shapes + Text, tanpa dataset"),
    ("5", "h05-musiman-idn.png", "Seasonality IDN-THA", "Combination — mean_cases (bar) vs mean_rain_mm (line), filter country = Indonesia"),
    ("5", "h05-musiman-tha.png", "Seasonality IDN-THA", "Sama, filter country = Thailand"),
    ("6", "h06-heatmap-jeda.png", "Lag correlation - national", "Heat map — predictor x lag, measure r"),
    ("6", "h06-scatter-suhu.png", "Monthly series IDN-THA", "Scatter — X temp_c_lag2, Y cases, warna enso_phase_lag4"),
    ("7", "h07-fase-enso.png", "ENSO phase - averages", "Bar — mean_cases_per_month per enso_phase_lag4, sort by order"),
    ("7", "h07-anomali.png", "Lag correlation - anomaly", "Heat map — sama seperti h06 tapi pada anomali"),
    ("8", "h08-kalender-idn.png", "Risk calendar IDN", "Heat map — province x month, measure share_percent"),
    ("8", "h08-kalender-tha.png", "Risk calendar THA", "Sama untuk 77 provinsi Thailand"),
    ("9", "h09-insidens.png", "Province incidence 18-20", "Bar horizontal — measure mean, 10 teratas + 3 terbawah"),
    ("9", "h09-wash.png", "WASH by country", "Bar — piped_water_%, urut menaik"),
    ("9", "h09-banjir.png", "City flood vulnerability", "Bar — exposed_2020, 8 kota teratas"),
    ("10", "h10-kalender-prioritas.png", "Risk calendar IDN", "Heat map — measure status_code, filter 6 provinsi prioritas"),
    ("10", "h10-deret-alarm.png", "Monthly series IDN-THA", "Time series — cases + reference line threshold_p75, warna alarm_el_nino"),
    ("11", "h11-deret-aturan.png", "Monthly series IDN-THA", "Time series — sama, warna alarm_rule_d"),
    ("11", "h11-aturan.png", "Trigger rules - evaluation", "Bar — precision_% dan alarm_coverage_% per rule"),
    ("12", "h12-luar-sampel.png", "Trigger rules - out of sample", "Bar — precision_%, sensitivity_% per period, kelompok country"),
    ("12", "h12-tolok-ukur.png", "EWS benchmark", "Table widget apa adanya (5 baris)"),
    ("13", "h13-dampak.png", "Monetary impact", "Bar bertingkat — dua measure biaya per scenario"),
    ("13", "h13-tenggang.png", "El Nino episodes - lead time", "Table — episode, alarm_fires, cases_cross_p75, lead_time_months"),
    ("14", "h14-kekeringan.png", "Drought x water access", "Scatter — X piped_water_%, Y r_drought, ukuran nino_multiplier, TANPA garis tren"),
]

# Cadangan yang tidak punya slot PNG tapi disiapkan untuk pertanyaan juri.
GRAFIK_CADANGAN: list[tuple[str, str]] = [
    ("Province consistency IDN", "Bar horizontal — ratio_nino_vs_other per province, reference line di 1,0 (halaman 7)"),
    ("Rules vs endemic channel", "Table — aturan vs definisi wabah WHO/PAHO (halaman 12)"),
    ("Flood vs dengue panel", "Dua scatter berdampingan (halaman 14) — kiri X `disaster_events` Y `cases` "
     "(tampak kuat), kanan X `disaster_events_per_100k` Y `incidence_per_100k` (datar). "
     "Judulnya yang bercerita, bukan garis trennya"),
    ("Flood vs dengue tests", "Table — 9 uji dengan kolom `verdict` (halaman 14)"),
]

# --------------------------------------------------------------------------
# Tipe kolom di layar impor SAC
# --------------------------------------------------------------------------
KOLOM_TANGGAL = {"date", "start_date", "end_date"}
# Angka yang sebenarnya label: SAC menebaknya Measure, harus diubah jadi Dimension.
KOLOM_DIMENSI_ANGKA = {
    "year", "month", "order", "lag", "province_code",
    "district_city_code", "peak_month", "piped_water_year", "lag_drought", "data_year",
}
CATATAN_KOLOM = {
    "month_name": "urutkan lewat Sort by `month`, jangan alfabetis",
    "enso_phase_lag4": "urutkan lewat Sort by `order` (ada di ENSO phase - averages)",
    "enso_phase": "urutkan La Nina -> Neutral -> El Nino secara manual",
    "period": "biarkan teks (yyyy-MM), jangan diubah jadi Date",
    "date": "ubah tipe ke Date, format yyyy-MM-dd",
    "status_code": "biarkan **Measure** — jadi warna heat map halaman 10 (0 Normal / 1 Watch / 2 Peak)",
    "complete": "filter = True sebelum membandingkan antar negara",
    "verdict": "kolom penutup cerita halaman 14 — tampilkan apa adanya di table widget",
    "denominator": "Raw vs Per 100k — pakai sebagai warna/kelompok di grafik r",
    "peak_month": "teks, tidak ada kolom angkanya — urutkan manual kalau dipakai di sumbu",
    "2018": "format lebar: insidens per 100k tahun itu; untuk grafik peringkat pakai `mean`",
    "2019": "idem",
    "2020": "idem",
}

KETERANGAN_SUMBER_EN = {
    "dengue_iklim_bulanan": ("Dengue climate monthly panel", "⭐"),
    "dengue_asean": ("Dengue ASEAN raw", ""),
    "iklim_bulanan_asean": ("Climate monthly ASEAN", ""),
    "enso_oni_bulanan": ("ENSO ONI monthly", ""),
    "penduduk_provinsi_indonesia": ("Population province Indonesia", ""),
    "wash_rumahtangga_asean": ("WASH households ASEAN", ""),
    "wash_fasyankes_asean": ("WASH health facilities ASEAN", ""),
    "bencana_kabkota_indonesia": ("Disasters district Indonesia", ""),
    "sampah_kabkota_indonesia": ("Waste district Indonesia", ""),
    "kota_asean_paparan_banjir": ("City flood exposure ASEAN", ""),
    "kota_asean_kualitas_udara": ("City air quality ASEAN", ""),
}


def tipe_sac(df: pd.DataFrame, kolom: str) -> str:
    if kolom in KOLOM_TANGGAL:
        return "**Date**"
    if pd.api.types.is_numeric_dtype(df[kolom]):
        # angka yang sebenarnya label — SAC selalu menebaknya Measure
        return "**Dimension** ⚠" if kolom in KOLOM_DIMENSI_ANGKA else "Measure"
    return "Dimension"


def tulis_csv(df: pd.DataFrame, berkas: Path) -> dict:
    """Tulis satu CSV berbahasa Inggris siap impor SAC."""
    df = en.terjemahkan(df)
    berkas.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(berkas, index=False, encoding="utf-8",
              date_format="%Y-%m-%d", lineterminator="\n")
    return {"nama": berkas.stem, "berkas": berkas, "baris": len(df),
            "kolom": df.shape[1], "byte": berkas.stat().st_size, "df": df}


def ukuran(byte: int) -> str:
    if byte >= 1e6:
        return f"{byte/1e6:.1f} MB"
    return f"{byte/1e3:.0f} KB" if byte >= 1e4 else f"{byte/1e3:.1f} KB"


def ekspor_storyboard() -> dict[str, dict]:
    """19 tabel siap grafik, satu CSV per dataset."""
    grafik = xl.lembar_grafik()
    meta: dict[str, dict] = {}
    for asal, lembar, halaman, ket in xl.URUTAN:
        if asal == "hitung":
            df, sumber = grafik[lembar], "dihitung ulang dari data/siap-sac/"
        else:
            nama = asal.split(":", 1)[1]
            df = xl.rapikan(pd.read_csv(xl.KELUARAN / f"{nama}.csv"), nama)
            sumber = f"analisis/keluaran/{nama}.csv"
        info = tulis_csv(df, TUJUAN / f"{lembar}.csv")
        info.update(halaman=halaman, keterangan=ket, sumber=sumber)
        meta[lembar] = info
    # bonus: seluruh angka yang dikutip storyboard, sebagai rujukan (bukan bahan grafik)
    tulis_csv(xl.baca_angka_kunci(), TUJUAN / "Key figures.csv")
    return meta


def ekspor_sumber() -> list[dict]:
    """11 himpunan data sumber, isi sama dengan data/siap-sac/ tapi berbahasa Inggris."""
    hasil = []
    for csv in sorted(xl.SIAP_SAC.glob("*.csv")):
        nama_en, tanda = KETERANGAN_SUMBER_EN.get(csv.stem, (csv.stem, ""))
        df = pd.read_csv(csv, low_memory=False)
        info = tulis_csv(df, SUMBER / f"{nama_en}.csv")
        info.update(asal=csv.name, tanda=tanda,
                    keterangan=xl.KETERANGAN_SAC.get(csv.stem, ""))
        hasil.append(info)
    return hasil


def tabel_kolom(info: dict) -> list[str]:
    baris = [f"### {info['nama']}", "",
             f"`{info['berkas'].relative_to(AKAR)}` · {info['baris']:,} baris × "
             f"{info['kolom']} kolom · {ukuran(info['byte'])}", "",
             "| Kolom | Tipe di SAC | Catatan |", "|---|---|---|"]
    df = info["df"]
    for kol in df.columns:
        baris.append(f"| `{kol}` | {tipe_sac(df, kol)} | {CATATAN_KOLOM.get(kol, '')} |")
    baris.append("")
    return baris


def tulis_md(meta: dict[str, dict], sumber: list[dict]) -> Path:
    b: list[str] = []
    t = b.append
    t("# Daftar dataset CSV untuk impor ke SAP Analytics Cloud")
    t("")
    t("Dihasilkan otomatis oleh `analisis/ekspor_csv.py` — **jangan sunting manual**,")
    t("suntingan akan tertimpa. Perbarui dengan `.venv/bin/python analisis/ekspor_csv.py`.")
    t("")
    t("Seluruh isi CSV (nama kolom dan isi sel kategori) **berbahasa Inggris**, jadi label")
    t("yang muncul di grafik SAC bisa langsung masuk storyboard tanpa diedit.")
    t("Nama berkas sengaja dibuat **sama persis** dengan nama dataset di")
    t("`NASKAH-STORYBOARD.md`, jadi kolom *Name* di layar impor SAC sudah benar sejak awal —")
    t("tidak perlu menyalin apa pun kalau nama bawaannya tidak diubah.")
    t("")
    t("## Cara impor (ulangi untuk tiap berkas)")
    t("")
    t("1. SAC → menu ☰ → **Files** → tombol **+ Import** → *Data from a CSV file*")
    t("   (atau *Modeler → New Model → Import a CSV file* kalau ingin model, bukan dataset).")
    t("2. Pilih berkas dari folder `ekspor-csv/`. Biarkan nama bawaannya.")
    t("3. Di layar *Data Settings*: separator **Comma**, encoding **UTF-8**,")
    t("   *Use first row as column headers* **aktif**, pemisah desimal **titik**.")
    t("4. Betulkan tipe kolom sesuai tabel bagian C di bawah — kolom bertanda ⚠ selalu")
    t("   ditebak SAC sebagai *Measure* padahal seharusnya *Dimension*; kalau dibiarkan,")
    t("   `year` dan `month` akan **dijumlahkan** dan grafiknya salah.")
    t("5. **Create** → tunggu selesai → ulangi untuk berkas berikutnya.")
    t("")
    t("Tiga jebakan yang paling sering bikin grafik salah:")
    t("")
    t("- `date` harus bertipe **Date** (format `yyyy-MM-dd`); `period` biarkan **teks**.")
    t("- `month`, `year`, `order`, `lag` harus **Dimension**, bukan Measure — kalau tidak,")
    t("  SAC menjumlahkannya. Pengecualian: `status_code` memang dipakai sebagai Measure.")
    t("- `month_name` dan `enso_phase_lag4` terurut alfabetis (Apr, Aug, Dec…). Betulkan")
    t("  lewat *Sort → by* `month` / `order`, atau pakai kolom angkanya di sumbu.")
    t("")
    t("---")
    t("")
    t("## A. Dataset storyboard — impor sesuai urutan ini")
    t("")
    t(f"**Delapan yang pertama sudah cukup untuk seluruh 15 halaman.** Sisanya cadangan")
    t("untuk pertanyaan juri dan grafik opsional.")
    t("")
    t("| # | Nama dataset (= nama berkas) | Baris × kolom | Ukuran | Halaman | Isi |")
    t("|---|---|---|---|---|---|")
    for i, nama in enumerate(URUTAN_IMPOR, start=1):
        m = meta[nama]
        tanda = "" if i <= WAJIB else " ○"
        t(f"| {i}{tanda} | `{nama}.csv` | {m['baris']:,} × {m['kolom']} | "
          f"{ukuran(m['byte'])} | {m['halaman']} | {m['keterangan']} |")
    t("")
    t("○ = opsional. Ekstra: `Key figures.csv` — seluruh angka yang dikutip storyboard,")
    t("dikelompokkan per halaman. Bukan bahan grafik, tapi berguna saat menulis teks slide.")
    t("")
    t("---")
    t("")
    t("## B. Slot grafik → dataset")
    t("")
    t("Nama berkas PNG mengikuti `storyboard/gambar-sac/BACA-DULU.md`; taruh hasil ekspor")
    t("SAC di folder itu dan `storyboard/bangun.sh` memasangnya otomatis ke dek.")
    t("")
    t("| Hal | Berkas PNG | Dataset | Resep singkat |")
    t("|---|---|---|---|")
    for hal, png, ds, resep in GRAFIK:
        nama_ds = "—" if ds == "—" else f"`{ds}`"
        t(f"| {hal} | `{png}` | {nama_ds} | {resep} |")
    t("")
    t("Cadangan (tanpa slot tetap, siapkan kalau ditanya juri):")
    t("")
    for ds, resep in GRAFIK_CADANGAN:
        t(f"- `{ds}` — {resep}")
    t("")
    t("---")
    t("")
    t("## C. Tipe kolom per dataset")
    t("")
    t("⚠ = angka yang sebenarnya label; **wajib** diubah dari Measure ke Dimension di layar impor.")
    t("")
    for nama in URUTAN_IMPOR:
        b.extend(tabel_kolom(meta[nama]))
    t("---")
    t("")
    t("## D. Himpunan data sumber (`ekspor-csv/sumber/`)")
    t("")
    t("Tidak perlu untuk 15 halaman — ini bahan mentah kalau ingin membuat grafik sendiri di")
    t("SAC atau menjawab pertanyaan yang tidak terjawab tabel di atas. Isinya sama dengan")
    t("`data/siap-sac/*.csv`, hanya diterjemahkan ke bahasa Inggris.")
    t("")
    t("Aturan tipe kolom yang sama berlaku di sini: `year`, `month`, `province_code`, dan")
    t("`district_city_code` harus diubah jadi **Dimension**. Dua berkas terbesar (5–7 MB)")
    t("perlu satu-dua menit di layar impor SAC — impor hanya kalau memang dipakai.")
    t("")
    t("| Nama dataset (= nama berkas) | Baris × kolom | Ukuran | Asal | Isi |")
    t("|---|---|---|---|---|")
    for s in sorted(sumber, key=lambda x: (x["tanda"] == "", x["nama"])):
        t(f"| {s['tanda']} `{s['nama']}.csv` | {s['baris']:,} × {s['kolom']} | "
          f"{ukuran(s['byte'])} | `{s['asal']}` | {s['keterangan']} |")
    t("")
    t("⭐ = tabel utama analisis (satu baris = provinsi-bulan, jeda 0–3 bulan sudah dihitung).")
    t("Kunci gabung antar dataset: `iso3` + `year` (+ `period` untuk dengue × iklim).")
    t("")
    berkas = TUJUAN / "IMPOR-SAC.md"
    berkas.write_text("\n".join(b) + "\n", encoding="utf-8")
    return berkas


if __name__ == "__main__":
    TUJUAN.mkdir(parents=True, exist_ok=True)
    print("Dataset storyboard (siap grafik, satu berkas per dataset SAC):")
    meta = ekspor_storyboard()
    hilang = set(URUTAN_IMPOR) ^ set(meta)
    if hilang:
        raise SystemExit(f"URUTAN_IMPOR tidak sinkron dengan ekspor_xlsx.URUTAN: {hilang}")
    for i, nama in enumerate(URUTAN_IMPOR, start=1):
        m = meta[nama]
        print(f"  {i:>2}. {nama + '.csv':<38} {m['baris']:>7,} baris × {m['kolom']:>2} "
              f"kolom  {ukuran(m['byte']):>8}")
    print("\nHimpunan data sumber (bahasa Inggris):")
    sumber = ekspor_sumber()
    for s in sumber:
        print(f"      {s['nama'] + '.csv':<38} {s['baris']:>7,} baris × {s['kolom']:>2} "
              f"kolom  {ukuran(s['byte']):>8}")
    berkas = tulis_md(meta, sumber)
    print(f"\nDaftar siap salin: {berkas.relative_to(AKAR)}")
    print("Selesai.")
