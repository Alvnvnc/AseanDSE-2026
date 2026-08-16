#!/usr/bin/env bash
# Mengunduh ulang semua sumber mentah. Berkas yang sudah ada dilewati.
set -euo pipefail
AKAR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$AKAR"/{kesehatan,iklim,wash,kota,sampah,siap-sac}

# ---- OpenDengue V1.3 (figshare, DOI 10.6084/m9.figshare.24259573.v4) ----
cd "$AKAR/kesehatan"
[ -f Spatial_extract_V1_3.zip ] || curl -L -o Spatial_extract_V1_3.zip \
  "https://ndownloader.figshare.com/files/54854153"
[ -f National_extract_V1_3.zip ] || curl -L -o National_extract_V1_3.zip \
  "https://ndownloader.figshare.com/files/54854150"
python3 - <<'PY'
import zipfile, os
for z, d in [("Spatial_extract_V1_3.zip", "spatial"), ("National_extract_V1_3.zip", "national")]:
    if not os.path.isdir(d):
        zipfile.ZipFile(z).extractall(d)
PY

# ---- Iklim bulanan ERA5 0,25° via API World Bank CCKP ----
# Pola dataset: era5-x0.25_timeseries_{var}_timeseries_monthly_1950-2024_mean_historical_era5_x0.25_mean
cd "$AKAR/iklim"
for iso in BRN KHM IDN LAO MYS MMR PHL SGP THA VNM; do
  for var in tas pr; do
    f="${var}_${iso}.json"
    [ -f "$f" ] || curl -s -o "$f" \
      "https://cckpapi.worldbank.org/cckp/v1/era5-x0.25_timeseries_${var}_timeseries_monthly_1950-2024_mean_historical_era5_x0.25_mean/${iso}?_format=json"
  done
done

# ---- Indeks ENSO / ONI bulanan (NOAA PSL, Nino 3.4) ----
[ -f oni_nino34.txt ] || curl -L -o oni_nino34.txt \
  "https://psl.noaa.gov/data/correlation/oni.data"

# ---- WASH rumah tangga (WHO/UNICEF JMP, rilis 2025) ----
cd "$AKAR/wash"
[ -f jmp_household_wld.xlsx ] || curl -L -o jmp_household_wld.xlsx \
  "https://washdata.org/data/country/WLD/household/download"
[ -f jmp_healthcare_wld.xlsx ] || curl -L -o jmp_healthcare_wld.xlsx \
  "https://washdata.org/data/country/WLD/healthcare/download"

# ---- Kualitas udara (WHO Ambient Air Quality Database V6.1, 31 Jan 2024) ----
# V6.1 adalah rilis terbaru yang benar-benar ada; tidak ada v7/v8.
cd "$AKAR/kota"
[ -f who_aaq_v6_1_2024.xlsx ] || curl -L -o who_aaq_v6_1_2024.xlsx \
  "https://cdn.who.int/media/docs/default-source/air-pollution-documents/air-quality-and-health/who_ambient_air_quality_database_version_2024_(v6.1).xlsx?sfvrsn=c504c0cd_3&download=true"

# ---- Paparan banjir kota (GHS-UCDB R2024A V1.2, JRC) — 264 MB, unduhan lambat ----
[ -f GHS_UCDB_GLOBE_R2024A_V1_2.zip ] || curl -L -o GHS_UCDB_GLOBE_R2024A_V1_2.zip \
  "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_UCDB_GLOBE_R2024A/GHS_UCDB_GLOBE_R2024A/V1-2/GHS_UCDB_GLOBE_R2024A_V1_2.zip"
python3 - <<'PY'
import zipfile, os
# hanya GeoPackage yang diekstrak; XLSX 175 MB tidak dipakai
if not os.path.exists("GHS_UCDB_GLOBE_R2024A.gpkg"):
    with zipfile.ZipFile("GHS_UCDB_GLOBE_R2024A_V1_2.zip") as z:
        z.extract("GHS_UCDB_GLOBE_R2024A.gpkg")
        z.extract("readme_V1_2.txt")
PY

# ---- Sampah kab/kota (SIPSN, KLH) ----
# Datanya tabel HTML statis di beranda, bukan API — halamannya disimpan apa adanya.
cd "$AKAR/sampah"
[ -f sipsn_beranda.html ] || curl -L -o sipsn_beranda.html \
  "https://sampahnasional.kemenlh.go.id/"

# ---- Penduduk provinsi Indonesia (BPS, proyeksi SP2020) ----
# www.bps.go.id memakai tantangan Cloudflare sehingga tidak bisa diambil skrip.
# webapi.bps.go.id bisa, tapi perlu kunci gratis: https://webapi.bps.go.id/developer/
mkdir -p "$AKAR/penduduk"
cd "$AKAR/penduduk"
# Cadangan tanpa kunci: halaman BPS yang terlanjur diarsipkan Wayback.
# Proyeksi SP2010, 2018-2020, 34 provinsi.
[ -f bps_penduduk_provinsi_arsip_2018-2020.html ] || curl -L -o bps_penduduk_provinsi_arsip_2018-2020.html \
  "http://web.archive.org/web/20221204025957/https://www.bps.go.id/indicator/12/1886/1/jumlah-penduduk-hasil-proyeksi-menurut-provinsi-dan-jenis-kelamin.html"

if [ -n "${BPS_KEY:-}" ]; then
  python3 "$AKAR/unduh_bps.py"   # seri utama: SP2020, 2020-2024, 38 provinsi
else
  echo "Lewat: penduduk BPS seri SP2020 (BPS_KEY belum diisi) — memakai arsip 2018-2020."
  echo "       Daftar gratis di https://webapi.bps.go.id/developer/ lalu:"
  echo "       BPS_KEY=<kunci> bash $AKAR/unduh.sh"
fi

echo "Selesai. Jalankan: python3 $AKAR/siapkan.py"
