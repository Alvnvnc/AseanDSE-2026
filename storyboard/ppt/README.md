# storyboard/ppt — dek PowerPoint dari storyboard LaTeX

Kanvas dek LaTeX (960×540 bp) sama persis dengan kanvas PowerPoint 16:9
(13,333×7,5 inci), jadi berkas ini adalah port 1:1: koordinat, palet, teks, dan
23 grafik SAC dari `../gambar-siap/` dipakai apa adanya. 17 slide = 15 halaman
isi + 2 halaman referensi, sama seperti `../storyboard.pdf`. Catatan pembicara
sudah tertanam di tiap slide.

## Membangun

```bash
node bangun-ppt.js ../INDONESIA_SWALLOWGANK.pptx
```

Kebutuhan: Node.js (paket `pptxgenjs` sudah di `node_modules/`) dan Python
dengan Pillow (untuk `ukur.py`; skrip mencari `../../.venv/bin/python` lalu
`python3`).

Ekspor PDF (opsi kedua format yang diterima panitia):

```bash
soffice --headless --convert-to pdf INDONESIA_SWALLOWGANK.pptx
```

## Isi

| Berkas | Fungsi |
|---|---|
| `bangun-ppt.js` | generator utama; teks & geometri ditulis di sini |
| `ukur.py` | pengukur lebar teks (PIL + Liberation Sans, metrik = Arial) |
| `node_modules/` | `pptxgenjs` (tidak dilacak git) |

## Catatan desain

- Font: **Arial** (metrik paling dekat dengan TeX Gyre Heros/Helvetica yang
  dipakai storyboard; aman di semua mesin juri/Office).
- Bullet daftar digambar manual (kotak biru kecil) karena bullet bawaan
  pptxgenjs tidak andal untuk paragraf multi-gaya dan warnanya tidak bisa diatur.
- Lebar slot grafik dihitung dari `../gambar-siap/rasio.tex` — sumber yang sama
  dengan `\sacslot` di LaTeX, jadi bila grafik SAC diekspor ulang, jalankan
  `../bangun.sh` dulu lalu bangun ulang PPT.
- QA: render ulang ke PDF, potong jadi JPG (`pdftoppm -jpeg -r 120`), lalu
  bandingkan per halaman dengan `../storyboard.pdf`.
