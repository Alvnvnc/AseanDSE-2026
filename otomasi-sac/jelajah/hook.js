(() => {
  window.__log = [];
  const of = window.fetch;
  window.fetch = function (input, init) {
    const u = (typeof input === 'string') ? input : (input && input.url);
    const rec = {m: (init && init.method) || 'GET', u: String(u),
                 body: (init && init.body) ? String(init.body).slice(0, 4000000) : null, k: 'fetch'};
    window.__log.push(rec);
    return of.apply(this, arguments).then(r => { rec.status = r.status; return r; });
  };
  const oo = XMLHttpRequest.prototype.open, os = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (m, u) { this.__m = m; this.__u = u; return oo.apply(this, arguments); };
  XMLHttpRequest.prototype.send = function (body) {
    const rec = {m: this.__m, u: String(this.__u), body: body ? String(body).slice(0, 4000000) : null, k: 'xhr'};
    window.__log.push(rec);
    this.addEventListener('load', () => { rec.status = this.status; rec.len = (this.responseText||'').length;
                                          rec.resp = (this.responseText||'').slice(0,8000); });
    return os.apply(this, arguments);
  };
})();
