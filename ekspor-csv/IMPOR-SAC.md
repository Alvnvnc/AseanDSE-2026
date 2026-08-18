# Daftar dataset CSV untuk impor ke SAP Analytics Cloud

Dihasilkan otomatis oleh `analisis/ekspor_csv.py` — **jangan sunting manual**,
suntingan akan tertimpa. Perbarui dengan `.venv/bin/python analisis/ekspor_csv.py`.

Seluruh isi CSV (nama kolom dan isi sel kategori) **berbahasa Inggris**, jadi label
yang muncul di grafik SAC bisa langsung masuk storyboard tanpa diedit.
Nama berkas sengaja dibuat **sama persis** dengan nama dataset di
`NASKAH-STORYBOARD.md`, jadi kolom *Name* di layar impor SAC sudah benar sejak awal —
tidak perlu menyalin apa pun kalau nama bawaannya tidak diubah.

## Cara impor (ulangi untuk tiap berkas)

1. SAC → menu ☰ → **Files** → tombol **+ Import** → *Data from a CSV file*
   (atau *Modeler → New Model → Import a CSV file* kalau ingin model, bukan dataset).
2. Pilih berkas dari folder `ekspor-csv/`. Biarkan nama bawaannya.
3. Di layar *Data Settings*: separator **Comma**, encoding **UTF-8**,
   *Use first row as column headers* **aktif**, pemisah desimal **titik**.
4. Betulkan tipe kolom sesuai tabel bagian C di bawah — kolom bertanda ⚠ selalu
   ditebak SAC sebagai *Measure* padahal seharusnya *Dimension*; kalau dibiarkan,
   `year` dan `month` akan **dijumlahkan** dan grafiknya salah.
5. **Create** → tunggu selesai → ulangi untuk berkas berikutnya.

Tiga jebakan yang paling sering bikin grafik salah:

- `date` harus bertipe **Date** (format `yyyy-MM-dd`); `period` biarkan **teks**.
- `month`, `year`, `order`, `lag` harus **Dimension**, bukan Measure — kalau tidak,
  SAC menjumlahkannya. Pengecualian: `status_code` memang dipakai sebagai Measure.
- `month_name` dan `enso_phase_lag4` terurut alfabetis (Apr, Aug, Dec…). Betulkan
  lewat *Sort → by* `month` / `order`, atau pakai kolom angkanya di sumbu.

---

## A. Dataset storyboard — impor sesuai urutan ini

**Delapan yang pertama sudah cukup untuk seluruh 15 halaman.** Sisanya cadangan
untuk pertanyaan juri dan grafik opsional.

