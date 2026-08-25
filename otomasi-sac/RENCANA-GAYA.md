# Penyempurnaan gaya — status

Diperbarui 25 Agustus 2026. Semua butir selesai — tidak ada lagi yang
perlu disunting tangan di SAC.

| # | Butir | Status |
|---|---|---|
| 1 | Widget Table untuk `h12-tolok-ukur` & `h13-tenggang` | **selesai** |
| 2 | Rentang sumbu X `h06-scatter-suhu` | **selesai** — lewat API, `vizDefinition.axisRange` |
| 3 | `h13-dampak` bar bertingkat | **selesai** |
| 4 | Palet warna dek | **selesai**, termasuk sorotan per anggota (`story.data.colorSync`) |
| 5 | Tata letak `h03-alur` | **selesai** |
| 6 | Ukuran titik pencar (`h06`, `h14`) | **selesai** — `properties.general.pointScale` |

---

## 1. Widget Table — selesai

`tabel.py` membangun widget `sap.fpa.ui.story.entity.table.TableWidget` dari satu
tabel template (`templat-tabel.json` + `templat-tabel-entity.json`, diambil sekali
lewat UI). Polanya sama dengan grafik: ganti id cube, susun ulang `ffQuery`.

Bedanya dengan grafik: **kueri tabel tersimpan di entity**, bukan di widget —
di `data.content.segments[1].dataRegion.ffQuery`, dan berupa **string JSON**.

Dua hal yang perlu diperhatikan saat menambah tabel baru:

* **Tabel melebar mengikuti lebar halaman.** Slot tabel di dek berorientasi
  potret (270x348 bp), jadi halaman tabel sengaja dibuat sempit (820x1000) dan
  hasil tangkapannya dipangkas (`-trim`). Tanpa itu tabelnya jadi pita tipis
  yang tak terbaca.
* **Label panjang memaksa kolom melebar.** Karena itu ada dataset ringkas
  `EWS benchmark TABLE` dan `El Nino lead time TABLE` (dibuat oleh
  `ekspor-csv/perbaikan.py`) dengan teks yang dipendekkan — isinya sama.

Sisa yang belum rapi: kolom `alarm` dan `cases_cross` tetap dibaca SAC sebagai
tanggal, jadi tampil "Dec 1, 2009 (2009)" alih-alih "Dec '09". Isinya benar,
hanya lebih boros tempat.

Mau kembali ke bentuk bar? Ganti satu baris di `resep.py`:
`tipe="tabel"` -> `tipe="barcolumn"` (dan isi kembali `feeds`).

## 2. Rentang sumbu X `h06-scatter-suhu` — selesai

Suhu berkisar 24-27 C tetapi SAC menskalakan sumbu nilai sedemikian rupa sampai
selalu menyertakan nol, jadi titik-titiknya menggumpal di tepi kanan.

Kuncinya **`vizDefinition.axisRange`** — sejajar dengan `properties`, bukan di
dalamnya:

    "axisRange": [
      {"feed": "valueAxis",  "min": 24, "max": 27,     "dynamicAxisEnabled": false},
      {"feed": "valueAxis2", "min": 0,  "max": "auto", "dynamicAxisEnabled": false}
    ]

Dipakai lewat `rentang_sumbu={"valueAxis": (24, 27), "valueAxis2": (0, "auto")}`
di `resep.py`; `generator.buat_widget` yang menuliskannya (sekalian
`properties.axisSync = false`, seperti yang ditulis SAC sendiri).

Yang **tidak** berhasil sebelum ini: `vizDefinition.properties.valueAxis.*`,
`plotArea.primaryScale` (properti CVOM — diabaikan renderer SAC),
`axisTick.startOnTick`/`endOnTick`, `minPadding`/`maxPadding`, bendera
`isAutoLimiterOn` dan `shouldScaleChart`. Panel Builder maupun Styling juga
tidak memuat min/maks sama sekali.

Cara menemukannya, kalau perlu diulang untuk properti lain:

1. Cari nama fiturnya di berkas pesan i18n:
   `jelajah/cari-bundel.py "EDIT_AXIS:" 1400 2`. Dari situ ketahuan SAC
   menyebutnya **Edit Axis** dengan label *Minimum/Maximum Value*.
2. Buka fiturnya lewat UI: pilih grafik -> **⋮** -> **More Options** ->
   **Edit Axis** -> isi -> **Apply**.
3. `jelajah/dump-story.py sebelum.json`, Ctrl+S, `dump-story.py sesudah.json`,
   lalu bandingkan per-entity (id yang sama dibandingkan isinya).

Catatan: menyimpan lewat UI membawa efek samping — kanvas halaman diubah
mengikuti lebar jendela (1400 -> 1812) dan subjudul kosong diisi teks
"Subtitle". Keduanya hilang begitu `bangun-story.py` dijalankan lagi.

## 3. `h13-dampak` bar bertingkat — selesai

Tipe diubah ke `stackedbar`. Yang lebih penting: **datanya diperbaiki**.
Menumpuk "hospitalisation low" dan "hospitalisation high" berarti menjumlahkan
dua perkiraan yang saling menggantikan — hasilnya angka yang tidak berarti.

Dataset `Monetary impact STACK` memecahnya jadi dasar + selisih:

    hospitalisation low   = batas bawah
    extra up to high      = batas atas - batas bawah

sehingga tinggi total batang = batas atas (3.680 / 7.370 / 11.050 ribu US$).

## 4. Palet warna dek — sebagian

