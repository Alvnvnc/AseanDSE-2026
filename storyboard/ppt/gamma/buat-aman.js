#!/usr/bin/env node
/*
 * buat-aman.js — versi "aman impor" dari dek Gamma.
 *
 * Sebagian aplikasi (Canva, Google Slides, WPS Office, PowerPoint lama) membuang
 * font ter-embed dan elemen SVG saat mengimpor PPTX, sehingga dek tampak kosong.
 * Versi ini mengganti tiap slide dengan SATU gambar penuh hasil render PDF
 * (200 dpi) sehingga tampil identik di aplikasi mana pun. Catatan pembicara
 * tetap diikutsertakan. Konsekuensinya: teks tidak lagi bisa disunting per elemen.
 *
 * Pakai:
 *   pdftoppm -jpeg -r 200 -jpegopt quality=90 ../../INDONESIA_SWALLOWGANK-gamma.pdf /tmp/opencode/aman/s
 *   node buat-aman.js /tmp/opencode/aman
 */
const fs = require('fs');
const path = require('path');
const PptxGenJS = require('../node_modules/pptxgenjs');

const base = __dirname;
const dir = process.argv[2] || '/tmp/opencode/aman';
const out = process.argv[3] || path.join(base, '..', '..', 'INDONESIA_SWALLOWGANK-gamma-aman.pptx');
const catatan = JSON.parse(fs.readFileSync(path.join(base, 'catatan.json'), 'utf8'));

const p = new PptxGenJS();
p.layout = 'LAYOUT_WIDE';
p.author = 'Swallowgank — Institut Teknologi Sepuluh Nopember';
p.title = 'Four Months\u2019 Notice — Pawang (versi aman)';

for (let i = 1; i <= catatan.length; i++) {
  const s = p.addSlide();
  const f = path.join(dir, `s-${String(i).padStart(2, '0')}.jpg`);
  s.addImage({ path: f, x: 0, y: 0, w: 13.3333, h: 7.5 });
  const n = catatan[i - 1];
  if (n && n.length) s.addNotes(n.join('\n'));
}
p.writeFile({ fileName: out }).then(() => console.log('OK ->', path.relative(process.cwd(), out)));
