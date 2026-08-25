# Otomasi SAP Analytics Cloud

Membangun grafik SAC lewat **REST internal SAC**, bukan lewat klik satu per satu.
Satu grafik yang sudah ada dipakai sebagai *template*, lalu diperbanyak dengan
dataset / tipe / measure / dimensi / filter yang berbeda.

Semua grafik tetap **dihasilkan dan dirender oleh SAP Analytics Cloud** — yang
diotomasi hanya cara merakit definisinya.

## Cara pakai

```sh
# 1. jalankan Edge kedua yang bisa dikendalikan (profil terpisah, sesi login ikut)
LOG=/tmp/edge-sac.log otomasi-sac/edge-mulai.sh          # --reset untuk profil bersih

# 2. petakan dataset di tenant (id cube + dimensi + measure)
.venv/bin/python otomasi-sac/petakan-dataset.py otomasi-sac/dataset-sac.json

# 3. bangun story berisi satu grafik per halaman
.venv/bin/python otomasi-sac/bangun-story.py

# 4. tangkap tiap grafik jadi PNG ke storyboard/gambar-sac/
.venv/bin/python otomasi-sac/tangkap.py                  # atau sebut nama berkasnya
```

Impor CSV baru (kalau tipe kolomnya perlu dibetulkan):

```sh
python3 ekspor-csv/perbaikan.py                      # tulis CSV yang sudah dibetulkan
.venv/bin/python otomasi-sac/impor-semua.py          # impor semuanya ke SAC
```

Kalau sesi login kedaluwarsa: buka jendela Edge otomasi itu, login sekali, selesai.

## Kenapa perlu CSV perbaikan

SAC menentukan sendiri kolom mana yang jadi **dimensi** dan mana yang jadi
**measure** saat impor, dan tidak selalu sesuai kebutuhan grafik:

- kolom angka yang perlu jadi sumbu (mis. `lag`) diperlakukan sebagai measure
  -> ditambah kolom teks pendamping (`lag_label` = `L00`..`L12`);
- beberapa kolom persen justru jadi dimensi -> nama dirapikan tanpa `%`;
- kolom teks berformat (`US$1.47M`, `44%`, `50-100%`) tidak bisa jadi measure
  -> dipecah jadi kolom angka murni.

Dataset hasil impor ulang diberi akhiran ` FIX` supaya yang lama tetap utuh.

## Berkas

| Berkas | Isi |
|---|---|
| `edge-mulai.sh` | Menjalankan Edge kedua dengan port debug CDP 9222 |
| `sac.py` | Sambungan ke Edge + konstanta tenant/story |
| `api.py` | Pemanggil REST internal SAC (pakai cookie + `FPA_CSRF_TOKEN` halaman) |
| `sac_story.py` | Baca/tulis isi story (`getContent` / `updateContent`) |
| `generator.py` | Merakit widget grafik dari template + resep |
| `resep.py` | **23 resep grafik**, terjemahan dari `storyboard/storyboard.tex` |
| `bangun-story.py` | Membuat story `swalloy-grafik`, satu grafik per halaman |
| `tangkap.py` | Menangkap tiap grafik jadi PNG (skala 2x) |
| `petakan-dataset.py` | Mendaftar semua DATASET: id cube, dimensi, measure |
| `impor-semua.py` | Impor CSV jadi DATASET baru lewat UI (untuk `ekspor-csv/perbaikan/`) |
| `periksa-gambar.py` | Uji mutu PNG: ukuran, berat, dan deteksi gambar kosong |
| `daftar-isi.py` | Daftar seluruh isi folder SAC (story, dataset, cube) |
| `lihat-halaman.py` | Buka satu halaman story dan tangkap layarnya |
| `RENCANA-GAYA.md` | Status penyempurnaan gaya — 6 butir, semuanya selesai lewat API |
| `alur.py` | Membangun halaman diagram alur h03 (Shapes + Text) |
| `tabel.py` | Membangun widget Table dari template |
| `sorot.py` | Sorotan warna per anggota dimensi (`story.data.colorSync`) |
| `palet.py` | Menerapkan palet warna dek ke seluruh grafik |
| `jelajah/` | Skrip pembongkaran SAC — sudah selesai tugasnya, lihat `jelajah/BACA-DULU.md` |
| `dataset-sac.json` | Hasil pemetaan dataset (dipakai `bangun-story.py`) |
| `halaman.json` | Peta `berkas -> pageId/widgetId` hasil pembangunan |
| `templat-widget.json` | Widget grafik contoh yang jadi template |
| `story-asli.json` | Cadangan isi `swalloy-story` sebelum apa pun disentuh |

## Yang dipelajari dari REST SAC

Endpoint: `POST /sap/fpa/services/rest/epm/contentlib?tenant=O`
dengan header `x-csrf-token: window.FPA_CSRF_TOKEN`.

