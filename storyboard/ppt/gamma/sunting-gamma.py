#!/usr/bin/env python3
"""sunting-gamma.py — sunting lokal ekspor Gamma menjadi dek siap submit.

Masukan : ekspor-mentah.pptx   (unduhan mentah dari API Gamma, tema Consultant)
Keluaran: ../../INDONESIA_SWALLOWGANK-gamma.pptx

Yang disunting (agar sesuai storyboard & aturan panitia):
1. Slide 2 — kartu stat disusun ulang: 1.26M & 9.6M di baris atas, tiga negara
   (Vietnam 368k, Filipina 220k, Thailand 159k) di baris kedua; grafik kanan
   diperbesar. (Ekspor Gamma menghilangkan Thailand 159k.)
2. Semua slide — tipografi: apostrof ’ dan kutip ganda “ ” (menggantikan ' dan ").
3. Catatan pembicara — disalin dari dek native (INDONESIA_SWALLOWGANK-latex.pptx)
   ke notesSlide ekspor Gamma (Gamma hanya menulis nomor halaman di sana).
4. Nomor halaman kanan bawah: 2–15, lalu R1/R2 untuk halaman referensi,
   mengikuti konvensi kaki halaman storyboard.

Jalankan dari direktori mana saja:
    python3 sunting-gamma.py
"""
import json
import os
import re
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'ekspor-mentah.pptx')
NATIVE = os.path.join(BASE, '..', '..', 'INDONESIA_SWALLOWGANK-latex.pptx')
DST = os.path.join(BASE, '..', '..', 'INDONESIA_SWALLOWGANK-gamma.pptx')

P = 12700
z = zipfile.ZipFile(SRC)
items = {n: z.read(n) for n in z.namelist()}


def slide(n):
    return items[f'ppt/slides/slide{n}.xml'].decode('utf-8')


def simpan_slide(n, x):
    items[f'ppt/slides/slide{n}.xml'] = x.encode('utf-8')


def sp_of(x, nama):
    for m in re.finditer(r'<p:sp>.*?</p:sp>', x, re.S):
        if f'name="{nama}"' in m.group(0):
            return m.group(0)
    raise KeyError(nama)


def ganti_sp(x, nama, baru):
    lama = sp_of(x, nama)
    return x.replace(lama, baru, 1)


def set_off(blok, x=None, y=None):
    def r(m):
        a = x if x is not None else m.group(1)
        b = y if y is not None else m.group(2)
        return f'<a:off x="{a}" y="{b}"/>'
    return re.sub(r'<a:off x="(-?\d+)" y="(-?\d+)"/>', r, blok, count=1)


def set_ext(blok, cx=None, cy=None):
    def r(m):
        a = cx if cx is not None else m.group(1)
        b = cy if cy is not None else m.group(2)
        return f'<a:ext cx="{a}" cy="{b}"/>'
    return re.sub(r'<a:ext cx="(\d+)" cy="(\d+)"/>', r, blok, count=1)


def get_off(blok):
    m = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>', blok)
    return int(m.group(1)), int(m.group(2))


def get_ext(blok):
    m = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"/>', blok)
    return int(m.group(1)), int(m.group(2))


def ganti_teks(blok, baru):
    return re.sub(r'<a:t>.*?</a:t>', f'<a:t>{baru}</a:t>', blok, count=1, flags=re.S)


def ganti_id(blok, baru, nama):
    return re.sub(r'<p:cNvPr id="\d+" name="[^"]*"', f'<p:cNvPr id="{baru}" name="{nama}"', blok, count=1)


# =====================================================================
# 1. SLIDE 2 — kartu stat
# =====================================================================
s2 = slide(2)
x7 = sp_of(s2, 'Text 7')
numW = get_ext(x7)[0]
labW = int(285.6 * P)
labH = get_ext(sp_of(s2, 'Text 8'))[1]
y_lab2 = get_off(sp_of(s2, 'Text 9'))[1]
y_num2 = get_off(x7)[1]
y_lab1 = get_off(sp_of(s2, 'Text 8'))[1]


def pusat(c, lebar):
    return int(c * P) - lebar // 2


c1, c2, c3 = 194.8, 480.0, 765.2