| # | Nama dataset (= nama berkas) | Baris × kolom | Ukuran | Halaman | Isi |
|---|---|---|---|---|---|
| 1 | `Monthly series IDN-THA.csv` | 328 × 20 | 39 KB | 6, 7, 10, 11 | The backbone: national monthly series from 2010 — cases, anomaly, lagged ONI/temperature/rainfall, P75 threshold, alarm status. |
| 2 | `ENSO phase - averages.csv` | 5 × 6 | 0.2 KB | 7 | The ace card: mean cases per month in Indonesia by the ENSO phase 4 months earlier (strong El Nino vs neutral). |
| 3 | `Risk calendar IDN.csv` | 420 × 7 | 18 KB | 8, 10 | Share of cases per month per Indonesian province + Peak/Watch/Normal status (status_code 2/1/0). |
| 4 | `Dengue national annual.csv` | 537 × 6 | 22 KB | 2 | Dengue cases by country and year (9 ASEAN countries); the 'complete' column flags the years that are safe to compare. |
| 5 | `Seasonality IDN-THA.csv` | 24 × 7 | 1.3 KB | 5 | Mean cases, rainfall and temperature per calendar month (complete years from 2010) — the seasonal curve. |
| 6 | `Province incidence 18-20.csv` | 34 × 6 | 1.3 KB | 9, 12 | Incidence per 100k population, 2018-2020 ONLY (official BPS denominator). Basis for geographic prioritisation. |
| 7 | `Trigger rules - evaluation.csv` | 4 × 5 | 0.2 KB | 11 | Alarm rules A-D compared on the full 2010-2024 data: coverage, sensitivity, precision, lift. |
| 8 | `Monetary impact.csv` | 3 × 6 | 0.4 KB | 13 | Scenarios of 10/20/30% of peak-season cases averted -> value in US$ and Rp per year. |
| 9 ○ | `Lag correlation - national.csv` | 54 × 5 | 2.1 KB | 6 | Correlation of cases against temperature/rainfall/ONI at lags of 0-8 months, raw series (seasonality still in). |
| 10 ○ | `Lag correlation - anomaly.csv` | 54 × 5 | 2.0 KB | 7 | The same correlations but on ANOMALIES (seasonal effect removed) — evidence the signal is more than seasonality. |
| 11 ○ | `Province consistency IDN.csv` | 34 × 4 | 1.5 KB | 7 | Ratio of cases in El Nino months to other months per province — evidence the effect is not an artefact of national aggregation. |
| 12 ○ | `Risk calendar THA.csv` | 924 × 7 | 36 KB | 8 | The same risk calendar for Thailand's 77 provinces (cross-country replication). |
| 13 ○ | `City flood vulnerability.csv` | 25 × 7 | 1.5 KB | 9 | The 25 ASEAN cities with the largest population inside the 100-year flood zone (2020 & 2030 projection). |
| 14 ○ | `WASH by country.csv` | 10 × 6 | 0.5 KB | 9 | Piped water, drinking water and sanitation access by country (latest year) — the SDG 6 layer. |
| 15 ○ | `Trigger rules - out of sample.csv` | 4 × 7 | 0.3 KB | 12 | Blind test: rules built on 2010-2016, tested on 2017-2024 (Indonesia & Thailand). |
| 16 ○ | `Rules vs endemic channel.csv` | 4 × 6 | 0.2 KB | 12 | The rules tested against the standard WHO/PAHO outbreak definition (endemic channel, 5-year mean+2SD). |
| 17 ○ | `EWS benchmark.csv` | 5 × 5 | 0.4 KB | 12 | Our rule's performance set beside published dengue early warning systems. |
| 18 ○ | `El Nino episodes - lead time.csv` | 5 × 6 | 0.3 KB | 13 | Every El Nino episode since 2009: when the alarm fires, when cases cross P75, how many months of lead time that buys. |
| 19 ○ | `Drought x water access.csv` | 7 × 8 | 0.4 KB | 14 | Test of the drought x water-access innovation angle — EXPLORATORY (n=7) and DROPPED as a causal claim. |
| 20 ○ | `Flood vs dengue tests.csv` | 9 × 6 | 0.9 KB | 14 | Nine tests of the flood/disaster -> dengue link. The raw correlation (+0.66) is a population artefact: it vanishes per capita (-0.14). Reported as a NULL result. |
| 21 ○ | `Flood vs dengue panel.csv` | 99 × 10 | 6.2 KB | 14 | The province-year panel behind those tests (33 provinces x 2018-2020) — feeds the raw-vs-per-capita scatter pair. |

○ = opsional. Ekstra: `Key figures.csv` — seluruh angka yang dikutip storyboard,
dikelompokkan per halaman. Bukan bahan grafik, tapi berguna saat menulis teks slide.

---

## B. Slot grafik → dataset

Nama berkas PNG mengikuti `storyboard/gambar-sac/BACA-DULU.md`; taruh hasil ekspor
SAC di folder itu dan `storyboard/bangun.sh` memasangnya otomatis ke dek.

