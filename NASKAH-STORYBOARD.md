# Naskah storyboard ASEAN DSE 2026 — siap eksekusi di SAP Analytics Cloud

Teks slide dalam **bahasa Inggris** (salin apa adanya ke SAC); catatan kerja, resep grafik,
dan antisipasi juri dalam **bahasa Indonesia**.

- Sumber angka: `ekspor-xlsx/ASEAN_DSE_hasil_analisis.xlsx` (21 lembar, urutannya = urutan halaman ini);
  versi CSV per dataset untuk diimpor ke SAC ada di `ekspor-csv/` (daftar: `ekspor-csv/IMPOR-SAC.md`).
  Seluruh isi berkas .xlsx — nama lembar, nama kolom, dan isi sel kategori — **berbahasa Inggris**,
  jadi label yang muncul di grafik SAC bisa langsung dipakai. CSV kerja tetap bahasa Indonesia.
- Setiap angka di naskah ini sudah diverifikasi `analisis/analisis_storyboard.ipynb`. **Jangan menambah angka baru** yang tidak ada di berkas itu.
- Purwarupa visual tiap halaman ada di `analisis/gambar/` — pakai sebagai acuan bentuk, tapi **grafik final wajib dibuat di SAC**.

## Judul cerita — rekomendasi ganti

| | |
|---|---|
| **Judul lama** | "Hujan Hari Ini, Wabah Bulan Depan" |
| **Masalah** | Analisis sendiri menunjukkan **hujan justru runtuh** sebagai prediktor antar-tahun (r +0,40 → +0,24 pada anomali). Judul yang menonjolkan hujan akan bertabrakan dengan halaman 7 dan 14. |
| **Judul baru** | **"Four Months' Notice: turning El Niño into a dengue alarm for ASEAN"** |
| Alternatif | "The Alarm Is Already Public: El Niño as ASEAN's dengue early warning" |

---

## Sebelum mulai: urutan impor dataset ke SAC

SAC hanya menerima **satu dataset per berkas**, jadi lembar-lembar di bawah sudah dipecah jadi
CSV satu-satu di **`ekspor-csv/`** — nama berkasnya sama persis dengan nama lembar di tabel ini,
jadi *Create Dataset from File* langsung memberi nama yang benar. Daftar lengkapnya, termasuk
tipe kolom yang harus dibetulkan, ada di **`ekspor-csv/IMPOR-SAC.md`**.
**Delapan lembar pertama sudah menutup 15 halaman**; sisanya opsional.

| # | Lembar (Sheet) | Untuk halaman |
|---|---|---|
| 1 | `Monthly series IDN-THA` | 6, 7, 10, 11 — impor duluan, paling banyak dipakai |
| 2 | `ENSO phase - averages` | 7 (kartu as) |
| 3 | `Risk calendar IDN` | 8, 10 |
| 4 | `Dengue national annual` | 2 |
| 5 | `Seasonality IDN-THA` | 5 |
| 6 | `Province incidence 18-20` | 9, 12 |
| 7 | `Trigger rules - evaluation` | 11 |
| 8 | `Monetary impact` | 13 |
| 9 | `Lag correlation - national` + `Lag correlation - anomaly` | 6, 7 |
| 10 | `Province consistency IDN` | 7 (cadangan pertanyaan juri) |
| 11 | `City flood vulnerability`, `WASH by country` | 9 |
| 12 | `Trigger rules - out of sample`, `Rules vs endemic channel`, `EWS benchmark` | 12 |
| 13 | `El Nino episodes - lead time` | 13 |
| 14 | `Drought x water access` | 14 |

**Tiga setelan yang wajib dicek di layar impor** (kalau tidak, grafiknya salah):

1. `date` → ubah tipe ke **Date**, format `yyyy-MM-dd`. Kolom `period` biarkan teks.
2. Kolom angka yang sebenarnya label — `month`, `order`, `status_code`, `year`, `lag` —
   ubah dari **Measure** ke **Dimension**.
