#!/usr/bin/env bash
# Bangun storyboard ASEAN DSE 2026 dan periksa kepatuhan aturan panitia.
set -uo pipefail
cd "$(dirname "$0")"

TEX=storyboard.tex
PDF=storyboard.pdf

echo "==> kompilasi (2 lintasan)"
for i in 1 2; do
  if ! pdflatex -interaction=nonstopmode -halt-on-error -file-line-error "$TEX" >/dev/null 2>&1; then
    echo "GAGAL pada lintasan $i. Kesalahan:"
    grep -E "^(\./)?storyboard\.tex:[0-9]+|^! " storyboard.log | head -20
    exit 1
  fi
done

[ -f "$PDF" ] || { echo "PDF tidak terbentuk."; exit 1; }

HAL=$(pdfinfo "$PDF" | awk '/^Pages:/{print $2}')
UKURAN=$(pdfinfo "$PDF" | awk '/^File size:/{print $3}')
DIM=$(pdfinfo "$PDF" | sed -n 's/^Page size: *//p' | head -1)
MB=$(awk -v b="$UKURAN" 'BEGIN{printf "%.2f", b/1048576}')

# Halaman referensi ditandai nomor "R1", "R2", ... pada \kaki — dihitung dari
# berkas .tex supaya cek di bawah tetap benar kalau referensinya lebih sehalaman.
REF=$(grep -oE '\}\{R[0-9]*\}' "$TEX" | wc -l)
[ "$REF" -lt 1 ] && REF=1
ISI=$((HAL-REF))

echo
echo "==> hasil"
printf '   halaman  : %s  (%s isi + %s referensi)\n' "$HAL" "$ISI" "$REF"
printf '   ukuran   : %s MB\n' "$MB"
printf '   dimensi  : %s\n' "$DIM"

echo
echo "==> cek aturan panitia"
if [ "$ISI" -le 15 ]; then
  echo "   [OK]    $ISI halaman isi, batas 15 (referensi tidak dihitung)"
else
  echo "   [GAGAL] $ISI halaman isi, batas 15"
fi
if awk -v m="$MB" 'BEGIN{exit !(m<=20)}'; then
  echo "   [OK]    $MB MB, batas 20 MB"
else
  echo "   [GAGAL] $MB MB, batas 20 MB"
fi

echo
echo "==> slot grafik SAC"
KOSONG=0; TERISI=0
while read -r nama; do
  [ -z "$nama" ] && continue
  if [ -f "gambar-sac/$nama.png" ]; then
    BYTES=$(stat -c%s "gambar-sac/$nama.png")
    if [ "$BYTES" -gt 2097152 ]; then
      echo "   [>2MB]  $nama.png  -- panitia membatasi 2 MB per gambar"
    else
      echo "   [terisi] $nama.png"
    fi
    TERISI=$((TERISI+1))
  else
    echo "   [kosong] $nama.png"
    KOSONG=$((KOSONG+1))
  fi
done < <(sed -e '/^[[:space:]]*%/d' -n -e 's/.*\\sacslot{[^}]*}{[^}]*}{[^}]*}{[^}]*}{\([^}]*\)}.*/\1/p' "$TEX")

echo
echo "   $TERISI terisi, $KOSONG masih placeholder."
[ "$KOSONG" -gt 0 ] && echo "   Ekspor grafik dari SAP Analytics Cloud (>=1600 px), simpan dengan nama di atas."

echo
echo "==> berkas siap submit"
# Panitia mewajibkan nama "NEGARA_NAMA TIM" (contoh: LAO PDR_TEAM DATA).
# Nama tim & negara dibaca dari storyboard.tex supaya tidak pernah beda.
TIM=$(sed -n 's/^\\newcommand{\\NamaTim}{\(.*\)}$/\1/p' "$TEX")
NEG=$(sed -n 's/^\\newcommand{\\Negara}{\(.*\)}$/\1/p' "$TEX")
if [ -n "$TIM" ] && [ -n "$NEG" ] && ! printf '%s' "$TIM$NEG" | grep -q '\['; then
  KIRIM="$(printf '%s_%s' "$NEG" "$TIM" | tr '[:lower:]' '[:upper:]').pdf"
  cp -f "$PDF" "$KIRIM"
  printf '   %s  (%s MB)\n' "$KIRIM" "$MB"
else
  echo "   Isi dulu \\NamaTim di $TEX, lalu jalankan ulang."
fi