| Hal | Berkas PNG | Dataset | Resep singkat |
|---|---|---|---|
| 2 | `h02-tren-tahunan.png` | `Dengue national annual` | Line — cases per year, filter complete = True |
| 2 | `h02-per-negara.png` | `Dengue national annual` | Bar horizontal — cases per country, latest complete year |
| 3 | `h03-alur.png` | — | Shapes + Text, tanpa dataset |
| 5 | `h05-musiman-idn.png` | `Seasonality IDN-THA` | Combination — mean_cases (bar) vs mean_rain_mm (line), filter country = Indonesia |
| 5 | `h05-musiman-tha.png` | `Seasonality IDN-THA` | Sama, filter country = Thailand |
| 6 | `h06-heatmap-jeda.png` | `Lag correlation - national` | Heat map — predictor x lag, measure r |
| 6 | `h06-scatter-suhu.png` | `Monthly series IDN-THA` | Scatter — X temp_c_lag2, Y cases, warna enso_phase_lag4 |
| 7 | `h07-fase-enso.png` | `ENSO phase - averages` | Bar — mean_cases_per_month per enso_phase_lag4, sort by order |
| 7 | `h07-anomali.png` | `Lag correlation - anomaly` | Heat map — sama seperti h06 tapi pada anomali |
| 8 | `h08-kalender-idn.png` | `Risk calendar IDN` | Heat map — province x month, measure share_percent |
| 8 | `h08-kalender-tha.png` | `Risk calendar THA` | Sama untuk 77 provinsi Thailand |
| 9 | `h09-insidens.png` | `Province incidence 18-20` | Bar horizontal — measure mean, 10 teratas + 3 terbawah |
| 9 | `h09-wash.png` | `WASH by country` | Bar — piped_water_%, urut menaik |
| 9 | `h09-banjir.png` | `City flood vulnerability` | Bar — exposed_2020, 8 kota teratas |
| 10 | `h10-kalender-prioritas.png` | `Risk calendar IDN` | Heat map — measure status_code, filter 6 provinsi prioritas |
| 10 | `h10-deret-alarm.png` | `Monthly series IDN-THA` | Time series — cases + reference line threshold_p75, warna alarm_el_nino |
| 11 | `h11-deret-aturan.png` | `Monthly series IDN-THA` | Time series — sama, warna alarm_rule_d |
| 11 | `h11-aturan.png` | `Trigger rules - evaluation` | Bar — precision_% dan alarm_coverage_% per rule |
| 12 | `h12-luar-sampel.png` | `Trigger rules - out of sample` | Bar — precision_%, sensitivity_% per period, kelompok country |
| 12 | `h12-tolok-ukur.png` | `EWS benchmark` | Table widget apa adanya (5 baris) |
| 13 | `h13-dampak.png` | `Monetary impact` | Bar bertingkat — dua measure biaya per scenario |
| 13 | `h13-tenggang.png` | `El Nino episodes - lead time` | Table — episode, alarm_fires, cases_cross_p75, lead_time_months |
| 14 | `h14-kekeringan.png` | `Drought x water access` | Scatter — X piped_water_%, Y r_drought, ukuran nino_multiplier, TANPA garis tren |

Cadangan (tanpa slot tetap, siapkan kalau ditanya juri):

- `Province consistency IDN` — Bar horizontal — ratio_nino_vs_other per province, reference line di 1,0 (halaman 7)
- `Rules vs endemic channel` — Table — aturan vs definisi wabah WHO/PAHO (halaman 12)
- `Flood vs dengue panel` — Dua scatter berdampingan (halaman 14) — kiri X `disaster_events` Y `cases` (tampak kuat), kanan X `disaster_events_per_100k` Y `incidence_per_100k` (datar). Judulnya yang bercerita, bukan garis trennya
- `Flood vs dengue tests` — Table — 9 uji dengan kolom `verdict` (halaman 14)

---

## C. Tipe kolom per dataset

⚠ = angka yang sebenarnya label; **wajib** diubah dari Measure ke Dimension di layar impor.

### Monthly series IDN-THA

`ekspor-csv/Monthly series IDN-THA.csv` · 328 baris × 20 kolom · 39 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `country` | Dimension |  |
| `period` | Dimension | biarkan teks (yyyy-MM), jangan diubah jadi Date |
| `date` | **Date** | ubah tipe ke Date, format yyyy-MM-dd |
| `year` | **Dimension** ⚠ |  |
| `month` | **Dimension** ⚠ |  |
| `month_name` | Dimension | urutkan lewat Sort by `month`, jangan alfabetis |
| `cases` | Measure |  |
| `cases_anomaly_z` | Measure |  |
| `threshold_p75` | Measure |  |
| `peak_case_month` | Dimension |  |
| `alarm_rule_d` | Dimension |  |
| `alarm_el_nino` | Dimension |  |
| `enso_phase_lag4` | Dimension | urutkan lewat Sort by `order` (ada di ENSO phase - averages) |
| `oni` | Measure |  |
| `oni_lag3` | Measure |  |
| `oni_lag4` | Measure |  |
| `temp_c` | Measure |  |
| `temp_c_lag2` | Measure |  |
| `rain_mm` | Measure |  |
| `rain_mm_lag1` | Measure |  |

