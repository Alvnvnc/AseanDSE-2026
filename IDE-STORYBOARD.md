# Ide storyboard: "Hujan Hari Ini, Wabah Bulan Depan"

**Sistem peringatan dini dengue berbasis iklim untuk ASEAN — SDG 3 (kesehatan) × SDG 13 (iklim), dengan lapisan kerentanan SDG 6 (air & sanitasi).**

Satu kalimat pitch: *iklim memberi kita jeda 1–3 bulan sebelum kasus dengue melonjak —
jeda itu bisa diubah menjadi alarm dini yang murah, dan datanya sudah terbuka untuk
seluruh ASEAN.*

> **Verifikasi 8 Agustus 2026:** seluruh 12 klaim angka di berkas ini diuji ulang oleh
> `analisis/analisis_storyboard.ipynb` — semuanya cocok. Dua catatan dari notebook:
> (1) **jangan klaim "rekor 2023–24" dari data sendiri** — dalam data kita tahun rekor
> adalah 2019 (1,26 jt kasus) karena Vietnam & Filipina hanya lengkap sampai 2022;
> sitasi WHO/Tian dkk. 2025 untuk 2023–24. (2) Evaluasi ambang pemicu (hal. 11):
> aturan "musim puncak (Jan–Apr) DAN ONI jeda-4 ≥ 0,5" menandai 11,6% bulan dengan
> **presisi 100%** (semua bulan beralarm benar-benar kuartil teratas kasus; lift 4×) —
> angka jadi untuk halaman viabilitas.

## Hasil analisis pendalaman (9 Agustus 2026) — amunisi menjawab juri

Lima uji tambahan di notebook (bagian "Analisis pendalaman"); angka lengkap siap salin
ada di `analisis/keluaran/angka_kunci_storyboard.md`.

1. **"Korelasimu cuma musim?" — Tidak.** Setelah semua deret diubah jadi anomali
   (z-score per bulan kalender), ONI Indonesia bertahan **r = +0,56** (dari +0,59),
   dan suhu justru **menguat** ke +0,57 (dari +0,47); ONI Thailand menguat ke +0,41.
   Yang runtuh hanya hujan (+0,40 → +0,24; Thailand → −0,11) — jadi **jangan jadikan
   hujan prediktor utama**; perannya musiman, bukan antar-tahun. (`g09`)
2. **"Artefak agregat nasional?" — Tidak.** Rasio kasus bulan-El-Niño ÷ bulan lain > 1
   di **33/34 provinsi Indonesia** (uji tanda p = 2×10⁻⁹; satu-satunya pengecualian
   Aceh ≈ 1,0) dan **70/77 provinsi Thailand** (p = 2×10⁻¹⁴). (`g10`)
3. **"Aturanmu overfit?" — Tidak.** Aturan dari 2010–2016 diuji buta di 2017–2024:
   presisi **tetap 100%** (lift 3,9). Replikasi Thailand dengan prediktor terbaiknya
   (Jun–Sep DAN anomali suhu jeda-2 > 0): presisi uji 67%, lift 2,7.
4. **Tenggang nyata per episode** (`episode_elnino_tenggang.csv`): alarm ONI teramati
   memberi tenggang 0–3 bulan sebelum kasus melewati P75 (2023-24: alarm Sep-2023,
   lewat ambang Des-2023), dan **setiap** episode El Niño sejak 2009 berpuncak jauh di
   atas ambang (19–32 rb kasus/bulan vs P75 11,9 rb). Framing yang benar di storyboard:
   nilai utama alarm adalah **memprediksi separah apa musim yang datang** (plus arah
   provinsi mana), bukan menggeser tanggal mulainya; tenggang memanjang lagi bila
   memakai **ramalan** ONI NOAA/BMKG yang terbit berbulan-bulan di muka.
5. **Prioritas adopsi fase-1** (insidens resmi 2018–2020 + bulan puncak):
   Bali (134/100rb, puncak Mei!), Kaltara (115, Des), Kaltim (112, Jan) — kontras 14×
   dengan provinsi terendah; jadwal siaga per provinsi di `kalender_risiko_idn.csv`.
