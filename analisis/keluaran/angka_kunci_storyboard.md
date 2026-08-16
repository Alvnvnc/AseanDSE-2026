# Angka kunci storyboard — dihitung & diverifikasi notebook analisis
(jendela 2010+, sumber di README; semua bisa direproduksi sel-per-sel)

## Kepala cerita (halaman 7)
- El Niño kuat = **21,4 rb kasus/bulan** vs netral 7,6 rb di Indonesia (2,8x); El Niño biasa 12,3 rb.
- Sinyal BUKAN musim semata: korelasi ONI jeda 3-4 terhadap **anomali** kasus
  (musim sudah dibuang) tetap **r = +0.56**.
- Efek konsisten antar provinsi: **33/34 provinsi Indonesia** (uji tanda p = 2e-09)
  dan 70/77 provinsi Thailand (p = 1.8e-14) kasusnya lebih tinggi pada bulan El Niño.

## Aturan alarm (halaman 11-12)
- "Musim puncak (Jan-Apr) DAN ONI jeda-4 >= 0,5" pada data penuh 2010-2024:
  presisi 100%, lift 4x, menyala hanya 11,6% bulan.
- **Uji luar-sampel** (aturan dari 2010-2016, diuji buta 2017-2024):
  presisi 100%, sensitivitas 44%, lift 3.91.
- Replikasi Thailand ("Jun/Jul/Agu/Sep DAN suhu 2 bulan
  lalu di atas normal): lift uji 2.67.

## Tenggang waktu nyata (halaman 10-11)
- Episode El Niño 2023-24: alarm menyala 2023-09, kasus melewati P75 pada
  2023-12 -> tenggang 3 bulan; puncaknya 32,049 kasus/bulan.
- Seluruh episode sejak 2009 tercatat di `episode_elnino_tenggang.csv`; pakai ramalan
  ONI (bukan teramati) untuk tenggang lebih panjang lagi.

## Prioritas wilayah (halaman 9, 12)
- Insidens tertinggi 2018-2020: Bali (134/100rb),
  Kalimantan Utara (115), Kalimantan Timur (112).
- Bulan puncak tersering: Indonesia Jan (20 prov), Feb (8 prov) dari 35 provinsi;
  Thailand Jul (38 prov), Agu (16 prov) dari 77 provinsi.

## Dampak (halaman 13)
- Rata-rata 104,753 kasus/tahun (Indonesia, tahun lengkap 2015-2023); 44% jatuh di Jan-Apr.
- Skenario: 10% kasus musim puncak tercegah = ~4,656 kasus/tahun;
  20% = ~9,312; 30% = ~13,968.

## Sudut inovasi: kekeringan x akses air (halaman 9 / inovasi) — eksploratif, n=7
- Efek kekeringan per negara (r anomali paling negatif, jeda 3-8):
  Indonesia -0.31 (jeda 7, pipa 20%); Thailand -0.18 (jeda 5, pipa 50%); Vietnam -0.14 (jeda 7, pipa 15%); Kamboja -0.18 (jeda 5, pipa 10%); Laos -0.06 (jeda 4, pipa 21%); Malaysia -0.14 (jeda 8, pipa 93%); Singapura -0.14 (jeda 8, pipa 100%).
- Moderasi akses perpipaan: Spearman rho = +0.34 (p = 0.46);
  vs pengganda El Nino: rho = +0.54 (p = 0.22). n kecil -> laporkan sebagai ARAH.
- Indonesia: efek kekeringan jeda-7 r -0.31; setelah dikontrol ONI jeda-4
  tersisa r parsial -0.15.

## Standar & tolok ukur (halaman 11-12)
- Ambang ONI >= 0,5 di aturan kami = definisi resmi El Nino NOAA/CPC - bukan ambang karangan.
- Terhadap definisi wabah STANDAR (kanal endemis WHO/PAHO, mean+2SD 5 tahun): 21 bulan
  wabah di 2010+; aturan D: sensitivitas 29%,
  spesifisitas 91%,
  presisi 30%, lift 2.46.
- Tolok ukur EWS terpublikasi (utk konteks, bukan tandingan langsung): PPV 43-86%
  (tinjauan 17 EWS, Baharom 2022); EWARS Meksiko PPV 83% (Cardenas 2021); EWARS-csd
  Kolombia median PPV 75% (Schlesinger 2024). Rincian: `benchmark_ews.csv`.

## Dampak dalam dolar (halaman 13)
- 10% kasus musim puncak tercegah (~4,656 kasus) = **US$1.5-3.7 juta/tahun**
  (Rp 24-59 miliar; jangkar biaya rawat inap US$316-791:
  Wilastonegoro 2020, Nadjib 2019). Jangkar paling konservatif (US$90/episode): US$0.42 jt.
- Pembanding beban nasional dengue: US$381 jt (2015) - US$681 jt (2017) per tahun.

## Kejujuran data (halaman 14)
- Rekor dalam data = 2019 (1,26 jt kasus, 9 negara); total 2023-24 tak bisa dibandingkan
  (VNM & PHL lengkap hanya s.d. 2022) -> sitasi WHO/Tian dkk. untuk 2023-24.
- Insidens hanya 2018-2020 (penyebut resmi BPS); di luar itu kasus mentah, jangan
  memeringkat antar wilayah.
- Korelasi bukan kausalitas -> bingkai sebagai early warning; mekanisme dari literatur.