| Aksi | Guna |
|---|---|
| `getContent` | Baca story. Isi sebenarnya ada di `cdata.content` (string JSON) |
| `updateContent` | Simpan story. **`cdata` = objek `entities` itu sendiri**, bukan pembungkusnya |
| `copyResource` | Menyalin story/dataset |
| `startEdit` / `stopEdit` | Kunci edit |
| `getRepoView` | Daftar isi folder (story, dataset, cube) |

`updateOpt.localVer` harus **`metadata.version`** dari `getContent` — bukan
`updateCounter`. Kalau salah, jawabannya `INCONSISTENT_VERSION`.

## Jebakan yang sudah dilewati

1. **String entity-id itu identitas tekstual.** `json.dumps` Python menyisipkan
   spasi (`{"datasetId": "x"}`), SAC menulis tanpa spasi (`{"datasetId":"x"}`).
   Kalau tidak sama persis, grafik gagal dengan *"invalid entity in the data feed"*.
   Semua id dibuat lewat `generator.jdump`.
2. **Halaman baru harus didaftarkan** di entity `:application`
   (`appPages` + `app.names`). Tanpa itu halaman tersimpan di JSON tapi tidak
   muncul di tab bar SAC.
3. **`initialUQMExternalState.usedDimensions` / `usedMeasures` wajib konsisten**
   dengan `bindings`. Sisa referensi dimensi lama membuat grafik ditolak.
4. **Sumbu `Free` harus tetap memuat `CustomDimension2` dan `Version`.**
5. **Filter multi-nilai**: satu `FilterOperation` per nilai. Kalau semua nilai
   ditumpuk dalam satu operasi, SAC hanya memakai nilai pertama.
6. **Nama tipe grafik** bukan tebakan bebas — hanya 23 id terdaftar di renderer:
   `line, barcolumn, stackedbar, heatmap, scatterplot, bubble, clusterbubble,`
   `combstackedbcl, area, nonstackedarea, pie, waterfall, marimekko, treemap,`
   `icicle, boxplot, bullet, metric, timeseries, radar, histogram, funnel, gauge`.
   Tidak ada `bar` maupun `column` — keduanya `barcolumn`.
   Memakai id yang tidak terdaftar membuat seluruh halaman gagal render
   (*"e is not a constructor"*).
7. **Judul kustom** perlu `headerProperties.hasUserModifiedTitle = true`.
8. **SAC menyimpan cache lokal**; sesudah menulis lewat API, muat ulang halaman
   dengan cache dibuang kalau perubahan belum kelihatan.
9. Halaman tertentu dibuka langsung lewat
   `#/story2&/s2/<storyId>/?pageId=<pageId>&mode=view`.
10. **Scatterplot tidak memakai `categoryAxis`.** Dimensinya harus lewat feed
    `color`; kalau ditaruh di `categoryAxis`, sumbunya tergambar tapi tanpa
    satu titik pun. `valueAxis` = sumbu X, `valueAxis2` = sumbu Y.
11. **Grafik kombinasi** (`combstackedbcl`) hanya menggambar garis kalau
    measure-nya juga terdaftar di `initialUQMExternalState.usedSecondaryMeasures`.
12. **Bubble** butuh measure ketiga; feed `size` saja belum cukup.
13. **Klik UI5 harus pakai mouse sungguhan.** `element.click()` dari JavaScript
    sering diabaikan; cari kotaknya lewat JS lalu `page.mouse.click(x, y)`.
14. Layar buat dataset bisa dibuka langsung:
    `#/dataset&/ds/?mode=create&defaultLocation=PRIVATE_<USER>`.
15. **`page.screenshot()` Playwright mengabaikan `deviceScaleFactor` CDP.** Untuk
    PNG beresolusi tinggi, pakai `Page.captureScreenshot` dengan `clip.scale`.
16. **SAC hanya menggambar bagian halaman yang terlihat.** Kalau kanvas lebih
    tinggi dari viewport, separuh grafik keluar kosong dan label sumbunya hilang.
    `tangkap.py` menyetel viewport mengikuti ukuran tiap halaman sebelum memuat.
17. **Rasio halaman mengikuti slot dek** (`\sacslot` di `storyboard.tex`), dibatasi
    1.0–3.0. Tanpa ini grafik 16:9 masuk ke slot potret dan menyisakan ruang
    kosong besar.
18. **Granularitas titik scatter = anggota feed non-`categoryAxis`.** Untuk satu
    titik per bulan yang diwarnai fase ENSO: `color` = fase, `shape` = periode.