3. `month_name` dan `enso_phase_lag4` akan terurut alfabetis (Apr, Aug, Dec…). Perbaiki dengan
   *Sort → by* `month` / `order`, atau pakai kolom angkanya di sumbu.

Palet konsisten satu cerita: biru `#2A78D6` (kasus/normal), oranye `#E8833A` (alarm/El Niño),
merah `#C53232` (puncak/wabah), abu `#8A8F98` (konteks, ambang).

---

# Halaman 1 — Cover

**On-slide text**

> ## Four Months' Notice
> ### Turning El Niño into a dengue early-warning alarm for ASEAN
> SDG 3 × SDG 13 × SDG 6 · Team [nama tim] · [institusi] · Indonesia
> Built entirely on open data in SAP Analytics Cloud

**Visual**: tanpa grafik. Satu gambar latar (nyamuk/genangan/awan) + blok warna palet cerita.

**Catatan penyaji**: sebut tiga SDG di kalimat pertama — juri memberi bobot pada relevansi SDG.

---

# Halaman 2 — The problem (bobot 10%)

**On-slide text**

> ## Dengue is ASEAN's fastest-moving climate-sensitive disease
> **1.26 million cases in 2019** — the worst year in our nine-country panel
> - Vietnam 368k · Philippines 220k · Thailand 159k (latest complete year per country)
> - The 2023–24 El Niño added an estimated **9.6 million cases worldwide** (Tian et al., 2025)
> - Outbreaks are still fought **reactively** — after cases surge
>
> Source: OpenDengue V1.3 (national totals, complete-reporting years only)

**Grafik utama** — *Line chart*
- Dataset: `Dengue national annual`
- Filter: `complete` = True; `year` 2000–2024
- Measure: `cases` (Sum) · Dimension (sumbu X): `year`
- Beri **Reference line** di 2019 + label "record in our data"

**Grafik pendamping** — *Bar chart horizontal*
- Measure `cases` · Dimension `country`, filter tahun lengkap terbaru per negara (2022–2023)
- Urutkan menurun, warna biru, sorot Indonesia dengan oranye

**Catatan penyaji**: jangan pernah bilang "rekor 2023–24" dari data kita — Vietnam & Filipina
hanya lengkap sampai 2022, jadi total 2023–24 pasti terlihat turun secara artifisial. Untuk
2023–24 pakai sitasi Tian dkk. 2025. Ini justru poin jual di halaman 14.

**Antisipasi juri** — *"Kenapa 2019, bukan 2024?"* → "Karena panel kami hanya membandingkan
tahun dengan pelaporan lengkap di 9 negara. Kami sengaja tidak mengklaim rekor yang tidak bisa
kami buktikan sendiri."

---

# Halaman 3 — The question

**On-slide text**

> ## Climate data arrives months before patients do
> **Can a freely available climate index tell a health office how bad the coming season will be — early enough to act?**
> - **SDG 3** Health: reduce dengue burden
> - **SDG 13** Climate: use climate information for adaptation
> - **SDG 6** Water: target the most vulnerable districts
> Our test: does the signal survive when we remove the seasonal cycle, hold out unseen years, and use the WHO outbreak definition?

**Visual**: tanpa dataset. Diagram alur di SAC (Shapes + Text):
`Climate index (ONI, monthly, public)` → `3–4 month lag` → `Dengue surge` → `Action window: PSN/3M, larviciding, stockpiles`

**Catatan penyaji**: tiga syarat uji yang disebut di halaman ini adalah janji yang ditagih juri
di halaman 7, 12, dan 14 — pastikan ketiganya benar-benar dijawab.

---

# Halaman 4 — Data & method

**On-slide text**

