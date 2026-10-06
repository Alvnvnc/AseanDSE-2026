# Jalur Gamma — ekspor AI yang disunting lokal

Dek versi desain modern dibuat lewat **API Gamma** (public-api.gamma.app), lalu
disunting di sini agar sesuai storyboard dan aturan panitia.

| Berkas | Isi |
|---|---|
| `masukan.txt` | 17 kartu teks (pemisah `---`) + URL publik grafik SAC, dikirim sebagai `inputText` |
| `ekspor-mentah.pptx` | Unduhan mentah dari Gamma (tema *Consultant*, `textMode: preserve`, `imageOptions.source: noImages`) |
| `sunting-gamma.py` | Skrip suntingan lokal → menulis `../../INDONESIA_SWALLOWGANK-gamma.pptx` |

## Parameter generate yang dipakai

```json
{
  "textMode": "preserve",
  "cardSplit": "inputTextBreaks",
  "format": "presentation",
  "themeId": "consultant",
  "exportAs": "pptx",
  "imageOptions": { "source": "noImages" },
  "cardOptions": { "dimensions": "16x9" }
}
```

Grafik SAC disisipkan sebagai URL mentah (bukan markdown) ke
`raw.githubusercontent.com/.../storyboard/gambar-siap/*.png`; Gamma mengambil
dan me-host ulang gambar itu saat generate.

## Yang disunting `sunting-gamma.py`

1. **Slide 2** — kartu stat disusun ulang (1.26M & 9.6M di atas; Vietnam 368k,
   Filipina 220k, **Thailand 159k** di baris kedua — ekspor Gamma menghilangkan
   Thailand) dan grafik kanan diperbesar.
2. **Tipografi** — apostrof `’` dan kutip ganda `“ ”` di semua slide.
3. **Catatan pembicara** — disalin dari dek native
   (`INDONESIA_SWALLOWGANK-latex.pptx`) ke notesSlide (Gamma hanya menulis
   nomor halaman di notes-nya).
4. **Nomor halaman** kanan bawah: 2–15, lalu R1/R2 — agar rujukan
   “answered p. 7/12/14” di dek mudah dilacak.
5. **Sampul gelap** — tema *Consultant* aslinya putih polos; sampul diubah ke
   navy `#0E2340` + teks putih + chip SDG merah/biru/oranye, mengikuti
   identitas storyboard.

Skrip juga menulis `catatan.json` (17 × daftar baris catatan) yang dipakai
`buat-aman.js`.

## Versi "aman impor" (`buat-aman.js`)

Canva, Google Slides, WPS, dan PowerPoint lama sering membuang font ter-embed
dan elemen SVG saat mengimpor, sehingga dek tampak lebih kosong daripada
aslinya. Versi aman mengganti tiap slide dengan satu gambar penuh hasil render
PDF, jadi tampil identik di aplikasi mana pun (catatan pembicara tetap ikut):

```bash
pdftoppm -jpeg -r 200 -jpegopt quality=90 \
  ../../INDONESIA_SWALLOWGANK-gamma.pdf /tmp/opencode/aman/s
node buat-aman.js /tmp/opencode/aman
# -> ../../INDONESIA_SWALLOWGANK-gamma-aman.pptx
```

Menjalankan ulang suntingan: `python3 sunting-gamma.py` (murni XML, tanpa
dependensi Python tambahan).
