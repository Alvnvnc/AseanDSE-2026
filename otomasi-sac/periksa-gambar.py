#!/usr/bin/env python3
"""Cek cepat hasil tangkapan: ukuran, berat, dan apakah gambarnya kosong.

Grafik yang gagal render menghasilkan gambar nyaris polos — ketahuan dari
simpangan baku warna yang sangat kecil dan porsi piksel putih yang sangat besar.
"""
import subprocess
import sys
from pathlib import Path

FOLDER = Path("/home/alvn/Documents/Riset/AseanDSE-2026/storyboard/gambar-sac")
BATAS_MB = 2.0


def ukur(p: Path) -> dict:
    out = subprocess.run(
        ["magick", str(p), "-format", "%w %h %[fx:standard_deviation] %[fx:mean]", "info:"],
        capture_output=True, text=True).stdout.split()
    w, h, sd, rerata = int(out[0]), int(out[1]), float(out[2]), float(out[3])
    return {"w": w, "h": h, "sd": sd, "rerata": rerata, "mb": p.stat().st_size / 1048576}


gagal = []
print(f"{'berkas':26s} {'ukuran':>12s} {'MB':>6s} {'ragam':>7s}  catatan")
for p in sorted(FOLDER.glob("*.png")):
    m = ukur(p)
    catatan = []
    if m["sd"] < 0.02:
        catatan.append("NYARIS KOSONG")
    if m["w"] < 1600:
        catatan.append(f"lebar {m['w']} < 1600")
    if m["mb"] > BATAS_MB:
        catatan.append(f"{m['mb']:.1f} MB > {BATAS_MB} MB")
    if catatan:
        gagal.append(p.name)
    print(f"{p.stem:26s} {m['w']:5d}x{m['h']:<6d} {m['mb']:6.2f} {m['sd']:7.3f}  "
          f"{'; '.join(catatan) if catatan else 'ok'}")

print(f"\n{len(list(FOLDER.glob('*.png')))} gambar, {len(gagal)} perlu diperiksa ulang")
if gagal:
    print("  ->", ", ".join(gagal))
sys.exit(1 if gagal else 0)