6. **Standar baku diaplikasikan** (`g12`, `ambang_pemicu_vs_kanal_endemis.csv`,
   `benchmark_ews.csv`): terhadap definisi wabah **kanal endemis** (mean+2SD, praktik
   WHO/PAHO — yang otomatis menghapus musim), aturan musiman murni kehilangan nilai
   (lift 0,85), dan **seluruh nilai tambah datang dari El Niño** (aturan B: sens 62%,
   lift 2,1; aturan D: spesifisitas 91%, lift 2,5) — bukti independen kepala cerita.
   PPV 30% vs tolok ukur EWARS 43–86% dijelaskan jujur: kami tanpa model statistik dan
   bulanan, EWARS bermodel penuh mingguan; ambang ONI ≥ 0,5 kami = definisi resmi
   NOAA/CPC.
7. **Dampak dalam dolar** (`dampak_moneter.csv`): 10% kasus musim puncak tercegah =
   **US$1,5–3,7 juta/tahun (Rp 24–59 miliar)**, jangkar biaya rawat inap US$316–791
   per kasus (Nadjib 2019; Wilastonegoro 2020); pembanding beban dengue nasional
   US$381–681 juta/tahun.
8. **Klaim inovasi lama diuji dan direvisi** (`g11`, `inovasi_kekeringan_akses_air.csv`):
   interaksi kekeringan × akses air tidak terpisahkan dari efek El Niño di data kita
   (r parsial −0,15) dan tidak termoderasi akses pipa (ρ = +0,34, p = 0,46, n = 7) —
   lihat butir 3 di atas untuk posisi inovasi penggantinya. Catatan metode: pengganda
   El Niño antar negara **jangan** dibandingkan langsung — jendela panelnya beda
   (negara ≤2010 punya pengganda ≈1,0 karena era El Niño yang tertangkap berbeda).

## Mengapa ide ini kuat

1. **Sinyalnya sudah terverifikasi di data kita sendiri** (bukan sekadar klaim makalah).
   Dihitung dari `dengue_iklim_bulanan.csv`, agregat nasional bulanan 2010–2024:

   | Negara | Prediktor | Jeda terbaik | Korelasi |
   |---|---|---|---|
   | Indonesia (1,72 jt kasus) | **ONI (El Niño)** | **3–4 bulan** | **r = +0,59** |
   | Indonesia | Suhu | 2–3 bulan | r = +0,47 |
   | Indonesia | Hujan | 1–2 bulan | r = +0,40 |
   | Thailand (612 rb kasus) | Suhu | 2–3 bulan | r = +0,57 |
   | Thailand | Hujan | 0–1 bulan | r = +0,48 |
   | Thailand | ONI | 6–7 bulan | r = +0,28 |

   Pola jeda ini persis yang dilaporkan literatur: hujan menaikkan kasus dengan jeda
   1–3 bulan, suhu bekerja lebih lambat lewat siklus nyamuk.

   **Temuan paling kuat — dan ini jadi kepala cerita**: untuk Indonesia, indeks El Niño
   (ONI) mengalahkan suhu maupun hujan, dengan tenggang **3–4 bulan**. Rata-rata kasus
   per bulan menurut fase ENSO 4 bulan sebelumnya (kolom `fase_enso_jeda4`):

   | Fase ENSO | Rata-rata kasus/bulan | n bulan |
   |---|---|---|
   | La Niña kuat | 7.189 | 3 |
   | La Niña | 8.111 | 50 |
   | Netral | 7.597 | 68 |
   | El Niño | 12.338 | 35 |
   | **El Niño kuat** | **21.383** | 16 |

   Karena ONI dipublikasikan bulanan **dan diramalkan berbulan-bulan ke depan**, ini alarm
   dini yang benar-benar bisa dipakai — bukan sekadar korelasi retrospektif.

   **Sampaikan sinyal ini dengan jujur** (dan itu justru menguatkan halaman keterbatasan):
   yang kokoh adalah **kontras El Niño vs sisanya** — bertahan di semua jeda 2–7 bulan,
   dengan El Niño kuat konsisten ±2,5–3× bulan netral. Yang **tidak** kokoh adalah urutan
   La Niña vs Netral: keduanya praktis setara dan urutannya berbalik tergantung jeda
   (monotonik penuh baru muncul di jeda 5–7, sementara korelasi justru memuncak di jeda 4).
   Jadi jangan klaim "makin La Niña makin aman" — klaim yang benar adalah
   **"El Niño menaikkan risiko, dan El Niño kuat menaikkannya tajam"**.
   Kategori La Niña kuat hanya 3 bulan pengamatan, terlalu tipis untuk disimpulkan.