### ENSO phase - averages

`ekspor-csv/ENSO phase - averages.csv` · 5 baris × 6 kolom · 0.2 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `enso_phase_lag4` | Dimension | urutkan lewat Sort by `order` (ada di ENSO phase - averages) |
| `order` | **Dimension** ⚠ |  |
| `mean_cases_per_month` | Measure |  |
| `n_months` | Measure |  |
| `ratio_vs_neutral` | Measure |  |
| `enough_data` | Dimension |  |

### Risk calendar IDN

`ekspor-csv/Risk calendar IDN.csv` · 420 baris × 7 kolom · 18 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `country` | Dimension |  |
| `province` | Dimension |  |
| `month` | **Dimension** ⚠ |  |
| `month_name` | Dimension | urutkan lewat Sort by `month`, jangan alfabetis |
| `share_percent` | Measure |  |
| `status` | Dimension |  |
| `status_code` | Measure | biarkan **Measure** — jadi warna heat map halaman 10 (0 Normal / 1 Watch / 2 Peak) |

### Dengue national annual

`ekspor-csv/Dengue national annual.csv` · 537 baris × 6 kolom · 22 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `country` | Dimension |  |
| `iso3` | Dimension |  |
| `year` | **Dimension** ⚠ |  |
| `cases` | Measure |  |
| `source_resolution` | Dimension |  |
| `complete` | Measure | filter = True sebelum membandingkan antar negara |

### Seasonality IDN-THA

`ekspor-csv/Seasonality IDN-THA.csv` · 24 baris × 7 kolom · 1.3 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `country` | Dimension |  |
| `month` | **Dimension** ⚠ |  |
| `month_name` | Dimension | urutkan lewat Sort by `month`, jangan alfabetis |
| `mean_cases` | Measure |  |
| `mean_rain_mm` | Measure |  |
| `mean_temp_c` | Measure |  |
| `complete_years_window` | Dimension |  |

### Province incidence 18-20

`ekspor-csv/Province incidence 18-20.csv` · 34 baris × 6 kolom · 1.3 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `province` | Dimension |  |
| `2018` | Measure | format lebar: insidens per 100k tahun itu; untuk grafik peringkat pakai `mean` |
| `2019` | Measure | idem |
| `2020` | Measure | idem |
| `mean` | Measure |  |
| `peak_month` | Dimension | teks, tidak ada kolom angkanya — urutkan manual kalau dipakai di sumbu |

### Trigger rules - evaluation

`ekspor-csv/Trigger rules - evaluation.csv` · 4 baris × 5 kolom · 0.2 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `rule` | Dimension |  |
| `alarm_coverage_%` | Measure |  |
| `sensitivity_%` | Measure |  |
| `precision_%` | Measure |  |
| `lift` | Measure |  |

### Monetary impact

`ekspor-csv/Monetary impact.csv` · 3 baris × 6 kolom · 0.4 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `scenario` | Dimension |  |
| `cases/year` | Measure |  |
| `conservative (avg episode, US$90)` | Dimension |  |
| `hospitalisation low (US$316)` | Dimension |  |
| `hospitalisation high (US$791)` | Dimension |  |
| `Rp/year (hospitalisation anchor)` | Dimension |  |

### Lag correlation - national

`ekspor-csv/Lag correlation - national.csv` · 54 baris × 5 kolom · 2.1 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `iso3` | Dimension |  |
| `predictor` | Dimension |  |
| `lag` | **Dimension** ⚠ |  |
| `r` | Measure |  |
| `n_months` | Measure |  |

### Lag correlation - anomaly