> ## Nine open datasets, one monthly panel, zero paid sources
> | Data | Rows | Coverage |
> |---|---|---|
> | Dengue cases (OpenDengue V1.3) | 70,397 | 10 countries, 1955–2025 |
> | Dengue × climate monthly panel | 55,329 | province-month, lags pre-computed |
> | Temperature & rainfall (World Bank CCKP, ERA5) | 9,000 | monthly, 1950–2024 |
> | ONI El Niño index (NOAA CPC) | 918 | monthly, 1950–2026 |
> | Water & sanitation (WHO/UNICEF JMP) | 8,692 | 2000–2024 |
> | Population (BPS Indonesia) | 140 | provinces, denominators |
> | Flood exposure (GHSL) | 30,348 | 836 cities, 1975–2030 |
>
> **Method**: monthly national series 2010+ · lagged correlations · anomalies (seasonality removed)
> · a two-condition trigger rule · out-of-sample test on unseen years · WHO/PAHO endemic-channel benchmark
> All charts built in SAP Analytics Cloud.

**Visual**: tabel di atas sebagai *Table widget* atau teks; tambahkan ikon SDG.

**Catatan penyaji**: sebutkan satu kalimat metode yang jarang dipakai peserta lain — "we removed
the seasonal cycle before believing any correlation". Itu pembeda di mata juri analisis (25%).

---

# Halaman 5 — Analysis 1: the season (bobot analisis 25%)

**On-slide text**

> ## Dengue has a calendar — and it is not the same calendar everywhere
> - **Indonesia**: cases peak **Jan–Apr** (Jan avg 15,099/month vs Sep 6,003 — 2.5×), right after the Dec rainfall peak
> - **Thailand**: cases climb with the **onset** of the wet season and peak **Jun–Sep** (Jul avg 8,110 vs Feb 1,465 — 5.5×)
> - Same disease, opposite halves of the year → a regional alarm must be **local in timing**
>
> Source: national monthly means, complete years only (IDN 2010–2023, THA 2010–2022)

**Grafik** — *Combination chart (Column & Line)*, dua widget bersebelahan (Indonesia | Thailand)
- Dataset: `Seasonality IDN-THA` · Filter `country`
- Column (kiri, sumbu utama): `mean_cases` — biru
- Line (kanan, sumbu sekunder): `mean_rain_mm` — abu putus-putus
- Dimension sumbu X: `month` (bukan `month_name`, supaya urut) — ganti labelnya lewat *Sort by* `month`
- Sorot 4 kolom tertinggi dengan warna merah

**Catatan penyaji**: hati-hati — di Thailand puncak **hujan** justru September, sesudah puncak
kasus (Juli). Jadi kalimatnya harus "naik bersama **awal** musim hujan", bukan "mengikuti puncak
hujan". Kalau salah ucap, satu juri yang jeli akan mematahkannya di halaman berikutnya.

**Antisipasi juri** — *"Bukankah ini cuma musim biasa?"* → "Betul, dan itu tepatnya alasan kami
tidak berhenti di sini. Halaman 7 menunjukkan apa yang tersisa setelah musim dibuang."

---

# Halaman 6 — Analysis 2: the lag

**On-slide text**

> ## The climate signal arrives 1–4 months before the cases
> | | Best predictor | Lag | r |
> |---|---|---|---|
> | **Indonesia** | **ONI (El Niño index)** | **4 months** | **+0.59** |
> | Indonesia | Temperature | 3 months | +0.47 |
> | Indonesia | Rainfall | 1 month | +0.40 |
> | **Thailand** | Temperature | 3 months | +0.57 |
> | Thailand | Rainfall | same month | +0.48 |
>
> The lag *is* the opportunity: it is the time a health office has to act.
> Source: monthly national series, 2010+ (n = 172 months Indonesia)

**Grafik utama** — *Heat map*
- Dataset: `Lag correlation - national` · Filter `iso3` = IDN (widget kedua: THA)
- Dimension baris: `predictor` · Dimension kolom: `lag` · Measure: `r`
- Skala warna diverging −0,7 … +0,7, tampilkan nilai di sel

**Grafik pendamping** — *Scatterplot*
- Dataset: `Monthly series IDN-THA` · Filter `country` = Indonesia
- X: `temp_c_lag2` · Y: `cases` · Warna titik: `enso_phase_lag4`
- Aktifkan *Trend line → Linear*

