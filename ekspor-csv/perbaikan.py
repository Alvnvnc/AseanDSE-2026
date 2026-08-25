#!/usr/bin/env python3
"""Bikin ulang CSV yang tipenya salah waktu diimpor ke SAP Analytics Cloud.

Tiga masalah yang diperbaiki:
  1. `lag` perlu jadi DIMENSI (sumbu kolom heat map), bukan measure
     -> ditambah kolom teks `lag_label` ("L00".."L12", sudah urut alfabetis).
  2. Kolom persen terbaca sebagai dimensi -> nama dirapikan tanpa `%`
     dan nilainya ditulis ulang sebagai desimal bersih.
  3. Kolom uang berformat "US$1.47M" / "Rp 24-59 billion" -> ditambah kolom
     angka murni supaya bisa dipakai sebagai measure.

Keluaran: `ekspor-csv/perbaikan/*.csv` — impor ulang ke SAC (nama dataset baru).
Jalankan: python3 ekspor-csv/perbaikan.py
"""
import csv
import re
from pathlib import Path

SINI = Path(__file__).resolve().parent
KELUAR = SINI / "perbaikan"
KELUAR.mkdir(exist_ok=True)


def baca(nama):
    with (SINI / f"{nama}.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tulis(nama, baris, kolom):
    p = KELUAR / f"{nama}.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kolom)
        w.writeheader()
        w.writerows(baris)
    print(f"  {p.name:44s} {len(baris):4d} baris x {len(kolom)} kolom")


def bersih_persen(nama_baru, nama_asli):
    """Ganti nama kolom `x_%` -> `x_pct`, nilai tetap desimal."""
    baris = baca(nama_asli)
    peta = {k: (k[:-2] + "_pct" if k.endswith("_%") else k) for k in baris[0]}
    hasil = [{peta[k]: v for k, v in b.items()} for b in baris]
    tulis(nama_baru, hasil, list(peta.values()))


def tambah_lag_label(nama_baru, nama_asli):
    baris = baca(nama_asli)
    for b in baris:
        b["lag_label"] = f"L{int(float(b['lag'])):02d}"
    tulis(nama_baru, baris, list(baris[0].keys()))


def angka(teks):
    m = re.search(r"-?\d+(?:\.\d+)?", teks.replace(",", ""))
    return m.group(0) if m else ""


def rentang(teks):
    """'50-100%' -> ('50','100'); '44%' -> ('44','44'); '-' -> ('','')."""
    n = re.findall(r"\d+(?:\.\d+)?", teks)
    if not n:
        return "", ""
    return (n[0], n[-1]) if len(n) > 1 else (n[0], n[0])


print("Menulis CSV perbaikan:")

# 1. lag sebagai dimensi
tambah_lag_label("Lag correlation - national FIX", "Lag correlation - national")
tambah_lag_label("Lag correlation - anomaly FIX", "Lag correlation - anomaly")

# 2. kolom persen
bersih_persen("Trigger rules - evaluation FIX", "Trigger rules - evaluation")
bersih_persen("Trigger rules - out of sample FIX", "Trigger rules - out of sample")
bersih_persen("Rules vs endemic channel FIX", "Rules vs endemic channel")

# 3. EWS benchmark -> tambah kolom angka
baris = baca("EWS benchmark")
hasil = []
for b in baris:
    sl, sh = rentang(b["sensitivity"])
    pl, ph = rentang(b["specificity"])
    ql, qh = rentang(b["precision/PPV"])
    hasil.append({
        "system": b["system"], "source": b["source"],
        "sensitivity_text": b["sensitivity"], "specificity_text": b["specificity"],
        "precision_text": b["precision/PPV"],
        "sensitivity_low": sl, "sensitivity_high": sh,
        "specificity_low": pl, "specificity_high": ph,
        "precision_low": ql, "precision_high": qh,
    })
tulis("EWS benchmark FIX", hasil, list(hasil[0].keys()))

# 4. Monetary impact -> kolom angka juta USD
baris = baca("Monetary impact")
hasil = []
for b in baris:
    rp = re.findall(r"\d+", b["Rp/year (hospitalisation anchor)"])
    hasil.append({
        "scenario": b["scenario"],
        "cases_year": b["cases/year"],
        "conservative_usd_m": angka(b["conservative (avg episode, US$90)"]),
        "hospitalisation_low_usd_m": angka(b["hospitalisation low (US$316)"]),
        "hospitalisation_high_usd_m": angka(b["hospitalisation high (US$791)"]),
        "rp_low_billion": rp[0] if rp else "",
        "rp_high_billion": rp[1] if len(rp) > 1 else "",
        "rp_text": b["Rp/year (hospitalisation anchor)"],
    })
tulis("Monetary impact FIX", hasil, list(hasil[0].keys()))

print(f"\nSelesai -> {KELUAR}")


# ---------------------------------------------------------------------------
# Format panjang: satu kolom angka saja.
#
# SAC menebak sendiri kolom mana yang measure dan tebakannya tidak konsisten
# (pada `Trigger rules` dan `Monetary impact`, sebagian kolom persen tetap
# menjadi dimensi walau isinya angka bersih). Dengan format panjang hanya ada
# satu kolom angka, jadi tidak ada yang bisa salah dikira dimensi.
# ---------------------------------------------------------------------------

def panjang(nama_baru, nama_asli, kunci, metrik, nama_nilai="value", ubah=None):
    """kunci: kolom yang tetap jadi dimensi. metrik: kolom angka yang dilipat."""
    baris = baca(nama_asli)
    hasil = []
    for b in baris:
        for m in metrik:
            v = b[m]
            if v == "":
                continue
            hasil.append({**{k: b[k] for k in kunci},
                          "metric": m,
                          nama_nilai: ubah(v) if ubah else v})
    tulis(nama_baru, hasil, kunci + ["metric", nama_nilai])


print("\nFormat panjang:")
panjang("Trigger rules - evaluation LONG", "Trigger rules - evaluation",
        ["rule"], ["alarm_coverage_%", "sensitivity_%", "precision_%"])
panjang("Trigger rules - out of sample LONG", "Trigger rules - out of sample",
        ["country", "period"], ["coverage_%", "sensitivity_%", "precision_%"])

# biaya: ditulis dalam ribuan US$ (bilangan bulat) supaya pasti terbaca measure
baris = baca("Monetary impact")
hasil = []
for b in baris:
    for label, kolom in [("hospitalisation low (US$316)", "hospitalisation low (US$316)"),
                         ("hospitalisation high (US$791)", "hospitalisation high (US$791)"),
                         ("conservative (avg episode, US$90)",
                          "conservative (avg episode, US$90)")]:
        juta = float(angka(b[kolom]))
        hasil.append({"scenario": b["scenario"],
                      "metric": label.split(" (")[0],
                      "usd_thousand": str(int(round(juta * 1000)))})
tulis("Monetary impact LONG", hasil, ["scenario", "metric", "usd_thousand"])


# Bar bertingkat h13: menumpuk "low" dan "high" berarti menjumlahkan dua
# perkiraan yang saling menggantikan — keliru. Yang benar: batas bawah sebagai
# dasar, lalu selisihnya ke batas atas, sehingga tinggi total = batas atas.
baris = baca("Monetary impact")
hasil = []
for b in baris:
    rendah = float(angka(b["hospitalisation low (US$316)"])) * 1000
    tinggi = float(angka(b["hospitalisation high (US$791)"])) * 1000
    hasil.append({"scenario": b["scenario"], "metric": "hospitalisation low",
                  "usd_thousand": str(int(round(rendah)))})
    hasil.append({"scenario": b["scenario"], "metric": "extra up to high",
                  "usd_thousand": str(int(round(tinggi - rendah)))})
tulis("Monetary impact STACK", hasil, ["scenario", "metric", "usd_thousand"])


# ---------------------------------------------------------------------------
# Versi ringkas untuk dua widget Table di dek.
#
# Slot tabel di dek hanya 270x348 bp (potret). Label panjang membuat tabelnya
# melebar jadi pita tipis yang tak terbaca, jadi teksnya dipendekkan tanpa
# mengubah isinya — sumber lengkap tetap ada di kolom `source` dan di baris
# sumber pada halaman dek.
# ---------------------------------------------------------------------------

RINGKAS_SISTEM = {
    "Our rule D vs P75 (out-of-sample test 2017-2024)": "Rule D vs P75 (blind test)",
    "Our rule D vs endemic channel (2010-2024)": "Rule D vs endemic channel",
    "Range across 17 dengue EWS (systematic review)": "17 published EWS (range)",
    "WHO-TDR EWARS, Mexico (dengue)": "WHO-TDR EWARS, Mexico",
    "EWARS-csd, 11 Colombian cities (median)": "EWARS-csd, Colombia",
}

baris = baca("EWS benchmark")
hasil = []
for b in baris:
    sl, sh = rentang(b["sensitivity"])
    ql, qh = rentang(b["precision/PPV"])
    hasil.append({
        "system": RINGKAS_SISTEM.get(b["system"], b["system"]),
        "source": b["source"],
        "sensitivity_low": sl, "sensitivity_high": sh,
        "precision_low": ql, "precision_high": qh,
    })
tulis("EWS benchmark TABLE", hasil, list(hasil[0].keys()))

BULAN_SINGKAT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def bulan_pendek(ym):
    """'2009-12' -> \"Dec '09\" (apostrof mencegah SAC membacanya sebagai tanggal)."""
    t, b = ym.split("-")
    return f"{BULAN_SINGKAT[int(b) - 1]} '{t[2:]}"


baris = baca("El Nino episodes - lead time")
hasil = []
for b in baris:
    mulai, akhir = b["episode"].split("..")
    hasil.append({
        "episode": f"{mulai[:4]}/{akhir[2:4]}",
        "alarm": bulan_pendek(b["alarm_fires"]),
        "cases_cross": bulan_pendek(b["cases_cross_p75"]),
        "lead_time_months": b["lead_time_months"],
    })
tulis("El Nino lead time TABLE", hasil, list(hasil[0].keys()))
