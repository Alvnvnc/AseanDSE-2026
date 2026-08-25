"""Pasang hook fetch/XHR di halaman, muat ulang story, lalu dump semua panggilan."""
import json, sys, time
from collections import Counter
from playwright.sync_api import sync_playwright
import sac

OUT = sys.argv[1]
HOOK = r"""
(() => {
  window.__log = [];
  const push = (m, u, body, extra) => {
    try { window.__log.push({m, u: String(u), body: body ? String(body).slice(0, 4000) : null, ...extra}); }
    catch (e) {}
  };
  const of = window.fetch;
  window.fetch = function (input, init) {
    const u = (typeof input === 'string') ? input : (input && input.url);
    const m = (init && init.method) || (input && input.method) || 'GET';
    const body = init && init.body;
    const rec = {m, u: String(u), body: body ? String(body).slice(0, 4000) : null, k: 'fetch'};
    window.__log.push(rec);
    return of.apply(this, arguments).then(r => { rec.status = r.status; return r; });
  };
  const oo = XMLHttpRequest.prototype.open, os = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (m, u) { this.__m = m; this.__u = u; return oo.apply(this, arguments); };
  XMLHttpRequest.prototype.send = function (body) {
    const rec = {m: this.__m, u: String(this.__u), body: body ? String(body).slice(0, 4000) : null, k: 'xhr'};
    window.__log.push(rec);
    this.addEventListener('load', () => { rec.status = this.status; rec.len = (this.responseText || '').length; });
    return os.apply(this, arguments);
  };
})();
"""

with sync_playwright() as p:
    b, ctx, page = sac.sambung(p)
    page.add_init_script(HOOK)
    page.goto("about:blank")
    page.goto(sac.STORY_URL, wait_until="domcontentloaded", timeout=120000)
    time.sleep(60)
    log = page.evaluate("() => window.__log || []")

json.dump(log, open(OUT, "w"), indent=1)
c = Counter(f"{d.get('m')} {d.get('u','').split('?')[0]}" for d in log)
for k, v in c.most_common(60):
    print(f"{v:3d}  {k[:170]}")
print("total:", len(log), "->", OUT)