**Catatan penyaji**: kalimat kunci yang harus diucapkan pelan-pelan — *"the lag is the
opportunity"*. Itu jembatan ke seluruh separuh kedua cerita.

---

# Halaman 7 — Analysis 3: the ace card

**On-slide text**

> ## A strong El Niño nearly triples Indonesia's monthly dengue burden
> ### 21,383 vs 7,597 cases per month — 2.8×
> - Grouped by the ENSO phase **four months earlier** — so this is a forecast, not a hindsight
> - **Not just seasonality**: after removing the seasonal cycle, the ONI correlation holds at **r = +0.56**
> - **Not an aggregation artefact**: cases are higher in El Niño months in **33 of 34 Indonesian provinces** (sign test p = 2×10⁻⁹) and 70 of 77 Thai provinces
> - Rainfall does *not* survive the same test (+0.40 → +0.24) — we report that honestly
>
> Source: 172 months, Indonesia 2010–2024 · NOAA CPC definition: El Niño = ONI ≥ 0.5

**Grafik utama** — *Bar chart*
- Dataset: `ENSO phase - averages`
- Measure: `mean_cases_per_month` · Dimension: `enso_phase_lag4`, *Sort by* `order`
- Warna bertingkat biru → oranye → merah; label data aktif
- Tambahkan **Reference line** di nilai `Neutral` (7,597)
- Beri catatan kaki kecil: "La Niña kuat: only 3 months observed — too thin to conclude"

**Grafik pendamping (siapkan di halaman cadangan, munculkan kalau ditanya)**
- *Heat map* dari `Lag correlation - anomaly` (bukti "bukan musim")
- *Bar horizontal* dari `Province consistency IDN`: Measure `ratio_nino_vs_other`, Dimension
  `province`, reference line di 1,0 — 33 dari 34 batang ada di kanan garis

**Catatan penyaji**: ini halaman kartu as. Urutan bicaranya: (1) angka besar 2,8×, (2) "kami
sudah menduga Anda akan bilang ini cuma musim — jadi kami buang musimnya, dan sinyalnya
bertahan", (3) "kami juga sudah menduga Anda akan bilang ini artefak nasional — 33 dari 34
provinsi". Jangan mengklaim "makin La Niña makin aman": La Niña dan Netral praktis setara,
dan urutannya berbalik tergantung jeda.

**Antisipasi juri** — *"Korelasi bukan kausalitas."* → "Setuju sepenuhnya, dan kami tidak
mengklaim kausalitas. Kami mengklaim **kelayakan sebagai peringatan dini** — dan itu diuji
dengan cara yang berbeda, di halaman 12."

---

# Halaman 8 — Analysis 4: where and when

**On-slide text**

> ## The alarm must be set province by province
> - **Indonesia**: 20 of 35 provinces peak in **January**, 8 in February — but **Bali peaks in May** and North Kalimantan in December
> - **Thailand**: 38 of 77 provinces peak in **July**, 16 in August
> - A single national alert date would be wrong for a third of Indonesia
>
> Source: share of annual cases by calendar month, per province

**Grafik** — *Heat map*, dua widget (Indonesia | Thailand)
- Dataset: `Risk calendar IDN` / `Risk calendar THA`
- Dimension baris: `province` (urutkan menurut bulan puncak, bukan alfabetis)
- Dimension kolom: `month` · Measure: `share_percent`
- Skala warna sekuensial putih → merah; sorot baris Bali dengan garis tebal

**Catatan penyaji**: Bali adalah anekdot terbaik di seluruh dek — provinsi dengan insidens
tertinggi, tapi puncaknya Mei, tiga bulan setelah kalender nasional. Sebut namanya, jangan
hanya "some provinces".

---

# Halaman 9 — Analysis 5: who gets hit hardest (SDG 6 layer)

**On-slide text**

