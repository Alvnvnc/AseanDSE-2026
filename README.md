# ASEAN Data Science Explorers 2026 — paket data & studi kasus

Sumber berlabel ✅ **sudah diunduh dan diverifikasi** pada 7 Agustus 2026; berlabel ⏳
masih rencana (belum ada di folder ini). Tidak ada yang butuh login; yang tersedia sudah
dikonversi ke CSV format panjang (*long format*) siap impor ke SAP Analytics Cloud.

**Ide storyboard terpilih & argumennya: lihat `IDE-STORYBOARD.md`.**
**Naskah 15 halaman siap eksekusi: `NASKAH-STORYBOARD.md`.**
**Bedah 15 dek finalis 2024–2025 + celah dek kita: `ANALISIS-FINALIS.md`.**
**Dek PDF (LaTeX, 16:9, slot grafik SAC): `storyboard/` — jalankan `storyboard/bangun.sh`.**
**Daftar CSV siap impor SAC + urutan & tipe kolomnya: `ekspor-csv/IMPOR-SAC.md`.**
**Panduan kerja membangun 23 grafik di SAC: `storyboard/panduan-sac.pdf`.**
**Membangun grafiknya otomatis (tanpa mengklik satu per satu): `otomasi-sac/`.**

## Tenggat

| Tahap | Tanggal |
|---|---|
| **Pendaftaran ditutup** | **14 Agustus 2026** (sudah diperpanjang) |
| **Submit storyboard** | **4 September 2026** |
| Penjurian storyboard | 7–24 September 2026 |
| Pengumuman shortlist | 30 September 2026 |
| National Finals | 12–23 Oktober 2026 |
| Regional Final | 24–26 November 2026 |

## Aturan yang mengikat

- Enam SDG yang boleh dipilih: **2, 3, 6, 11, 12, 13**
  (diverifikasi dari nama berkas ikon di HTML aseandse.org: `sdgs2`, `sdgs3`, `SDG_6`, `sdg11`, `sdg12`, `sdg13`).
  Daftar 3/4/5/8/9/11 yang beredar di internet adalah edisi sebelum 2024 — **sudah tidak berlaku**.
- Storyboard: PDF *landscape*, maks. **15 halaman** (termasuk sampul, di luar halaman referensi), maks. 20 MB.
- **Semua grafik wajib dihasilkan SAP Analytics Cloud.**
- Tim 2 orang, usia 18–30, kewarganegaraan sama.
- Penamaan berkas: `NEGARA_NAMA TIM`.

## Bobot penjurian

| Kriteria | Bobot |
|---|---|
| Analysis & Insights | 25% |
| Relevancy & Impact | 20% |
| Viability | 15% |
| Innovation | 15% |
| Presentation Delivery | 15% |
| Problem Definition | 10% |

Konsekuensinya: dataset harus cukup kaya untuk **digabung antar sumber**. Satu tren garis
tunggal hanya menyentuh bobot 10%.

## Isi paket

### `data/siap-sac/` — siap impor, tidak perlu diolah lagi

