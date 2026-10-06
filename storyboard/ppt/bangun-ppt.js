#!/usr/bin/env node
/*
 * bangun-ppt.js — port dek storyboard (LaTeX, kanvas 960x540 bp) ke PowerPoint 16:9.
 *
 * Kanvas LaTeX 960x540 bp = 13,333x7,5 inci = persis layout "WIDE" PowerPoint,
 * jadi 1 bp = 1/72 inci dan semua koordinat storyboard.tex bisa dipakai apa
 * adanya. Teks diambil dari storyboard.tex (sudah final), grafik dari
 * gambar-siap/ (rasionya dibaca dari gambar-siap/rasio.tex, sumber yang sama
 * yang dipakai \sacslot di LaTeX).
 *
 * Jalankan:  node bangun-ppt.js
 * Hasil:     ../INDONESIA_SWALLOWGANK.pptx  (+ cetak instruksi ekspor PDF)
 */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const PptxGenJS = require('pptxgenjs');

// ------------------------------------------------------------------ ukur teks
// Lebar teks diukur lewat PIL + Liberation Sans (metrik sama dengan Arial),
// supaya tinggi daftar dan lebar chip cocok dengan hasil render PowerPoint.
const _ukurCache = new Map();
let _py = null;
function cariPython() {
  if (_py) return _py;
  const kandidat = [process.env.PYTHON,
    path.join(__dirname, '..', '..', '.venv', 'bin', 'python'), 'python3'].filter(Boolean);
  for (const py of kandidat) {
    try { execFileSync(py, ['-c', 'import PIL'], { stdio: 'ignore' }); _py = py; return py; } catch { /* coba berikutnya */ }
  }
  throw new Error('Python dengan Pillow tidak ditemukan — ukur.py membutuhkannya.');
}
function ukur(teks, fs, bold = false) {
  const kunci = (bold ? 'B' : 'R') + fs + '|' + teks;
  if (_ukurCache.has(kunci)) return _ukurCache.get(kunci);
  const keluar = execFileSync(cariPython(), [path.join(__dirname, 'ukur.py')], {
    input: JSON.stringify([{ t: teks, fs, bold }]),
    encoding: 'utf8',
  });
  const w = JSON.parse(keluar)[0];
  _ukurCache.set(kunci, w);
  return w;
}
// jumlah baris hasil word-wrap pada lebar wBp (meniru LibreOffice/PowerPoint)
function bungkus(teks, wBp, fs) {
  let total = 0;
  for (const para of String(teks).replace(/[*~]/g, '').split('\n')) {
    const kata = para.split(/\s+/).filter(Boolean);
    if (!kata.length) { total += 1; continue; }
    let baris = 1, kini = '';
    for (const k of kata) {
      const coba = kini ? kini + ' ' + k : k;
      if (ukur(coba, fs) <= wBp || !kini) kini = coba;
      else { baris += 1; kini = k; }
    }
    total += baris;
  }
  return total;
}

// ------------------------------------------------------------------ rasio gambar
function bacaRasio() {
  const berkas = path.join(__dirname, '..', 'gambar-siap', 'rasio.tex');
  const t = fs.readFileSync(berkas, 'utf8');
  const out = {};
  for (const m of t.matchAll(/rasio@([\w-]+)\\endcsname\{([0-9.]+)\}/g)) {
    out[m[1]] = parseFloat(m[2]);
  }
  return out;
}
const RASIO = bacaRasio();
const GAMBAR = (nama) => path.join(__dirname, '..', 'gambar-siap', nama + '.png');

// ------------------------------------------------------------------ konstanta
const W = 960, H = 540, ML = 36, MR = 924, CW = 888, CTOP = 424;
const COL = { accent: '2A78D6', alarm: 'E8833A', peak: 'C53232', muted: '8A8F98',
  ink: '14202E', soft: 'F2F5F9', line: 'C9D3E0', deep: '0E2340', white: 'FFFFFF',
  // warna hasil campur opacity di atas latar (kartu deep / putih):
  deep4: '2D4059',      // putih 13% di atas deep  (angka "4" besar)
  deepSub: '737F90',    // putih 42% di atas deep  (keterangan sampul)
  deepLine: '566579',   // putih 30% di atas deep  (garis sampul)
};
const FS = { nav: 9, eye: 10, head: 25, sub: 15.5, body: 13.5, sml: 10.5, tny: 8.5, kpi: 44, kpimid: 30 };
const LHF = { nav: 11, eye: 12, head: 29, sub: 20, body: 18.5, sml: 14, tny: 11, kpi: 48, kpimid: 34 };
const FONT = 'Arial';
const IN = (v) => v / 72;            // bp -> inci
const TOP = (v) => (H - v) / 72;     // y dari bawah -> inci tepi ATAS
const BOT = (v) => (H - v) / 72;     // y dari bawah -> inci tepi BAWAH

// ------------------------------------------------------------------ runs teks
// Marka: **tebal**  *miring*  ~~redup~~  \n = baris baru dalam paragraf
function runs(text, base = {}) {
  const out = [];
  // apostrof tipografis: LaTeX otomatis mengubah ' menjadi ’
  text = String(text).replace(/'/g, '\u2019');
  const push = (t, st) => { if (t !== '') out.push({ text: t, options: { ...base, ...st } }); };
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|~~[^~]+~~|\n\n|\n)/g;
  let m, last = 0;
  while ((m = re.exec(text))) {
    if (m.index > last) push(text.slice(last, m.index), {});
    const s = m[0];
    if (s === '\n' || s === '\n\n') {
      if (out.length) out[out.length - 1].options.breakLine = true;
      else push(' ', { breakLine: true });
      if (s === '\n\n') push(' ', { breakLine: true });
    } else if (s.startsWith('**')) push(s.slice(2, -2), { bold: true });
    else if (s.startsWith('~~')) push(s.slice(2, -2), { color: COL.muted });
    else push(s.slice(1, -1), { italic: true });
    last = m.index + s.length;
  }
  if (last < text.length) push(text.slice(last), {});
  return out;
}

// perkiraan lebar/tinggi teks (untuk mengukur chip, dan tinggi kotak)
function lebarTeks(s, fs, bold = false) {
  let w = 0;
  for (const ch of s) {
    if ('iljI.,;:!|`\' '.includes(ch)) w += 0.30;
    else if ('mwMW'.includes(ch)) w += 0.85;
    else if (ch === ' ') w += 0.28;
    else w += bold ? 0.57 : 0.53;
  }
  return w * fs;
}
function jumlahBaris(s, wBp, fs, bold) {
  let n = 0;
  for (const para of String(s).split('\n')) {
    n += Math.max(1, Math.ceil(lebarTeks(para.replace(/[*~]/g, ''), fs, bold) / wBp));
  }
  return n;
}

