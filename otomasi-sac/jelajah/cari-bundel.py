"""Cari pola teks di seluruh bundel JS yang sudah dimuat halaman."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from playwright.sync_api import sync_playwright
import sac

pola = sys.argv[1]
konteks = int(sys.argv[2]) if len(sys.argv) > 2 else 90
maks = int(sys.argv[3]) if len(sys.argv) > 3 else 60

JS = """async ([pola, konteks, maks]) => {
  const re = new RegExp(pola, 'g');
  const urls = [...new Set(performance.getEntriesByType('resource')
      .map(e => e.name).filter(u => /\\.js(\\?|$)/.test(u)))];
  const hasil = [];
  let byte = 0;
  for (const u of urls) {
    let t;
    try { t = await (await fetch(u)).text(); } catch (e) { continue; }
    byte += t.length;
    let m;
    re.lastIndex = 0;
    while ((m = re.exec(t)) !== null) {
      hasil.push({u: u.split('/').slice(-2).join('/'),
                  s: t.slice(Math.max(0, m.index - konteks), m.index + konteks)});
      if (hasil.length >= maks) return {urls: urls.length, byte, hasil};
    }
  }
  return {urls: urls.length, byte, hasil};
}"""

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    r = page.evaluate(JS, [pola, konteks, maks])
print(f"berkas js: {r['urls']}  total byte: {r['byte']:,}  cocok: {len(r['hasil'])}")
for h in r["hasil"]:
    print(f"--- {h['u']}\n    {h['s']}")