`ekspor-csv/Lag correlation - anomaly.csv` · 54 baris × 5 kolom · 2.0 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `iso3` | Dimension |  |
| `predictor` | Dimension |  |
| `lag` | **Dimension** ⚠ |  |
| `r` | Measure |  |
| `n_months` | Measure |  |

### Province consistency IDN

`ekspor-csv/Province consistency IDN.csv` · 34 baris × 4 kolom · 1.5 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `province` | Dimension |  |
| `ratio_nino_vs_other` | Measure |  |
| `n_months_nino` | Measure |  |
| `direction` | Dimension |  |

### Risk calendar THA

`ekspor-csv/Risk calendar THA.csv` · 924 baris × 7 kolom · 36 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `country` | Dimension |  |
| `province` | Dimension |  |
| `month` | **Dimension** ⚠ |  |
| `month_name` | Dimension | urutkan lewat Sort by `month`, jangan alfabetis |
| `share_percent` | Measure |  |
| `status` | Dimension |  |
| `status_code` | Measure | biarkan **Measure** — jadi warna heat map halaman 10 (0 Normal / 1 Watch / 2 Peak) |

### City flood vulnerability

`ekspor-csv/City flood vulnerability.csv` · 25 baris × 7 kolom · 1.5 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `country` | Dimension |  |
| `city` | Dimension |  |
| `city_population_2025` | Measure |  |
| `exposed_2020` | Measure |  |
| `percent_2020` | Measure |  |
| `exposed_2030` | Measure |  |
| `growth_2020_2030_%` | Measure |  |

### WASH by country

`ekspor-csv/WASH by country.csv` · 10 baris × 6 kolom · 0.5 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `country` | Dimension |  |
| `data_year` | **Dimension** ⚠ |  |
| `piped_water_%` | Measure |  |
| `at_least_basic_water_%` | Measure |  |
| `safely_managed_water_%` | Measure |  |
| `at_least_basic_sanitation_%` | Measure |  |

### Trigger rules - out of sample

`ekspor-csv/Trigger rules - out of sample.csv` · 4 baris × 7 kolom · 0.3 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `period` | Dimension | biarkan teks (yyyy-MM), jangan diubah jadi Date |
| `n_months` | Measure |  |
| `coverage_%` | Measure |  |
| `sensitivity_%` | Measure |  |
| `precision_%` | Measure |  |
| `lift` | Measure |  |
| `country` | Dimension |  |

### Rules vs endemic channel

`ekspor-csv/Rules vs endemic channel.csv` · 4 baris × 6 kolom · 0.2 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `rule` | Dimension |  |
| `coverage_%` | Measure |  |
| `sensitivity_%` | Measure |  |
| `specificity_%` | Measure |  |
| `precision_%` | Measure |  |
| `lift` | Measure |  |

### EWS benchmark

`ekspor-csv/EWS benchmark.csv` · 5 baris × 5 kolom · 0.4 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `system` | Dimension |  |
| `sensitivity` | Dimension |  |
| `specificity` | Dimension |  |
| `precision/PPV` | Dimension |  |
| `source` | Dimension |  |

### El Nino episodes - lead time

`ekspor-csv/El Nino episodes - lead time.csv` · 5 baris × 6 kolom · 0.3 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `episode` | Dimension |  |
| `oni_peak` | Measure |  |
| `alarm_fires` | Dimension |  |
| `cases_cross_p75` | Dimension |  |
| `lead_time_months` | Measure |  |
| `peak_cases_12m` | Measure |  |

### Drought x water access

`ekspor-csv/Drought x water access.csv` · 7 baris × 8 kolom · 0.4 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `country` | Dimension |  |
| `window` | Dimension |  |
| `r_drought` | Measure |  |
| `lag_drought` | **Dimension** ⚠ |  |
| `r_oni_lag4` | Measure |  |
| `nino_multiplier` | Measure |  |
| `piped_water_%` | Measure |  |
| `piped_water_year` | **Dimension** ⚠ |  |

### Flood vs dengue tests

`ekspor-csv/Flood vs dengue tests.csv` · 9 baris × 6 kolom · 0.9 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `test` | Dimension |  |
| `denominator` | Dimension | Raw vs Per 100k — pakai sebagai warna/kelompok di grafik r |
| `r` | Measure |  |
| `p_value` | Measure |  |
| `n` | Measure |  |
| `verdict` | Dimension | kolom penutup cerita halaman 14 — tampilkan apa adanya di table widget |