// ------------------------------------------------------------------ primitif
function tNW(s, bx, by, w, isi, o = {}) {          // jangkar kiri-atas pada (bx,by)
  const fs = o.fs ?? FS.body, lh = o.lh ?? LHF.body;
  const h = o.h ?? Math.max(20, jumlahBaris(isi, w, fs, o.bold) * lh + 8);
  s.addText(runs(isi, { fontFace: FONT, fontSize: fs, color: o.color ?? COL.ink,
    ...(o.bold ? { bold: true } : {}), ...(o.italic ? { italic: true } : {}) }),
    { x: IN(bx), y: TOP(by), w: IN(w), h: IN(h), align: o.align ?? 'left',
      valign: 'top', margin: 0, lineSpacing: lh, ...(o.cs ? { charSpacing: o.cs } : {}) });
}
function tSW(s, bx, byBottom, w, isi, o = {}) {    // jangkar kiri-bawah: tumbuh ke atas
  const fs = o.fs ?? FS.sml, lh = o.lh ?? LHF.sml;
  const h = Math.max(14, jumlahBaris(isi, w, fs, o.bold) * lh + 6);
  s.addText(runs(isi, { fontFace: FONT, fontSize: fs, color: o.color ?? COL.ink,
    ...(o.bold ? { bold: true } : {}) }),
    { x: IN(bx), y: BOT(byBottom) - IN(h), w: IN(w), h: IN(h), align: o.align ?? 'left',
      valign: 'bottom', margin: 0, lineSpacing: lh });
}
function tSE(s, bxKanan, byBottom, w, isi, o = {}) { // jangkar kanan-bawah
  const fs = o.fs ?? FS.tny, lh = o.lh ?? LHF.tny;
  const h = lh + 6;
  s.addText(runs(isi, { fontFace: FONT, fontSize: fs, color: o.color ?? COL.muted,
    ...(o.bold ? { bold: true } : {}) }),
    { x: IN(bxKanan - w), y: BOT(byBottom) - IN(h), w: IN(w), h: IN(h), align: 'right',
      valign: 'bottom', margin: 0, lineSpacing: lh });
}
function tMid(s, bx, by, w, isi, o = {}) {         // tengah-kiri vertikal pada y
  const fs = o.fs ?? FS.tny, lh = o.lh ?? LHF.tny;
  const h = lh + 6;
  s.addText(runs(isi, { fontFace: FONT, fontSize: fs, color: o.color ?? COL.ink,
    ...(o.bold ? { bold: true } : {}) }),
    { x: IN(bx), y: TOP(by) - IN(h / 2), w: IN(w), h: IN(h), align: o.align ?? 'left',
      valign: 'middle', margin: 0, lineSpacing: lh });
}
function rect(s, bx, byTop, w, h, o = {}) {
  s.addShape(o.round ? 'roundRect' : 'rect', {
    x: IN(bx), y: TOP(byTop), w: IN(w), h: IN(h),
    fill: o.fill ? { color: o.fill, ...(o.transparency ? { transparency: o.transparency } : {}) }
      : { color: 'FFFFFF', transparency: 100 },
    line: o.line ? { color: o.line, width: o.lw ?? 0.6, ...(o.transparency ? { transparency: o.transparency } : {}) } : { type: 'none' },
    ...(o.round ? { rectRadius: IN(o.radius ?? 4) } : {}) });
}
function garisH(s, x1, y, x2, o = {}) {
  s.addShape('line', { x: IN(x1), y: TOP(y), w: IN(x2 - x1), h: 0,
    line: { color: o.color ?? COL.line, width: o.width ?? 0.6, ...(o.transparency ? { transparency: o.transparency } : {}) } });
}
function garisV(s, x, y1, y2, o = {}) {
  s.addShape('line', { x: IN(x), y: TOP(y1), w: 0, h: IN(y1 - y2),
    line: { color: o.color ?? COL.line, width: o.width ?? 0.6 } });
}

