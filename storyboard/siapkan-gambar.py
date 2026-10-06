#!/usr/bin/env python3
r"""
Siapkan ekspor SAC untuk dek: buang judul bawaan, chrome widget, sisa tooltip,
lalu rapatkan margin putih.

SAC mengekspor tiap widget dengan judulnya sendiri di baris atas. Judul itu
sudah ditulis ulang oleh \sacslot di LaTeX dengan ukuran yang terbaca, jadi
versi bawaannya cuma menggandakan teks dan memakan tinggi gambar. Skrip ini
memotongnya, lalu memangkas margin putih supaya bidang plot mengisi slot.

  gambar-sac/*.png  ->  gambar-siap/*.png
r"""
import os
import numpy as np
from PIL import Image

SUMBER = "gambar-sac"
TUJUAN = "gambar-siap"
RASIO = "gambar-siap/rasio.tex"

# Baris yang dipotong dari atas, per berkas. Default 100 menghapus garis tipis
# di baris 6-7 dan pita judul di baris 47-73 pada semua ekspor persegi.
POTONG_ATAS = {
    "h03-alur": 0,              # diagram bentuk, tidak berjudul
    "h08-kalender-tha": 194,    # tooltip nyangkut; sisa bingkainya habis di baris 193
    "h12-tolok-ukur": 175,      # judul + baris chrome widget SAC
    "h13-tenggang": 175,        # sama
}
DEFAULT_ATAS = 100

BATAS_PUTIH = 247   # di atas ini dianggap latar
PADDING = 8         # sisa napas di tepi, dalam piksel sumber

# Peta panas memakai skala merah-putih saja, jadi piksel biru di dalamnya pasti
# sisa keadaan hover SAC (label bulan tersorot, garis seleksi sel) dan bukan
# data. Untuk berkas ini saja, biru itu ditimpa warna tetangga terdekat.
TANPA_BIRU_SAH = {
    "h06-heatmap-jeda",
    "h07-anomali",
    "h08-kalender-idn",
    "h08-kalender-tha",
    "h10-kalender-prioritas",
}


LABEL_GELAP = (74, 74, 74)   # abu label sumbu bawaan SAC


def hapus_sorotan(im):
    """Bersihkan keadaan hover SAC dari peta panas.

    Dua jenis sisa, dan keduanya harus ditangani berbeda:
      - teks label sumbu yang tersorot biru (mis. bulan "Jan") duduk di margin
        putih; itu data yang sah, jadi cuma diwarnai ulang jadi abu label;
      - garis seleksi sel duduk di atas bidang plot yang berwarna; itu chrome,
        jadi ditimpa piksel non-biru terdekat pada baris yang sama.
    Pembedanya: apakah lingkungan mendatar piksel itu putih atau tidak.
    """
    a = np.asarray(im).astype(np.int16)
    biru = (a[:, :, 2] - a[:, :, 0] > 30) & (a[:, :, 2] > 110)
    if not biru.any():
        return im

    abu = np.asarray(im.convert("L")).astype(np.int16)
    keluar = a.copy()
    lebar = a.shape[1]
    JENDELA = 45

    for y in np.flatnonzero(biru.any(axis=1)):
        baris = biru[y]
        bersih = np.flatnonzero(~baris)
        if not len(bersih):
            continue
        for x in np.flatnonzero(baris):
            kiri, kanan = max(0, x - JENDELA), min(lebar, x + JENDELA)
            tetangga = abu[y, kiri:kanan][~baris[kiri:kanan]]
            latar_putih = len(tetangga) and (tetangga > 245).mean() > 0.7
            if latar_putih:
                keluar[y, x] = LABEL_GELAP
            else:
                keluar[y, x] = a[y, bersih[np.abs(bersih - x).argmin()]]
    return Image.fromarray(keluar.astype(np.uint8))


def pangkas(path_masuk, path_keluar):
    im = Image.open(path_masuk).convert("RGB")
    nama = os.path.splitext(os.path.basename(path_masuk))[0]

    atas = POTONG_ATAS.get(nama, DEFAULT_ATAS)
    if atas:
        im = im.crop((0, atas, im.width, im.height))

    if nama in TANPA_BIRU_SAH:
        im = hapus_sorotan(im)

    a = np.asarray(im.convert("L"))
    tinta = a < BATAS_PUTIH
    baris = np.flatnonzero(tinta.any(axis=1))
    kolom = np.flatnonzero(tinta.any(axis=0))
    if not len(baris) or not len(kolom):
        im.save(path_keluar)
        return im.size, im.size

    y0 = max(0, baris[0] - PADDING)
    y1 = min(a.shape[0], baris[-1] + 1 + PADDING)
    x0 = max(0, kolom[0] - PADDING)
    x1 = min(a.shape[1], kolom[-1] + 1 + PADDING)

    hasil = im.crop((x0, y0, x1, y1))
    hasil.save(path_keluar, optimize=True)
    return Image.open(path_masuk).size, hasil.size


def main():
    os.makedirs(TUJUAN, exist_ok=True)
    rasio_tex = [
        "% Dibuat otomatis oleh siapkan-gambar.py -- jangan disunting tangan.",
        "% Rasio lebar/tinggi tiap gambar yang sudah dipangkas, supaya \\sacslot",
        "% bisa menghitung lebar kotak dari tingginya dan menggambar bingkai",
        "% kartu yang persis sebesar gambarnya.",
    ]
    for berkas in sorted(os.listdir(SUMBER)):
        if not berkas.endswith(".png"):
            continue
        nama = os.path.splitext(berkas)[0]
        lama, baru = pangkas(os.path.join(SUMBER, berkas),
                             os.path.join(TUJUAN, berkas))
        rasio = baru[0] / baru[1]
        rasio_tex.append(
            f"\\expandafter\\def\\csname rasio@{nama}\\endcsname{{{rasio:.4f}}}")
        print(f"{berkas:30s} {lama[0]}x{lama[1]} -> {baru[0]}x{baru[1]}"
              f"  (w/h {rasio:.2f})")
    with open(RASIO, "w") as f:
        f.write("\n".join(rasio_tex) + "\n")
    print(f"\n-> {RASIO} ({len(rasio_tex) - 4} rasio)")


if __name__ == "__main__":
    main()