> ## The same alarm, aimed at the most exposed places
> - Highest incidence 2018–2020: **Bali 134**, North Kalimantan 115, East Kalimantan 112 per 100k — **14× the lowest province** (Papua, 9)
> - Indonesia has the **lowest piped-water access in ASEAN: 21.8%** (JMP 2024) — households store water, and stored water breeds *Aedes*
> - **12.9 million people in Bangkok** and 1.7 million in Jakarta live in the 1-in-100-year flood zone
> - We use this to **target** the alarm, not to explain it (see p.14)
>
> Sources: BPS denominators (2018–2020 only) · WHO/UNICEF JMP · GHSL

**Grafik utama** — *Bar chart horizontal*
- Dataset: `Province incidence 18-20` · Measure `mean` · Dimension `province`, urut menurun, ambil 10 teratas + 3 terbawah
- Warna merah untuk 3 teratas

**Grafik pendamping** — *Bar chart*
- Dataset: `WASH by country` · Measure `piped_water_%` · Dimension `country`, urut menaik
- Indonesia paling kiri, warna oranye — visual yang langsung "menampar"

**Grafik ketiga (opsional, kalau ruang cukup)** — *Bubble/bar* dari `City flood vulnerability`:
Measure `exposed_2020`, Dimension `city`, 8 kota teratas

**Catatan penyaji**: kalimat "we use this to target, not to explain" wajib diucapkan — itu yang
mencegah juri menuduh kita mengklaim kausalitas WASH yang tidak kita punya buktinya.

**Antisipasi juri** — *"Kenapa insidensnya hanya 2018–2020?"* → "Karena itu satu-satunya periode
dengan penyebut penduduk resmi BPS per provinsi yang kami punya. Di luar itu kami hanya punya
kasus mentah, dan memeringkat wilayah dengan kasus mentah hanya akan memeringkat jumlah
penduduk."

---

# Halaman 10 — Synthesis: the risk calendar

**On-slide text**

> ## From signal to schedule: a risk calendar every health office can read
> - Each province gets three states — **Peak · Watch · Normal** — from its own case history
> - The El Niño index sets **how severe** the coming peak will be; the calendar sets **when** it arrives
> - Real lead times, every El Niño episode since 2009: **0–3 months** on observed ONI — and longer on NOAA/BMKG *forecast* ONI
>
> Source: 5 El Niño episodes, 2009–2024

**Grafik utama** — *Heat map* `Risk calendar IDN` difilter 6 provinsi prioritas
(Bali, Kalimantan Utara, Kalimantan Timur, Gorontalo, DKI Jakarta, Jawa Barat),
Measure `status_code`, palet 3 warna (0 abu, 1 kuning, 2 merah)

**Grafik pendamping** — *Time series* dari `Monthly series IDN-THA` (Indonesia):
Line `cases`, Reference line `threshold_p75` (11,932), warna titik/latar menurut `alarm_el_nino`

**Catatan penyaji**: framing yang benar dan sudah diuji — alarm ini memprediksi **separah apa**
musim yang datang, bukan menggeser tanggal mulainya. Jangan menjanjikan "3 bulan lebih awal"
sebagai angka tunggal; katakan 0–3 bulan pada ONI teramati, lebih panjang pada ONI ramalan.

---

# Halaman 11 — The solution (bobot inovasi 15%)

**On-slide text**

> ## Two conditions. No model. No code.
> ### "If the month is Jan–Apr **AND** ONI four months ago was ≥ 0.5 → raise alert"
> - Fires in only **11.6% of months** — and **every single one** was a top-quartile dengue month (**precision 100%, lift 4×**)
> - Both inputs are public and free: NOAA publishes ONI monthly, the calendar comes from the office's own records
> - Runs in a spreadsheet, a WhatsApp broadcast, or this SAC dashboard
>
> Source: Indonesia 2010–2024, 172 months · threshold ONI ≥ 0.5 is NOAA's own El Niño definition