19. **Rentang sumbu nilai ada di `vizDefinition.axisRange`**, bukan di
    `vizDefinition.properties` — dan tidak dipengaruhi `isAutoLimiterOn`,
    `shouldScaleChart`, maupun `plotArea.primaryScale` (properti CVOM itu
    diabaikan). Bentuknya satu entri per feed:

        "axisRange": [
          {"feed": "valueAxis",  "min": 24, "max": 27,     "dynamicAxisEnabled": false},
          {"feed": "valueAxis2", "min": 0,  "max": "auto", "dynamicAxisEnabled": false}
        ]

    `"auto"` berarti biarkan SAC yang menentukan. SAC juga menulis
    `properties.axisSync = false` bersamaan. Di UI namanya **Edit Axis**
    (widget ⋮ -> More Options -> Edit Axis). Dipakai lewat `rentang_sumbu=`
    di resep; tanpa itu sumbu nilai selalu menyertakan nol, sehingga pencar
    suhu 24-27 C menggumpal di tepi.
20. **Palet warna** diambil dari palet yang ditunjuk
    `story.data.namedColorStates.defaultPalettes`; menimpa isinya mengubah semua
    grafik sekaligus (`palet.py`). Pada palet gradasi, kunci `"0"` adalah nilai
    **tertinggi**, bukan terendah.
21. **Kueri widget Table** ada di entity `analyticgrid.table`
    (`data.content.segments[1].dataRegion.ffQuery`, berupa string JSON), bukan di
    widget-nya. Tabel juga melebar mengikuti lebar halaman.
22. Pictogram bawaan "panah" sebenarnya `<line>` tanpa `viewBox` yang menggambar
    pada y=30 — tak terlihat di widget setinggi 16 px. `alur.py` memakai SVG
    sendiri yang ber-`viewBox`.
23. **Ukuran titik pencar** ada di `properties.general.pointScale` — dan
    sarangnya ganda: `{"general": {"pointScale": {"pointScale": 3}}}` untuk
    300%. `plotArea.markerSize` (properti CVOM) diabaikan. Di UI: panel
    **Styling -> Data Points -> Data Marker Size**. Penting karena gambar
    2816 px dikecilkan ke slot dek selebar ~460 px, jadi titik bawaannya
    tinggal sekitar satu piksel.
24. **Menyimpan lewat UI mengubah hal lain tanpa diminta**: kanvas halaman
    disesuaikan dengan lebar jendela (1400 -> 1812), subjudul kosong diisi teks
    "Subtitle", dan entity `analyticgrid.table` yatim dibuang. Karena itu
    sesudah menyunting lewat UI, jalankan lagi `bangun-story.py` supaya
    halamannya kembali ke bentuk resep.
25. **Sorotan warna per anggota** (mis. Indonesia oranye di antara negara lain)
    ada di `story.data.colorSync` — **tingkat story, bukan widget** — berkunci
    ganda dataset lalu dataset+dimensi:

        colorSync['[{"datasetId":"<ds>"}]']
                 ['[{"datasetId":"<ds>"},{"dimensionId":"country"}]'] = {
            "colors": [...12 warna palet...],
            "explicitColorAssignments":       {"Indonesia": "#e8833a"},
            "explicitColorSwatchAssignments": {"Indonesia": ""},
            "id": "<id standardPalette>",
            "mappingPaletteId": "sapColorfulPalette",
            "preferredMappingPaletteId": "sapColorfulPalette"}

    Karena berkunci dataset+dimensi, satu penetapan berlaku untuk semua grafik
    yang memakai keduanya. Syaratnya: **dimensi itu harus ada di feed `color`**
    — kalau cuma di `categoryAxis`, penetapannya diabaikan. SAC juga menolak
    kalau grafiknya punya lebih dari satu measure atau lebih dari satu dimensi
    di feed Colour. Di UI: chip dimensi pada bagian Colour -> **•••** ->
    **Colour Sync** -> **Assign Colours...** (`sorot.py`).
26. **Menyembunyikan legenda butuh dua bendera.** `legendGroup.visible = false`
    saja tidak berpengaruh; selama `legendGroup.responsive` masih `true`, SAC
    mengatur legendanya sendiri dan menimpa bendera itu. Harus keduanya
    (`resep.TANPA_LEGENDA`).

## Pengurutan (`ffQuery.SortRepo.Elements`)

Arahnya `"Asc"` / `"Desc"` — **bukan** `"Ascending"`/`"Descending"`
(nilai yang salah diterima diam-diam lalu diabaikan).

```jsonc
// urut menurun menurut nilai measure
{"SortType": "Measure", "Direction": "Desc", "MeasureName": "cases", "Dimension": "country"}

// urut menurut anggota dimensi
{"SortType": "Field", "Direction": "Asc", "FieldName": "period", "Dimension": "period"}

// urutan kustom (mis. Jan..Dec, atau fase ENSO dari La Nina ke El Nino)
{"SortType": "Field", "Direction": "Asc", "FieldName": "month_name",
 "Dimension": "month_name", "CustomSort": ["Jan", "Feb", "..."]}
```

Batas jumlah anggota (Top-N) ditulis sebagai `"Top": 8` pada elemen dimensi di
`ffQuery.DimensionsRepo.Elements`.
