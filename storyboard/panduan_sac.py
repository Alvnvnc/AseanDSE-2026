#!/usr/bin/env python3
"""Bangkitkan panduan kerja PDF untuk membangun 23 grafik di SAP Analytics Cloud.

Resep tiap grafik TIDAK diketik ulang di sini — dibaca langsung dari
`storyboard.tex` (argumen makro `\\sacslot`), jadi panduan dan dek tidak mungkin
berbeda isi. Kalau resep di dek diubah, jalankan ulang skrip ini.

Keluaran: `storyboard/panduan-sac.pdf` (A4 tegak, bahasa Indonesia — ini dokumen
kerja, bukan bahan submit).

Jalankan: python3 storyboard/panduan_sac.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

SINI = Path(__file__).resolve().parent
DEK = SINI / "storyboard.tex"
KELUAR = SINI / "panduan-sac.tex"

# Konteks tiap halaman dek: judul kerja + kenapa halaman itu ada.
HALAMAN = {
    "02": ("Masalah", "Beban dengue ASEAN. Dua grafik dari satu dataset."),
    "03": ("Pertanyaan", "Tanpa dataset — diagram alur murni Shapes + Text."),
    "05": ("Analisis 1: musim", "Dua widget kembar, beda filter negara."),
    "06": ("Analisis 2: jeda", "Heat map korelasi + scatter pendukung."),
    "07": ("Analisis 3: kartu as", "Halaman terpenting. Bar fase ENSO."),
    "08": ("Analisis 4: di mana \\& kapan", "Dua heat map kalender, IDN vs THA."),
    "09": ("Analisis 5: siapa paling terpukul", "Tiga bar sempit berdampingan."),
    "10": ("Sintesis: kalender risiko", "Heat map prioritas + deret alarm."),
    "11": ("Solusi", "Deret aturan melebar + bar perbandingan aturan."),
    "12": ("Kelayakan", "Uji luar sampel + tabel tolok ukur."),
    "13": ("Dampak", "Bar biaya + tabel tenggang waktu."),
    "14": ("Batas \\& etika data", "Scatter hasil nol — sengaja tanpa garis tren."),
}

# Urutan kerja per dataset: bangun semua grafik dari satu dataset sekaligus,
# supaya tidak bolak-balik ganti sumber data di SAC.
GUGUS = [
    ("Monthly series IDN-THA", ["h06-scatter-suhu", "h10-deret-alarm", "h11-deret-aturan"]),
    ("Dengue national annual", ["h02-tren-tahunan", "h02-per-negara"]),
    ("Risk calendar IDN", ["h08-kalender-idn", "h10-kalender-prioritas"]),
    ("Seasonality IDN-THA", ["h05-musiman-idn", "h05-musiman-tha"]),
    ("Lag correlation - national / anomaly", ["h06-heatmap-jeda", "h07-anomali"]),
    ("ENSO phase - averages", ["h07-fase-enso"]),
    ("Risk calendar THA", ["h08-kalender-tha"]),
    ("Province incidence 18-20 / WASH / City flood",
     ["h09-insidens", "h09-wash", "h09-banjir"]),
    ("Trigger rules - evaluation / out of sample / EWS benchmark",
     ["h11-aturan", "h12-luar-sampel", "h12-tolok-ukur"]),
    ("Monetary impact / El Nino episodes", ["h13-dampak", "h13-tenggang"]),
    ("Drought x water access", ["h14-kekeringan"]),
    ("tanpa dataset", ["h03-alur"]),
]


def baca_slot() -> list[dict]:
    """Ambil argumen \\sacslot dari dek: lebar, tinggi, nama, judul, jenis, resep."""
    baris = DEK.read_text(encoding="utf-8").splitlines()
    tex = "\n".join(b for b in baris if not b.lstrip().startswith("%"))

    def argumen(s: str, i: int) -> list[str]:
        out: list[str] = []
        while i < len(s) and s[i] in " \n\t":
            i += 1
        while i < len(s) and s[i] == "{":
            dalam, j = 0, i
            while j < len(s):
                if s[j] == "{":
                    dalam += 1
                elif s[j] == "}":
                    dalam -= 1
                    if dalam == 0:
                        break
                j += 1
            out.append(s[i + 1:j])
            i = j + 1
            while i < len(s) and s[i] in " \n\t":
                i += 1
        return out

    slot = []
    for m in re.finditer(r"\\sacslot", tex):
        a = argumen(tex, m.end())
        if len(a) < 8:
            continue
        rapi = lambda t: " ".join(t.split())  # noqa: E731
        slot.append({"lebar": int(a[2]), "tinggi": int(a[3]), "nama": a[4],
                     "judul": rapi(a[5]), "jenis": rapi(a[6]), "resep": rapi(a[7]),
                     "halaman": a[4][1:3]})
    return slot


def lebar_ekspor(bp: int) -> int:
    """Lebar PNG minimal: 2,5x lebar slot, dibulatkan ke atas per 100 px, min 1600."""
    return max(1600, -(-int(bp * 2.5) // 100) * 100)


PREAMBUL = r"""\documentclass[10pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{textcomp}
\usepackage[left=17mm,right=17mm,top=16mm,bottom=17mm]{geometry}
\usepackage{tgheros}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{array}

\definecolor{accent}{HTML}{2A78D6}
\definecolor{alarm}{HTML}{E8833A}
\definecolor{peak}{HTML}{C53232}
\definecolor{muted}{HTML}{8A8F98}
\definecolor{ink}{HTML}{14202E}
\definecolor{soft}{HTML}{F2F5F9}
\definecolor{line}{HTML}{C9D3E0}

\color{ink}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyfoot[L]{\footnotesize\color{muted}Panduan kerja SAC \textbullet\ ASEAN DSE 2026
  \textbullet\ dibangkitkan \texttt{storyboard/panduan\_sac.py}}
\fancyfoot[R]{\footnotesize\color{muted}\thepage}

% judul bagian
\newcommand{\bagian}[1]{%
  \par\vspace{11pt}%
  {\color{accent}\rule{\linewidth}{1.6pt}}\par\vspace{3pt}%
  {\fontsize{13}{16}\selectfont\bfseries #1}\par\vspace{2pt}}
\newcommand{\subbagian}[1]{%
  \par\vspace{7pt}{\fontsize{11}{13}\selectfont\bfseries\color{accent} #1}\par\vspace{1pt}}

% kotak centang
\newcommand{\kotak}{\tikz[baseline=-0.05em]{\draw[line width=0.7pt, color=muted,
  rounded corners=1pt] (0,0) rectangle (0.62em,0.62em);}}

% contoh warna
\newcommand{\swatch}[1]{\tikz[baseline=-0.15em]{\fill[#1, rounded corners=1.5pt]
  (0,0) rectangle (1.5em,0.72em);}}

% blok satu slot grafik
% \slot{nama-berkas}{judul}{jenis}{resep}{ukuran}
\newcommand{\slotblok}[5]{%
  \par\vspace{6pt}%
  \noindent\begin{minipage}{\linewidth}%
  \kotak\ \texttt{\bfseries #1.png}\hfill{\footnotesize\color{muted}#5}\par
  \vspace{1pt}{\color{muted}\rule{\linewidth}{0.4pt}}\par\vspace{3pt}
  {\small\textbf{#2}}\par\vspace{1pt}
  {\small\color{accent}#3}\par\vspace{2pt}
  {\footnotesize #4}\par
  \end{minipage}\par\vspace{2pt}}
"""


def bangun_tex(slot: list[dict]) -> str:
    per_hal: dict[str, list[dict]] = {}
    for s in slot:
        per_hal.setdefault(s["halaman"], []).append(s)

    b: list[str] = [PREAMBUL, r"\begin{document}", ""]
    t = b.append

    # ---------------------------------------------------------------- sampul
    t(r"{\fontsize{21}{25}\selectfont\bfseries Membangun 23 grafik di SAP Analytics Cloud}\par")
    t(r"\vspace{2pt}{\fontsize{12}{15}\selectfont\color{muted}"
      r"ASEAN DSE 2026 \textbullet\ \textit{Four Months' Notice} \textbullet\ "
      r"panduan kerja, bukan bahan submit}\par")
    t(r"\vspace{4pt}{\color{alarm}\rule{\linewidth}{2.5pt}}\par")

    t(r"\bagian{Posisi Anda sekarang}")
    t(r"Dataset sudah diimpor ke SAC. Yang tersisa: membuat "
      f"{len(slot)} grafik, mengekspornya jadi PNG, lalu satu perintah untuk "
      r"merakit dek. Tata letak dek \textbf{tidak perlu disentuh} --- setiap kotak "
      r"putus-putus di \texttt{storyboard.pdf} otomatis berganti jadi gambar begitu "
      r"berkas PNG-nya ada.")

    t(r"\begin{enumerate}[leftmargin=1.4em, itemsep=2pt, topsep=3pt]")
    t(r"\item[\textbf{1.}] \textbf{Selesai} --- impor dataset "
      r"(\texttt{ekspor-csv/}, urutan di \texttt{IMPOR-SAC.md}).")
    t(r"\item[\textbf{2.}] Buat grafiknya di SAC mengikuti katalog di halaman berikut. "
      r"Bekerja per \emph{dataset}, bukan per halaman dek --- lihat urutan yang disarankan.")
    t(r"\item[\textbf{3.}] Ekspor tiap widget jadi PNG, simpan ke "
      r"\texttt{storyboard/gambar-sac/} dengan \textbf{nama persis} seperti di katalog.")
    t(r"\item[\textbf{4.}] Jalankan \texttt{./storyboard/bangun.sh} --- ia mengompilasi dek, "
      r"melaporkan slot mana yang masih kosong, dan memeriksa aturan panitia "
      r"(15 halaman, 20 MB, 2 MB per gambar).")
    t(r"\item[\textbf{5.}] Isi nama tim \& institusi di \texttt{storyboard.tex}, "
      r"lalu salin PDF-nya jadi \texttt{INDONESIA\_<NAMA TIM>.pdf}.")
    t(r"\end{enumerate}")

    t(r"\bagian{Setel sekali di awal}")
    t(r"\subbagian{Palet --- pakai di setiap grafik}")
    t(r"Grafik SAC harus menyatu dengan dek. Setel warna seri secara manual di tiap "
      r"widget (\textit{Styling} $\rightarrow$ warna seri); tema bawaan SAC akan "
      r"menabrak palet dek.")
    t(r"\vspace{2pt}\par")
    t(r"\begin{tabular}{@{}l l l@{}}")
    t(r"\swatch{accent} & \texttt{\#2A78D6} & kasus, kondisi normal \\[2pt]")
    t(r"\swatch{alarm} & \texttt{\#E8833A} & alarm, El Ni\~no \\[2pt]")
    t(r"\swatch{peak} & \texttt{\#C53232} & puncak, wabah \\[2pt]")
    t(r"\swatch{muted} & \texttt{\#8A8F98} & konteks, garis ambang \\")
    t(r"\end{tabular}")

    t(r"\subbagian{Syarat ekspor gambar (aturan panitia)}")
    t(r"\begin{itemize}[leftmargin=1.2em, itemsep=1pt, topsep=2pt]")
    t(r"\item Format \textbf{PNG}, latar \textbf{putih atau transparan} --- "
      r"jangan tema gelap SAC.")
    t(r"\item Lebar minimal tertera di tiap entri katalog (2,5$\times$ lebar slot). "
      r"Ini yang membuat grafik tetap tajam saat juri memperbesar.")
    t(r"\item \textbf{Maksimal 2 MB per gambar.} Kalau lewat: "
      r"\texttt{mogrify -resize 1800x -strip -quality 92 nama.png}")
    t(r"\item Judul grafik di dalam gambar boleh dimatikan --- dek sudah mencetak "
      r"judulnya sendiri di atas slot. Yang wajib terbaca: label sumbu, legenda, "
      r"label data.")
    t(r"\end{itemize}")

    t(r"\subbagian{Tiga jebakan yang membuat grafik diam-diam salah}")
    t(r"\begin{enumerate}[leftmargin=1.4em, itemsep=2pt, topsep=2pt]")
    t(r"\item \texttt{year}, \texttt{month}, \texttt{order}, \texttt{lag} ditebak SAC "
      r"sebagai \textit{Measure} lalu \textbf{dijumlahkan}. Ubah jadi "
      r"\textit{Dimension} di layar impor. Kebalikannya: \texttt{status\_code} "
      r"\textbf{harus tetap Measure} --- itu yang jadi warna heat map halaman 10.")
    t(r"\item \texttt{date} bertipe \textbf{Date} (\texttt{yyyy-MM-dd}); "
      r"\texttt{period} biarkan \textbf{teks}.")
    t(r"\item \texttt{month\_name} dan \texttt{enso\_phase\_lag4} terurut alfabetis "
      r"(Apr, Aug, Dec\dots). Betulkan lewat \textit{Sort by} \texttt{month} / "
      r"\texttt{order}, atau pakai kolom angkanya di sumbu.")
    t(r"\end{enumerate}")

    t(r"\subbagian{Membuat dan mengekspor satu grafik --- diulang " + str(len(slot)) + r"$\times$}")
    t(r"\begin{enumerate}[leftmargin=1.4em, itemsep=1pt, topsep=2pt]")
    t(r"\item \textit{Stories} $\rightarrow$ buka story Anda $\rightarrow$ "
      r"\textit{Insert} $\rightarrow$ \textbf{Chart}.")
    t(r"\item Panel \textit{Builder}: pilih dataset, lalu isi \textit{Measures} dan "
      r"\textit{Dimensions} sesuai resep.")
    t(r"\item Terapkan \textit{Filters}, \textit{Sort}, dan warna dari resep. "
      r"\textit{Reference line} ada di \textit{Styling} $\rightarrow$ "
      r"\textit{Chart Reference Line}.")
    t(r"\item Widget \textit{\textbf{$\vdots$}} $\rightarrow$ \textit{Export} "
      r"$\rightarrow$ \textbf{PNG}. Kalau menu itu tidak ada: "
      r"\textit{Export} $\rightarrow$ \textit{PDF} untuk seluruh halaman lalu potong "
      r"per widget, atau tangkap layar pada tampilan penuh.")
    t(r"\item Simpan ke \texttt{storyboard/gambar-sac/} dengan nama dari katalog.")
    t(r"\end{enumerate}")

    # ---------------------------------------------------------------- urutan kerja
    t(r"\bagian{Urutan kerja yang disarankan --- per dataset, bukan per halaman}")
    t(r"Ganti dataset di SAC jauh lebih mahal daripada ganti jenis grafik. "
      r"Kelompok di bawah mengurutkan " + str(len(slot)) + r" grafik menurut sumber datanya, "
      r"jadi satu dataset cukup dibuka sekali.")
    t(r"\vspace{3pt}\par")
    t(r"\begin{tabular}{@{}p{0.40\linewidth} p{0.56\linewidth}@{}}")
    for dataset, nama_slot in GUGUS:
        kiri = r"\small\textbf{" + dataset.replace("&", r"\&") + "}"
        kanan = r"\small\texttt{" + r"} \texttt{".join(n for n in nama_slot) + "}"
        t(kiri + " & " + kanan + r" \\[4pt]")
    t(r"\end{tabular}")

    # ---------------------------------------------------------------- katalog
    t(r"\bagian{Katalog " + str(len(slot)) + r" slot grafik}")
    t(r"Nama berkas \textbf{harus persis}. Ukuran di kanan atas tiap entri = ukuran "
      r"slot di dek dan lebar PNG minimal yang sepadan.")

    for hal in sorted(per_hal):
        judul, ket = HALAMAN.get(hal, ("", ""))
        t(r"\subbagian{Halaman " + str(int(hal)) + r" --- " + judul + r"}")
        t(r"{\footnotesize\color{muted}" + ket + r"}\par")
        for s in per_hal[hal]:
            ukuran = (f"slot {s['lebar']}$\\times${s['tinggi']} bp "
                      f"\\textbullet\\ ekspor $\\geq$ {lebar_ekspor(s['lebar'])} px")
            t(r"\slotblok{" + s["nama"] + "}{" + s["judul"] + "}{" + s["jenis"]
              + "}{" + s["resep"] + "}{" + ukuran + "}")

    # ---------------------------------------------------------------- checklist
    t(r"\bagian{Cek terakhir sebelum submit}")
    t(r"\texttt{bangun.sh} sudah memeriksa empat yang pertama secara otomatis. "
      r"Sisanya harus dibaca sendiri.")
    t(r"\begin{itemize}[leftmargin=1.4em, itemsep=3pt, topsep=3pt, label={\kotak}]")
    for butir in [
        r"23 slot terisi --- \texttt{bangun.sh} melaporkan sisa yang kosong",
        r"Tidak ada PNG di atas 2 MB",
        r"Total PDF di bawah 20 MB",
        r"15 halaman isi persis; halaman Referensi di luar hitungan",
        r"Nama tim, institusi, dan negara sudah diisi di \texttt{storyboard.tex} "
        r"(tiga baris \texttt{\textbackslash NamaTim} dkk.)",
        r"Setiap grafik benar-benar dibuat di SAC --- bukan gambar dari notebook. "
        r"Purwarupa di \texttt{analisis/gambar/} hanya acuan bentuk",
        r"Judul cerita konsisten dengan temuan: hujan \textbf{bukan} prediktor utama",
        r"Tidak ada klaim ``rekor 2023--24'' dari data sendiri "
        r"(Vietnam \& Filipina hanya lengkap sampai 2022)",
        r"Tidak ada peringkat wilayah memakai kasus mentah --- insidens hanya 2018--2020",
        r"Sensitivitas 44\% disebutkan, tidak disembunyikan",
        r"Skenario 10\% ditandai sebagai asumsi, bukan temuan",
        r"Sumber tercantum di kaki tiap halaman berdata",
        r"Berkas disalin jadi \texttt{INDONESIA\_<NAMA TIM>.pdf}",
    ]:
        t(r"\item " + butir)
    t(r"\end{itemize}")

    t(r"\bagian{Kalau ada yang meleset}")
    t(r"\begin{itemize}[leftmargin=1.2em, itemsep=2pt, topsep=2pt]")
    t(r"\item \textbf{Angka di grafik beda dengan naskah} --- hampir selalu tipe kolom. "
      r"Periksa \texttt{year}/\texttt{month} tidak sedang dijumlahkan sebagai Measure.")
    t(r"\item \textbf{Bulan terurut Apr, Aug, Dec} --- \textit{Sort by} kolom angkanya, "
      r"bukan kolom namanya.")
    t(r"\item \textbf{Provinsi hilang di peta/heat map} --- nama provinsi sengaja tidak "
      r"diterjemahkan supaya penjodohan geografis tidak pecah; jangan diedit di SAC.")
    t(r"\item \textbf{Slot tetap kosong setelah PNG ditaruh} --- nama berkas beda satu "
      r"karakter. \texttt{bangun.sh} mencetak nama yang dicarinya.")
    t(r"\end{itemize}")

    t(r"\end{document}")
    return "\n".join(b) + "\n"


def main() -> int:
    if not DEK.exists():
        print(f"tidak menemukan {DEK}", file=sys.stderr)
        return 1
    slot = baca_slot()
    if not slot:
        print("tidak ada \\sacslot yang terbaca di storyboard.tex", file=sys.stderr)
        return 1
    KELUAR.write_text(bangun_tex(slot), encoding="utf-8")
    print(f"{len(slot)} slot terbaca dari storyboard.tex -> {KELUAR.name}")

    if not shutil.which("pdflatex"):
        print("pdflatex tidak ada; .tex sudah ditulis, kompilasi manual.")
        return 0
    for lintasan in (1, 2):
        hasil = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-file-line-error", KELUAR.name],
            cwd=SINI, capture_output=True, text=True)
        if hasil.returncode != 0:
            print(f"GAGAL pada lintasan {lintasan}:", file=sys.stderr)
            for b in hasil.stdout.splitlines():
                if b.startswith("./panduan-sac.tex:") or b.startswith("! "):
                    print("  " + b, file=sys.stderr)
            return 1
    pdf = SINI / "panduan-sac.pdf"
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    hal = re.search(r"^Pages:\s+(\d+)", info, re.M)
    print(f"  {pdf.relative_to(SINI.parent)}  "
          f"{hal.group(1) if hal else '?'} halaman, {pdf.stat().st_size/1e3:.0f} KB")
    for tmp in ("panduan-sac.aux", "panduan-sac.log", "panduan-sac.out"):
        (SINI / tmp).unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