**Grafik utama** — *Bar chart* perbandingan aturan
- Dataset: `Trigger rules - evaluation`
- Measures: `precision_%` dan `alarm_coverage_%` · Dimension: `rule`
- Sorot baris D dengan merah, sisanya abu — ceritanya: aturan D menyala paling jarang tapi paling tepat

**Grafik pendamping** — *Time series* `Monthly series IDN-THA` (Indonesia), Line `cases`,
warna menurut `alarm_rule_d`, Reference line `threshold_p75`

**Catatan penyaji**: tekankan "no model, no code". Pesaing akan menjanjikan machine learning;
nilai jual kita adalah **bisa benar-benar dijalankan** dinkes provinsi minggu depan.

---

# Halaman 12 — Viability (bobot 15%)

**On-slide text**

> ## We tried to break our own rule. It held.
> - **Out-of-sample test**: rule built on 2010–2016, tested blind on 2017–2024 → **precision still 100%**, sensitivity 44%, lift 3.9
> - Against the **WHO/PAHO endemic-channel** outbreak definition (which removes seasonality by construction): specificity **91%**, lift 2.5 — and *all* of the value comes from the El Niño condition, not the season
> - Published dengue EWS report PPV 43–86% (17-system review) — we reach a comparable PPV **with no statistical model and monthly data**
> - Replicates in Thailand with its own best predictor (temperature anomaly, lag 2): lift 2.7
>
> **Adoption in three phases**: 1) Bali, N. & E. Kalimantan pilot · 2) all 38 provinces · 3) ASEAN peers
> **Cost**: open data, monthly refresh, existing staff

**Grafik utama** — *Bar chart* `Trigger rules - out of sample`:
Measures `precision_%`, `sensitivity_%` · Dimension `period` (latih vs UJI), dikelompokkan per `country`

**Grafik pendamping** — *Table widget* `EWS benchmark` apa adanya (5 baris), kolom sumber
ditampilkan — kejujuran pembanding ini yang dinilai

**Catatan penyaji**: kalimat pembuka halaman ini — *"We tried to break our own rule"* — adalah
kalimat paling kuat di dek. Sebutkan sensitivitas 44% dengan suara yang sama percaya dirinya
seperti presisi 100%: kita melewatkan sebagian bulan puncak, tapi kita **tidak pernah**
membunyikan alarm palsu.

**Antisipasi juri** — *"Sensitivitas 44% itu rendah."* → "Betul. Kami memilih presisi daripada
sensitivitas, karena alarm palsu yang berulang adalah cara tercepat membuat dinkes berhenti
mempercayai sistem. Aturan ini adalah lapisan **eskalasi**, di atas surveilans rutin yang
tetap berjalan."

---

# Halaman 13 — Impact (bobot 20%)

**On-slide text**

> ## Acting 4–8 weeks earlier is worth US$1.5–3.7 million a year — in Indonesia alone
> - Indonesia averages **104,753 cases/year** (complete years 2015–2023); **44% fall in Jan–Apr**
> - Prevent just **10%** of peak-season cases = **4,656 cases/year**
> - At Indonesia's published hospitalisation cost of US$316–791/case → **US$1.5–3.7 M (Rp 24–59 billion)/year**
> - For scale: dengue costs Indonesia **US$381–681 M/year** (Nadjib 2019; Wilastonegoro 2020)
> - Lead time is real: in the 2023–24 episode the alarm fired **Sep 2023**, cases crossed the peak threshold **Dec 2023**
>
> Sources: cost per case from peer-reviewed Indonesian studies; case counts from our panel

**Grafik utama** — *Bar chart bertingkat*
- Dataset: `Monetary impact` · Measures `hospitalisation low (US$316)` & `hospitalisation high (US$791)`
  · Dimension `scenario`
- Tambahkan **Numeric Point (KPI tile)** besar: `4,656 cases/year prevented`

**Grafik pendamping** — *Table* `El Nino episodes - lead time` (5 baris): kolom episode,
alarm_menyala, kasus_lewat_P75, tenggang_bulan