// ------------------------------------------------------------------ komponen dek
function navbar(s, aktif) {
  garisH(s, ML, 506, MR);
  const lbl = ['Problem', 'Method', 'Analysis', 'Synthesis', 'Solution', 'Viability', 'Impact', 'Limits'];
  lbl.forEach((nama, i) => {
    const cx = 36 + 111 * (i + 0.5);
    const on = (i + 1) === aktif;
    s.addText(runs(nama, { fontFace: FONT, fontSize: FS.nav, color: on ? COL.accent : COL.muted, bold: on }),
      { x: IN(cx - 50), y: TOP(517) - IN(8), w: IN(100), h: IN(16), align: 'center',
        valign: 'middle', margin: 0, lineSpacing: LHF.nav });
    if (on) garisH(s, cx - 32, 506, cx + 32, { color: COL.accent, width: 2.2 });
  });
}
function kepala(s, eyebrow, judul) {
  tNW(s, ML, 490, CW, eyebrow.toUpperCase(), { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  tNW(s, ML, 475, CW, judul, { fs: FS.head, lh: LHF.head, color: COL.ink, bold: true });
}
function kaki(s, sumber, nomor) {
  garisH(s, ML, 50, MR);
  tSW(s, ML, 12, 780, sumber, { fs: FS.tny, lh: LHF.tny, color: COL.muted });
  tSE(s, MR, 12, 60, String(nomor), { fs: FS.tny, lh: LHF.tny, bold: true });
}
function kpi(s, bx, byTop, w, h, angka, label, warna) {
  rect(s, bx, byTop, w, h, { round: true, radius: 4, fill: warna });
  tNW(s, bx + 14, byTop - 10, w - 28, angka, { fs: FS.kpi, lh: LHF.kpi, color: 'FFFFFF', bold: true });
  tSW(s, bx + 14, byTop - h + 12, w - 28, label, { fs: FS.sml, lh: LHF.sml, color: 'FFFFFF' });
}
function chip(s, bx, byTop, warna, isi, fs = FS.tny) {
  const w = ukur(isi, fs, true) + 24, h = fs * 1.45 + 8;
  rect(s, bx, byTop, w, h, { round: true, radius: 3, fill: warna });
  tMid(s, bx + 12, byTop - h / 2 + 1, w - 12, isi, { fs, lh: fs * 1.4, color: 'FFFFFF', bold: true });
  return { w, h };
}
function sdgchips(s, bx, byTop, daftar) {
  let x = bx;
  for (const [isi, warna] of daftar) {
    const w = ukur(isi, FS.sml, true) + 20, h = FS.sml * 1.45 + 8;
    rect(s, x, byTop, w, h, { round: true, radius: 3, fill: warna });
    tMid(s, x + 10, byTop - h / 2 + 1, w - 20, isi, { fs: FS.sml, lh: LHF.sml, color: 'FFFFFF', bold: true });
    x += w + 6;
  }
}
function slot(s, { kiri, kanan, y, tinggi, nama, judul }) {
  const w = tinggi * RASIO[nama];
  const bx = kanan ? kanan - w : kiri;
  tNW(s, bx, y, w, judul, { fs: FS.sml, lh: LHF.sml, color: COL.ink, bold: true });
  const yGambar = y - 16;
  s.addImage({ path: GAMBAR(nama), x: IN(bx), y: TOP(yGambar), w: IN(w), h: IN(tinggi) });
  rect(s, bx, yGambar, w, tinggi, { round: true, radius: 3, line: COL.line });
}
function simpulan(s, bx, y, w, isi) {
  garisV(s, bx, y, y - 24, { color: COL.alarm, width: 2.4 });
  tNW(s, bx + 12, y, w - 14, isi, { fs: FS.sml, lh: LHF.sml, color: COL.ink });
}
function kutip(s, bx, yTop, yBot, w, isi) {
  garisV(s, bx, yTop, yBot, { color: COL.alarm, width: 3 });
  tNW(s, bx + 14, yTop, w, isi, { fs: 14, lh: 19, color: COL.ink, bold: true });
}
function butir(s, bx, byTop, w, daftar, o = {}) {
  // bullet digambar manual (kotak biru kecil) karena bullet bawaan pptxgenjs
  // tidak andal pada paragraf multi-gaya dan warnanya tidak bisa diatur.
  const fs = o.fs ?? FS.sml, lh = o.lh ?? LHF.sml;
  const jeda = o.jeda ?? 8;
  let y = byTop;
  for (const it of daftar) {
    const teks = typeof it === 'string' ? it : it.isi;
    const n = bungkus(teks, w - 14, fs);
    const h = n * lh + 2;
    rect(s, bx + 1.5, y - 3.2, 4.2, 4.2, { fill: COL.accent });
    tNW(s, bx + 13, y, w - 13, teks, { fs, lh, color: o.color ?? COL.ink });
    y -= (h + jeda);
  }
}

// ------------------------------------------------------------------ dokumen
const pres = new PptxGenJS();
pres.layout = 'LAYOUT_WIDE';          // 13,333 x 7,5 inci = 960 x 540 bp
pres.author = 'Swallowgank — Institut Teknologi Sepuluh Nopember';
pres.company = 'ASEAN Data Science Explorers 2026';
pres.title = 'Four Months\u2019 Notice — Pawang';

// =====================================================================
// HALAMAN 1 — SAMPUL
// =====================================================================
{
  const s = pres.addSlide();
  rect(s, 0, 540, W, 540, { fill: COL.deep });
  rect(s, 852, 540, 36, 540, { fill: COL.accent });
  rect(s, 888, 540, 36, 540, { fill: COL.alarm });
  rect(s, 924, 540, 36, 540, { fill: COL.peak });

  tNW(s, 836 - 260, 435, 260, '4', { fs: 150, lh: 150, color: COL.deep4, bold: true, align: 'right', h: 190 });
  tNW(s, 836 - 230, 264, 230, 'months of public notice before\na dengue season turns severe',
    { fs: FS.sml, lh: LHF.sml, color: COL.deepSub, align: 'right' });

  tNW(s, 60, 489, 700, 'ASEAN DATA SCIENCE EXPLORERS 2026', { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  tNW(s, 60, 458, 720, "Four Months' Notice", { fs: 56, lh: 60, color: 'FFFFFF', bold: true });
  tNW(s, 60, 388, 600, 'Turning El Niño into a dengue early-warning alarm for ASEAN',
    { fs: 21, lh: 27, color: 'FFFFFF' });
  garisH(s, 60, 348, 160, { color: COL.alarm, width: 3 });
  tNW(s, 60, 328, 580, 'A freely available climate index gives ASEAN health offices months of ' +
    'warning before a dengue season turns severe. We turn that lag into a two-condition alert ' +
    'rule that any provincial health office can run today, with no model, no code and no paid data.',
    { fs: FS.sub, lh: LHF.sub, color: 'FFFFFF' });
  sdgchips(s, 60, 226, [['SDG 3 Health', COL.peak], ['SDG 13 Climate', COL.accent], ['SDG 6 Water', COL.alarm]]);
  garisH(s, 60, 172, 836, { color: COL.deepLine });
  tNW(s, 60, 152, 700, '**Team Swallowgank**  ~~|~~  Institut Teknologi Sepuluh Nopember  ~~|~~  Indonesia',
    { fs: FS.body, lh: LHF.body, color: 'FFFFFF' });
  tSW(s, 60, 40, 500, 'All charts built in SAP Analytics Cloud', { fs: FS.sml, lh: LHF.sml, color: COL.line });
  s.addNotes('Opening (30 detik):\n- Greet the judges; perkenalkan tim: Swallowgank, ITS, Indonesia.\n- Satu kalimat kunci: "We turned a free climate index into a dengue alarm that any district health office can run — with no model and no code."\n- Sebut semua grafik dibangun di SAP Analytics Cloud.');
}

// =====================================================================
// HALAMAN 2 — THE PROBLEM
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 1);
  kepala(s, 'The problem', "Dengue is ASEAN's fastest-moving climate-sensitive disease");
  kpi(s, 36, CTOP, 198, 100, '1.26M', 'cases in 2019, the worst year in our nine-country panel', COL.peak);
  butir(s, 36, 312, 198, [
    'Vietnam 368k, Philippines 220k, Thailand 159k ~~(latest complete year each)~~',
    'The 2023–24 El Niño added an estimated **9.6 million cases worldwide** ~~(Tian et al., 2025)~~',
    'Outbreaks are still fought **reactively**, only once cases surge',
  ]);
  slot(s, { kiri: 252, y: CTOP, tinggi: 298, nama: 'h02-tren-tahunan', judul: 'ASEAN dengue cases, 2000–2024' });
  slot(s, { kanan: 924, y: CTOP, tinggi: 298, nama: 'h02-per-negara', judul: 'Cases by country, latest complete year' });
  simpulan(s, 252, 100, 672, 'The burden is large, rising and spiky. Spikes are what an alarm can catch; ' +
    'a trend line is not something a health office can act on.');
  kaki(s, 'Source: OpenDengue V1.3, national totals, complete-reporting years only. We do not claim a ' +
    '2023–24 record, because our panel is incomplete for Vietnam and the Philippines after 2022.', 2);
  s.addNotes('- The problem: dengue is ASEAN\'s fastest-moving climate-sensitive disease.\n- 1.26 million cases in 2019 (worst year in our nine-country panel).\n- Spikes, not trends, are what a health office can act on — that is the opening for an early-warning alarm.');
}

// =====================================================================
// HALAMAN 3 — THE QUESTION
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 1);
  kepala(s, 'The question', 'Climate data arrives months before patients do');
  rect(s, 36, CTOP, 888, 80, { round: true, radius: 4, fill: COL.soft });
  garisV(s, 36, CTOP, 344, { color: COL.alarm, width: 4 });
  tNW(s, 54, 406, 852, 'Can a freely available climate index tell a health office how bad the coming ' +
    'season will be, early enough to act?', { fs: 20, lh: 26, color: COL.ink, bold: true });
  butir(s, 36, 318, 288, [
    '**SDG target 3.3**: end the epidemics of neglected tropical diseases, of which dengue is one',
    '**SDG target 13.1**: strengthen resilience and adaptive capacity to climate-related hazards',
    '**SDG target 6.1**: safe water for all. Where piped water is absent, households store it, and *Aedes* breeds in the store',
  ]);
  garisH(s, 36, 168, 324);
  tNW(s, 36, 154, 288, '**ASEAN priority.** Dengue sits under **ASEAN Health Cluster 2**, ' +
    '*Responding to All Hazards and Emerging Threats*, whose ASEAN Dengue Day statements ask ' +
    'member states for earlier and better coordinated action.', { fs: FS.sml, lh: LHF.sml });
  slot(s, { kanan: 924, y: 318, tinggi: 136, nama: 'h03-alur', judul: 'From public index to public action' });
  tNW(s, 360, 150, 500, 'WHAT WOULD MAKE US WRONG', { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  [['Signal is only the wet season', 'answered p. 7'],
   ['Rule was tuned on its own test years', 'answered p. 12'],
   ['Our innovation angle does not hold', 'answered p. 14']].forEach(([uji, jawab], i) => {
    const cx = 360 + 192 * i;
    rect(s, cx, 132, 176, 74, { round: true, radius: 4, fill: COL.soft });
    tNW(s, cx + 14, 118, 148, uji, { fs: FS.sml, lh: LHF.sml });
    tSW(s, cx + 14, 68, 148, jawab, { fs: FS.tny, lh: LHF.tny, color: COL.accent, bold: true });
  });
  kaki(s, 'Every claim on the following pages is tested against the three objections above, ' +
    'and each test has its own page.', 3);
  s.addNotes('- The question: can a free, public climate index give a health office enough notice?\n- Ties to SDG 3.3, 13.1 and 6.1 and to ASEAN Health Cluster 2.\n- We promise nothing to the judges we do not test: the three cards are the three ways we could be wrong, each answered on p. 7, 12 and 14.');
}

// =====================================================================
// HALAMAN 4 — DATA & METHOD
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 2);
  kepala(s, 'Data & method', 'Nine open datasets, one monthly panel, zero paid sources');
  // tabel dataset — posisi baris mengikuti ukuran asli (pitch 28,57 bp;
  // baris "monthly panel" dua baris sehingga jarak ke baris berikutnya 47 bp)
  const wKol = [296, 74, 176];
  const barisTabel = [
    ['Dengue cases (OpenDengue V1.3)', '70,397', '10 countries, 1955–2025'],
    ['Dengue × climate monthly panel', '55,329', 'province-month, lags\npre-computed'],
    ['Temperature & rainfall (CCKP, ERA5)', '9,000', 'monthly, 1950–2024'],
    ['ONI El Niño index (NOAA CPC)', '918', 'monthly, 1950–2026'],
    ['Water & sanitation (WHO/UNICEF JMP)', '8,692', '2000–2024'],
    ['Population (BPS Indonesia)', '140', 'provinces, denominators'],
    ['Flood exposure (GHSL)', '30,348', '836 cities, 1975–2030'],
  ];
  const yBaris = [393.3, 364.7, 317.7, 289.2, 260.6, 232.0, 203.5];
  tNW(s, 36, 414, wKol[0], 'DATA', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true });
  tNW(s, 332, 414, wKol[1], 'ROWS', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true, align: 'right' });
  tNW(s, 424, 414, wKol[2], 'COVERAGE', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true });
  garisH(s, 36, 396, 600);
  barisTabel.forEach((r, i) => {
    const y = yBaris[i];
    tNW(s, 36, y, wKol[0], r[0], { fs: FS.body, lh: LHF.body });
    tNW(s, 332, y, wKol[1], r[1], { fs: FS.body, lh: LHF.body, align: 'right' });
    tNW(s, 424, y, wKol[2], r[2], { fs: FS.body, lh: LHF.body });
  });
  // pita angka
  [['175k', 'rows in the joined panel'], ['9', 'countries with monthly data'],
   ['212', 'provinces covered'], ['0', 'paid or login-only sources']].forEach(([ang, lbl], i) => {
    const cx = 36 + 144 * i;
    tNW(s, cx, 180, 128, ang, { fs: FS.kpimid, lh: LHF.kpimid, color: COL.peak, bold: true });
    tNW(s, cx, 139.5, 128, lbl, { fs: FS.tny, lh: LHF.tny, color: COL.muted });
  });
  sdgchips(s, 36, 102, [['SDG 3', COL.peak], ['SDG 13', COL.accent], ['SDG 6', COL.alarm]]);
  tNW(s, 36, 74, 564, '~~Every table joins on the same two keys, iso3 and year, with period ' +
    'added for the monthly dengue × climate panel. Nothing is entered by hand.~~', { fs: FS.tny, lh: LHF.tny });
  // panel METHOD
  rect(s, 624, CTOP, 300, 366, { round: true, radius: 4, fill: COL.soft });
  tNW(s, 644, 404, 260, 'METHOD', { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  butir(s, 644, 382, 260, [
    'Monthly national series, 2010+',
    'Lagged correlations, 0–4 months',
    '**Anomalies**: the seasonal cycle is removed before we accept any correlation',
    'A two-condition trigger rule',
    'Out-of-sample test on unseen years',
    'WHO/PAHO endemic-channel benchmark',
  ]);
  garisH(s, 644, 124, 904);
  tNW(s, 644, 110, 260, 'All charts built in SAP Analytics Cloud.', { fs: FS.sml, lh: LHF.sml, color: COL.accent, bold: true });
  kaki(s, 'Nine sources, all public: OpenDengue · World Bank CCKP (ERA5) · NOAA CPC · ' +
    'WHO/UNICEF JMP · BPS · GHSL · SIPSN KLHK · BNPB. No licence, no login, no cost.', 4);
  s.addNotes('- Nine public datasets, zero paid sources; joins on iso3 + year (+ period).\n- 175k rows, 9 countries, 212 provinces — all reproducible.\n- Method: lagged correlations, anomalies before accepting any correlation, and an out-of-sample test we do not hide (p. 12).');
}

// =====================================================================
// HALAMAN 5 — ANALYSIS 1: THE SEASON
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 3);
  kepala(s, 'Analysis 1 · the season', 'Dengue has a calendar, and it is not the same one everywhere');
  butir(s, 36, CTOP, 198, [
    '**Indonesia** peaks **Jan–Apr**, right after the December rainfall peak\n~~Jan 15,099 cases/month against Sep 6,003 = 2.5×~~',
    '**Thailand** climbs with the **onset** of the wet season and peaks **Jun–Sep**\n~~Jul 8,110 against Feb 1,465 = 5.5×~~',
    'One disease, two calendars in opposite halves of the year',
  ], { jeda: 10 });
  kutip(s, 36, 148, 96, 180, 'A regional alarm has to be local in its timing.');
  slot(s, { kiri: 252, y: CTOP, tinggi: 312, nama: 'h05-musiman-idn', judul: 'Indonesia: cases vs rainfall by month' });
  slot(s, { kanan: 924, y: CTOP, tinggi: 312, nama: 'h05-musiman-tha', judul: 'Thailand: cases vs rainfall by month' });
  simpulan(s, 252, 88, 672, "Rainfall alone cannot set the date: Thailand's rain peaks in September, " +
    'two months *after* its cases. Something earlier in the chain is doing the work.');
  kaki(s, 'Source: national monthly means, complete years only (IDN 2010–2023, THA 2010–2022).', 5);
  s.addNotes('- Dengue has a calendar, and it differs across ASEAN: Indonesia peaks Jan–Apr (2.5× swing), Thailand peaks Jun–Sep (5.5× swing).\n- One disease, two calendars in opposite halves of the year.\n- Rainfall alone cannot set the date — Thailand\'s rain peaks after its cases. Something earlier in the chain is doing the work.');
}