**Selesai:** `palet.py` menimpa palet yang sedang ditunjuk
`namedColorStates.defaultPalettes`, jadi seluruh grafik ikut sekaligus:

* seri: `#2A78D6` biru, `#E8833A` oranye, `#C53232` merah, `#8A8F98` abu;
* gradasi heat map: putih hangat -> merah dek.

Catatan penting: pada palet gradasi, kunci **`"0"` memetakan nilai TERTINGGI**
dan `"100"` nilai terendah — terbalik dari dugaan. Merah karena itu ditaruh di
`"0"`.

**Sorotan per anggota — selesai.** Disimpan di **tingkat story**, bukan di
widget: `story.data.colorSync`, berkunci ganda (dataset, lalu dataset+dimensi):

    colorSync['[{"datasetId":"<ds>"}]']
             ['[{"datasetId":"<ds>"},{"dimensionId":"country"}]'] = {
        "colors": [...12 warna palet...],
        "explicitColorAssignments":       {"Indonesia": "#e8833a"},
        "explicitColorSwatchAssignments": {"Indonesia": ""},
        "id": "<id standardPalette>",
        "mappingPaletteId": "sapColorfulPalette",
        "preferredMappingPaletteId": "sapColorfulPalette"}

Karena kuncinya dataset+dimensi, satu penetapan berlaku untuk **semua** grafik
yang memakai keduanya — itulah kenapa SAC menyebutnya *colour sync*. Ditulis
oleh `sorot.py`, diminta lewat kunci `sorot=` di `resep.py`.

Dua syarat yang perlu diingat:

* **Dimensinya harus ada di feed `color`.** Kalau cuma di `categoryAxis`,
  penetapannya diabaikan. Karena itu `h02-per-negara` dan `h07-fase-enso`
  sekarang menaruh dimensinya di dua feed sekaligus.
* SAC menolak kalau grafiknya punya lebih dari satu measure, atau lebih dari
  satu dimensi di feed Colour (pesan `ASSIGNED_COLORS_DISABLED`).

Ikutannya: menaruh dimensi di feed `color` memunculkan legenda yang isinya
persis sama dengan label sumbu kategori. Untuk mematikannya perlu **dua**
bendera — `legendGroup.visible = false` **dan** `legendGroup.responsive = false`.
Dengan `responsive` masih `true`, SAC mengatur legendanya sendiri dan menimpa
`visible` (`resep.TANPA_LEGENDA`).

Yang dipakai sekarang:

| Grafik | Dimensi | Warna |
|---|---|---|
| `h02-per-negara` | `country` | Indonesia oranye, sembilan negara lain biru dek |
| `h07-fase-enso` | `enso_phase_lag4` | biru tua -> biru muda -> abu -> oranye -> merah |
| `h06-scatter-suhu` | `enso_phase_lag4` | sama, jadi bahasa warna ENSO konsisten di dua halaman |

Cara menemukannya (sama seperti butir 2): `cari-bundel.py "Assign Colou?r"`
menemukan kunci pesan `ASSIGN_COLOR`; menelusuri pemakaiannya di bundel
menunjukkan itu item pada *token actions menu*, yaitu menu **•••** pada chip
dimensi. Jalurnya: chip dimensi di bagian **Colour** -> **•••** ->
**Colour Sync** -> **Assign Colours...**

Yang tidak dikejar: menyorot aturan D di `h11-aturan`. Di grafik itu `rule` ada
di sumbu kategori sementara feed `color` dipakai `metric` (precision vs
coverage) — dan itu memang pembagian warna yang benar untuk grafiknya. Menukar
keduanya hanya demi sorotan akan merusak bacaannya; aturan D sudah ditonjolkan
lewat teks halaman.

## 6. Ukuran titik pencar — selesai

Gambar SAC 2816 px dikecilkan ke slot dek yang lebarnya sekitar 460 px, jadi
titik pencar bawaan tinggal sekitar satu piksel — pada `h14-kekeringan` (7 titik)
praktis tak terlihat, pada `h06-scatter-suhu` polanya sulit dibaca.

Kuncinya `properties.general.pointScale`, dengan sarang ganda:

    {"general": {"pointScale": {"pointScale": 3}}}      # 300%

`plotArea.markerSize` (properti CVOM) diabaikan. Di UI: panel **Styling** ->
**Data Points** -> **Data Marker Size**. Dipakai lewat `PENANDA(skala)` di
`resep.py`: `h06` 2.0x, `h14` 3.0x.

Sekalian di `h14`: sumbu X dipatok `(0, 105)` — akses air ledeng maksimum 100%,
sedangkan sumbu otomatis SAC melebar sampai 120 dan menyisakan seperlima lebar
kosong di kanan.

## 5. Tata letak `h03-alur` — selesai

Halaman lama di `swalloy-story` punya dua masalah:

* isinya satu baris tipis (rasio 9:1) sementara slot dek 2,41:1, jadi gambarnya
  mengecil dan menyisakan ruang kosong;
* "panah"-nya sebenarnya pictogram `<line>` yang menggambar garis pada y=30,
  padahal widget-nya hanya 16 px tinggi — garisnya tergunting dan tak terlihat
  sama sekali di dek.

`alur.py` membangun ulang halaman itu: kotak proporsional berwarna palet dek,
panah SVG sendiri (garis + kepala panah, ber-`viewBox` sehingga ikut ukuran
widget), teks 30 px, dan kotak pembatas yang rasionya persis 2,41 (ruang putih
ditambahkan seimbang oleh `tangkap.py` lewat kunci `rasio`).
