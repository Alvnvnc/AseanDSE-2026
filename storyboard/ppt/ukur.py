#!/usr/bin/env python3
"""ukur.py — ukur lebar teks untuk bangun-ppt.js.

Menerima JSON [{t, fs, bold}] dari stdin, mencetak JSON lebar (dalam bp) per
entri. Memakai Liberation Sans, yang metriknya identik dengan Arial — font yang
sama yang dipakai LibreOffice saat merender QA dan hampir semua PowerPoint di
mesin juri.
"""
import json
import sys

from PIL import ImageFont

REG = '/usr/share/fonts/liberation/LiberationSans-Regular.ttf'
BOLD = '/usr/share/fonts/liberation/LiberationSans-Bold.ttf'
SKALA = 8  # ukur pada 8x lalu bagi, supaya presisi pecahan tetap dapat

_cache = {}


def font(fs, bold):
    kunci = (round(fs * 100), bool(bold))
    if kunci not in _cache:
        _cache[kunci] = ImageFont.truetype(BOLD if bold else REG, max(1, round(fs * SKALA)))
    return _cache[kunci]


def main():
    items = json.load(sys.stdin)
    hasil = []
    for it in items:
        f = font(it['fs'], it.get('bold', False))
        hasil.append(f.getlength(it['t']) / SKALA)
    print(json.dumps(hasil))


if __name__ == '__main__':
    main()