// =====================================================================
// HALAMAN 6 — ANALYSIS 2: THE LAG
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 3);
  kepala(s, 'Analysis 2 · the lag', 'The climate signal arrives 1–4 months before the cases');
  // tabel prediktor
  let ty = CTOP;
  tNW(s, 36, ty, 96, 'PREDICTOR', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true });
  tNW(s, 132, ty, 46, 'LAG', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true, align: 'right' });
  tNW(s, 178, ty, 46, 'R', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true, align: 'right' });
  garisH(s, 36, ty - 16, 234);
  const baris6 = [
    ['grp', 'INDONESIA'],
    ['row', '**ONI (El Niño)**', '**4 mo**', '**+0.59**'],
    ['row', 'Temperature', '3 mo', '+0.47'],
    ['row', 'Rainfall', '1 mo', '+0.40'],
    ['grp', 'THAILAND'],
    ['row', '**Temperature**', '**3 mo**', '**+0.57**'],
    ['row', 'Rainfall', 'same mo', '+0.48'],
    ['garis'],
  ];
  ty -= 30;
  for (const r of baris6) {
    if (r[0] === 'garis') { garisH(s, 36, ty + 10, 234); break; }
    if (r[0] === 'grp') {
      garisH(s, 36, ty + 12, 234);
      tNW(s, 36, ty, 198, r[1], { fs: FS.tny, lh: LHF.tny, color: COL.accent, bold: true });
      ty -= 22;
    } else {
      tNW(s, 36, ty, 96, r[1], { fs: FS.sml, lh: LHF.sml });
      tNW(s, 132, ty, 46, r[2], { fs: FS.sml, lh: LHF.sml, align: 'right' });
      tNW(s, 178, ty, 46, r[3], { fs: FS.sml, lh: LHF.sml, align: 'right' });
      ty -= 24;
    }
  }
  kutip(s, 36, 164, 96, 180, 'The lag *is* the opportunity: it is the time a health office has to act.');
  slot(s, { kiri: 252, y: CTOP, tinggi: 312, nama: 'h06-heatmap-jeda', judul: 'Correlation by predictor and lag' });
  slot(s, { kanan: 924, y: CTOP, tinggi: 312, nama: 'h06-scatter-suhu', judul: 'Temperature (lag 2) vs cases, Indonesia' });
  simpulan(s, 252, 88, 672, 'Every predictor peaks at a lag of one month or more, so none of them is a ' +
    'coincident symptom. The best one, ONI, is also the one published earliest and freely.');
  kaki(s, 'Source: monthly national series, 2010+ (n = 172 months, Indonesia).', 6);
  s.addNotes('- The climate signal arrives 1–4 months before cases — the lag is the opportunity.\n- Best predictor for Indonesia: ONI at lag 4 (r = +0.59); every predictor peaks at lag ≥ 1 month.\n- The best predictor is also the earliest-published and free (NOAA CPC).');
}

