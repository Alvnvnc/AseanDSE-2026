#!/usr/bin/env python3
"""Mengubah data mentah menjadi CSV format panjang siap impor SAP Analytics Cloud.

Keluaran (data/siap-sac/):
  - dengue_asean.csv        : kasus dengue 10 negara ASEAN (OpenDengue V1.3, ekstrak spasial)
  - iklim_bulanan_asean.csv : suhu & curah hujan bulanan 10 negara (ERA5 via World Bank CCKP)
  - wash_rumahtangga_asean.csv : air/sanitasi/higiene rumah tangga (JMP 2025) — butuh openpyxl
"""
import csv
import json
import os
import re

AKAR = os.path.dirname(os.path.abspath(__file__))
KELUAR = os.path.join(AKAR, "siap-sac")
os.makedirs(KELUAR, exist_ok=True)

ASEAN = {
    "BRN": "Brunei Darussalam",
    "KHM": "Kamboja",
    "IDN": "Indonesia",
    "LAO": "Laos",
    "MYS": "Malaysia",
    "MMR": "Myanmar",
    "PHL": "Filipina",
    "SGP": "Singapura",
    "THA": "Thailand",
    "VNM": "Vietnam",
}


# OpenDengue memakai dua ejaan untuk provinsi yang sama pada era berbeda
# (sebagian terpotong, mis. "KALIMANTAN SELATA"). Sudah diperiksa: tiap pasangan
# nol bulan tumpang tindih, jadi aman digabung. Tanpa ini satu provinsi muncul
# dua kali di peta SAC dan gabungan ke peta wilayah gagal.
ALIAS_PROVINSI = {
    "IDN": {
        # varian di seri bulanan
        "NANGROE ACEH DARUSSALAM": "ACEH",
        "KALIMANTAN SELATA": "KALIMANTAN SELATAN",
        "D.I YOGYA": "DAERAH ISTIMEWA YOGYAKARTA",
        "BABEL": "BANGKA BELITUNG",
        "SUMATERA SELATA": "SUMATERA SELATAN",
        "SULAWESI SELATA": "SULAWESI SELATAN",
        "NUSATENGGARA BARAT": "NUSA TENGGARA BARAT",
        "NUSATENGGARA TIMUR": "NUSA TENGGARA TIMUR",
        # varian yang hanya muncul di seri tahunan — ejaannya lain lagi,
        # perhatikan "NANGGROE" dobel G di sini vs "NANGROE" tunggal di atas
        "NANGGROE ACEH DARUSSALAM": "ACEH",
        "KEPULAUAN BANGKA BELITUNG": "BANGKA BELITUNG",
        "KEPULAUAN-RIAU": "KEPULAUAN RIAU",
        "DI YOGYAKARTA": "DAERAH ISTIMEWA YOGYAKARTA",
    },
    # 1993-2002 tercatat "PRACHIN BURI", 2003+ "PHACHINBURI".
    # Catatan: Sa Kaeo baru muncul terpisah sejak 2003, jadi angka sebelum itu
    # kemungkinan masih mencakup wilayah Sa Kaeo.
    "THA": {"PHACHINBURI": "PRACHIN BURI"},
}


def siapkan_dengue():
    sumber = os.path.join(AKAR, "kesehatan", "spatial", "Spatial_extract_V1_3.csv")
    tujuan = os.path.join(KELUAR, "dengue_asean.csv")
    n = 0
    with open(sumber, newline="") as fin, open(tujuan, "w", newline="") as fout:
        pembaca = csv.DictReader(fin)
        penulis = csv.writer(fout)
        penulis.writerow([
            "negara", "iso3", "provinsi", "kab_kota",
            "tanggal_mulai", "tanggal_akhir", "tahun", "kasus",
            "definisi_kasus", "resolusi_spasial", "resolusi_waktu",
        ])
        for b in pembaca:
            iso = b["ISO_A0"]
            if iso not in ASEAN:
                continue
            prov = "" if b["adm_1_name"] == "NA" else b["adm_1_name"]
            prov = ALIAS_PROVINSI.get(iso, {}).get(prov, prov)
            penulis.writerow([
                ASEAN[iso], iso, prov,
                "" if b["adm_2_name"] == "NA" else b["adm_2_name"],
                b["calendar_start_date"], b["calendar_end_date"],
                b["Year"], b["dengue_total"],
                b["case_definition_standardised"], b["S_res"], b["T_res"],
            ])
            n += 1
    print(f"dengue_asean.csv: {n} baris")


def siapkan_iklim():
    tujuan = os.path.join(KELUAR, "iklim_bulanan_asean.csv")
    n = 0
    with open(tujuan, "w", newline="") as fout:
        penulis = csv.writer(fout)
        penulis.writerow(["negara", "iso3", "tahun", "bulan", "periode", "suhu_c", "hujan_mm"])
        for iso, nama in sorted(ASEAN.items()):
            with open(os.path.join(AKAR, "iklim", f"tas_{iso}.json")) as f:
                tas = json.load(f)["data"][iso]
            with open(os.path.join(AKAR, "iklim", f"pr_{iso}.json")) as f:
                pr = json.load(f)["data"][iso]
            for periode in sorted(tas):
                tahun, bulan = periode.split("-")
                penulis.writerow([nama, iso, tahun, int(bulan), periode,
                                  tas[periode], pr.get(periode, "")])
                n += 1
    print(f"iklim_bulanan_asean.csv: {n} baris")