untuk = {
    'Text 4': dict(off=(pusat(c1, numW), y_num2)),                       # 368k
    'Text 5': dict(off=(pusat(c1, labW), y_lab1), ext=(labW, labH)),     # Vietnam
    'Text 6': dict(off=(pusat(c1, labW), y_lab2), ext=(labW, labH)),     # latest
    'Text 7': dict(off=(pusat(c2, numW), y_num2)),                       # 220k
    'Text 8': dict(off=(pusat(c2, labW), y_lab1), ext=(labW, labH)),     # Filipina
    'Text 9': dict(off=(pusat(c2, labW), y_lab2), ext=(labW, labH)),     # latest
}
delta = y_num2 - 954088
untuk['Text 10'] = dict(off=(None, get_off(sp_of(s2, 'Text 10'))[1] - delta))  # 9.6M naik
untuk['Text 11'] = dict(off=(None, get_off(sp_of(s2, 'Text 11'))[1] - delta))
untuk['Text 12'] = dict(off=(None, get_off(sp_of(s2, 'Text 12'))[1] - delta))

for nama, op in untuk.items():
    blok = sp_of(s2, nama)
    ox, oy = op['off']
    blok = set_off(blok, ox, oy)
    if 'ext' in op:
        blok = set_ext(blok, *op['ext'])
    s2 = ganti_sp(s2, nama, blok)

# Thailand 159k = klon trio 220k/Filipina
klon = []
for src, baru_id, baru_nama, teks, off in [
    ('Text 7', 61, 'Text 61', '159k', (pusat(c3, numW), y_num2)),
    ('Text 8', 62, 'Text 62', 'Thailand', (pusat(c3, labW), y_lab1)),
    ('Text 9', 63, 'Text 63', 'Latest complete year', (pusat(c3, labW), y_lab2)),
]:
    b = sp_of(s2, src)
    b = ganti_id(b, baru_id, baru_nama)
    b = ganti_teks(b, teks)
    b = set_off(b, *off)
    if src != 'Text 7':
        b = set_ext(b, labW, labH)
    klon.append(b)
s2 = s2.replace('</p:spTree>', ''.join(klon) + '</p:spTree>', 1)

# grafik kanan (bar chart) diperbesar
for mm in re.finditer(r'<p:pic>.*?</p:pic>', s2, re.S):
    if 'rId2' in mm.group(0):
        b = mm.group(0)
        ox, oy = get_off(b)
        b = set_off(b, int(763.8 * P - 236 * P / 2), oy)
        b = set_ext(b, int(236 * P), int(236 / 1.0789 * P))
        s2 = s2.replace(mm.group(0), b, 1)
        break
simpan_slide(2, s2)
print('slide 2: kartu stat disusun ulang + Thailand 159k + grafik diperbesar')

# =====================================================================
# 2. TIPOGRAFI — apostrof & kutip ganda (semua slide)
# =====================================================================
def tipografi(x):
    def t(m):
        isi = m.group(1)
        isi = isi.replace('&apos;', '\u2019').replace('&#39;', '\u2019').replace("'", '\u2019')
        return f'<a:t>{isi}</a:t>'
    x = re.sub(r'<a:t>(.*?)</a:t>', t, x, flags=re.S)

    def per_para(m):
        p = m.group(0)
        if '&quot;' in p:
            ke = [0]

            def g(_m):
                ke[0] += 1
                return '\u201c' if ke[0] % 2 else '\u201d'
            p = re.sub(r'&quot;', g, p)
        return p
    return re.sub(r'<a:p>.*?</a:p>', per_para, x, flags=re.S)

for n in range(1, 18):
    simpan_slide(n, tipografi(slide(n)))
print('tipografi: apostrof dan kutip ganda dibereskan')

# =====================================================================
# 3. CATATAN PEMBICARA — dari dek native ke notesSlide Gamma
# =====================================================================
zn = zipfile.ZipFile(NATIVE)
catatan = {}


def unesc(t):
    return (t.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
             .replace('&apos;', "'").replace('&#39;', "'").replace('&amp;', '&'))


for n in sorted([n for n in zn.namelist() if re.match(r'ppt/notesSlides/notesSlide\d+\.xml$', n)],
                key=lambda s: int(re.search(r'(\d+)', s).group(1))):
    x = zn.read(n).decode('utf-8')
    par = []
    for m in re.finditer(r'<a:p>(.*?)</a:p>', x, re.S):
        t = unesc(''.join(re.findall(r'<a:t>(.*?)</a:t>', m.group(1), re.S)))
        for baris in re.split(r'\r?\n', t):
            if baris.strip():
                par.append(baris.strip())
    catatan[int(re.search(r'(\d+)', n).group(1))] = par


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def ap(t):
    return t.replace("'", '\u2019')