// =====================================================================
// HALAMAN 7 — ANALYSIS 3: THE STRONGEST SIGNAL
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 3);
  kepala(s, 'Analysis 3 · the strongest signal', "A strong El Niño nearly triples Indonesia's monthly dengue burden");
  kpi(s, 36, CTOP, 198, 104, '2.8×', '21,383 vs 7,597 cases per month, grouped by the ENSO phase four months earlier', COL.peak);
  butir(s, 36, 306, 198, [
    'The grouping uses the ENSO phase **four months earlier**, so this is a forecast rather than hindsight',
    '**Not merely seasonality.** With the seasonal cycle removed, the ONI correlation still holds at **r = +0.56**',
    '**Not an aggregation artefact.** Cases run higher in El Niño months in **33 of 34 Indonesian provinces** ~~(sign test p = 2×10⁻⁹)~~ and in 70 of 77 Thai provinces',
    'Rainfall does *not* survive the same test, falling from +0.40 to +0.24, and we report that',
  ], { fs: FS.tny, lh: LHF.tny, jeda: 6 });
  slot(s, { kiri: 252, y: CTOP, tinggi: 344, nama: 'h07-fase-enso', judul: 'Mean monthly cases by ENSO phase (lag 4)' });
  slot(s, { kanan: 924, y: CTOP, tinggi: 344, nama: 'h07-anomali', judul: 'Same signal, seasonality removed' });
  chip(s, 258, 398, COL.peak, 'Strong El Niño: 21,383 cases/month');
  kaki(s, 'Source: 172 months, Indonesia 2010–2024 · NOAA CPC definition: El Niño = ONI ≥ 0.5. ' +
    'We claim early-warning feasibility, not causation.', 7);
  s.addNotes('- Strongest signal: a strong El Niño (lag 4) nearly triples the monthly burden — 21,383 vs 7,597 cases/month.\n- It is not just seasonality (anomaly r = +0.56) and not an aggregation artefact (33 of 34 provinces).\n- Rainfall does not survive the same test — we report that too. Claim is feasibility of early warning, not causation.');
}

// =====================================================================
// HALAMAN 8 — ANALYSIS 4: WHERE AND WHEN
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 3);
  kepala(s, 'Analysis 4 · where and when', 'The alarm must be set province by province');
  butir(s, 36, CTOP, 198, [
    '**Indonesia**: 20 of 35 provinces peak in **January**, 8 in February, but **Bali peaks in May** and North Kalimantan in December',
    '**Thailand**: 38 of 77 provinces peak in **July**, 16 in August',
    'A single national alert date would be wrong for a third of Indonesia',
  ]);
  kutip(s, 36, 190, 122, 180, 'Same colour scale, same twelve rows. Only the calendar moves.');
  slot(s, { kiri: 252, y: CTOP, tinggi: 303, nama: 'h08-kalender-idn', judul: 'Indonesia: share of annual cases by month' });
  slot(s, { kanan: 924, y: CTOP, tinggi: 303, nama: 'h08-kalender-tha', judul: 'Thailand: share of annual cases by month' });
  simpulan(s, 252, 96, 672, 'This is why the rule carries a month condition as well as a climate one. ' +
    "The index says how bad; the province's own calendar says when.");
  kaki(s, 'Source: share of annual cases by calendar month, per province.', 8);
  s.addNotes('- The alarm must be set province by province: peaks scatter from December to May.\n- A single national alert date would be wrong for a third of Indonesia.\n- Hence the rule has a month condition as well as a climate one: the index says how bad, the calendar says when.');
}

// =====================================================================
// HALAMAN 9 — ANALYSIS 5: WHO IS HIT HARDEST
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 3);
  kepala(s, 'Analysis 5 · who is hit hardest', 'The same alarm, aimed at the most exposed places');
  butir(s, 36, CTOP, 432, [
    'Highest incidence 2018–2020: **Bali 134**, North Kalimantan 115, East Kalimantan 112 per 100k, which is **14× the lowest province** (Papua, 9)',
    'Indonesia has the **lowest piped-water access in ASEAN** at 21.8% ~~(JMP 2024)~~. Households therefore store water, and stored water breeds *Aedes*',
  ], { fs: FS.tny, lh: LHF.tny });
  butir(s, 492, CTOP, 432, [
    '**12.9 million people in Bangkok** and 1.7 million in Jakarta live in the 1-in-100-year flood zone',
    'We use these three layers to **target** the alarm, not to explain the disease. The one place we tried to explain it, the claim failed ~~(p. 14)~~',
  ], { fs: FS.tny, lh: LHF.tny });
  slot(s, { kiri: 36, y: 348, tinggi: 265, nama: 'h09-insidens', judul: 'Incidence per 100k, 2018–2020' });
  slot(s, { kiri: 334, y: 348, tinggi: 265, nama: 'h09-wash', judul: 'Piped water access, ASEAN' });
  slot(s, { kanan: 924, y: 348, tinggi: 265, nama: 'h09-banjir', judul: 'Flood-zone population, top cities' });
  kaki(s, 'Sources: BPS denominators, 2018–2020 only, the only years with official provincial ' +
    'denominators · WHO/UNICEF JMP · GHSL. We never rank regions using raw case counts.', 9);
  s.addNotes('- Who gets hit hardest: incidence is 14× higher in the top province (Bali) than the lowest.\n- Indonesia has ASEAN\'s lowest piped-water access (21.8%) — stored water breeds Aedes.\n- Flood exposure (Bangkok 12.9M, Jakarta 1.7M in the 1-in-100-year zone) is used to target the alarm, not to explain the disease.');
}

// =====================================================================
// HALAMAN 10 — SYNTHESIS: THE RISK CALENDAR
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 4);
  kepala(s, 'Synthesis', 'From signal to schedule: a risk calendar every health office can read');
  butir(s, 36, CTOP, 198, [
    'Each province gets three states, **Peak**, **Watch** and **Normal**, derived from its own case history',
    'The El Niño index sets **how severe** the coming peak will be; the calendar sets **when** it arrives',
    'Real lead times, every El Niño episode since 2009: **0–3 months** on observed ONI, longer still on NOAA and BMKG *forecast* ONI',
  ]);
  kutip(s, 36, 166, 112, 180, 'Two public numbers, one page, no model to maintain.');
  slot(s, { kiri: 252, y: CTOP, tinggi: 311, nama: 'h10-kalender-prioritas', judul: 'Risk calendar, six priority provinces' });
  slot(s, { kanan: 924, y: CTOP, tinggi: 311, nama: 'h10-deret-alarm', judul: 'Cases vs the P75 outbreak threshold' });
  simpulan(s, 252, 88, 672, "The threshold is the WHO-style P75 of the province's own history, not a number " +
    'we picked. Everything above the orange line is what the alarm is trying to anticipate.');
  kaki(s, 'Source: 5 El Niño episodes, 2009–2024. The alarm predicts how severe the coming season ' +
    'will be; it does not shift its start date.', 10);
  s.addNotes('- Synthesis: every province gets Peak / Watch / Normal states derived from its own history.\n- The index says how severe; the calendar says when.\n- Real lead times: 0–3 months on observed ONI, longer on forecast ONI.');
}

// =====================================================================
// HALAMAN 11 — THE SOLUTION
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 5);
  kepala(s, 'The solution', 'Two conditions. No model. No code.');
  rect(s, 36, CTOP, 888, 72, { round: true, radius: 4, fill: COL.peak });
  tNW(s, 54, 406, 852, '"If the month is Jan–Apr **AND** ONI four months ago was ≥ 0.5 → raise alert"',
    { fs: 21, lh: 27, color: 'FFFFFF', bold: true });
  kpi(s, 36, 338, 180, 84, '11.6%', 'of months fire the alert', COL.accent);
  kpi(s, 230, 338, 180, 84, '100%', 'precision, every alert in a top-quartile month', COL.peak);
  kpi(s, 424, 338, 180, 84, '4×', 'lift over the base rate', COL.alarm);
  butir(s, 36, 246, 570, [
    'Both inputs are public and free: NOAA publishes ONI monthly, the calendar comes from the office\'s own records',
    'It runs in a spreadsheet, a WhatsApp broadcast or the SAC page on p. 15. Where a statistical forecast ' +
      'needs a trained model and a data team, a provincial office can start this next week',
  ], { fs: FS.tny, lh: LHF.tny });
  slot(s, { kiri: 36, y: 196, tinggi: 122, nama: 'h11-deret-aturan', judul: 'When the rule fired, 2010–2024' });
  slot(s, { kanan: 924, y: 338, tinggi: 264, nama: 'h11-aturan', judul: 'Precision vs alert frequency, four rules' });
  kaki(s, 'Source: Indonesia 2010–2024, 172 months · the ONI ≥ 0.5 threshold is NOAA\'s own El Niño ' +
    'definition, not a value we tuned.', 11);
  s.addNotes('- The solution in one line: two conditions, no model, no code — "If the month is Jan–Apr AND ONI four months ago was ≥ 0.5 → raise alert".\n- 11.6% of months fire; 100% of alerts landed in a top-quartile month; 4× lift over base rate.\n- Both inputs are free and public; it runs on a spreadsheet, a WhatsApp broadcast, or the SAC page.');
}

