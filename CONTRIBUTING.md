# Standar kerja repo AseanDSE-2026

## Format pesan commit

Mengikuti [Conventional Commits](https://www.conventionalcommits.org), dengan deskripsi
berbahasa Indonesia:

```
<tipe>(<cakupan>): <deskripsi singkat, imperatif, huruf kecil, tanpa titik>

<badan: KENAPA perubahan ini, bukan APA — boleh kosong untuk perubahan sepele>

<catatan kaki: Refs #12, BREAKING CHANGE: ...>
```

### Tipe

| Tipe | Dipakai untuk |
|---|---|
| `data` | paket data berubah: `data/siap-sac/`, skrip unduh/siapkan |
| `analisis` | notebook, temuan, angka hasil analisis |
| `docs` | naskah storyboard, README, catatan |
| `feat` | skrip atau kemampuan baru (mis. ekspor xlsx) |
| `fix` | perbaikan kekeliruan angka, bug skrip |
| `chore` | konfigurasi, perkakas, pembersihan |

### Cakupan yang dipakai

`siap-sac`, `notebook`, `storyboard`, `ekspor`, `bps`, `repo`

### Aturan

- Deskripsi maksimal 72 karakter, kalimat perintah ("tambah", bukan "menambahkan"/"ditambahkan").
- Satu commit = satu perubahan yang bisa dijelaskan dalam satu kalimat.
- **Kalau sebuah commit mengubah angka yang dikutip storyboard, sebutkan angka lama → baru
  di badan pesan.** Ini yang membuat riwayat bisa diaudit saat penjurian.
- Jangan commit `.env`, isi `.venv/`, atau data mentah (lihat `.gitignore`).

### Contoh

```
analisis(notebook): koreksi jendela panel Vietnam jadi <=2022

Total 2023-24 sebelumnya ikut menghitung Vietnam yang datanya berhenti 2022,
sehingga tahun rekor salah tampil. Rekor dalam data: 2023 (1,29 jt) -> 2019 (1,26 jt).
```

```
docs(storyboard): ganti judul jadi "Four Months' Notice"
```

## Template commit

Template pesan sudah terpasang di repo ini:

```bash
git config commit.template .gitmessage
```

`git commit` tanpa `-m` akan membuka template beserta daftar tipe.

## Sebelum push

1. `git status` — pastikan tidak ada `.env`, `.venv/`, atau berkas > 50 MB.
2. Kalau `data/siap-sac/` berubah, jalankan ulang ekspor Excel-nya:
   `.venv/bin/python analisis/ekspor_xlsx.py`
3. Angka di `NASKAH-STORYBOARD.md` hanya boleh berubah lewat notebook — jangan disunting manual.