def siapkan_wash():
    try:
        import openpyxl
    except ImportError:
        print("wash_rumahtangga_asean.csv: DILEWATI (openpyxl tidak terpasang)")
        return

    # indikator -> (kolom dasar di sheet, label Indonesia)
    LEMBAR = {
        "wat": ("Air minum", {
            "wat_sm": "Dikelola aman",
            "wat_basal": "Minimal dasar",
            "wat_lim": "Terbatas",
            "wat_unimp": "Tidak layak",
            "wat_ns": "Air permukaan",
            "wat_pip": "Perpipaan",
        }),
        "san": ("Sanitasi", {
            "san_sm": "Dikelola aman",
            "san_basal": "Minimal dasar",
            "san_lim": "Terbatas",
            "san_unimp": "Tidak layak",
            "san_ns": "BAB terbuka",
            "san_sew": "Tersambung selokan",
        }),
        "hyg": ("Higiene (CTPS)", {
            "hyg_bas": "Dasar",
            "hyg_lim": "Terbatas",
            "hyg_ns": "Tanpa fasilitas",
        }),
    }
    WILAYAH = {"r": "Perdesaan", "u": "Perkotaan", "t": "Total"}

    wb = openpyxl.load_workbook(
        os.path.join(AKAR, "wash", "jmp_household_wld.xlsx"), read_only=True)
    tujuan = os.path.join(KELUAR, "wash_rumahtangga_asean.csv")
    n = 0
    with open(tujuan, "w", newline="") as fout:
        penulis = csv.writer(fout)
        penulis.writerow(["negara", "iso3", "tahun", "populasi_ribu",
                          "layanan", "indikator", "wilayah", "persen"])
        for lembar, (layanan, indikator) in LEMBAR.items():
            ws = wb[lembar]
            baris = ws.iter_rows(values_only=True)
            hdr = [str(h) if h is not None else "" for h in next(baris)]
            idx = {h: i for i, h in enumerate(hdr)}
            for b in baris:
                iso = b[idx["iso3"]]
                if iso not in ASEAN:
                    continue
                tahun = int(b[idx["year"]])
                pop = b[idx["pop_t"]]
                for kol, label in indikator.items():
                    for kode_w, nama_w in WILAYAH.items():
                        nilai = b[idx.get(f"{kol}_{kode_w}", -1)]
                        if nilai is None or nilai == "":
                            continue
                        penulis.writerow([ASEAN[iso], iso, tahun,
                                          round(pop, 1) if pop else "",
                                          layanan, label, nama_w,
                                          round(float(nilai), 2)])
                        n += 1
    print(f"wash_rumahtangga_asean.csv: {n} baris")


def siapkan_wash_fasyankes():
    try:
        import openpyxl
    except ImportError:
        print("wash_fasyankes_asean.csv: DILEWATI (openpyxl tidak terpasang)")
        return

    LAYANAN = {
        "wat": "Air minum",
        "san": "Sanitasi",
        "hyg": "Higiene tangan",
        "wman": "Pengelolaan limbah medis",
        "clean": "Kebersihan lingkungan",
    }
    TINGKAT = {"bas": "Dasar", "lim": "Terbatas", "none": "Tanpa layanan"}
    LINGKUP = {"n": "Nasional", "u": "Perkotaan", "r": "Perdesaan",
               "h": "Rumah sakit", "nh": "Non-rumah sakit"}

    wb = openpyxl.load_workbook(
        os.path.join(AKAR, "wash", "jmp_healthcare_wld.xlsx"), read_only=True)
    tujuan = os.path.join(KELUAR, "wash_fasyankes_asean.csv")
    n = 0
    with open(tujuan, "w", newline="") as fout:
        penulis = csv.writer(fout)
        penulis.writerow(["negara", "iso3", "tahun",
                          "layanan", "tingkat", "lingkup", "persen"])
        for lembar, layanan in LAYANAN.items():
            ws = wb[lembar]
            baris = ws.iter_rows(values_only=True)
            hdr = [str(h) if h is not None else "" for h in next(baris)]
            idx = {h: i for i, h in enumerate(hdr)}
            if "iso3" not in idx:
                print(f"wash_fasyankes: lembar {lembar} tanpa kolom iso3, dilewati")
                continue
            for b in baris:
                iso = b[idx["iso3"]]
                if iso not in ASEAN:
                    continue
                tahun = int(b[idx["year"]])
                for kode_t, nama_t in TINGKAT.items():
                    for kode_l, nama_l in LINGKUP.items():
                        kol = f"{lembar}_{kode_t}_{kode_l}"
                        if kol not in idx:
                            continue
                        nilai = b[idx[kol]]
                        if nilai is None or nilai == "":
                            continue
                        try:
                            nilai = round(float(nilai), 2)
                        except ValueError:
                            continue  # penanda seperti "-" atau "<1"
                        penulis.writerow([ASEAN[iso], iso, tahun,
                                          layanan, nama_t, nama_l, nilai])
                        n += 1
    print(f"wash_fasyankes_asean.csv: {n} baris")


def _angka_id(teks):
    """Angka dari tabel SIPSN -> float, atau '' bila kosong.

    Tabelnya mencampur dua konvensi dalam satu halaman, jadi pemisahnya
    ditentukan per nilai (sudah disurvei atas ke-514 baris):
      '22,10'     koma selalu desimal, titik jadi pemisah ribuan
      '2.784 tpd' titik + tepat 3 digit = pemisah ribuan -> 2784
      '54.15'     titik + 1-2 digit    = desimal         -> 54,15
    """
    if teks is None:
        return ""
    t = str(teks).strip()
    for buang in ("tpd", "ton/hari", "%"):
        t = t.replace(buang, "")
    t = t.strip()
    if t in ("", "-", "NA", "n/a"):
        return ""
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif "." in t:
        kepala, _, ekor = t.rpartition(".")
        if len(ekor) == 3 and kepala:
            t = t.replace(".", "")  # pemisah ribuan
    try:
        return float(t)
    except ValueError:
        return ""