2. **Didukung literatur mutakhir dan spesifik Asia Tenggara** — tinjauan sistematis 2025
   menegaskan suhu & hujan berasosiasi kuat dengan insidens dengue di Asia Tenggara dan
   secara eksplisit menyerukan integrasi data iklim ke sistem peringatan dini; pemodelan
   memproyeksikan lonjakan besar (Chiang Mai bisa >10× pada 2090-an, skenario SSP585).
   El Niño 2023–24 diestimasi menambah 9,6 juta kasus global. (Sitasi lengkap di bawah.)

3. **Sudut inovasi — DIREVISI setelah diuji (9 Agu 2026, Pendalaman 6).** Klaim lama
   "interaksi kekeringan × akses air" **tidak selamat dari uji data sendiri**: efek
   defisit hujan Indonesia (r = −0,31, jeda 7) menyusut ke r parsial −0,15 setelah
   dikontrol ONI (sebagian besar bayangan El Niño), dan moderasi akses perpipaan
   lintas 7 negara hanyalah derau (Spearman ρ = +0,34, p = 0,46; Malaysia/Singapura
   yang 93–100% berpipa efek kekeringannya setara Vietnam yang 15%). **Jangan klaim
   interaksi ini dari data kita** — sebut mekanisme penimbunan air hanya sebagai
   rasional dari literatur (Lowe dkk. 2021; Gibb dkk. 2023).

   Inovasi yang benar-benar bisa kita pertahankan dengan data sendiri:
   - **Aturan pemicu operasional yang tervalidasi luar-sampel** (presisi 100% pada
     2017–2024 yang tak pernah dilihat aturannya) + **kalender risiko per provinsi**
     — bukan model kotak-hitam, bisa dijalankan dinkes tanpa satu baris kode.
   - **Lapisan WASH sebagai penyasaran, bukan kausalitas**: akses air/sanitasi memilah
     provinsi prioritas fase-1 (lintas-SDG 3×13×6), dipisahkan tegas dari klaim mekanisme.
   - **Kejujuran metodologis sebagai fitur**: kami menguji sudut inovasi kami sendiri
     dan merevisinya — persis perilaku yang dinilai di halaman keterbatasan (dan jarang
     dilakukan peserta lain).

