#!/usr/bin/env python3
"""Ekspor semua data proyek ke berkas Excel (.xlsx).

Menghasilkan dua hal di `ekspor-xlsx/`:

1. `ASEAN_DSE_hasil_analisis.xlsx` — satu buku kerja berisi seluruh tabel hasil
   analisis (`analisis/keluaran/*.csv`) plus lembar "Daftar isi" dan "Angka kunci".
   Ini yang dipakai menulis naskah storyboard / bikin grafik cepat di Excel.
2. `sac/<nama>.xlsx` — satu berkas per himpunan data mentah (`data/siap-sac/*.csv`),
   karena SAP Analytics Cloud mengimpor satu himpunan data per berkas.

Jalankan: .venv/bin/python analisis/ekspor_xlsx.py
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

AKAR = Path(__file__).resolve().parent.parent
KELUARAN = AKAR / "analisis" / "keluaran"
SIAP_SAC = AKAR / "data" / "siap-sac"
TUJUAN = AKAR / "ekspor-xlsx"

WARNA_KEPALA = PatternFill("solid", fgColor="1F4E79")
FONT_KEPALA = Font(bold=True, color="FFFFFF")

# Urutan lembar = urutan halaman storyboard.
# asal "csv:<nama>" dibaca dari analisis/keluaran/, "hitung" dihasilkan lembar_grafik()
# (definisi identik dengan analisis_storyboard.ipynb).
URUTAN: list[tuple[str, str, str, str]] = [
    ("csv:dengue_asean_nasional_tahunan", "Dengue nasional tahunan", "2",
     "Kasus dengue per negara per tahun (9 negara ASEAN); kolom 'lengkap' menandai tahun yang boleh dibandingkan."),
    ("hitung", "Musiman IDN-THA", "5",
     "Rata-rata kasus, hujan, dan suhu per bulan kalender (tahun lengkap 2010+) — kurva musiman."),
    ("csv:korelasi_jeda_nasional", "Korelasi jeda - nasional", "6",
     "Korelasi kasus vs suhu/hujan/ONI pada jeda 0-8 bulan, deret mentah (musim belum dibuang)."),
    ("hitung", "Deret bulanan IDN-THA", "6, 7, 10, 11",
     "Tulang punggung: deret bulanan nasional 2010+ — kasus, anomali, ONI/suhu/hujan berjeda, ambang P75, status alarm."),
    ("hitung", "Fase ENSO - rerata", "7",
     "Kartu as: rata-rata kasus/bulan Indonesia menurut fase ENSO 4 bulan sebelumnya (El Nino kuat vs netral)."),
    ("csv:korelasi_jeda_anomali", "Korelasi jeda - anomali", "7",
     "Korelasi yang sama tapi atas ANOMALI (efek musim dibuang) — bukti sinyalnya bukan sekadar musim."),
    ("hitung", "Konsistensi provinsi IDN", "7",
     "Rasio kasus bulan El Nino / bulan lain per provinsi — bukti efeknya bukan artefak agregat nasional."),
    ("csv:kalender_risiko_idn", "Kalender risiko IDN", "8, 10",
     "Pangsa kasus tiap bulan per provinsi Indonesia + status Puncak/Waspada/Normal (status_kode 2/1/0)."),
    ("csv:kalender_risiko_tha", "Kalender risiko THA", "8",
     "Kalender risiko yang sama untuk 77 provinsi Thailand (replikasi lintas negara)."),
    ("csv:insidens_provinsi_2018_2020", "Insidens provinsi 18-20", "9, 12",
     "Insidens per 100rb penduduk, HANYA 2018-2020 (penyebut resmi BPS). Dasar prioritas wilayah."),
    ("hitung", "Kerentanan kota banjir", "9",
     "25 kota ASEAN dengan penduduk terbanyak di zona banjir 100 tahunan (2020 & proyeksi 2030)."),
    ("hitung", "WASH negara", "9",
     "Akses air perpipaan, air minum, dan sanitasi per negara (tahun terbaru) — lapisan SDG 6."),
    ("csv:ambang_pemicu_evaluasi", "Aturan pemicu - evaluasi", "11",
     "Perbandingan aturan alarm A-D pada data penuh 2010-2024: cakupan, sensitivitas, presisi, lift."),
    ("csv:ambang_pemicu_luar_sampel", "Aturan pemicu - luar sampel", "12",
     "Uji buta: aturan disusun dari 2010-2016, diuji pada 2017-2024 (Indonesia & Thailand)."),
    ("csv:ambang_pemicu_vs_kanal_endemis", "Aturan vs kanal endemis", "12",
     "Aturan diuji terhadap definisi wabah standar WHO/PAHO (kanal endemis, mean+2SD 5 tahun)."),
    ("csv:benchmark_ews", "Tolok ukur EWS", "12",
     "Kinerja aturan kami disandingkan dengan sistem peringatan dini dengue terpublikasi."),
    ("csv:episode_elnino_tenggang", "Episode El Nino - tenggang", "13",
     "Tiap episode El Nino sejak 2009: kapan alarm menyala, kapan kasus melewati P75, berapa bulan tenggangnya."),
    ("csv:dampak_moneter", "Dampak moneter", "13",
     "Skenario 10/20/30% kasus musim puncak tercegah -> nilai US$ dan Rp per tahun."),
    ("csv:inovasi_kekeringan_akses_air", "Kekeringan x akses air", "14",
     "Uji sudut inovasi kekeringan x akses air — EKSPLORATIF (n=7) dan GUGUR sebagai klaim kausal."),
]

KETERANGAN_SAC: dict[str, str] = {
    "dengue_asean": "Kasus dengue ASEAN mentah dari OpenDengue (semua resolusi ruang & waktu).",
    "dengue_iklim_bulanan": "Tabel analisis utama: kasus bulanan + suhu/hujan/ONI dengan jeda 0-4 bulan.",
    "iklim_bulanan_asean": "Suhu dan curah hujan bulanan per negara, 1950-sekarang.",
    "enso_oni_bulanan": "Indeks ONI bulanan NOAA/CPC + fase ENSO (ambang resmi 0,5).",
    "penduduk_provinsi_indonesia": "Penduduk provinsi Indonesia (BPS WebAPI) — penyebut insidens 2018-2020.",
    "wash_rumahtangga_asean": "Akses air minum & sanitasi rumah tangga (JMP WHO/UNICEF).",
    "wash_fasyankes_asean": "Akses air & sanitasi di fasilitas layanan kesehatan (JMP WHO/UNICEF).",
    "bencana_kabkota_indonesia": "Kejadian bencana per kabupaten/kota Indonesia (BNPB).",
    "sampah_kabkota_indonesia": "Timbulan & pengelolaan sampah per kabupaten/kota (SIPSN KLHK).",
    "kota_asean_paparan_banjir": "Penduduk kota ASEAN yang terpapar banjir (GHSL).",
    "kota_asean_kualitas_udara": "Konsentrasi PM2.5/PM10/NO2 kota ASEAN (WHO Ambient Air Quality).",
}

POLA_RIBUAN = re.compile(r"^-?\d{1,3}(,\d{3})+$")


def rapikan(df: pd.DataFrame, nama: str) -> pd.DataFrame:
    """Beri nama kolom tanpa judul dan ubah angka ber-pemisah-ribuan jadi numerik."""
    ganti = {"ambang_pemicu_luar_sampel": "periode", "ambang_pemicu_vs_kanal_endemis": "aturan"}
    df = df.rename(columns={c: ganti.get(nama, "keterangan")
                            for c in df.columns if str(c).startswith("Unnamed:")})
    for kol in df.columns:
        if df[kol].dtype == "object" or pd.api.types.is_string_dtype(df[kol]):
            teks = df[kol].dropna().astype(str)
            if len(teks) and teks.map(lambda v: bool(POLA_RIBUAN.match(v))).all():
                df[kol] = pd.to_numeric(df[kol].astype(str).str.replace(",", "", regex=False))
    return df


def tulis(df: pd.DataFrame, penulis: pd.ExcelWriter, lembar: str, bekukan: bool = True) -> None:
    df.to_excel(penulis, sheet_name=lembar, index=False)
    ws = penulis.book[lembar]
    for sel in ws[1]:
        sel.fill = WARNA_KEPALA
        sel.font = FONT_KEPALA
        sel.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 30
    if bekukan:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
    for i, kol in enumerate(df.columns, start=1):
        contoh = df[kol].dropna().astype(str).head(200).str.len().max()
        lebar = max(len(str(kol)) + 4, int(contoh if pd.notna(contoh) else 8) + 2)
        ws.column_dimensions[get_column_letter(i)].width = min(max(lebar, 10), 42)


def baca_angka_kunci() -> pd.DataFrame:
    berkas = KELUARAN / "angka_kunci_storyboard.md"
    bagian, baris = "", []
    for teks in berkas.read_text(encoding="utf-8").splitlines():
        teks = teks.rstrip()
        if teks.startswith("## "):
            bagian = teks[3:].strip()
        elif teks.startswith("- "):
            baris.append({"bagian": bagian, "poin": teks[2:].strip()})
        elif teks.startswith("  ") and baris:  # lanjutan butir sebelumnya
            baris[-1]["poin"] += " " + teks.strip()
    df = pd.DataFrame(baris)
    df["poin"] = df["poin"].str.replace("**", "", regex=False).str.replace("`", "", regex=False)
    return df


NAMA_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
FASE_URUT = ["La Nina kuat", "La Nina", "Netral", "El Nino", "El Nino kuat"]


def seri_nasional(iso: str, d, ik, oni):
    """Deret bulanan nasional — definisi identik dengan notebook (sel 3)."""
    kasus = d[d["iso3"] == iso].groupby("periode")["kasus"].sum().rename("kasus")
    iklim = ik[ik["iso3"] == iso].set_index("periode")[["suhu_c", "hujan_mm"]]
    ens = oni.set_index("periode")[["oni", "fase"]]
    s = pd.concat([kasus, iklim, ens], axis=1)
    s.index = pd.PeriodIndex(s.index, freq="M")
    s = s.sort_index()
    ada = s[s["kasus"].notna()].index
    s = s.reindex(pd.period_range(ada.min(), ada.max(), freq="M"))
    s["tahun"], s["bulan"] = s.index.year, s.index.month
    return s


def tahun_lengkap(s, mulai: int = 2010) -> list[int]:
    n = s[s["kasus"].notna() & (s["tahun"] >= mulai)].groupby("tahun")["bulan"].nunique()
    return sorted(n[n == 12].index)


def lembar_grafik() -> dict[str, pd.DataFrame]:
    """Hitung ulang lembar siap-grafik dari data sumber di data/siap-sac/."""
    d = pd.read_csv(SIAP_SAC / "dengue_iklim_bulanan.csv", low_memory=False)
    ik = pd.read_csv(SIAP_SAC / "iklim_bulanan_asean.csv")
    oni = pd.read_csv(SIAP_SAC / "enso_oni_bulanan.csv")
    hasil: dict[str, pd.DataFrame] = {}

    # --- bulan puncak Indonesia (4 bulan dengan rata-rata kasus tertinggi) ---
    s_idn = seri_nasional("IDN", d, ik, oni)
    th_idn = tahun_lengkap(s_idn)
    puncak_idn = sorted(s_idn[s_idn["tahun"].isin(th_idn)].groupby("bulan")["kasus"].mean()
                        .nlargest(4).index)

    # --- 1. deret bulanan nasional IDN & THA ---
    deret = []
    for iso, nama in [("IDN", "Indonesia"), ("THA", "Thailand")]:
        s = seri_nasional(iso, d, ik, oni)
        s["suhu_jeda2"] = s["suhu_c"].shift(2)
        s["hujan_jeda1"] = s["hujan_mm"].shift(1)
        s["oni_jeda3"], s["oni_jeda4"] = s["oni"].shift(3), s["oni"].shift(4)
        s["fase_jeda4"] = s["fase"].shift(4)
        s = s[s.index >= "2010-01"].dropna(subset=["kasus"]).copy()
        p75 = s["kasus"].quantile(0.75)
        rer = s.groupby("bulan")["kasus"].transform("mean")
        sd = s.groupby("bulan")["kasus"].transform("std")
        s["kasus_anomali_z"] = (s["kasus"] - rer) / sd
        s["negara"] = nama
        s["periode"] = s.index.astype(str)
        s["tanggal"] = s.index.to_timestamp()
        s["nama_bulan"] = [NAMA_BULAN[b - 1] for b in s["bulan"]]
        s["ambang_P75"] = round(p75)
        s["bulan_puncak_kasus"] = (s["kasus"] >= p75).map({True: "Ya", False: "Tidak"})
        if iso == "IDN":
            alarm = s["bulan"].isin(puncak_idn) & (s["oni_jeda4"] >= 0.5)
            s["alarm_aturan_D"] = alarm.map({True: "Ya", False: "Tidak"})
            s["alarm_El_Nino"] = (s["oni_jeda4"] >= 0.5).map({True: "Ya", False: "Tidak"})
        else:  # Thailand memakai anomali suhu jeda-2, bukan ONI
            s["alarm_aturan_D"] = "n/a"
            s["alarm_El_Nino"] = (s["oni_jeda4"] >= 0.5).map({True: "Ya", False: "Tidak"})
        deret.append(s)
    kol = ["negara", "periode", "tanggal", "tahun", "bulan", "nama_bulan", "kasus",
           "kasus_anomali_z", "ambang_P75", "bulan_puncak_kasus", "alarm_aturan_D",
           "alarm_El_Nino", "fase_jeda4", "oni", "oni_jeda3", "oni_jeda4",
           "suhu_c", "suhu_jeda2", "hujan_mm", "hujan_jeda1"]
    dr = pd.concat(deret)[kol].reset_index(drop=True)
    num = dr.select_dtypes("number").columns
    dr[num] = dr[num].round(3)
    hasil["Deret bulanan IDN-THA"] = dr

    # --- 2. profil musiman (tahun lengkap 2010+) ---
    baris = []
    for iso, nama in [("IDN", "Indonesia"), ("THA", "Thailand")]:
        s = seri_nasional(iso, d, ik, oni)
        v = s[s["tahun"].isin(tahun_lengkap(s))]
        g = v.groupby("bulan").agg(kasus_rerata=("kasus", "mean"),
                                   hujan_rerata_mm=("hujan_mm", "mean"),
                                   suhu_rerata_c=("suhu_c", "mean"))
        th = tahun_lengkap(s)
        for b, r in g.iterrows():
            baris.append({"negara": nama, "bulan": b, "nama_bulan": NAMA_BULAN[b - 1],
                          "kasus_rerata": round(r["kasus_rerata"]),
                          "hujan_rerata_mm": round(r["hujan_rerata_mm"], 1),
                          "suhu_rerata_c": round(r["suhu_rerata_c"], 2),
                          "jendela_tahun_lengkap": f"{th[0]}-{th[-1]} (n={len(th)})"})
    hasil["Musiman IDN-THA"] = pd.DataFrame(baris)

    # --- 3. rata-rata kasus menurut fase ENSO jeda-4 (kartu as halaman 7) ---
    s = seri_nasional("IDN", d, ik, oni)
    s["fase_j4"] = s["fase"].shift(4)
    v = s[s.index >= "2010-01"].dropna(subset=["kasus", "fase_j4"])
    tab = v.groupby("fase_j4")["kasus"].agg(["mean", "count"]).reindex(FASE_URUT)
    netral = tab.loc["Netral", "mean"]
    hasil["Fase ENSO - rerata"] = pd.DataFrame({
        "fase_enso_jeda4": FASE_URUT,
        "urutan": range(1, 6),
        "rerata_kasus_per_bulan": tab["mean"].round().astype(int).values,
        "n_bulan": tab["count"].astype(int).values,
        "rasio_thd_netral": (tab["mean"] / netral).round(2).values,
        "cukup_data": ["Tidak (n=3)" if n < 10 else "Ya" for n in tab["count"]],
    })

    # --- 4. konsistensi antar provinsi Indonesia ---
    p = d[(d["iso3"] == "IDN") & (d["tahun"] >= 2010)].dropna(subset=["kasus", "fase_enso_jeda4"])
    baris = []
    for prov, g in p.groupby("provinsi"):
        nino = g["fase_enso_jeda4"].isin(["El Nino", "El Nino kuat"])
        if nino.sum() >= 12 and (~nino).sum() >= 24 and g.loc[~nino, "kasus"].mean() > 0:
            baris.append({"provinsi": str(prov).title(),
                          "rasio_nino_vs_lain": round(g.loc[nino, "kasus"].mean() /
                                                      g.loc[~nino, "kasus"].mean(), 2),
                          "n_bulan_nino": int(nino.sum()),
                          "arah": "Naik saat El Nino" if g.loc[nino, "kasus"].mean() >
                                  g.loc[~nino, "kasus"].mean() else "Tidak naik"})
    hasil["Konsistensi provinsi IDN"] = (pd.DataFrame(baris)
                                         .sort_values("rasio_nino_vs_lain", ascending=False)
                                         .reset_index(drop=True))

    # --- 5. paparan banjir kota (halaman 9) ---
    b = pd.read_csv(SIAP_SAC / "kota_asean_paparan_banjir.csv")
    piv = (b[b["indikator"] == "Penduduk terpapar banjir 100 tahunan"]
           .pivot_table(index=["negara", "kota", "penduduk_kota_2025"],
                        columns="tahun", values="nilai").reset_index())
    piv = piv.rename(columns={2020: "terpapar_2020", 2030: "terpapar_2030"})
    # pakai indikator persen bawaan GHSL (penyebut = penduduk tahun itu), bukan hitungan sendiri
    pers = (b[(b["indikator"] == "Persen penduduk terpapar banjir 100 tahunan") & (b["tahun"] == 2020)]
            .set_index(["negara", "kota"])["nilai"].rename("persen_2020"))
    piv = piv.join(pers, on=["negara", "kota"])
    piv["pertumbuhan_2020_2030_%"] = ((piv["terpapar_2030"] / piv["terpapar_2020"] - 1) * 100)
    piv = piv[piv["penduduk_kota_2025"] >= 500_000].nlargest(25, "terpapar_2020")
    piv[["penduduk_kota_2025", "terpapar_2020", "terpapar_2030"]] = \
        piv[["penduduk_kota_2025", "terpapar_2020", "terpapar_2030"]].round(0)
    piv[["persen_2020", "pertumbuhan_2020_2030_%"]] = piv[["persen_2020", "pertumbuhan_2020_2030_%"]].round(1)
    hasil["Kerentanan kota banjir"] = piv[["negara", "kota", "penduduk_kota_2025",
                                           "terpapar_2020", "persen_2020", "terpapar_2030",
                                           "pertumbuhan_2020_2030_%"]].reset_index(drop=True)

    # --- 6. WASH per negara, tahun terbaru (halaman 9) ---
    w = pd.read_csv(SIAP_SAC / "wash_rumahtangga_asean.csv")
    w = w[(w["wilayah"] == "Total") & w["persen"].notna()]
    pilih = [("Air minum", "Perpipaan", "air_perpipaan_%"),
             ("Air minum", "Minimal dasar", "air_minimal_dasar_%"),
             ("Air minum", "Dikelola aman", "air_dikelola_aman_%"),
             ("Sanitasi", "Minimal dasar", "sanitasi_minimal_dasar_%")]
    tab, tahun_maks = None, {}
    for layanan, ind, nama_kol in pilih:
        sub = w[(w["layanan"] == layanan) & (w["indikator"] == ind)]
        sub = sub.loc[sub.groupby("negara")["tahun"].idxmax()][["negara", "tahun", "persen"]]
        tahun_maks[nama_kol] = int(sub["tahun"].max())
        sub = sub.rename(columns={"persen": nama_kol}).drop(columns="tahun")
        tab = sub if tab is None else tab.merge(sub, on="negara", how="outer")
    tab.insert(1, "tahun_data", max(tahun_maks.values()))
    tab = tab[["negara", "tahun_data"] + [k for _, _, k in pilih]]
    hasil["WASH negara"] = tab.sort_values("air_perpipaan_%").round(1).reset_index(drop=True)
    return hasil


def buku_analisis() -> Path:
    keluar = TUJUAN / "ASEAN_DSE_hasil_analisis.xlsx"
    isi = []
    with pd.ExcelWriter(keluar, engine="openpyxl") as penulis:
        # tempat penampung; daftar isi ditulis ulang di akhir agar berada di depan
        pd.DataFrame({"a": [0]}).to_excel(penulis, sheet_name="Daftar isi", index=False)
        tulis(baca_angka_kunci(), penulis, "Angka kunci")
        penulis.book["Angka kunci"].column_dimensions["B"].width = 110
        for sel in penulis.book["Angka kunci"]["B"]:
            sel.alignment = Alignment(wrap_text=True, vertical="top")

        grafik = lembar_grafik()
        for asal, lembar, halaman, ket in URUTAN:
            if asal == "hitung":
                df, sumber = grafik[lembar], "dihitung ulang dari data/siap-sac/"
            else:
                nama = asal.split(":", 1)[1]
                df, sumber = rapikan(pd.read_csv(KELUARAN / f"{nama}.csv"), nama), f"{nama}.csv"
            tulis(df, penulis, lembar)
            isi.append({"lembar": lembar, "halaman": halaman, "isi": ket,
                        "baris": len(df), "kolom": df.shape[1], "berkas asal": sumber})

        del penulis.book["Daftar isi"]
        df_isi = pd.DataFrame(
            [{"lembar": "Angka kunci", "halaman": "semua",
              "isi": "Semua angka yang dikutip di storyboard, dikelompokkan per halaman.",
              "baris": "-", "kolom": "-", "berkas asal": "angka_kunci_storyboard.md"}] + isi)
        tulis(df_isi, penulis, "Daftar isi", bekukan=False)
        penulis.book.move_sheet("Daftar isi", offset=-(len(penulis.book.sheetnames) - 1))
        penulis.book["Daftar isi"].column_dimensions["C"].width = 95
        for sel in penulis.book["Daftar isi"]["C"]:
            sel.alignment = Alignment(wrap_text=True, vertical="top")
    return keluar


def buku_sac() -> list[tuple[str, int, int, float]]:
    folder = TUJUAN / "sac"
    folder.mkdir(parents=True, exist_ok=True)
    hasil = []
    for csv in sorted(SIAP_SAC.glob("*.csv")):
        df = pd.read_csv(csv, low_memory=False)
        keluar = folder / f"{csv.stem}.xlsx"
        with pd.ExcelWriter(keluar, engine="openpyxl") as penulis:
            tulis(df, penulis, csv.stem[:31])
        hasil.append((csv.stem, len(df), df.shape[1], keluar.stat().st_size / 1e6))
        print(f"  {keluar.name:<45} {len(df):>7,} baris  {keluar.stat().st_size/1e6:>5.1f} MB")
    return hasil


if __name__ == "__main__":
    TUJUAN.mkdir(parents=True, exist_ok=True)
    print("Buku kerja hasil analisis:")
    berkas = buku_analisis()
    print(f"  {berkas.relative_to(AKAR)}  ({berkas.stat().st_size/1e6:.1f} MB)")
    print("\nHimpunan data untuk SAC (satu berkas per himpunan data):")
    buku_sac()
    print("\nSelesai.")