### Flood vs dengue panel

`ekspor-csv/Flood vs dengue panel.csv` · 99 baris × 10 kolom · 6.2 KB

| Kolom | Tipe di SAC | Catatan |
|---|---|---|
| `province` | Dimension |  |
| `year` | **Dimension** ⚠ |  |
| `cases` | Measure |  |
| `population` | Measure |  |
| `n_months` | Measure |  |
| `incidence_per_100k` | Measure |  |
| `houses_flooded` | Measure |  |
| `disaster_events` | Measure |  |
| `houses_flooded_per_100k` | Measure |  |
| `disaster_events_per_100k` | Measure |  |

---

## D. Himpunan data sumber (`ekspor-csv/sumber/`)

Tidak perlu untuk 15 halaman — ini bahan mentah kalau ingin membuat grafik sendiri di
SAC atau menjawab pertanyaan yang tidak terjawab tabel di atas. Isinya sama dengan
`data/siap-sac/*.csv`, hanya diterjemahkan ke bahasa Inggris.

Aturan tipe kolom yang sama berlaku di sini: `year`, `month`, `province_code`, dan
`district_city_code` harus diubah jadi **Dimension**. Dua berkas terbesar (5–7 MB)
perlu satu-dua menit di layar impor SAC — impor hanya kalau memang dipakai.

| Nama dataset (= nama berkas) | Baris × kolom | Ukuran | Asal | Isi |
|---|---|---|---|---|
| ⭐ `Dengue climate monthly panel.csv` | 55,329 × 21 | 6.7 MB | `dengue_iklim_bulanan.csv` | Main analysis table: monthly cases + temperature/rainfall/ONI at lags 0-4 months. |
|  `City air quality ASEAN.csv` | 622 × 8 | 30 KB | `kota_asean_kualitas_udara.csv` | PM2.5/PM10/NO2 concentrations in ASEAN cities (WHO Ambient Air Quality). |
|  `City flood exposure ASEAN.csv` | 30,348 × 8 | 2.7 MB | `kota_asean_paparan_banjir.csv` | ASEAN city population exposed to flooding (GHSL). |
|  `Climate monthly ASEAN.csv` | 9,000 × 7 | 374 KB | `iklim_bulanan_asean.csv` | Monthly temperature and rainfall by country, 1950-present. |
|  `Dengue ASEAN raw.csv` | 70,397 × 11 | 5.8 MB | `dengue_asean.csv` | Raw ASEAN dengue cases from OpenDengue (all space & time resolutions). |
|  `Disasters district Indonesia.csv` | 17,500 × 8 | 1.3 MB | `bencana_kabkota_indonesia.csv` | Disaster events per Indonesian district/city (BNPB). |
|  `ENSO ONI monthly.csv` | 918 × 5 | 27 KB | `enso_oni_bulanan.csv` | Monthly NOAA/CPC ONI index + ENSO phase (official 0.5 threshold). |
|  `Population province Indonesia.csv` | 140 × 6 | 9.4 KB | `penduduk_provinsi_indonesia.csv` | Indonesian province population (BPS WebAPI) — incidence denominator 2018-2020. |
|  `WASH health facilities ASEAN.csv` | 5,625 × 7 | 334 KB | `wash_fasyankes_asean.csv` | Water & sanitation access in health-care facilities (JMP WHO/UNICEF). |
|  `WASH households ASEAN.csv` | 8,692 × 8 | 551 KB | `wash_rumahtangga_asean.csv` | Household drinking water & sanitation access (JMP WHO/UNICEF). |
|  `Waste district Indonesia.csv` | 514 × 18 | 79 KB | `sampah_kabkota_indonesia.csv` | Waste generation & management per district/city (SIPSN KLHK). |

⭐ = tabel utama analisis (satu baris = provinsi-bulan, jeda 0–3 bulan sudah dihitung).
Kunci gabung antar dataset: `iso3` + `year` (+ `period` untuk dengue × iklim).