// =====================================================================
// HALAMAN 12 — VIABILITY
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 6);
  kepala(s, 'Viability', 'We tried to break our own rule. It held.');
  butir(s, 36, CTOP, 270, [
    '**Out-of-sample test**: rule built on 2010–2016, tested blind on 2017–2024 → **precision still 100%**, sensitivity 44%, lift 3.9',
    'Against the **WHO/PAHO endemic-channel** definition, specificity is **91%** and lift 2.5. *All* of the value comes from the El Niño condition rather than from the season',
    'Published dengue early-warning systems report PPV 43–86% ~~(17-system review)~~. We reach a comparable PPV **using monthly data and no statistical model**',
    'Replicates in Thailand with its own best predictor (temperature anomaly, lag 2): lift 2.7',
  ], { fs: FS.tny, lh: LHF.tny, jeda: 5 });
  rect(s, 36, 150, 270, 92, { round: true, radius: 4, fill: COL.soft });
  tNW(s, 52, 139, 240, 'ADOPTION IN THREE PHASES', { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  tNW(s, 52, 119.5, 240, '**1** Bali, N. & E. Kalimantan pilot  ~~→~~  **2** all 38 provinces  ~~→~~\n' +
    '**3** ASEAN peers\n~~Cost: open data, monthly refresh, existing staff. No new licence and no new headcount.~~',
    { fs: FS.tny, lh: LHF.tny });
  slot(s, { kiri: 324, y: CTOP, tinggi: 317, nama: 'h12-luar-sampel', judul: 'Train vs blind test, Indonesia and Thailand' });
  tNW(s, 672, CTOP, 252, 'How we compare to published EWS', { fs: FS.sml, lh: LHF.sml, bold: true });
  // tabel pembanding
  const xT = [672, 818, 870];
  const wT = [146, 52, 52];
  let by = 404;
  tNW(s, xT[0], by, wT[0], 'SYSTEM', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true });
  tNW(s, xT[1], by, wT[1], 'SENS. %', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true, align: 'right' });
  tNW(s, xT[2], by, wT[2], 'PPV %', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true, align: 'right' });
  garisH(s, 672, by - 14, 924);
  const tab12 = [
    ['17 published EWS *(range)*\n~~Baharom et al. 2022~~', '50–100', '43–86', 34],
    ['EWARS-csd, Colombia\n~~Schlesinger et al. 2024~~', '97', '75', 30],
    ['WHO/TDR EWARS, Mexico\n~~Cárdenas et al. 2021~~', '100', '83', 30],
    ['GARIS'],
    ['**Rule D vs P75** *(blind test)*\n~~this deck~~', '**44**', '**100**', 30],
    ['**Rule D vs endemic channel**\n~~this deck~~', '**29**', '**30**', 30],
    ['GARIS'],
  ];
  by -= 22;
  for (const r of tab12) {
    if (r[0] === 'GARIS') { garisH(s, 672, by + 12, 924); by -= 8; continue; }
    tNW(s, xT[0], by, wT[0], r[0], { fs: FS.tny, lh: LHF.tny });
    tNW(s, xT[1], by, wT[1], r[1], { fs: FS.tny, lh: LHF.tny, align: 'right' });
    tNW(s, xT[2], by, wT[2], r[2], { fs: FS.tny, lh: LHF.tny, align: 'right' });
    by -= r[3];
  }
  tNW(s, 672, 132, 252, '~~We report the endemic-channel row even though it is our worst result. ' +
    'It is the harder benchmark, and hiding it would be the kind of selective reporting this deck argues against.~~',
    { fs: FS.tny, lh: LHF.tny });
  kaki(s, 'We chose precision over sensitivity: a repeated false alarm is the fastest way to make a ' +
    'health office stop trusting the system. This rule is an escalation layer on top of routine ' +
    'surveillance, not a replacement.', 12);
  s.addNotes('- Viability: we tried to break our own rule. Out-of-sample (built 2010–16, blind 2017–24): precision still 100%, lift 3.9.\n- Benchmarked against WHO/PAHO endemic channel and 17 published EWS (PPV 43–86%); we reach comparable PPV with no statistical model.\n- It replicates in Thailand. We chose precision over sensitivity, and we print our worst row too.');
}

// =====================================================================
// HALAMAN 13 — IMPACT
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 7);
  kepala(s, 'Impact · Indonesia alone', 'Acting 4–8 weeks earlier is worth US$1.5–3.7 million a year');
  kpi(s, 36, CTOP, 258, 96, '4,656', 'cases/year prevented in Indonesia, under the most conservative scenario', COL.peak);
  butir(s, 36, 314, 258, [
    'Indonesia averages **104,753 cases/year** ~~(complete years 2015–2023)~~; **44% fall in Jan–Apr**',
    'Prevent just **10%** of peak-season cases ~~(an assumption, not a finding)~~ = 4,656 cases/year',
    "At Indonesia's published hospitalisation cost of US$316–791/case → **US$1.5–3.7 M (Rp 24–59 billion)/year**",
    'For scale, dengue costs Indonesia **US$381–681 M/year** ~~(Nadjib 2019; Wilastonegoro 2020)~~',
  ], { fs: FS.tny, lh: LHF.tny, jeda: 5 });
  kutip(s, 36, 186, 86, 240, 'Every figure here is either published or a stated assumption. None of them is a model output.');
  slot(s, { kiri: 312, y: CTOP, tinggi: 344, nama: 'h13-dampak', judul: 'Avoided cost by scenario' });
  tNW(s, 508, CTOP, 416, 'Lead time, every El Niño episode since 2009', { fs: FS.sml, lh: LHF.sml, bold: true });
  // tabel tenggang
  const xE = [508, 586, 690, 810];
  const wE = [78, 104, 120, 114];
  let ey = 404;
  tNW(s, xE[0], ey, wE[0], 'EPISODE', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true });
  tNW(s, xE[1], ey, wE[1], 'ALARM FIRES', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true });
  tNW(s, xE[2], ey, wE[2], 'CASES CROSS P75', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true });
  tNW(s, xE[3], ey, wE[3], 'LEAD TIME', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true, align: 'right' });
  garisH(s, 508, ey - 16, 924);
  ey -= 28;
  [['2009/10', 'Dec 2009', 'Jan 2010', '1 month'],
   ['2014/16', 'Feb 2015', 'Feb 2015', '0'],
   ['2018/19', 'Jan 2019', 'Jan 2019', '0'],
   ['2019/20', 'Mar 2020', 'Mar 2020', '0'],
   ['**2023/24**', '**Sep 2023**', '**Dec 2023**', '**3 months**']].forEach((r, i, arr) => {
    tNW(s, xE[0], ey, wE[0], r[0], { fs: FS.sml, lh: LHF.sml });
    tNW(s, xE[1], ey, wE[1], r[1], { fs: FS.sml, lh: LHF.sml });
    tNW(s, xE[2], ey, wE[2], r[2], { fs: FS.sml, lh: LHF.sml });
    tNW(s, xE[3], ey, wE[3], r[3], { fs: FS.sml, lh: LHF.sml, align: 'right' });
    ey -= 25;
    if (i === arr.length - 1) garisH(s, 508, ey + 12, 924);
  });
  rect(s, 508, 196, 416, 82, { round: true, radius: 4, fill: COL.soft });
  tNW(s, 524, 182, 384, 'THE LEAD TIME IS OBSERVED, NOT ASSUMED', { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  tNW(s, 524, 162, 384, 'Three of five episodes gave zero months on *observed* ONI, and we print that. ' +
    'The value comes from the two that did not, and from the fact that NOAA and BMKG publish a ' +
    '*forecast* ONI months ahead of the observed one, on which the same rule fires earlier still.',
    { fs: FS.tny, lh: LHF.tny });
  kaki(s, 'Sources: cost per case from peer-reviewed Indonesian studies; case counts from our own panel. ' +
    'The cheapest anchor (US$90/episode) still gives US$0.42 M, so we have not chosen the most flattering figure.', 13);
  s.addNotes('- Impact, conservative: acting 4–8 weeks earlier is worth US$1.5–3.7M a year in Indonesia (4,656 cases prevented under a stated 10% assumption).\n- Every figure is published or a stated assumption — none is a model output.\n- Lead time is observed, not assumed: we print the three episodes that gave zero months too.');
}

// =====================================================================
// HALAMAN 14 — LIMITS & DATA ETHICS
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 8);
  kepala(s, 'Limits & data ethics', 'What we tested and threw away');
  butir(s, 36, CTOP, 504, [
    '**We falsified our own innovation angle.** "Drought × water access" looked promising (r = −0.31) but collapsed after controlling for El Niño (partial r = −0.15) and showed no moderation by piped access (ρ = +0.34, p = 0.46, n = 7). **We dropped the claim.**',
    '**We do not claim a 2023–24 record**, because our panel is incomplete for Vietnam and the Philippines after 2022.',
    '**Incidence only for 2018–2020**, the only years with official BPS denominators. Elsewhere we use raw counts and never rank regions by them.',
    '**Flood and disaster records look correlated with dengue (r = +0.66) until the counts are divided by population**, at which point the association reverses (r = −0.14). We report the null.',
    'Correlation is not causation. This is an **early-warning** claim, and the mechanism is cited from the literature.',
  ], { fs: FS.body, lh: LHF.body, jeda: 9 });
  kutip(s, 36, 134, 88, 486, 'A rule that survives its own falsification tests is worth more to a health ' +
    'office than a larger claim that has never been tested.');
  slot(s, { kanan: 924, y: CTOP, tinggi: 344, nama: 'h14-kekeringan', judul: 'No relationship (ρ = +0.34, p = 0.46, n = 7)' });
  kaki(s, 'This page is not an apology. We tested our own best idea, it failed the test, and we removed it.', 14);
  s.addNotes('- Limits & data ethics: we tested our own best idea ("drought × water access"), it failed, and we removed it.\n- We do not claim records the panel cannot support; incidence only where official denominators exist.\n- Correlation is not causation — this is an early-warning claim with the mechanism cited from the literature.');
}

