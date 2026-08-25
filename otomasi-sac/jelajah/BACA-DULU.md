# Skrip penjelajahan

Berkas di sini dipakai untuk **membongkar cara kerja SAP Analytics Cloud** —
memetakan endpoint REST-nya, menemukan bentuk payload simpan, mencari nama tipe
grafik, dan menguji satu per satu konfigurasi feed sampai grafiknya render.

Semuanya sudah selesai tugasnya; hasilnya terangkum di `../README.md` dan
terpakai di pipeline (`bangun-story.py`, `tangkap.py`). Disimpan kalau-kalau SAC
berubah dan perlu dibongkar ulang.

| Berkas | Gunanya waktu itu |
|---|---|
| `rekon-*.py` | Memetakan endpoint, frame, bundel JS, dan daftar dataset |
| `rekam-save*.py` | Merekam payload `updateContent` asli saat tombol Save ditekan |
| `rekam-ina.py` | Membaca pesan galat query InA saat grafik gagal render |
| `uji-*.py` | Uji tulis & uji generator di story salinan |
| `impor-langkah*.py`, `impor-dataset.py` | Menelusuri alur impor CSV di UI |
| `coba-pageid.py`, `cek-*.py`, `buka.py` | Uji navigasi halaman dan tab story |
| `hook.js` | Penyadap `fetch`/XHR yang disuntikkan ke halaman |
| `pandu.py` | **Masih dipakai.** Pandu UI langkah demi langkah — Edge tetap hidup antar pemanggilan, jadi tiap perintah bekerja pada halaman yang sama |
| `cari-bundel.py` | **Masih dipakai.** Cari pola teks di seluruh bundel JS yang dimuat halaman — cara tercepat menemukan nama fitur/properti SAC |
| `dump-story.py` | **Masih dipakai.** Simpan JSON story apa adanya, untuk dibandingkan sebelum/sesudah suntingan UI |
| `uji-skala.py` | Sisipkan properti percobaan ke `vizDefinition` satu halaman lalu simpan |

## Cara membongkar properti yang belum diketahui

Tiga langkah ini yang akhirnya menemukan `vizDefinition.axisRange`:

1. `cari-bundel.py "EDIT_AXIS:" 1400 2` — berkas pesan i18n memuat nama fitur
   dan label dialognya, jadi ketahuan menu mana yang dicari.
2. `pandu.py` untuk membuka menunya dan mengisi dialognya.
3. `dump-story.py sebelum.json` -> Ctrl+S -> `dump-story.py sesudah.json`, lalu
   bandingkan **per entity berdasarkan id** (jumlah entity bisa berubah sendiri:
   SAC membuang entity yatim saat menyimpan).
