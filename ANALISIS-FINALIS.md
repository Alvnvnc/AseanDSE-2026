# Apa yang sebenarnya dikirim finalis ASEAN DSE

Basis: **15 dek finalis** yang diunduh dari galeri resmi
[aseandse.org/asean-dse-storyboard](https://aseandse.org/asean-dse-storyboard/)
(angkatan 2024 dan 2025), plus halaman
[Data Analytics Storyboard Requirement](https://aseandse.org/data-analytics-storyboard-requirement/)
dan [Judging Criteria](https://aseandse.org/judging-criteria/). Diakses 17 Agustus 2026.

## ⚠ Peringatan penting soal basis ini

Berkas di galeri itu **bukan storyboard 15 halaman**. Panjangnya 26–79 halaman
(median **48**) — itu dek presentasi National/Regional Finals, tahap *sesudah*
storyboard lolos seleksi. Jadi:

- Untuk **struktur naratif, konvensi desain, dan cara finalis menyusun argumen**,
  dek ini sahih dan langsung berguna.
- Untuk **kepadatan per halaman pada storyboard 15 halaman**, angkanya tidak bisa
  dipakai mentah — storyboard adalah versi mampat dari busur yang sama.

## Aturan resmi (dikutip dari halaman panitia)

| | |
|---|---|
| Format | PDF, **landscape** |
| Ukuran | maks. **20 MB**; tiap gambar maks. **2 MB** |
| Halaman | maks. **15 termasuk sampul**, **di luar** halaman referensi |
| Grafik | **wajib dihasilkan SAP Analytics Cloud**, harus jelas terbaca |
| Nama berkas | `NEGARA_NAMA TIM` (mis. `LAO PDR_TEAM DATA`) |
| Sampul wajib memuat | judul, nama tim, institusi, negara, SDG, **deskripsi singkat** |

Bobot penjurian: Analysis & Insights 25% · Relevancy & Impact 20% · Viability 15%
· Innovation 15% · Presentation Delivery 15% · Problem Definition 10%.

## Temuan 1 — tidak satu pun dek diekspor dari SAC

Metadata *Producer* dari 15 berkas:

| Alat | Jumlah |
|---|---|
| Canva | 4 |
| Microsoft PowerPoint | 4 |
| Adobe PDF Library (InDesign/Illustrator) | 4 |
| iLovePDF | 1 |
| tanpa metadata | 2 |
| **SAP Analytics Cloud** | **0** |

Pemeriksaan `pdfimages` mengonfirmasi polanya: grafik di dalam dek adalah
**raster PNG/JPEG tertempel**, berukuran 880×610 sampai 1316×1006 px, terpasang
pada 85–120 ppi efektif.

**Artinya**: aturan "grafik wajib dihasilkan SAC" ditafsirkan sebagai *grafiknya
dibuat di SAC lalu diekspor sebagai gambar* — bukan *seluruh PDF diekspor dari
SAC*. Tata letaknya dikerjakan di alat desain. Inilah yang membuat pendekatan
LaTeX di `storyboard/` sah: posisinya persis sama dengan Canva dan PowerPoint.

## Temuan 2 — geometri halaman seragam 16:9

Semua 15 dek 16:9. Rinciannya 1440×810 pt (11 dek), 960×540 (3), 720×405 (1).
`storyboard/storyboard.tex` memakai **960×540 bp**, rasio identik.

## Temuan 3 — busur naratif yang berulang

Diverifikasi halaman per halaman pada 4 dek (CircularEat/Brunei, Agrigrow/Indonesia,
MentaLink/Singapura, GreenLoop/Malaysia). Polanya konsisten:

1. **Sampul** — judul + tagline + tim/institusi/negara
2. **Kait emosional** — satu klaim mengejutkan atau analogi, tanpa grafik
   (MentaLink membuka dengan *"We All Know a Heart Attack is an Emergency"* dan
   baru masuk kesehatan jiwa lima halaman kemudian)
3. **Analisis isu**, dipecah jadi Issue 1 / Issue 2 / Issue 3 dengan halaman
   pemisah bernomor
4. **Rumusan masalah** — sering ditulis sebagai *"How might we…"*
5. **Solusi berupa produk bernama** + mockup antarmuka
6. **Fitur per pemangku kepentingan** (konsumen, vendor, pemerintah)
7. **Linimasa implementasi** (Tahun 1/2/3, atau 2025–2029)
8. **Keselarasan dengan ASEAN Blueprint / SDG indicator**
9. **Model bisnis / ekonomi**
10. **Referensi** (1–3 halaman) → **lampiran** (bisa 12 halaman)

Konvensi desain yang muncul berulang:

- **Breadcrumb bagian di setiap halaman.** Agrigrow: `Problem · Data analytics ·
  Solution · Implementation · Conclusion`. GreenLoop: `Problem Statement · Issue
  Analysis · Recommendation · Implementation`. Bagian aktif disorot.
  *Sudah diadopsi di dek kita.*
- **Judul dua tingkat**: label bagian kecil di atas, lalu judul besar yang sering
  berupa pertanyaan (*"HOW MUCH FOOD IS WASTED IN ASEAN ALONE?"*), lalu judul
  grafik sendiri.
- **Halaman pernyataan tanpa grafik** untuk memberi jeda napas — CircularEat
  memakai 6 dari 39 halaman untuk ini.
- **Baris sumber di kaki setiap halaman berdata.**

Kepadatan teks: median **57 kata/halaman**; dek terkuat 86–115 kata/halaman.
Dek kita berada di kisaran atas rentang itu — sesuai, karena storyboard dinilai
dari dokumen, bukan dari presentasi lisan.

## Temuan 4 — celah dek kita dibanding rata-rata finalis

| | Rata-rata finalis | Dek kita |
|---|---|---|
| Produk bernama + mockup UI | **15 dari 15** punya (CircularEat, Agrigrow, MentaLink, GreenLoop, Nurture Hub) | tidak ada — solusi kita berupa *aturan*, bukan produk |
| Keselarasan ASEAN Blueprint / work plan | halaman tersendiri di sebagian besar dek | belum ada |
| Peran pemangku kepentingan disebut namanya | umum (pemerintah, NGO, swasta) | baru "adoption in three phases" |
| Sentuhan AI / teknologi digital | hampir semua | **sengaja tidak ada** |
| Lampiran | 5–12 halaman | belum ada |

Tiga hal yang perlu diputuskan:

1. **Produk.** Panitia menyatakan tim *"encouraged to create an app or
   technological prototype"* untuk memperkuat pencalonan di National Finals.
   Kuota 15 halaman kita masih menyisakan **satu halaman** (14 halaman isi
   terpakai). Halaman 15 di berkas LaTeX sudah disiapkan sebagai tempatnya.
2. **Risiko pada bobot Innovation (15%).** Sub-kriteria resminya menyebut
   *"Integration of AI and digital technology"*. Posisi kita — *"Two conditions.
   No model. No code."* — adalah kekuatan besar untuk **Viability**, tapi
   berhadapan langsung dengan sub-kriteria itu. Ini pilihan sadar, bukan
   kelalaian; siapkan jawabannya, atau bungkus aturan tersebut sebagai dashboard/
   aplikasi supaya dua-duanya kena.
3. **ASEAN work plan.** Kriteria Problem Definition menyebut *"connection to
   specific ASEAN work plans/priorities"* secara eksplisit. Satu kalimat di
   halaman 3 atau 12 sudah cukup menutup ini.

## Temuan 5 — di mana dek kita justru unggul

Dari 15 dek yang dibaca, **tidak satu pun** melakukan hal-hal berikut:

- **Memfalsifikasi ide sendiri di depan juri.** Halaman 14 kita membuang sudut
  inovasi "kekeringan × akses air" setelah gagal uji. Tidak ada tandingannya di
  15 dek itu.
- **Uji luar sampel.** Aturan dilatih 2010–2016, diuji buta 2017–2024.
- **Pembanding terhadap sistem terpublikasi.** PPV 43–86% dari tinjauan 17 sistem
  EWS dengue.
- **Melaporkan hasil nol.** Korelasi banjir r = +0,66 yang runtuh jadi −0,14
  setelah dibagi penduduk.

Bobot Analysis & Insights adalah **25%**, yang terbesar. Empat hal di atas persis
yang dinilai di sana, dan tak satu pun dibayar dengan halaman tambahan — semuanya
sudah muat.

---

Berkas dek finalis yang diunduh tidak dimasukkan ke repo (hak cipta peserta).
Untuk mengunduh ulang, tautannya ada di galeri resmi yang disebut di atas.
