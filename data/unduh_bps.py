#!/usr/bin/env python3
"""Mengunduh penduduk provinsi dari WebAPI BPS.

www.bps.go.id dilindungi Cloudflare (tantangan interaktif) sehingga tidak bisa
diambil skrip; webapi.bps.go.id bisa, tapi butuh kunci gratis dari
https://webapi.bps.go.id/developer/

Pakai:
    BPS_KEY=xxxx python3 unduh_bps.py            # unduh + simpan mentah
    BPS_KEY=xxxx python3 unduh_bps.py --telusuri # hanya lihat daftar variabel

Kunci juga dibaca otomatis dari berkas .env di akar proyek
(baris BPS_KEY=... atau BPS_API_KEY=...), jadi cukup: python3 data/unduh_bps.py

Keluaran: data/penduduk/bps_penduduk_provinsi.json (respons mentah, untuk sitasi)
"""
import json
import os
import sys
import urllib.request

AKAR = os.path.dirname(os.path.abspath(__file__))
TUJUAN = os.path.join(AKAR, "penduduk")
DASAR = "https://webapi.bps.go.id/v1/api/list"

# "Jumlah Penduduk Hasil Proyeksi menurut Provinsi dan Jenis Kelamin".
# Bisa ditimpa lewat BPS_VAR bila BPS mengganti ID-nya.
VAR = os.environ.get("BPS_VAR", "1886")
DOMAIN = "0000"  # 0000 = nasional; provinsi muncul sebagai "vervar"


def kunci():
    k = os.environ.get("BPS_KEY", "").strip() or os.environ.get("BPS_API_KEY", "").strip()
    if not k:
        env = os.path.join(os.path.dirname(AKAR), ".env")
        if os.path.exists(env):
            with open(env, encoding="utf-8") as f:
                for baris in f:
                    nama, _, nilai = baris.strip().partition("=")
                    if nama in ("BPS_KEY", "BPS_API_KEY") and nilai:
                        k = nilai.strip().strip('"').strip("'")
    if not k:
        sys.exit("BPS_KEY belum diisi. Daftar gratis di https://webapi.bps.go.id/developer/\n"
                 "lalu jalankan:  BPS_KEY=<kunci> python3 unduh_bps.py")
    return k


# WAF BPS ("Perimeter WAF Block") menolak User-Agent bawaan urllib dengan 403 —
# kirim UA peramban biasa supaya permintaan sampai ke API-nya.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def ambil(param):
    url = DASAR + "?" + "&".join(f"{k}={v}" for k, v in param.items())
    permintaan = urllib.request.Request(url, headers={"User-Agent": UA,
                                                      "Accept": "application/json"})
    with urllib.request.urlopen(permintaan, timeout=120) as r:
        d = json.loads(r.read().decode("utf-8"))
    if str(d.get("status", "")).lower() not in ("ok", "1", "true"):
        sys.exit(f"BPS menolak permintaan: {d.get('message') or d}")
    return d


def telusuri():
    """Daftar variabel bertema kependudukan, untuk memastikan ID yang benar."""
    hal = 1
    while True:
        d = ambil({"model": "var", "domain": DOMAIN, "lang": "ind",
                   "key": kunci(), "page": str(hal)})
        for v in d.get("data", [[], []])[1]:
            label = str(v.get("title") or v.get("label") or "")
            if "penduduk" in label.lower():
                print(f'  var {v.get("var_id") or v.get("val")}: {label}')
        total = d.get("data", [{}])[0].get("pages", 1)
        if hal >= total:
            break
        hal += 1


def unduh():
    k = kunci()

    # API kini MEWAJIBKAN parameter th (ID tahun, bukan tahun literal!) dan
    # membatasi maksimal 3 tahun per permintaan — jadi: tanya dulu tahun yang
    # tersedia, ambil per gugus <= 3, lalu gabungkan jadi satu JSON.
    d_th = ambil({"model": "th", "domain": DOMAIN, "var": VAR, "key": k})
    peta = {}
    for t in d_th.get("data", [[], []])[1]:
        try:
            peta[int(t["th"])] = int(t["th_id"])
        except (KeyError, TypeError, ValueError):
            continue
    if not peta:
        sys.exit(f"BPS tidak mengembalikan daftar tahun untuk var {VAR}")

    rentang = os.environ.get("BPS_TAHUN", "2018-2024")
    awal, _, akhir = rentang.partition("-")
    mau = [th for th in sorted(peta) if int(awal) <= th <= int(akhir or awal)]
    if not mau:
        sys.exit(f"var {VAR} tidak punya tahun dalam rentang {rentang}; "
                 f"tersedia: {sorted(peta)} (atur lewat BPS_TAHUN=awal-akhir)")
    print(f"var {VAR}: tahun tersedia {sorted(peta)}, diambil {mau}")

    d = None
    for i in range(0, len(mau), 3):
        gugus = mau[i:i + 3]
        potong = ambil({"model": "data", "domain": DOMAIN, "var": VAR,
                        "lang": "ind", "key": k,
                        "th": ";".join(str(peta[t]) for t in gugus)})
        if potong.get("data-availability") != "available":
            print(f"  ! tahun {gugus}: {potong.get('data-availability')} — dilewati")
            continue
        if d is None:
            d = potong
        else:
            d["datacontent"].update(potong.get("datacontent", {}))
            ada = {t["val"] for t in d["tahun"]}
            d["tahun"] += [t for t in potong.get("tahun", []) if t["val"] not in ada]
    if d is None:
        sys.exit("tidak ada satu pun gugus tahun yang mengembalikan data")

    os.makedirs(TUJUAN, exist_ok=True)
    berkas = os.path.join(TUJUAN, "bps_penduduk_provinsi.json")
    with open(berkas, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    print(f"tersimpan: {berkas}")
    print(f"  provinsi : {len(d.get('vervar', []))}")
    print(f"  tahun    : {[t.get('label') for t in d.get('tahun', [])]}")
    print(f"  turvar   : {[t.get('label') for t in d.get('turvar', [])]}")
    print(f"  nilai    : {len(d.get('datacontent', {}))}")


if __name__ == "__main__":
    telusuri() if "--telusuri" in sys.argv else unduh()