4. **Viabilitasnya konkret**: rekomendasi bukan "bangun AI", melainkan ambang pemicu
   sederhana (misal: "suhu bulanan > persentil-90 dan hujan kumulatif 2 bulan > X mm →
   naikkan status siaga, gencarkan PSN/3M 4–8 minggu sebelum musim puncak") — pendekatan
   *no-regrets* yang diadvokasi literatur One Health untuk Vietnam, cocok dengan bobot
   juri: analisis 25%, relevansi-dampak 20%, viabilitas 15%.

## Kerangka 15 halaman (bobot juri dalam kurung)

1. Sampul — judul + tim.
2. **Masalah (10%)**: beban dengue ASEAN, rekor 2023–24, peta kasus per negara.
3. Pertanyaan analisis: bisakah iklim jadi alarm dini? Kerangka SDG 3×13×6.
4. Data & metode: 9 dataset terbuka, semua grafik dari SAP Analytics Cloud.
5. **Analisis 1 (25%)**: musiman dengue vs hujan — kurva bulanan tumpang tindih (THA, IDN).
6. Analisis 2: *scatter + jeda* — suhu jeda 2–3 bulan vs kasus (r≈0,5–0,6).
7. **Analisis 3 (kartu as)**: batang rata-rata kasus menurut fase ENSO 4 bulan sebelumnya —
   El Niño kuat 21,4 rb vs netral 7,6 rb kasus/bulan di Indonesia (±2,8×).
8. Analisis 4: peta panas provinsi × bulan (Indonesia/Thailand) — di mana & kapan alarm.
9. Analisis 5: lapisan kerentanan — akses air perpipaan/sanitasi + penduduk di zona banjir.
10. Sintesis: "kalender risiko" per negara (bulan siaga per provinsi).
11. **Solusi (15% inovasi)**: dasbor SAC + ambang pemicu sederhana per provinsi.
12. **Viabilitas (15%)**: siapa memakai (dinkes provinsi), biaya ~nol (data terbuka,
    diperbarui bulanan), langkah adopsi 3 fase.
13. **Dampak (20%)**: intervensi 4–8 minggu lebih awal; sensitivitas: bila 10% kasus
    puncak tercegah = X ribu kasus/tahun (hitung di SAC).
14. Keterbatasan & etika data (kejujuran = nilai plus di penjurian).
15. Referensi (di luar hitungan 15 halaman menurut aturan).

## Data yang SUDAH siap impor SAC (`data/siap-sac/`)

| Berkas | Baris | Cakupan |
|---|---|---|
| **`dengue_iklim_bulanan.csv`** | **55.329** | **Pakai ini untuk Analisis 1–4.** Provinsi-bulan, 7 negara: kasus + suhu/hujan jeda 0–3 bln + ONI jeda 0/3/4 + fase ENSO — jeda sudah dihitung |
| `dengue_asean.csv` | 70.397 | 10 negara, 1955–2025, nama provinsi sudah dinormalkan |
| `iklim_bulanan_asean.csv` | 9.000 | suhu & hujan bulanan 10 negara, 1950–2024 (ERA5 0,25°) |
| `enso_oni_bulanan.csv` | 918 | ONI bulanan 1950–2026 + label fase |
| `wash_rumahtangga_asean.csv` | 8.692 | air/sanitasi/higiene rumah tangga, 2000–2024 |
| `wash_fasyankes_asean.csv` | 5.625 | WASH fasilitas kesehatan, 2003–2024 |
| `kota_asean_paparan_banjir.csv` | 30.348 | 836 kota, penduduk terpapar banjir 10 & 100 tahunan, 1975→2030 |
| `kota_asean_kualitas_udara.csv` | 622 | PM2.5/PM10/NO2 kota ASEAN (berhenti 2021) |
| `sampah_kabkota_indonesia.csv` | 514 | timbulan & pengelolaan sampah semua kab/kota Indonesia |

Kunci gabung antar-tabel: `iso3` + `tahun` (+ `periode` untuk dengue×iklim).

**Cakupan panel bulanan-provinsi** — jauh lebih kaya dari dugaan awal: Thailand punya
**30 tahun penuh** (1993–2022, 77 provinsi), Indonesia 15 tahun (2004–2024, 38 provinsi),
Vietnam 16 tahun (1995–2010, 64 provinsi), ditambah Kamboja, Laos, Malaysia, Singapura.
Hanya Thailand & Indonesia yang berlanjut setelah 2010.

## Bahan tambahan untuk halaman 9 (kerentanan)

`kota_asean_paparan_banjir.csv` memberi angka yang enak dipakai di halaman kerentanan —
banjir meninggalkan genangan, dan genangan adalah tempat berkembang biak nyamuk:

| Kota | Penduduk 2025 | Di zona banjir 100-thn (2020) | % | Proyeksi 2030 |
|---|---|---|---|---|
| Bangkok | 19,0 jt | 12,95 jt | **74,3%** | 15,36 jt |
| Manila | 25,9 jt | 5,37 jt | 22,0% | 5,90 jt |
| Ho Chi Minh City | 14,6 jt | 3,58 jt | 27,7% | 4,46 jt |
| Hanoi | 5,0 jt | 2,85 jt | 56,4% | 2,71 jt |
| Jakarta | 40,5 jt | 1,72 jt | 4,5% | 1,94 jt |

## ⚠️ Jebakan yang sudah diuji: bencana ≠ pendorong dengue (di data ini)

`bencana_kabkota_indonesia.csv` (478 kab/kota, 2018–2020) menggoda untuk dipakai
membuktikan "banjir → genangan → dengue". **Jangan** — sudah saya uji dan hasilnya nol:

Dihitung ulang di `analisis/analisis_storyboard.ipynb` (Pendalaman 6b) — panel
33 provinsi × 2018–2020 = 99 baris; hasilnya diekspor ke
`analisis/keluaran/banjir_vs_dengue_uji.csv` dan `banjir_vs_dengue_panel.csv`.

| Uji | Korelasi | p |
|---|---|---|
| Angka **mentah**: rumah terendam vs kasus dengue | **r = +0,54** ⚠️ menyesatkan | <0,001 |
| Angka mentah: jumlah kejadian vs kasus | **r = +0,66** ⚠️ menyesatkan | <0,001 |
| **Per 100 rb penduduk**: rumah terendam vs insidens | r = −0,14 | 0,17 |
| Per 100 rb: jumlah kejadian vs insidens | r = +0,01 | 0,90 |
| Jeda 1 tahun (banjir T → dengue T+1), per kapita | r = −0,05 | 0,68 |
| Perubahan antar-tahun **dalam provinsi yang sama** | r = −0,30 | 0,016 |

> **Koreksi (18 Agu 2026):** baris terakhir sebelumnya ditulis −0,16; hitungan ulang
> di notebook memberi **−0,30** (rumah terendam) dan **−0,33** (jumlah kejadian),
> keduanya signifikan. Empat baris lainnya reproduksi persis. Arah negatif yang
> signifikan itu **bukan** bukti banjir menekan dengue — dugaan terkuat adalah artefak
> pelaporan (tahun bencana berat = surveilans DBD terganggu). Tetap dilaporkan sebagai
> **hasil nol**, bukan temuan.

Korelasi mentah yang tampak kuat itu **artefak ukuran penduduk**: Jawa Barat punya
banyak bencana *dan* banyak kasus dengue semata-mata karena penduduknya 50 juta.
Begitu dinormalkan per kapita atau dilihat perubahannya dalam provinsi yang sama,
hubungannya hilang. Kalau grafik ini masuk storyboard tanpa normalisasi, satu
pertanyaan juri soal penyebut akan merobohkannya.

Kenapa hubungannya tak terdeteksi walau literatur bilang ada? Karena resolusinya
tidak cocok: bencana **tahunan per provinsi**, sedangkan mekanisme banjir→dengue
bekerja **mingguan sampai bulanan dan sangat lokal**. Datanya terlalu kasar untuk
menangkapnya — bukan bukti bahwa hubungan itu tidak ada.

**Pakai data ini sebagai konteks, bukan sebagai analisis**: mis. "X rumah terendam
per tahun di provinsi Y" di halaman masalah/kerentanan, berdampingan dengan paparan
banjir GHS (potensi termodelkan) — bencana BNPB adalah kejadian **teramati**.

## Risiko & mitigasi

- **Panel per negara berbeda jendela waktunya** — jangan bandingkan total antar negara
  begitu saja. Untuk analisis pasca-2010 pakai Indonesia (utama) & Thailand (replikasi);
  Vietnam/Kamboja/Laos/Malaysia hanya untuk periode ≤2010.
- Korelasi ≠ kausalitas → bingkai sebagai *early warning*, bukan klaim kausal;
  kutip tinjauan sistematis untuk mekanisme.
- **Insidens saat ini hanya untuk Indonesia 2018–2020** (BPS proyeksi SP2010, 34 provinsi,
  via arsip Wayback — 1.190 baris provinsi-bulan). Bisa naik ke 2020–2024/38 provinsi
  begitu kunci WebAPI BPS diisi. Di luar itu angkanya **kasus mentah**, jadi jangan
  memeringkat wilayah; pakai pola waktu. Kolom `insidens_per_100rb` sengaja dikosongkan
  kalau penduduknya tidak ada, bukan diisi taksiran.
  Contoh yang sudah bisa dipakai: insidens tahunan tertinggi 2018–2020 adalah
  **Bali 267,9 per 100 rb (2020)** dan Kalimantan Utara 255,0 (2019); terendah Maluku
  dan Papua di kisaran 4–6 — kontras yang jauh lebih bermakna daripada jumlah kasus mentah,
  karena Jawa Barat selalu menang di angka mentah semata-mata karena penduduknya terbanyak.
- Penduduk BPS bersifat **tahunan**, kasus bersifat **bulanan**; insidens bulanan dihitung
  memakai penduduk pertengahan tahun yang sama. Untuk perbandingan antarbulan itu wajar,
  tapi sebutkan asumsinya di halaman metode.
- Semua grafik wajib SAC → kolom jeda sudah dihitung di `dengue_iklim_bulanan.csv`,
  jadi tidak perlu *lagged join* di dalam SAC.
- Pemekaran wilayah: empat provinsi baru Papua hanya punya data 2023+; Prachin Buri
  (Thailand) sebelum 2003 kemungkinan masih mencakup Sa Kaeo.

## Sitasi kunci (untuk halaman referensi)

- Sutriyawan dkk. 2025 — tinjauan sistematis iklim–dengue Asia Tenggara; dorong EWS berbasis iklim.
- Wang dkk. 2023 (*Infectious Disease Modelling*) — proyeksi epidemi dengue di 4 kota Asia Tenggara sampai 2090-an.
- Wang dkk. 2022 (*Environment International*) — cuaca ekstrem & jeda 1–3 minggu risiko dengue.
- Lowe dkk. 2021 (*Lancet Planetary Health*) — kekeringan ekstrem menaikkan risiko dengue jeda 3–5 bulan di kota dengan pasokan air buruk.
- Gibb dkk. 2023 (*Nature Communications*) — infrastruktur air & pemanasan menjelaskan ekspansi dengue Vietnam.
- Tian dkk. 2025 (*Nature Communications*) — El Niño 2023–24 ≈ +9,6 juta kasus global.
- Quan dkk. 2026 (*Science in One Health*) — ambang pemicu meteorologis sederhana untuk EWS dengue Vietnam.

**Tambahan terverifikasi 9 Agu 2026** (pranala lengkap per klaim:
`analisis/keluaran/referensi_per_klaim.md`):

- **Djaafara dkk. 2026 (*PLOS NTD*)** — provinsi Indonesia 2010–2024 (data yang sama
  dengan kita): insidens tahun El Niño kuat **+96%**; menganjurkan sistem dua-tingkat
  "ENSO untuk kesiapan strategis + iklim lokal untuk taktis" — **validasi eksternal
  terkuat untuk desain kami**.
- Tian dkk. 2025 (*Nat Commun*) — juga: ENSO menjelaskan **63%** variasi kasus dengue
  57 negara; 2015-16 = +4,1 jt kasus.
- Hussain-Alkhateeb dkk. 2017/2018 (**WHO-TDR EWARS**, panduan operasional) — kerangka
  evaluasi sens/spes/PPV yang kami ikuti; Baharom dkk. 2022 (tolok ukur 17 EWS:
  PPV 43–86%); Cárdenas dkk. 2021 (EWARS Meksiko: sens 100%, PPV 83%); Schlesinger
  dkk. 2024 (EWARS-csd Kolombia: median sens 97%, PPV 75%).
- Nadjib dkk. 2019 (*PLoS NTD*) & Wilastonegoro dkk. 2020 (*AJTMH*) — biaya per kasus
  Indonesia US$90–791; beban nasional US$381–681 jt/tahun.
- Sasmono dkk. 2026 (*IJID Regions*) — Bali & Kaltim insidens tertinggi 2000–2020
  (**validasi independen peringkat kami**); faktor ekspansi pelaporan 1,66–34×.
- Childs dkk. 2025 (*PNAS*) — 18% insidens historis akibat pemanasan antropogenik.
- **Standar yang diaplikasikan langsung**: NOAA CPC ONI (El Niño = ONI ≥ 0,5) dan
  kanal endemis mean+2SD (WHO/PAHO) — lihat Pendalaman 7 di notebook.

Data: OpenDengue V1.3 (10.6084/m9.figshare.24259573.v4); World Bank CCKP ERA5 0,25°;
WHO/UNICEF JMP 2025.