| | Berkas | Baris | Isi |
|---|---|---|---|
| ⭐ | `dengue_iklim_bulanan.csv` | 55.329 | **Tabel utama storyboard.** Satu baris = provinsi-bulan: kasus + suhu/hujan jeda 0–3 bulan + ONI jeda 0/3/4 + fase ENSO. Jeda dihitung di sini karena SAC sulit melakukan *lagged join*. |
| ✅ | `dengue_asean.csv` | 70.397 | Kasus dengue 10 negara ASEAN, 1955–2025 (nama provinsi sudah dinormalkan) |
| ✅ | `iklim_bulanan_asean.csv` | 9.000 | Suhu & curah hujan bulanan 10 negara, 1950–2024 (ERA5 0,25°) |
| ✅ | `enso_oni_bulanan.csv` | 918 | Indeks ONI bulanan 1950–2026 + label fase (El Niño/La Niña/Netral) |
| ✅ | `wash_rumahtangga_asean.csv` | 8.692 | Air/sanitasi/higiene rumah tangga, 10 negara, 2000–2024 |
| ✅ | `wash_fasyankes_asean.csv` | 5.625 | WASH + limbah medis fasilitas kesehatan, 10 negara, 2003–2024 |
| ✅ | `sampah_kabkota_indonesia.csv` | 514 | Semua kabupaten/kota: timbulan, % terkelola, jenis TPA, bank sampah |
| ✅ | `kota_asean_kualitas_udara.csv` | 622 | PM2.5/PM10/NO2 kota ASEAN (WHO **V6.1**, Januari 2024) |
| ✅ | `kota_asean_paparan_banjir.csv` | 30.348 | **836 kota ASEAN**, penduduk terpapar banjir periode-ulang 10 & 100 tahun, 1975→2030 (GHS-UCDB R2024A V1.2) |
| ✅ | `bencana_kabkota_indonesia.csv` | 17.500 | Statistik Bencana Menurut Wilayah: 478 kab/kota × 2018–2020 × 14 indikator (kejadian, korban, rumah rusak/**terendam**, fasilitas rusak) |
| ✅ | `penduduk_provinsi_indonesia.csv` | 140 | Penduduk provinsi Indonesia dari **dua seri BPS** (lihat kolom `sumber`): SUPAS 2025 (38 provinsi, 2025) + proyeksi SP2010 via **WebAPI resmi** (34 provinsi, 2018–2020; nilai identik dengan arsip Wayback, dicek 93/93 baris yang beririsan). **Hanya 2018–2020 yang beririsan dengan data dengue** |

Kunci gabung: `iso3` + `tahun` (+ `periode` untuk dengue×iklim).

**Cakupan panel bulanan tingkat provinsi** (dari `dengue_iklim_bulanan.csv`) — jauh lebih
kaya dari dugaan awal, tapi jendelanya berbeda-beda per negara:

| Negara | Baris | Provinsi | Rentang | Tahun lengkap |
|---|---|---|---|---|
| Thailand | 27.024 | 77 | 1993-01–2022-12 | 30 |
| Vietnam | 12.273 | 64 | 1994-02–2010-12 | 16 |
| Indonesia | 7.461 | 38 | 2004-01–2024-07 | 15 |
| Kamboja | 3.680 | 24 | 1998-01–2010-12 | 13 |
| Laos | 2.731 | 18 | 1998-01–2010-12 | 13 |
| Malaysia | 1.944 | 10 | 1993-01–2010-12 | 18 |
| Singapura | 216 | 1 | 1993-01–2010-12 | 18 |

Hanya Thailand & Indonesia yang berlanjut setelah 2010; sisanya berhenti di 2010.

### `data/` — berkas mentah asli (untuk sitasi & pengecekan ulang)

`kesehatan/` (zip + CSV OpenDengue), `iklim/` (JSON CCKP per negara-variabel + ONI NOAA),
`wash/` (XLSX JMP rumah tangga & fasyankes), `sampah/` (HTML beranda SIPSN),
`kota/` (XLSX WHO + zip GHS-UCDB). Masih rencana: `pangan/`.

### `analisis/` — notebook Jupyter (dapur analisis storyboard)

- `analisis/analisis_storyboard.ipynb` — memverifikasi **12/12 klaim angka**
  `IDE-STORYBOARD.md`, membuat purwarupa **12 grafik** (`analisis/gambar/`), dan
  menghasilkan **9 tabel turunan + ringkasan angka jadi** (`analisis/keluaran/`,
  lihat `angka_kunci_storyboard.md`). Termasuk **analisis pendalaman** anti-bantahan
  juri: uji anomali (sinyal ONI/suhu bertahan setelah musim dibuang; hujan tidak),
  konsistensi 33/34 provinsi (p=2e-9), uji luar-sampel (presisi tetap 100% di
  2017–2024), tenggang per episode El Niño, peringkat insidens provinsi, dan **uji
  sudut inovasi kekeringan×akses-air (hasil: klaim lama TIDAK didukung data — sudah
  direvisi di IDE-STORYBOARD butir 3)**. Juga
  `dengue_asean_nasional_tahunan.csv` (dedup resolusi — **jangan** jumlahkan
  `dengue_asean.csv` mentah: 147 negara-tahun tampil di >1 resolusi, dobel hitung),
  `kalender_risiko_idn/tha.csv`, dan evaluasi ambang pemicu
  (aturan "musim puncak DAN El Niño" → presisi 100%, lift 4×).
- Jalankan: `.venv/bin/jupyter lab analisis/analisis_storyboard.ipynb`
  (venv: `python3 -m venv .venv && .venv/bin/pip install pandas matplotlib scipy jupyterlab nbformat nbconvert ipykernel openpyxl`).

### `ekspor-csv/` — CSV siap impor SAP Analytics Cloud (berbahasa Inggris)

SAC mengimpor **satu dataset per berkas**, jadi buku kerja 23 lembar tidak bisa dipakai
langsung. Folder ini memecahnya: **21 tabel siap grafik** di akarnya (nama berkas = nama
dataset yang dipakai `NASKAH-STORYBOARD.md`, jadi kolom *Name* di layar impor SAC sudah
benar sejak awal), plus **11 himpunan data sumber** di `sumber/` — yang terakhir ini
**tidak dilacak git** (17 MB duplikat bahasa Inggris dari `data/siap-sac/`); jalankan
`analisis/ekspor_csv.py` untuk membuatnya.

**`ekspor-csv/IMPOR-SAC.md` adalah daftar siap salinnya**: urutan impor (delapan pertama
sudah menutup 15 halaman), 23 slot grafik → dataset mana, dan tipe kolom yang harus
dibetulkan di layar impor (`year`/`month`/`lag` ditebak SAC sebagai Measure lalu
dijumlahkan — grafiknya salah kalau dibiarkan).

### `ekspor-xlsx/` — versi Excel

`ASEAN_DSE_hasil_analisis.xlsx` (23 lembar, urutan = urutan halaman naskah) untuk menulis
naskah dan cek angka cepat, plus `sac/*.xlsx` per himpunan data sumber. Isi sama dengan
`ekspor-csv/`; untuk impor ke SAC pakai CSV-nya.

### `otomasi-sac/` — membangun 23 grafik SAC tanpa mengklik satu per satu

Merakit 23 grafik dengan tangan di SAC makan waktu berjam-jam dan tidak bisa diulang:
satu perubahan resep berarti mengklik ulang semuanya. Folder ini menulis langsung ke
story lewat REST internal SAC, lalu menangkap tiap halaman jadi PNG 2x:

```sh
otomasi-sac/edge-mulai.sh                     # Edge kedua yang bisa dikendalikan CDP
.venv/bin/python otomasi-sac/bangun-story.py  # bangun/segarkan 23 grafiknya
.venv/bin/python otomasi-sac/tangkap.py       # tangkap PNG ke storyboard/gambar-sac/
bash storyboard/bangun.sh                     # susun ulang dek + cek aturan panitia
```

**Aturan panitia tetap terpenuhi**: grafiknya benar-benar dirender SAP Analytics Cloud —
yang diotomasi hanya penyusunan dan pengambilannya, bukan penggambarannya.

Resep tiap grafik ada di `otomasi-sac/resep.py` (dataset, feed, filter, urutan, warna).
Ubah di situ lalu jalankan ulang dua perintah pertama — tidak ada langkah manual di SAC.
`otomasi-sac/README.md` memuat cara kerjanya beserta **26 jebakan** yang sudah dilewati;
baca itu dulu sebelum menebak-nebak kalau SAC berubah. Langkah manual di
`storyboard/panduan-sac.pdf` tetap berlaku sebagai cadangan.

### Skrip

- `data/unduh.sh` — mengunduh ulang semua sumber mentah yang ✅ (idempoten)
- `data/unduh_bps.py` — penduduk provinsi dari WebAPI BPS (perlu kunci)
- `data/siapkan.py` — mengubah mentah menjadi CSV siap SAC
  (bagian WASH butuh `openpyxl`; tanpa itu bagian tersebut dilewati otomatis)
- `analisis/ekspor_csv.py` — membangun ulang `ekspor-csv/` **dan** `IMPOR-SAC.md`
- `analisis/ekspor_xlsx.py` — membangun ulang `ekspor-xlsx/`
- `storyboard/panduan_sac.py` — membangun ulang `storyboard/panduan-sac.pdf`
  (resep grafiknya dibaca dari `storyboard.tex`, tidak diketik ulang)
- `otomasi-sac/bangun-story.py` — membangun 23 grafik di SAC dari `resep.py`
- `otomasi-sac/tangkap.py` — menangkap tiap grafik jadi PNG ke `storyboard/gambar-sac/`
- `otomasi-sac/periksa-gambar.py` — uji mutu PNG (ukuran, berat, deteksi gambar kosong)
- `ekspor-csv/perbaikan.py` — membangun ulang `ekspor-csv/perbaikan/` (tabel yang perlu
  format panjang atau label yang dipendekkan sebelum diimpor ke SAC)

### Cara mengambil data penduduk BPS

**Seluruh** estat web BPS memakai tantangan interaktif Cloudflare (`cf-mitigated: challenge`)
— sudah diuji satu per satu: `www.bps.go.id`, `bps.go.id`, dan 12 subdomain provinsi
(`sulut`, `sumsel`, `jatim`, `jabar`, `jateng`, `bali`, `papua`, `kalsel`, `sulsel`,
`ntb`, `aceh`, `riau`) semuanya balas **403**. Tidak ada skrip yang bisa lewat; hanya
peramban sungguhan. Kedua API-nya (`webapi.bps.go.id` V1 dan `web-api.bps.go.id` V2)
bisa dihubungi tapi menolak tanpa kunci.

Karena itu ada **tiga jalur**, semuanya sudah didukung `siapkan.py`:

1. **WebAPI BPS (jalur utama — AKTIF sejak 9 Agu 2026, kunci tersimpan di `.env`)** —
   `unduh_bps.py` membaca kunci dari `.env` otomatis. Tiga jebakan API yang sudah
   ditangani skrip (jangan didiagnosis ulang): (a) **WAF BPS menolak User-Agent bawaan
   urllib/curl dengan 403 "Perimeter WAF Block"** — skrip memakai UA peramban;
   (b) parameter **`th` kini wajib**, berisi **ID tahun** (mis. 120 = 2020), bukan tahun
   literal; (c) **maksimal 3 tahun per permintaan** — skrip mengambil per gugus lalu
   menggabungkan JSON-nya.
2. **Query Builder BPS (unduh manual dari peramban)** — CSV SUPAS 2025 (38 provinsi,
   2025) yang ada sekarang tetap dipertahankan `siapkan.py` untuk tahun yang tidak
   dicakup WebAPI.
3. **Arsip Wayback (cadangan, tanpa kunci)** — proyeksi SP2010, 2018–2020, 34 provinsi;
   dipakai hanya bila JSON WebAPI belum ada.

**Batas yang ditemukan saat verifikasi WebAPI (9 Agu 2026):** var **1886** hanya punya
tahun **2015–2020** dan isinya **proyeksi SP2010** (nilai identik dengan arsip Wayback,
dicek 93/93 baris — jadi bukan seri SP2020, dan `siapkan.py` melabeli `sumber` dari
nilainya, bukan dari asumsi). Var **2781** (SUPAS) hanya 2025; var **1975** (pertengahan
tahun, 2017–2026) **nasional saja**. Artinya: **seri penduduk provinsi 2021–2024 belum
tersedia lewat WebAPI** — insidens tetap terbatas 2018–2020 sampai BPS menerbitkan
proyeksi interim per provinsi sebagai tabel dinamis.

`siapkan.py` selalu melaporkan irisan tahun penduduk × dengue, dan memberi peringatan
tegas kalau nol — supaya tidak baru ketahuan saat grafiknya dibuat di SAC.

```bash
python3 data/unduh_bps.py          # kunci terbaca dari .env (BPS_API_KEY=/BPS_KEY=)
python3 data/siapkan.py            # insidens per 100 rb ikut terhitung
# opsional: BPS_TAHUN=2018-2024 mengatur rentang; --telusuri melihat daftar variabel
```

Variabel yang dipakai: **1886** "Jumlah Penduduk Hasil Proyeksi menurut Provinsi dan
Jenis Kelamin"; timpa dengan `BPS_VAR=<id>` bila BPS mengubahnya. Setelah data masuk,
`dengue_iklim_bulanan.csv` otomatis terisi kolom `penduduk` dan `insidens_per_100rb`.

> **Jangan campur dua seri itu.** Kolom `sumber` di `penduduk_provinsi_indonesia.csv`
> menandai yang mana. Untuk 2020 keduanya ada tapi berbeda: proyeksi SP2010 menaksir
> Aceh 5.388.100 jiwa, sementara SP2020 sekitar 5.275.000 — selisih ±2%. Pakai satu
> seri saja per grafik, dan sebutkan yang mana di halaman metode.

## Sumber & sitasi

| Dataset | Sumber | Pranala |
|---|---|---|
| Dengue | OpenDengue v1.3, LSHTM (DOI 10.6084/m9.figshare.24259573.v4) | https://opendengue.org |
| Iklim | World Bank CCKP (ERA5 0,25°) | https://cckpapi.worldbank.org |
| Sampah | Sistem Informasi Pengelolaan Sampah Nasional, KLH | https://sampahnasional.kemenlh.go.id |
| Banjir kota | GHS Urban Centre Database R2024A **V1.2** (data 15 Mei 2026), JRC | https://human-settlement.emergency.copernicus.eu |
| Udara | WHO Ambient Air Quality Database **V6.1 (31 Jan 2024)** — versi terbaru yang benar-benar ada | https://who.int |
| WASH | WHO/UNICEF Joint Monitoring Programme 2025 | https://washdata.org |
| ENSO | Indeks ONI (Niño 3.4), NOAA PSL — ERSST v6 | https://psl.noaa.gov/data/correlation/oni.data |
| Pangan | FAOSTAT; SKPG Badan Pangan Nasional (belum diunduh) | https://fao.org/faostat ; https://data.badanpangan.go.id |

## Catatan jujur soal keterbatasan data

Semua catatan di bawah ini **diverifikasi langsung pada berkas yang ada di folder ini**.

- **Nama provinsi dengue harus dinormalkan.** OpenDengue memakai ejaan berbeda untuk
  provinsi yang sama di era berbeda, sebagian terpotong. Ada **dua lapis** masalah:
  di seri **bulanan** muncul `KALIMANTAN SELATA`, `SUMATERA SELATA`, `SULAWESI SELATA`,
  `D.I YOGYA`, `BABEL`, `NANGROE ACEH DARUSSALAM`, `NUSATENGGARA BARAT/TIMUR`; di seri
  **tahunan** muncul varian yang lain lagi — `NANGGROE ACEH DARUSSALAM` (dobel G!),
  `KEPULAUAN BANGKA BELITUNG`, `KEPULAUAN-RIAU`, `DI YOGYAKARTA`. Di Thailand
  `PHACHINBURI` vs `PRACHIN BURI`. Tanpa penggabungan, Indonesia tampil **42 nama**
  (seharusnya 38) dan Thailand 78 (seharusnya 77) — peta SAC akan pecah dan penduduk BPS
  gagal dijodohkan. `siapkan.py` sudah menggabungkan ke-13 pasangan; masing-masing sudah
  dicek **nol periode tumpang tindih** sebelum digabung.
- **Batas wilayah berubah**: Sa Kaeo (Thailand) baru tampil terpisah sejak 2003, jadi angka
  Prachin Buri sebelum 2003 kemungkinan masih mencakup wilayah Sa Kaeo. Provinsi hasil
  pemekaran Papua 2022 (Papua Tengah, Pegunungan, Selatan, Barat Daya) hanya punya data 2023+.
- **Dengue**: tujuh negara punya panel bulanan-provinsi yang layak (lihat tabel cakupan di
  atas), tapi **hanya Thailand & Indonesia berlanjut setelah 2010**. Filipina, Myanmar, dan
  Brunei tidak punya rangkaian bulanan tingkat provinsi sama sekali.
- **Sampah (SIPSN)**: datanya **tabel HTML statis di beranda**, bukan API — dan hanya
  **satu potret**, bukan panel tahunan. Tahun acuan tidak tercantum di halaman; konfirmasi
  ke portal sebelum menulis sitasi. Kolom `nilai_kinerja_ps` **kosong untuk seluruh 514 baris**,
  dan `progress_sa` hanya terisi 219 dari 514.
- **Angka SIPSN mencampur dua konvensi desimal dalam satu tabel**: `22,10` (koma desimal)
  bersebelahan dengan `54.15` (titik desimal) dan `2.784` (titik ribuan). `siapkan.py`
  memutuskan per nilai — titik dengan tepat 3 digit = ribuan, 1–2 digit = desimal.
- **Kualitas udara**: versi terbaru WHO yang benar-benar ada adalah **V6.1 (Januari 2024)**,
  bukan v8.0/2026. Cakupan ASEAN tipis: 622 baris, berhenti di **2021**, dan Laos cuma 1 kota.
- **GHS-UCDB**: `siapkan.py` memakai berkas **GeoPackage** (`.gpkg`) di dalam zip, bukan
  XLSX 175 MB — `.gpkg` itu SQLite, jadi bisa dibaca modul `sqlite3` bawaan tanpa pustaka
  tambahan, jauh lebih cepat, dan diakritik nama kota utuh (sudah dicek: `Cần Thơ` bukan
  `C?n Th?`, nol tanda `?` di seluruh 836 kota).
- **Kolom banjir GHS mudah tertukar.** `HZ_CEV_FLO_*` di tema HAZARD_RISK adalah **jumlah
  kejadian** banjir (nilai 1–9), *bukan* penduduk terpapar, dan hanya ada 2005/2010/2015.
  Yang benar untuk paparan penduduk adalah `EX_010_POP_*` dan `EX_100_POP_*` di tema
  EXPOSURE (periode ulang 10 & 100 tahun, 1975–2030). Angka 2025 & 2030 adalah **proyeksi**.
- **Nama kota WHO** sesekali memuat baris baru di dalam sel (mis. Ta Khmau, Kamboja);
  sudah dirapikan agar impor SAC tidak pecah.
- **Statistik Bencana memakai koma sebagai pemisah ribuan** (`199,136` = 199.136) —
  gaya Inggris, kebalikan dari SIPSN yang bergaya Indonesia. Tiap berkas punya baris
  "Jumlah"; `siapkan.py` memakainya sebagai uji silang (hasilnya **114/114 berkas cocok**)
  lalu membuangnya dari keluaran supaya tidak terhitung dua kali.
- **Struktur provinsi bencana berbeda dengan dengue.** Ekspornya memuat **34 label
  provinsi** — Papua sudah terpecah sebagian (`Papua Tengah` muncul terpisah) **mundur
  sampai 2018**, sedangkan dengue 2018–2020 masih memakai Papua lama. Kolom
  `provinsi_setara_dengue` menggabungkannya kembali (Papua Tengah → PAPUA); pakai kolom
  itu untuk menggabung, bukan kolom `provinsi`. **Papua Barat sama sekali tidak ada** di
  ekspor bencana, jadi irisan dengan dengue tinggal **33 provinsi**.
- **Panel dengue Indonesia bolong satu bulan di dua tahun**: **2016 tanpa Februari** dan
  **2020 tanpa September** — hilang untuk *seluruh* provinsi sekaligus, jadi total tahunan
  2016 & 2020 kurang ±1/12. Karena bolongnya seragam, perbandingan antar-provinsi di tahun
  yang sama tidak terganggu; yang harus hati-hati adalah perbandingan **antar tahun**.
- **IHME GBD** butuh akun dan dikirim lewat surel (batas 100.000 baris per permintaan) —
  dihindari dalam paket ini karena tenggat 4 September terlalu dekat.
