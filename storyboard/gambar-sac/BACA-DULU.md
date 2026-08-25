# Folder ekspor grafik SAP Analytics Cloud

> **Panduan kerja lengkapnya ada di `storyboard/panduan-sac.pdf`** — alur 5 langkah,
> palet, syarat ekspor, katalog 23 slot beserta resepnya, dan cek terakhir sebelum
> submit. Berkas ini hanya daftar ringkasnya.

Setiap kotak putus-putus di `storyboard.pdf` adalah **slot** yang menunggu satu berkas
PNG di folder ini. Begitu berkasnya ada, `pdflatex` otomatis memasang gambarnya
menggantikan kotak placeholder — tidak perlu menyunting `storyboard.tex`.

> **Sekarang ada jalur otomatis.** Grafiknya dibangun di SAC lewat REST internal
> (story `swalloy-grafik`, satu grafik per halaman) lalu ditangkap jadi PNG
> dengan nama yang persis seperti daftar di bawah:
>
> ```sh
> otomasi-sac/edge-mulai.sh                    # Edge kedua yang bisa dikendalikan
> .venv/bin/python otomasi-sac/bangun-story.py # bangun/segarkan grafiknya
> .venv/bin/python otomasi-sac/tangkap.py      # tangkap PNG ke folder ini
> ```
>
> Langkah manual di bawah tetap berlaku sebagai cadangan. Rinciannya:
> `otomasi-sac/README.md`.

## Cara kerja

1. Buat grafiknya di SAP Analytics Cloud mengikuti resep yang tertulis di dalam
   kotak placeholder (jenis grafik, dataset, measure, dimension, filter, sort).
2. Di SAC: klik widget → menu **⋮** → *Export* → **PNG**. Kalau menu itu tidak
   tersedia, pakai *Export → PDF* untuk seluruh halaman lalu potong per widget,
   atau tangkap layar pada tampilan penuh.
3. Simpan ke folder ini dengan **nama persis** seperti di daftar di bawah.
4. Jalankan `./bangun.sh` — skripnya melaporkan slot mana yang masih kosong.

## Syarat teknis

| | |
|---|---|
| Format | PNG |
| Lebar minimal | 1600 px (kotak terlebar di dek 636 bp; 1600 px ≈ 2,5× — tajam saat di-zoom juri) |
| Ukuran maksimal | **2 MB per gambar** (aturan panitia) |
| Latar | putih atau transparan, jangan abu-abu tema gelap |

Kalau PNG-nya lebih dari 2 MB:

```sh
# butuh imagemagick
mogrify -resize 1800x -strip -quality 92 nama-berkas.png
```

## Daftar berkas yang dibutuhkan

Halaman merujuk ke nomor halaman di `storyboard.pdf`.

| Hal | Nama berkas | Grafik |
|---|---|---|
| 2 | `h02-tren-tahunan.png` | Line chart — kasus dengue ASEAN 2000–2024 |
| 2 | `h02-per-negara.png` | Bar horizontal — kasus per negara, tahun lengkap terbaru |
| 3 | `h03-alur.png` | Diagram Shapes+Text — indeks publik → jeda → lonjakan → aksi |
| 5 | `h05-musiman-idn.png` | Combination chart — kasus vs hujan per bulan, Indonesia |
| 5 | `h05-musiman-tha.png` | Combination chart — kasus vs hujan per bulan, Thailand |
| 6 | `h06-heatmap-jeda.png` | Heat map — korelasi prediktor × jeda |
| 6 | `h06-scatter-suhu.png` | Scatterplot — suhu jeda 2 vs kasus |
| 7 | `h07-fase-enso.png` | Bar chart — rerata kasus per fase ENSO (jeda 4) |
| 7 | `h07-anomali.png` | Heat map — korelasi setelah musim dibuang |
| 8 | `h08-kalender-idn.png` | Heat map — share kasus per bulan per provinsi, IDN |
| 8 | `h08-kalender-tha.png` | Heat map — share kasus per bulan per provinsi, THA |
| 9 | `h09-insidens.png` | Bar horizontal — insidens per 100k, 2018–2020 |
| 9 | `h09-wash.png` | Bar chart — akses air perpipaan ASEAN |
| 9 | `h09-banjir.png` | Bar chart — penduduk di zona banjir 1:100 tahun |
| 10 | `h10-kalender-prioritas.png` | Heat map — kalender risiko 6 provinsi prioritas |
| 10 | `h10-deret-alarm.png` | Time series — kasus vs ambang P75 |
| 11 | `h11-deret-aturan.png` | Time series — kapan aturan D menyala, 2010–2024 |
| 11 | `h11-aturan.png` | Bar chart — presisi vs frekuensi alarm, 4 aturan |
| 12 | `h12-luar-sampel.png` | Bar chart — latih vs uji buta, IDN & THA |
| 12 | `h12-tolok-ukur.png` | Table widget — pembanding EWS terpublikasi |
| 13 | `h13-dampak.png` | Bar bertingkat — biaya rawat inap yang dihindari |
| 13 | `h13-tenggang.png` | Table — tenggang waktu tiap episode El Niño |
| 14 | `h14-kekeringan.png` | Scatterplot — kekeringan × akses air (hasil nol) |

Total **23 grafik**. Delapan dataset pertama di `NASKAH-STORYBOARD.md` sudah cukup
untuk seluruh daftar ini.

## Konsistensi warna

Pakai palet yang sama dengan dek supaya grafik SAC menyatu dengan tata letaknya:

| Peran | Hex |
|---|---|
| Kasus / kondisi normal | `#2A78D6` |
| Alarm / El Niño | `#E8833A` |
| Puncak / wabah | `#C53232` |
| Konteks, garis ambang | `#8A8F98` |