def siapkan_sampah():
    """Tabel SIPSN tertanam sebagai HTML statis di beranda (bukan API)."""
    import html
    import re

    sumber = os.path.join(AKAR, "sampah", "sipsn_beranda.html")
    if not os.path.exists(sumber):
        print("sampah_kabkota_indonesia.csv: DILEWATI (sipsn_beranda.html belum diunduh)")
        return

    KOLOM = [
        "no", "provinsi", "kab_kota", "jenis_tpa", "nama_tpa", "kelompok",
        "bsu_aktif", "bsu_tidak_aktif", "sampah_terkelola_bsu_ton",
        "bsi_aktif", "bsi_tidak_aktif", "sampah_terkelola_bsi_ton",
        "status_rips", "link_rips", "verifikasi_lapangan",
        "nilai_kinerja_ps", "progress_sa", "timbulan_ton_per_hari",
        "persen_terkelola", "persen_belum_terkelola",
    ]
    NUMERIK = {
        "bsu_aktif", "bsu_tidak_aktif", "sampah_terkelola_bsu_ton",
        "bsi_aktif", "bsi_tidak_aktif", "sampah_terkelola_bsi_ton",
        "nilai_kinerja_ps", "progress_sa", "timbulan_ton_per_hari",
        "persen_terkelola", "persen_belum_terkelola",
    }

    src = open(sumber).read()
    tbody = src[src.index("<tbody"):src.index("</tbody>")]
    tujuan = os.path.join(KELUAR, "sampah_kabkota_indonesia.csv")
    n = 0
    with open(tujuan, "w", newline="") as fout:
        penulis = csv.writer(fout)
        penulis.writerow([k for k in KOLOM if k not in ("no", "link_rips")])
        for tr in re.findall(r"<tr>(.*?)</tr>", tbody, re.S):
            sel = [html.unescape(" ".join(re.sub(r"<[^>]+>", " ", td).split()))
                   for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            if len(sel) != len(KOLOM):
                continue
            b = dict(zip(KOLOM, sel))
            penulis.writerow([
                _angka_id(b[k]) if k in NUMERIK else ("" if b[k] == "-" else b[k])
                for k in KOLOM if k not in ("no", "link_rips")
            ])
            n += 1
    print(f"sampah_kabkota_indonesia.csv: {n} baris")


def siapkan_udara():
    try:
        import openpyxl
    except ImportError:
        print("kota_asean_kualitas_udara.csv: DILEWATI (openpyxl tidak terpasang)")
        return

    sumber = os.path.join(AKAR, "kota", "who_aaq_v6_1_2024.xlsx")
    if not os.path.exists(sumber):
        print("kota_asean_kualitas_udara.csv: DILEWATI (berkas WHO belum diunduh)")
        return

    POLUTAN = {"pm25_concentration": "PM2.5",
               "pm10_concentration": "PM10",
               "no2_concentration": "NO2"}
    wb = openpyxl.load_workbook(sumber, read_only=True)
    ws = wb["Update 2024 (V6.1)"]
    baris = ws.iter_rows(values_only=True)
    hdr = [str(h) if h is not None else "" for h in next(baris)]
    idx = {h: i for i, h in enumerate(hdr)}

    tujuan = os.path.join(KELUAR, "kota_asean_kualitas_udara.csv")
    n = 0
    with open(tujuan, "w", newline="") as fout:
        penulis = csv.writer(fout)
        penulis.writerow(["negara", "iso3", "kota", "tahun",
                          "polutan", "konsentrasi_ug_m3", "cakupan_waktu_persen",
                          "jenis_stasiun"])
        for b in baris:
            iso = b[idx["iso3"]]
            if iso not in ASEAN:
                continue
            # satu nama kota Kamboja memuat baris baru di sumbernya
            kota = " ".join(str(b[idx["city"]] or "").replace(f"/{iso}", "").split())
            for kol, nama in POLUTAN.items():
                nilai = b[idx[kol]]
                if nilai in (None, "", "NA"):
                    continue
                try:
                    nilai = round(float(nilai), 3)
                except ValueError:
                    continue
                cak = b[idx.get(kol.replace("_concentration", "_tempcov"), -1)]
                try:
                    cak = round(float(cak), 1)
                except (TypeError, ValueError):
                    cak = ""
                # beberapa sel memuat baris baru; SAC lebih aman tanpa itu
                stasiun = " ".join(str(b[idx["type_of_stations"]] or "").split())
                penulis.writerow([ASEAN[iso], iso, kota, int(b[idx["year"]]),
                                  nama, nilai, cak, stasiun])
                n += 1
    print(f"kota_asean_kualitas_udara.csv: {n} baris")


def siapkan_enso():
    """Indeks ONI (Oceanic Nino Index) bulanan — penanda tahun El Nino/La Nina."""
    sumber = os.path.join(AKAR, "iklim", "oni_nino34.txt")
    if not os.path.exists(sumber):
        print("enso_oni_bulanan.csv: DILEWATI (oni_nino34.txt belum diunduh)")
        return

    def fase(v):
        if v >= 1.5:
            return "El Nino kuat"
        if v >= 0.5:
            return "El Nino"
        if v <= -1.5:
            return "La Nina kuat"
        if v <= -0.5:
            return "La Nina"
        return "Netral"

    tujuan = os.path.join(KELUAR, "enso_oni_bulanan.csv")
    n = 0
    with open(sumber) as fin, open(tujuan, "w", newline="") as fout:
        penulis = csv.writer(fout)
        penulis.writerow(["tahun", "bulan", "periode", "oni", "fase"])
        for garis in fin:
            bagian = garis.split()
            if len(bagian) != 13 or not bagian[0].isdigit():
                continue  # baris judul/catatan kaki
            tahun = int(bagian[0])
            for bulan, nilai in enumerate(bagian[1:], start=1):
                v = float(nilai)
                if v < -90:  # penanda kosong -99.9
                    continue
                penulis.writerow([tahun, bulan, f"{tahun}-{bulan:02d}",
                                  round(v, 2), fase(v)])
                n += 1
    print(f"enso_oni_bulanan.csv: {n} baris")


def siapkan_kota_banjir():
    """Paparan banjir kota dari GHS-UCDB R2024A (GeoPackage = SQLite).

    Dipakai .gpkg, bukan .xlsx, karena sqlite3 sudah ada di pustaka standar,
    jauh lebih cepat, dan diakritik nama kota (Cần Thơ) utuh.
    """
    import sqlite3

    sumber = os.path.join(AKAR, "kota", "GHS_UCDB_GLOBE_R2024A.gpkg")
    if not os.path.exists(sumber):
        print("kota_asean_paparan_banjir.csv: DILEWATI (GeoPackage belum diekstrak)")
        return

    NEGARA = {  # nama GADM di GHS-UCDB -> (nama Indonesia, iso3)
        "Indonesia": ("Indonesia", "IDN"), "Vietnam": ("Vietnam", "VNM"),
        "Thailand": ("Thailand", "THA"), "Philippines": ("Filipina", "PHL"),
        "Myanmar": ("Myanmar", "MMR"), "Malaysia": ("Malaysia", "MYS"),
        "Cambodia": ("Kamboja", "KHM"), "Laos": ("Laos", "LAO"),
        "Singapore": ("Singapura", "SGP"), "Brunei": ("Brunei Darussalam", "BRN"),
    }
    # periode ulang banjir -> label
    UKURAN = {
        "EX_010_POP": ("Penduduk terpapar banjir 10 tahunan", "jiwa"),
        "EX_100_POP": ("Penduduk terpapar banjir 100 tahunan", "jiwa"),
        "EX_100_SHP": ("Persen penduduk terpapar banjir 100 tahunan", "persen"),
    }
    TAHUN = [1975, 1980, 1985, 1990, 1995, 2000, 2005,
             2010, 2015, 2020, 2025, 2030]

    T = "GHSL_UCDB_THEME_EXPOSURE_GLOBE_R2024A"
    kolom = [f"{k}_{t}" for k in UKURAN for t in TAHUN]
    db = sqlite3.connect(sumber)
    pilih = ", ".join(['GC_UCN_MAI_2025', 'GC_CNT_GAD_2025', 'GC_POP_TOT_2025']
                      + [f'"{c}"' for c in kolom])
    tanda = ",".join("?" * len(NEGARA))
    kueri = (f'SELECT {pilih} FROM "{T}" '
             f'WHERE GC_CNT_GAD_2025 IN ({tanda}) ORDER BY GC_CNT_GAD_2025, GC_UCN_MAI_2025')

    tujuan = os.path.join(KELUAR, "kota_asean_paparan_banjir.csv")
    n = kota = 0
    with open(tujuan, "w", newline="") as fout:
        penulis = csv.writer(fout)
        penulis.writerow(["negara", "iso3", "kota", "penduduk_kota_2025",
                          "tahun", "indikator", "satuan", "nilai"])
        for b in db.execute(kueri, tuple(NEGARA)):
            nama_kota, nama_gadm, pop = b[0], b[1], b[2]
            negara, iso = NEGARA[nama_gadm]
            kota += 1
            for i, kol in enumerate(kolom, start=3):
                nilai = b[i]
                if nilai is None:
                    continue
                ukuran, satuan = UKURAN[kol.rsplit("_", 1)[0]]
                penulis.writerow([
                    negara, iso, nama_kota,
                    round(pop) if pop is not None else "",
                    int(kol.rsplit("_", 1)[1]), ukuran, satuan,
                    round(float(nilai), 2),
                ])
                n += 1
    print(f"kota_asean_paparan_banjir.csv: {n} baris ({kota} kota)")


# Nama provinsi BPS -> nama di OpenDengue (yang sudah dinormalkan lewat ALIAS_PROVINSI).
# Hanya yang berbeda yang perlu didaftarkan; sisanya sudah sama persis.
PROVINSI_BPS = {
    "KEP. BANGKA BELITUNG": "BANGKA BELITUNG",
    "KEPULAUAN BANGKA BELITUNG": "BANGKA BELITUNG",
    "KEP. RIAU": "KEPULAUAN RIAU",
    "DI YOGYAKARTA": "DAERAH ISTIMEWA YOGYAKARTA",
    "D.I. YOGYAKARTA": "DAERAH ISTIMEWA YOGYAKARTA",
    "DKI JAKARTA": "DKI JAKARTA",
}


def siapkan_bencana():
    """Statistik Bencana Menurut Wilayah (kab/kota) dari zip per tahun.

    Tiap zip = satu tahun, isinya 38 berkas provinsi. Angkanya bergaya Inggris
    (koma = pemisah ribuan) — beda dari SIPSN yang bergaya Indonesia.
    Tiap berkas punya baris "Jumlah"; dipakai sebagai uji silang, bukan diekspor.
    """
    try:
        import openpyxl
    except ImportError:
        print("bencana_kabkota_indonesia.csv: DILEWATI (openpyxl tidak terpasang)")
        return

    import glob
    import io
    import zipfile

    zips = sorted(glob.glob(os.path.join(AKAR, "bencana", "*.zip")))
    if not zips:
        print("bencana_kabkota_indonesia.csv: DILEWATI (zip bencana tidak ada)")
        return

    # posisi kolom -> nama indikator (lihat header bertingkat baris 5-7)
    KOLOM = {
        2: "Jumlah kejadian", 3: "Korban meninggal", 4: "Korban hilang",
        5: "Korban terluka", 6: "Korban menderita", 7: "Korban mengungsi",
        8: "Rumah rusak berat", 9: "Rumah rusak sedang", 10: "Rumah rusak ringan",
        11: "Rumah terendam", 12: "Fasilitas pendidikan rusak",
        13: "Fasilitas kesehatan rusak", 14: "Fasilitas peribadatan rusak",
        15: "Fasilitas umum rusak",
    }
    # Papua dipecah jadi 6 provinsi pada 2022, tapi ekspor ini memakai struktur
    # baru itu mundur sampai 2018 — sedangkan dengue 2018-2020 masih struktur lama.
    # Kolom `provinsi_setara_dengue` mengembalikannya agar bisa dijodohkan.
    PAPUA_LAMA = {
        "PAPUA": "PAPUA", "PAPUA SELATAN": "PAPUA",
        "PAPUA TENGAH": "PAPUA", "PAPUA PEGUNUNGAN": "PAPUA",
        "PAPUA BARAT": "PAPUA BARAT", "PAPUA BARAT DAYA": "PAPUA BARAT",
    }

    def angka(v):
        if v is None:
            return 0.0
        s = str(v).strip().replace(",", "")   # koma = pemisah ribuan
        if s in ("", "-"):
            return 0.0
        try:
            return float(s)
        except ValueError:
            return 0.0

    tujuan = os.path.join(KELUAR, "bencana_kabkota_indonesia.csv")
    n = n_berkas = 0
    beda = []
    with open(tujuan, "w", newline="") as fout:
        penulis = csv.writer(fout)
        penulis.writerow(["provinsi", "kode_provinsi", "provinsi_setara_dengue",
                          "kab_kota", "kode_kab_kota", "tahun",
                          "indikator", "nilai"])
        for z in zips:
            with zipfile.ZipFile(z) as zf:
                for nama in sorted(x for x in zf.namelist() if x.endswith(".xlsx")):
                    wb = openpyxl.load_workbook(io.BytesIO(zf.read(nama)), read_only=True)
                    ws = wb["statistik"]
                    baris = list(ws.iter_rows(values_only=True))
                    judul = next((c for c in baris[3] if c), "")
                    m = re.search(r"(\d+)\.\s*(.+?),\s*(\d{4})", str(judul))
                    if not m:
                        continue
                    kode_p, nama_p, tahun = m.group(1), m.group(2).strip(), int(m.group(3))
                    prov = nama_p.upper()
                    setara = PAPUA_LAMA.get(prov, PROVINSI_BPS.get(prov, prov))
                    n_berkas += 1

                    isi = [b for b in baris[8:]
                           if b[1] and str(b[1]).strip() not in ("Jumlah", "")]
                    total = next((b for b in baris
                                  if b[1] and str(b[1]).strip() == "Jumlah"), None)
                    for kol, ind in KOLOM.items():
                        if total is not None:
                            s = sum(angka(b[kol]) for b in isi)
                            t = angka(total[kol])
                            if abs(s - t) > 0.5:
                                beda.append(f"{nama_p} {tahun} {ind}: {s:,.0f} vs {t:,.0f}")
                    for b in isi:
                        wil = str(b[1]).strip()
                        mk = re.match(r"(\d+)\.\s*(.+)", wil)
                        kode_k, nama_k = (mk.group(1), mk.group(2).strip()) if mk else ("", wil)
                        for kol, ind in KOLOM.items():
                            penulis.writerow([nama_p, kode_p, setara, nama_k, kode_k,
                                              tahun, ind, round(angka(b[kol]))])
                            n += 1
    print(f"bencana_kabkota_indonesia.csv: {n} baris ({n_berkas} berkas provinsi-tahun)")
    if beda:
        print(f"   ! {len(beda)} kolom tidak sama dengan baris 'Jumlah': {beda[:3]}")


def _tulis_penduduk(baris, label_sumber=None):
    """Menulis CSV penduduk.

    `baris` = daftar (provinsi, tahun, jiwa) bila `label_sumber` diberikan,
    atau (provinsi, tahun, jiwa, sumber) bila tiap baris punya sumber sendiri.
    """
    tujuan = os.path.join(KELUAR, "penduduk_provinsi_indonesia.csv")
    with open(tujuan, "w", newline="") as fout:
        penulis = csv.writer(fout)
        penulis.writerow(["negara", "iso3", "provinsi", "tahun", "penduduk", "sumber"])
        for b in sorted(baris):
            nama, th, v = b[0], b[1], b[2]
            penulis.writerow(["Indonesia", "IDN", nama, th, round(v),
                              label_sumber or b[3]])


def _lapor_irisan_dengue(tahun_penduduk):
    """Memperingatkan kalau tahun penduduk tidak beririsan dengan data dengue.

    Tanpa irisan, kolom insidens akan kosong semua — lebih baik ketahuan di sini
    daripada baru disadari saat grafiknya dibuat di SAC.
    """
    berkas = os.path.join(KELUAR, "dengue_asean.csv")
    if not os.path.exists(berkas):
        return
    th_dengue = {int(b["tahun"]) for b in csv.DictReader(open(berkas))
                 if b["iso3"] == "IDN" and b["provinsi"]}
    irisan = sorted(tahun_penduduk & th_dengue)
    if irisan:
        print(f"   irisan dengan data dengue: {irisan[0]}-{irisan[-1]} "
              f"({len(irisan)} tahun)")
    else:
        print(f"   ! TIDAK ADA IRISAN dengan data dengue "
              f"(dengue {min(th_dengue)}-{max(th_dengue)}, "
              f"penduduk {min(tahun_penduduk)}-{max(tahun_penduduk)}) "
              f"-> kolom insidens akan kosong")


def _penduduk_querybuilder():
    """Hasil unduhan Query Builder BPS (CSV), tanpa perlu kunci.

    Bentuknya bertingkat: baris-2 jenis kelamin, baris-3 tahun, sejajar per kolom.
    Ditulis agar tahan berapa pun jumlah tahun yang dipilih — kolom "Jumlah" dicari
    lewat pasangan (jenis, tahun), bukan lewat posisi tetap.
    """
    berkas = os.path.join(AKAR, "penduduk", "bps_penduduk_provinsi_querybuilder.csv")
    if not os.path.exists(berkas):
        return [], ""

    with open(berkas, newline="", encoding="utf-8-sig") as f:
        semua = list(csv.reader(f))
    if len(semua) < 3:
        return [], ""

    judul = " ".join(semua[0])
    # Query Builder punya dua tata letak, tergantung ada tidaknya rincian jenis kelamin:
    #   A. baris-1 jenis kelamin, baris-2 tahun   (mis. "...menurut Provinsi dan Jenis Kelamin")
    #   B. baris-1 langsung tahun                  (mis. "Jumlah Penduduk Pertengahan Tahun")
    # Barisnya dicari, bukan diasumsikan, supaya keduanya jalan.
    def baris_tahun(b):
        isi = [s.strip() for s in b if s.strip()]
        return isi and sum(s.isdigit() and 1900 <= int(s) <= 2100 for s in isi) >= len(isi) / 2

    i_th = next((i for i in range(min(4, len(semua))) if baris_tahun(semua[i])), None)
    if i_th is None:
        return [], ""
    tahun = [s.strip() for s in semua[i_th]]

    atas = [s.strip() for s in semua[i_th - 1]] if i_th else []
    punya_jenis = any(s.lower() in ("laki-laki", "perempuan", "jumlah") for s in atas)
    kolom = [(i, int(tahun[i])) for i in range(len(tahun))
             if tahun[i].isdigit() and 1900 <= int(tahun[i]) <= 2100
             and (not punya_jenis or (i < len(atas) and atas[i].lower() == "jumlah"))]
    if not kolom:
        return [], ""

    # "(Ribu Jiwa)" di judul -> kalikan 1000. Tapi BPS sesekali menaruh satu kolom
    # dalam satuan jiwa di tabel ribu-jiwa yang sama (terlihat pada 2026), jadi
    # pengaliannya dibatalkan untuk nilai yang jadi mustahil besar.
    ribuan = "ribu jiwa" in judul.lower()

    catatan = ""
    baris = []
    for b in semua[i_th + 1:]:
        if not b or not b[0].strip():
            continue
        nama = b[0].strip().upper()
        if nama.startswith("CATATAN"):
            catatan = re.sub(r"<[^>]+>", " ", " ".join(b[1:]))
            catatan = " ".join(catatan.split())
            continue
        if nama == "INDONESIA":       # baris total nasional, bukan provinsi
            continue
        nama = PROVINSI_BPS.get(nama, nama)
        for i, th in kolom:
            if i >= len(b):
                continue
            v = b[i].replace(".", "").replace(",", ".").strip()
            try:
                nilai = float(v)
            except ValueError:
                continue
            if ribuan and nilai < 1e6:      # 1e6 ribu jiwa = 1 miliar, mustahil
                nilai *= 1000
            baris.append((nama, th, nilai))
    return baris, catatan


def _penduduk_arsip():
    """Cadangan: tabel BPS 2018-2020 dari arsip Wayback.

    Seluruh *.bps.go.id dilindungi tantangan Cloudflare, jadi tanpa kunci WebAPI
    satu-satunya BPS yang bisa diambil skrip adalah halaman yang terlanjur
    diarsipkan. Ini proyeksi berbasis SP2010 (34 provinsi) — beda seri dengan
    SP2020, karena itu kolom `sumber` di CSV wajib dibaca sebelum menggabungkan.
    """
    import re

    berkas = os.path.join(AKAR, "penduduk",
                          "bps_penduduk_provinsi_arsip_2018-2020.html")
    if not os.path.exists(berkas):
        return []

    teks = re.sub(r"\s+", " ",
                  re.sub(r"<[^>]+>", " ",
                         open(berkas, encoding="utf-8", errors="replace").read()))
    mulai = teks.find("ACEH")
    if mulai < 0:
        return []
    # tiap baris: NAMA lalu 9 angka (L/P/Jumlah x 2018/2019/2020)
    pola = re.compile(r"([A-Z][A-Z.'\- ]{2,40}?)\s+((?:\d[\d.]*\s+){8}\d[\d.]*)")
    baris = []
    for nama, angka in pola.findall(teks[mulai:mulai + 6000]):
        nama = nama.strip().upper()
        if nama == "INDONESIA":       # baris total nasional, bukan provinsi
            continue
        nama = PROVINSI_BPS.get(nama, nama)
        jumlah = angka.split()[6:9]   # tiga kolom "Jumlah"
        for tahun, nilai in zip((2018, 2019, 2020), jumlah):
            baris.append((nama, tahun, float(nilai) * 1000))  # ribu jiwa -> jiwa
    return baris


def siapkan_penduduk():
    """Penduduk provinsi Indonesia.

    Utama : WebAPI BPS (perlu kunci). Catatan 9 Agu 2026: var 1886 di WebAPI
            berisi proyeksi SP2010 2015-2020 (nilainya identik dengan arsip
            Wayback, sudah dicek 93/93 baris) — seri provinsi 2021-2024 belum
            tersedia lewat WebAPI; SUPAS 2025 (var 2781) hanya tahun 2025.
    Cadangan: arsip Wayback (proyeksi SP2010, 2018-2020, 34 provinsi) — tanpa kunci.
    """
    sumber = os.path.join(AKAR, "penduduk", "bps_penduduk_provinsi.json")
    if not os.path.exists(sumber):
        # gabungkan sumber tanpa-kunci: Query Builder (kalau ada) + arsip Wayback.
        # Keduanya BPS tapi beda seri, jadi label sumbernya dibedakan per baris.
        qb, catatan = _penduduk_querybuilder()
        berkas_qb = os.path.join(AKAR, "penduduk",
                                 "bps_penduduk_provinsi_querybuilder.csv")
        if not qb and os.path.exists(berkas_qb):
            print("   ! bps_penduduk_provinsi_querybuilder.csv ada tapi tidak memuat "
                  "baris provinsi mana pun.\n"
                  "     Di Query Builder BPS, ganti wilayahnya dari 'Indonesia' "
                  "menjadi '38 Provinsi'.")
        arsip = _penduduk_arsip()
        if not qb and not arsip:
            print("penduduk_provinsi_indonesia.csv: DILEWATI "
                  "(jalankan dulu: BPS_KEY=<kunci> python3 unduh_bps.py)")
            return

        label_qb = "BPS Query Builder"
        if "antar sensus" in catatan.lower() or "supas" in catatan.lower():
            label_qb = "BPS SUPAS 2025"
        bergabung = ([(n, t, v, label_qb) for n, t, v in qb]
                     + [(n, t, v, "BPS proyeksi SP2010 (arsip Wayback 2022-12-04)")
                        for n, t, v in arsip])
        _tulis_penduduk(bergabung)

        for label in dict.fromkeys(x[3] for x in bergabung):
            sub = [x for x in bergabung if x[3] == label]
            print(f"penduduk_provinsi_indonesia.csv: {len(sub)} baris — {label} "
                  f"({len({x[0] for x in sub})} provinsi, "
                  f"{min(x[1] for x in sub)}-{max(x[1] for x in sub)})")
        _lapor_irisan_dengue({x[1] for x in bergabung})
        return

    d = json.load(open(sumber, encoding="utf-8"))
    var = str(d["var"][0]["val"])
    isi = d["datacontent"]

    # turvar = jenis kelamin; ambil yang total bila ada, kalau tidak jumlahkan L+P
    turvar = d.get("turvar") or [{"val": 0, "label": "Total"}]
    total = [t for t in turvar
             if str(t.get("label", "")).strip().lower() in ("total", "jumlah", "laki-laki+perempuan")]
    turth = d.get("turtahun") or [{"val": 0}]

    baris = []
    for prov in d["vervar"]:
        nama = str(prov["label"]).strip().upper()
        if nama == "INDONESIA":       # baris total nasional, bukan provinsi
            continue
        nama = PROVINSI_BPS.get(nama, nama)
        for th in d["tahun"]:
            nilai = None
            pakai = total or turvar
            akumulasi = 0.0
            ada = False
            for tv in pakai:
                for tt in turth:
                    # kunci datacontent BPS = gabungan polos tanpa padding
                    # (vervar+var+turvar+th+turth, dicek langsung pada respons 2026);
                    # varian lama berpadding dipertahankan sebagai cadangan
                    for k in (f'{prov["val"]}{var}{tv["val"]}{th["val"]}{tt["val"]}',
                              f'{prov["val"]}{var}{int(tv["val"]):03d}{int(th["val"]):03d}{int(tt["val"]):02d}'):
                        if k in isi:
                            akumulasi += float(isi[k])
                            ada = True
                            break
            if ada:
                nilai = akumulasi
            if nilai is not None:
                baris.append((nama, int(th["label"]), nilai))

    if not baris:
        print("penduduk_provinsi_indonesia.csv: GAGAL — tidak ada nilai yang cocok; "
              "periksa struktur JSON BPS")
        return

    # BPS menerbitkan var ini dalam ribu jiwa; deteksi dari besaran totalnya
    # agar tidak salah kali 1000 kalau satuannya berubah.
    tahun_awal = min(t for _, t, _ in baris)
    total_awal = sum(v for _, t, v in baris if t == tahun_awal)
    ribuan = total_awal < 1_000_000  # Indonesia ~280 juta jiwa / ~280 ribu ribu-jiwa
    pengali = 1000 if ribuan else 1

    # jangan tebak serinya dari nama variabel — deteksi dari nilainya: proyeksi
    # SP2010 menaksir Aceh 2020 ±5.388 rb jiwa, SP2020 ±5.275 rb (lihat README)
    label = "BPS WebAPI"
    aceh2020 = next((v * pengali for n, t, v in baris if n == "ACEH" and t == 2020), None)
    if aceh2020 is not None:
        label = ("BPS proyeksi SP2010 (WebAPI)" if aceh2020 > 5_330_000
                 else "BPS proyeksi SP2020 (WebAPI)")

    # pertahankan seri Query Builder (mis. SUPAS 2025) untuk tahun yang tidak
    # dicakup WebAPI, supaya CSV-nya tidak kehilangan isi dibanding jalur tanpa kunci
    gabung = [(n, t, v * pengali, label) for n, t, v in baris]
    qb, catatan = _penduduk_querybuilder()
    if qb:
        label_qb = "BPS Query Builder"
        if "antar sensus" in catatan.lower() or "supas" in catatan.lower():
            label_qb = "BPS SUPAS 2025"
        th_web = {t for _, t, _ in baris}
        gabung += [(n, t, v, label_qb) for n, t, v in qb if t not in th_web]

    _tulis_penduduk(gabung)
    for lab in dict.fromkeys(x[3] for x in gabung):
        sub = [x for x in gabung if x[3] == lab]
        print(f"penduduk_provinsi_indonesia.csv: {len(sub)} baris — {lab} "
              f"({len({x[0] for x in sub})} provinsi, "
              f"{min(x[1] for x in sub)}-{max(x[1] for x in sub)})")
    _lapor_irisan_dengue({x[1] for x in gabung})

    # laporkan provinsi yang tidak berpasangan dengan data dengue — jangan diam-diam hilang
    berkas_d = os.path.join(KELUAR, "dengue_asean.csv")
    if os.path.exists(berkas_d):
        prov_d = {b["provinsi"] for b in csv.DictReader(open(berkas_d))
                  if b["iso3"] == "IDN" and b["provinsi"]}
        prov_b = {b[0] for b in baris}
        if prov_b - prov_d:
            print(f"   ! ada di BPS tapi tidak di dengue: {sorted(prov_b - prov_d)}")
        if prov_d - prov_b:
            print(f"   ! ada di dengue tapi tidak di BPS: {sorted(prov_d - prov_b)}")


def _geser(periode, jeda):
    """'2015-03' digeser mundur N bulan -> '2015-01' untuk jeda=2."""
    tahun, bulan = int(periode[:4]), int(periode[5:7]) - jeda
    while bulan < 1:
        bulan += 12
        tahun -= 1
    return f"{tahun}-{bulan:02d}"


def siapkan_analisis_jeda():
    """Tabel utama storyboard: kasus bulanan + iklim & ONI pada beberapa jeda.

    SAP Analytics Cloud tidak mudah melakukan gabung-berjeda, jadi kolom jeda
    dihitung di sini. Satu baris = satu provinsi-bulan.
    """
    JEDA = (0, 1, 2, 3)
    JEDA_ONI = (0, 3, 4)

    iklim = {}
    for iso in ASEAN:
        for var in ("tas", "pr"):
            berkas = os.path.join(AKAR, "iklim", f"{var}_{iso}.json")
            if os.path.exists(berkas):
                iklim[(iso, var)] = json.load(open(berkas))["data"][iso]

    oni = {}
    berkas_oni = os.path.join(KELUAR, "enso_oni_bulanan.csv")
    if os.path.exists(berkas_oni):
        for b in csv.DictReader(open(berkas_oni)):
            oni[b["periode"]] = (float(b["oni"]), b["fase"])

    # kasus bulanan per provinsi (hanya baris beresolusi bulan & Admin1)
    kasus = {}
    with open(os.path.join(KELUAR, "dengue_asean.csv")) as f:
        for b in csv.DictReader(f):
            if b["resolusi_waktu"] != "Month" or b["resolusi_spasial"] != "Admin1":
                continue
            kunci = (b["negara"], b["iso3"], b["provinsi"], b["tanggal_mulai"][:7])
            kasus[kunci] = kasus.get(kunci, 0.0) + float(b["kasus"] or 0)

    # penduduk provinsi (baru ada untuk Indonesia; sisanya dibiarkan kosong)
    penduduk = {}
    berkas_p = os.path.join(KELUAR, "penduduk_provinsi_indonesia.csv")
    if os.path.exists(berkas_p):
        for b in csv.DictReader(open(berkas_p)):
            penduduk[(b["iso3"], b["provinsi"], int(b["tahun"]))] = float(b["penduduk"])

    tujuan = os.path.join(KELUAR, "dengue_iklim_bulanan.csv")
    n = n_ins = 0
    with open(tujuan, "w", newline="") as fout:
        penulis = csv.writer(fout)
        penulis.writerow(
            ["negara", "iso3", "provinsi", "periode", "tahun", "bulan", "kasus"]
            + [f"suhu_jeda{j}" for j in JEDA]
            + [f"hujan_jeda{j}" for j in JEDA]
            + [f"oni_jeda{j}" for j in JEDA_ONI]
            + ["fase_enso_jeda4", "penduduk", "insidens_per_100rb"]
        )
        for (negara, iso, prov, per) in sorted(kasus):
            tas = iklim.get((iso, "tas"), {})
            pr = iklim.get((iso, "pr"), {})
            jml = round(kasus[(negara, iso, prov, per)], 1)
            baris = [negara, iso, prov, per, int(per[:4]), int(per[5:7]), jml]
            baris += [tas.get(_geser(per, j), "") for j in JEDA]
            baris += [pr.get(_geser(per, j), "") for j in JEDA]
            baris += [oni.get(_geser(per, j), ("", ""))[0] for j in JEDA_ONI]
            baris.append(oni.get(_geser(per, 4), ("", ""))[1])
            pop = penduduk.get((iso, prov, int(per[:4])))
            if pop:
                baris += [round(pop), round(jml / pop * 100_000, 3)]
                n_ins += 1
            else:
                baris += ["", ""]
            penulis.writerow(baris)
            n += 1
    print(f"dengue_iklim_bulanan.csv: {n} baris "
          f"({n_ins} di antaranya punya insidens per 100 rb)")


if __name__ == "__main__":
    siapkan_dengue()
    siapkan_iklim()
    siapkan_wash()
    siapkan_wash_fasyankes()
    siapkan_sampah()
    siapkan_udara()
    siapkan_enso()
    siapkan_kota_banjir()
    siapkan_bencana()
    siapkan_penduduk()
    siapkan_analisis_jeda()  # harus setelah penduduk agar insidens ikut terhitung