n_isi = 0
for i in range(1, 18):
    ns = f'ppt/notesSlides/notesSlide{i}.xml'
    x = items[ns].decode('utf-8')
    paras = catatan.get(i, [])
    if not paras:
        continue
    isi_xml = ''.join(
        f'<a:p><a:r><a:rPr lang="en-US" sz="1200" dirty="0"/><a:t>{esc(ap(t))}</a:t></a:r></a:p>'
        for t in paras)

    def ganti_body(m):
        blok = m.group(0)
        return re.sub(r'(<a:lstStyle/>).*?(</p:txBody>)', r'\1' + isi_xml + r'\2', blok, count=1, flags=re.S)

    x2 = re.sub(r'<p:sp>(?:(?!</p:sp>).)*?Notes Placeholder.*?</p:sp>', ganti_body, x, count=1, flags=re.S)
    if x2 != x:
        items[ns] = x2.encode('utf-8')
        n_isi += 1
print(f'catatan pembicara disuntikkan ke {n_isi} notesSlide')

with open(os.path.join(BASE, 'catatan.json'), 'w', encoding='utf-8') as f:
    json.dump([catatan.get(i, []) for i in range(1, 18)], f, ensure_ascii=False, indent=1)
print('catatan.json ditulis (dipakai buat-aman.js)')

# =====================================================================
# 4. NOMOR HALAMAN — kanan bawah, agar rujukan "p. 7/12/14" mudah dilacak
# =====================================================================
def nomor_halaman(x, teks):
    sp = (
        '<p:sp><p:nvSpPr><p:cNvPr id="90" name="Nomor Halaman"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="10922000" y="6553200"/><a:ext cx="609600" cy="203200"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
        '<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"/><a:lstStyle/>'
        f'<a:p><a:pPr algn="r" indent="0" marL="0"><a:buNone/></a:pPr>'
        f'<a:r><a:rPr lang="en-US" sz="900" dirty="0"><a:solidFill><a:srgbClr val="8A8F98"/></a:solidFill>'
        f'<a:latin typeface="Heebo"/></a:rPr><a:t>{teks}</a:t></a:r></a:p></p:txBody></p:sp>'
    )
    return x.replace('</p:spTree>', sp + '</p:spTree>', 1)

for n in range(2, 16):
    simpan_slide(n, nomor_halaman(slide(n), str(n)))
simpan_slide(16, nomor_halaman(slide(16), 'R1'))
simpan_slide(17, nomor_halaman(slide(17), 'R2'))
print('nomor halaman ditambahkan (2–15, R1, R2)')

# =====================================================================
# 5. SAMPUL GELAP — identitas storyboard: navy #0E2340, teks putih,
#    chip SDG merah/biru/oranye (tema Consultant aslinya putih polos)
# =====================================================================
s1 = slide(1)
s1 = s1.replace(
    '<p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></p:bgPr></p:bg>',
    '<p:bg><p:bgPr><a:solidFill><a:srgbClr val="0E2340"/></a:solidFill></p:bgPr></p:bg>', 1)


def warnai(nama, dari, ke):
    global s1
    blok = sp_of(s1, nama)
    s1 = s1.replace(blok, blok.replace(f'val="{dari}"', f'val="{ke}"'), 1)


warnai('Text 0', '152D47', 'FFFFFF')          # judul
warnai('Text 1', '4C4C4D', 'E7EDF5')          # subjudul + paragraf + baris tim
warnai('Text 8', '4C4C4D', '9FB0C7')          # "All charts..."
for sp_nama, warna in [('Shape 2', 'C53232'), ('Shape 4', '2A78D6'), ('Shape 6', 'E8833A')]:
    warnai(sp_nama, 'CCD7FF', warna)          # chip SDG: SDG3 / SDG13 / SDG6
for t_nama in ('Text 3', 'Text 5', 'Text 7'):
    warnai(t_nama, '4C4C4D', 'FFFFFF')
simpan_slide(1, s1)
print('sampul: navy gelap + chip SDG storyboard')

# =====================================================================
# tulis ulang pptx
# =====================================================================
with zipfile.ZipFile(DST, 'w', zipfile.ZIP_DEFLATED) as out:
    for n, b in items.items():
        out.writestr(n, b)
print('OK ->', os.path.relpath(DST))