**Catatan penyaji**: selalu sebut skenario 10% sebagai **skenario paling konservatif**, dan
sebutkan bahwa jangkar biaya paling murah (US$90/episode) memberi US$0,42 jt — menunjukkan kita
tidak memilih angka yang paling menguntungkan.

**Antisipasi juri** — *"Dari mana angka 10% tercegah?"* → "Itu asumsi, bukan temuan, dan kami
menandainya sebagai asumsi. Yang kami hitung dari data adalah penyebutnya: 104.753 kasus/tahun
dan 44% di musim puncak. Efektivitas intervensi 10% kami ambil sebagai skenario konservatif."

---

# Halaman 14 — Limits & data ethics

**On-slide text**

> ## What we tested and threw away
> - **We falsified our own innovation angle.** "Drought × water access" looked promising (r = −0.31) but collapsed after controlling for El Niño (partial r = −0.15) and showed no moderation by piped access (ρ = +0.34, p = 0.46, n = 7). We dropped the claim.
> - **We do not claim a 2023–24 record** — our panel is incomplete for Vietnam and the Philippines after 2022.
> - **Incidence only for 2018–2020**, the only years with official BPS denominators. Elsewhere we use raw counts and never rank regions by them.
> - **Flood/disaster records look correlated with dengue (r = +0.66) — until you divide by population** (r = −0.14). We report the null.
> - Correlation is not causation: this is an **early-warning** claim, with mechanism cited from the literature.

**Grafik** — *Scatterplot* `Drought x water access`:
X `piped_water_%`, Y `r_drought`, ukuran bubble `nino_multiplier`, label `country`
— sengaja ditampilkan **tanpa** garis tren, dengan judul "no relationship (ρ = +0.34, p = 0.46, n = 7)"

**Catatan penyaji**: halaman ini adalah senjata, bukan permintaan maaf. Nada bicaranya bangga:
*"we tested our own best idea and it failed — so we removed it."* Sangat sedikit peserta yang
melakukan ini, dan juri analisis mengenalinya seketika.

---

# Halaman 15 — References (di luar hitungan 15 halaman)

> **Data**: OpenDengue V1.3 (doi:10.6084/m9.figshare.24259573.v4) · World Bank CCKP (ERA5 0.25°) ·
> NOAA CPC Oceanic Niño Index · WHO/UNICEF JMP 2025 · BPS Indonesia (WebAPI) · GHSL (JRC) · SIPSN KLHK · BNPB
>
> **Literature**: Tian et al. 2025 *Nat Commun* · Djaafara et al. 2026 *PLOS NTD* ·
> Sutriyawan et al. 2025 · Lowe et al. 2021 *Lancet Planet Health* · Gibb et al. 2023 *Nat Commun* ·
> Baharom et al. 2022 · Cárdenas et al. 2021 · Schlesinger et al. 2024 ·
> Hussain-Alkhateeb et al. 2018 (WHO-TDR EWARS) · Nadjib et al. 2019 *PLoS NTD* ·
> Wilastonegoro et al. 2020 *AJTMH* · Sasmono et al. 2026 *IJID Regions* · Childs et al. 2025 *PNAS*

Pranala DOI per klaim ada di `analisis/keluaran/referensi_per_klaim.md` — **ganti pranala
consensus.app dengan DOI jurnal** sebelum submit.

---

## Cek terakhir sebelum submit (4 Sep 2026)

- [ ] 15 halaman persis; referensi di halaman terpisah
- [ ] Setiap grafik dibuat di SAC (bukan gambar tempelan dari notebook)
- [ ] Judul cerita konsisten dengan temuan (hujan **bukan** prediktor utama)
- [ ] Tidak ada klaim "rekor 2023–24" dari data sendiri
- [ ] Tidak ada peringkat wilayah memakai kasus mentah
- [ ] Sensitivitas 44% disebutkan, tidak disembunyikan
- [ ] Skenario 10% ditandai sebagai asumsi
- [ ] Sumber tercantum di kaki tiap halaman berdata