// =====================================================================
// HALAMAN 15 — PRODUK (PAWANG)
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 5);
  kepala(s, 'The product', 'Pawang: the rule, delivered on the first of every month');
  rect(s, ML, CTOP, CW, 62, { round: true, radius: 4, fill: COL.deep });
  tNW(s, 54, 412, 140, 'Pawang', { fs: 23, lh: 27, color: 'FFFFFF', bold: true });
  tNW(s, 196, 410, 706, '*Pawang* is the Indonesian and Malay word for someone who claims to know ' +
    'the weather months ahead. This one shows its working: a single SAC page that a district officer ' +
    'opens on the 1st, together with an automatic WhatsApp advisory. It escalates; it never declares an emergency.',
    { fs: FS.sml, lh: LHF.sml, color: 'FFFFFF' });
  tNW(s, ML, 348, CW, '**The digital layer does the fetching, not the deciding.** SAC refreshes the NOAA ' +
    'ONI feed and the office\'s own case calendar on a schedule, and SAC Smart Predict runs beside the ' +
    'rule as a second opinion. The alert itself remains the two-condition rule, which can be audited ' +
    'by hand, so no one has to trust a model they cannot inspect.', { fs: FS.sml, lh: LHF.sml });
  tNW(s, ML, 308, 260, 'What Bali opens on 1 October 2026', { fs: FS.sml, lh: LHF.sml, bold: true });
  // mockup dashboard
  rect(s, ML, 290, 444, 226, { round: true, radius: 5, fill: 'FFFFFF', line: COL.line, lw: 0.9 });
  rect(s, ML, 290, 444, 26, { fill: COL.soft });
  garisH(s, ML, 264, ML + 444);
  [12, 24, 36].forEach((dx) => {
    s.addShape('ellipse', { x: IN(ML + dx - 3), y: TOP(277) - IN(3), w: IN(6), h: IN(6), fill: { color: COL.line }, line: { type: 'none' } });
  });
  tMid(s, ML + 52 - 6, 277, 380, 'Pawang · Dinkes Prov. Bali · Oct 2026 · next refresh 1 Nov', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true });
  rect(s, 48, 254, 420, 34, { round: true, radius: 3, fill: COL.peak });
  tNW(s, 60, 250, 396, 'ALERT: Jan–Apr 2027. ONI in Sep 2026 was +1.3 (≥ 0.5).', { fs: FS.sml, lh: LHF.sml, color: 'FFFFFF', bold: true });
  tNW(s, 60, 234, 396, 'Expect a top-quartile season. Act now, not in January.', { fs: FS.tny, lh: LHF.tny, color: 'FFFFFF' });
  s.addImage({ path: GAMBAR('h11-deret-aturan'), x: IN(48), y: TOP(214), w: IN(420), h: IN(420 / RASIO['h11-deret-aturan']) });
  garisH(s, 48, 96, 468, { width: 0.5 });
  tNW(s, 48, 88, 420, '~~Blue: months the rule stayed silent  ·  Orange: months it fired  ·  ' +
    'Red line: the province\'s own P75 outbreak threshold~~', { fs: FS.tny, lh: LHF.tny });
  // tabel pemangku kepentingan
  tNW(s, 516, 308, 408, 'Who does what', { fs: FS.sml, lh: LHF.sml, bold: true });
  let wy = 288;
  tNW(s, 516, wy, 104, 'WHO', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true });
  tNW(s, 632, wy, 292, 'ROLE', { fs: FS.tny, lh: LHF.tny, color: COL.muted, bold: true });
  garisH(s, 516, wy - 14, 924);
  wy -= 24;
  [['**District health office** ~~gov\'t~~', 'Reads the advisory; moves PSN/3M, larviciding and stockpiles *forward* into the alerted window', 34],
   ['**Ministry of Health · BMKG** ~~gov\'t~~', 'Own the monthly refresh; BMKG\'s forecast ONI stretches the notice past four months', 34],
   ['**Jumantik cadres** ~~NGO & community~~', 'Larval checks and household messaging concentrated in the alerted months instead of spread thin all year', 34],
   ['**Cloud & telco partners** ~~private~~', 'Host the SAC tenant and the broadcast; one analyst-hour a month, no data team', 30],
  ].forEach(([who, peran, h], i, arr) => {
    tNW(s, 516, wy, 104, who, { fs: FS.sml, lh: LHF.sml });
    tNW(s, 632, wy, 292, peran, { fs: FS.sml, lh: LHF.sml });
    wy -= h;
    if (i === arr.length - 1) garisH(s, 516, wy + 12, 924);
  });
  rect(s, 516, 122, 408, 58, { round: true, radius: 4, fill: COL.soft });
  tNW(s, 532, 108, 376, 'SCALES BY SWAPPING ONE INPUT', { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  tNW(s, 532, 90, 376, 'Thailand already validates with its own predictor (temperature anomaly, lag 2, ' +
    'lift 2.7). Any ASEAN member repeats the fit on its own records.', { fs: FS.tny, lh: LHF.tny });
  kaki(s, 'The rule is the engine, not a feature of the product. Strip the dashboard away and a health ' +
    'office can still run Pawang on paper.', 15);
  s.addNotes('- The product: Pawang — the rule delivered on the 1st of every month as one SAC page plus an automatic WhatsApp advisory.\n- The digital layer (SAC refresh + Smart Predict) does the fetching, not the deciding; the alert stays auditable by hand.\n- Who does what: district office acts, MoH/BMKG own the refresh, Jumantik cadres target households, cloud partner hosts.\n- It scales by swapping one input — Thailand already replicates it.');
}

// =====================================================================
// HALAMAN 16 — REFERENSI 1/2
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 0);
  kepala(s, 'References 1/2', 'Data sources');
  tNW(s, ML, CTOP, 424, 'DATA', { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  tNW(s, ML, 406, 424, [
    'OpenDengue V1.3. doi:10.6084/m9.figshare.24259573.v4',
    '', 'World Bank Climate Change Knowledge Portal (ERA5 0.25° monthly temperature and precipitation).',
    '', 'NOAA Climate Prediction Center. Oceanic Niño Index (ONI v5).',
    '', 'WHO/UNICEF Joint Monitoring Programme for Water Supply, Sanitation and Hygiene, 2025 update.',
    '', 'BPS-Statistics Indonesia. Provincial population, WebAPI.',
    '', 'European Commission JRC. Global Human Settlement Layer (GHS-UCDB R2019A).',
    '', 'SIPSN, Ministry of Environment and Forestry, Indonesia.',
    '', 'BNPB. Indonesian Disaster Data and Information (DIBI).',
  ].join('\n'), { fs: FS.tny, lh: LHF.tny });
  tNW(s, ML, 236, 424, 'METHOD REFERENCE', { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  tNW(s, ML, 218, 424, 'Hussain-Alkhateeb L, et al. (2017). *Early warning and response system (EWARS) ' +
    'for dengue outbreaks: operational guide.* WHO/TDR technical document — no DOI assigned; the ' +
    'peer-reviewed description is Hussain-Alkhateeb 2018 on the next page.', { fs: FS.tny, lh: LHF.tny });
  tNW(s, 500, CTOP, 424, 'CLIMATE AND DENGUE', { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  tNW(s, 500, 406, 424, [
    'Tian Y, et al. (2025). Rising dengue risk with increasing El Niño–Southern Oscillation amplitude and teleconnections. *Nat Commun*. doi:10.1038/s41467-025-63655-0',
    '', 'Djaafara B, et al. (2026). Dengue transmission heterogeneity across Indonesia\'s archipelago: climate-driven spatiotemporal patterns and policy implications. *PLOS Negl Trop Dis*. doi:10.1371/journal.pntd.0014135',
    '', 'Mokhtar S, et al. (2024). Global risk of dengue outbreaks and the impact of El Niño events. *Environ Res*. doi:10.1016/j.envres.2024.119830',
    '', 'Sutriyawan A, et al. (2025). Impact of climate change on dengue incidence: a systematic review of evidence from Southeast Asia. *J Popul Soc Stud*. doi:10.25133/jpssv342026.028',
    '', 'Lowe R, et al. (2021). Combined effects of hydrometeorological hazards and urbanisation on dengue risk in Brazil. *Lancet Planet Health*. doi:10.1016/S2542-5196(20)30292-8',
    '', 'Gibb R, et al. (2023). Interactions between climate change, urban infrastructure and mobility are driving dengue emergence in Vietnam. *Nat Commun*. doi:10.1038/s41467-023-43954-0',
    '', 'Wang Y, et al. (2022). Impact of extreme weather on dengue fever infection in four Asian countries. *Environ Int*. doi:10.1016/j.envint.2022.107518',
    '', 'Choi Y, et al. (2016). Effects of weather factors on dengue fever incidence and implications for interventions in Cambodia. *BMC Public Health*. doi:10.1186/s12889-016-2923-2',
    '', 'Polrob P, et al. (2025). Nonlinear and lagged effects of climate variability on dengue incidence in Bangkok. *BMC Public Health*. doi:10.1186/s12889-025-25420-2',
  ].join('\n'), { fs: FS.tny, lh: LHF.tny });
  kaki(s, 'Reference pages — excluded from the 15-page limit per the official storyboard requirements. ' +
    'Every DOI was resolved against Crossref.', 'R1');
  s.addNotes('Reference pages (R1–R2) are for Q&A and due diligence; not part of the 15-page storyboard count.');
}

// =====================================================================
// HALAMAN 17 — REFERENSI 2/2
// =====================================================================
{
  const s = pres.addSlide();
  navbar(s, 0);
  kepala(s, 'References 2/2', 'Early-warning systems, cost, and validation');
  tNW(s, ML, CTOP, 424, 'EARLY-WARNING SYSTEMS', { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  tNW(s, ML, 406, 424, [
    'Hussain-Alkhateeb L, et al. (2018). Early warning and response system (EWARS) for dengue outbreaks: recent advancements towards widespread applications in critical settings. *PLOS ONE*. doi:10.1371/journal.pone.0196811',
    '', 'Baharom M, et al. (2022). Dengue early warning system as outbreak prediction tool: a systematic review. *Risk Manag Healthc Policy*. doi:10.2147/RMHP.S361106',
    '', 'Benitez-Valladares D, et al. (2021). Validation of the early warning and response system (EWARS) for dengue outbreaks: evidence from the national vector control program in Mexico. *PLOS Negl Trop Dis*. doi:10.1371/journal.pntd.0009261',
    '', 'Cárdenas R, et al. (2022). The early warning and response system (EWARS-TDR) for dengue outbreaks: can it also be applied to chikungunya and Zika outbreak warning? *BMC Infect Dis*. doi:10.1186/s12879-022-07197-6',
    '', 'Schlesinger P, et al. (2024). Enabling countries to manage outbreaks: statistical, operational, and contextual analysis of the EWARS-csd for dengue outbreaks. *Front Public Health*. doi:10.3389/fpubh.2024.1323618',
    '', 'Quan TM, et al. (2026). Climatic determinants and simple thresholds for dengue early warning in Vietnam: a One Health perspective. *Sci One Health*. doi:10.1016/j.soh.2026.100159',
  ].join('\n'), { fs: FS.tny, lh: LHF.tny });
  tNW(s, 500, CTOP, 424, 'BURDEN, COST, AND VALIDATION', { fs: FS.eye, lh: LHF.eye, color: COL.alarm, bold: true });
  tNW(s, 500, 406, 424, [
    'Nadjib M, et al. (2019). Economic burden of dengue in Indonesia. *PLOS Negl Trop Dis*. doi:10.1371/journal.pntd.0007038',
    '', 'Wilastonegoro NN, et al. (2020). Cost of dengue illness in Indonesia across hospital, ambulatory, and not medically attended settings. *Am J Trop Med Hyg*. doi:10.4269/ajtmh.19-0855',
    '', 'Shepard DS, et al. (2013). Economic and disease burden of dengue in Southeast Asia. *PLOS Negl Trop Dis*. doi:10.1371/journal.pntd.0002055',
    '', 'Shepard DS, et al. (2016). The global economic burden of dengue: a systematic analysis. *Lancet Infect Dis*. doi:10.1016/S1473-3099(16)00146-8',
    '', 'Sasmono RT, et al. (2026). Understanding the epidemiological trends and economic impact of dengue in Indonesia. *IJID Regions*. doi:10.1016/j.ijregi.2026.100860',
    '', 'Childs ML, et al. (2025). Climate warming is expanding dengue burden in the Americas and Asia. *PNAS*. doi:10.1073/pnas.2512350122',
  ].join('\n'), { fs: FS.tny, lh: LHF.tny });
  kaki(s, 'Reference pages — excluded from the 15-page limit per the official storyboard requirements. ' +
    'Every DOI was resolved against Crossref.', 'R2');
  s.addNotes('Reference pages (R1–R2) are for Q&A and due diligence; not part of the 15-page storyboard count.');
}

// ------------------------------------------------------------------ tulis
const OUT = process.argv[2] || path.join(__dirname, '..', 'INDONESIA_SWALLOWGANK.pptx');
pres.writeFile({ fileName: OUT }).then(() => {
  console.log('OK ->', OUT);
}).catch((e) => {
  console.error('GAGAL:', e);
  process.exit(1);
});
