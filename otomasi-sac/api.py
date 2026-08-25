"""Panggil REST internal SAC dari dalam halaman (pakai sesi + CSRF token yang ada)."""
from __future__ import annotations
import json

JS = r"""
async ([path, body]) => {
  const r = await fetch(path, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json;charset=UTF-8',
      'x-csrf-token': window.FPA_CSRF_TOKEN || '',
      'x-sap-fpa-app-name': 'story2',
    },
    credentials: 'include',
    body: JSON.stringify(body),
  });
  const t = await r.text();
  return {status: r.status, text: t};
}
"""


def panggil(page, path: str, body: dict):
    hasil = page.evaluate(JS, [path, body])
    teks = hasil["text"]
    try:
        return hasil["status"], json.loads(teks)
    except Exception:
        return hasil["status"], teks


def contentlib(page, action: str, data: dict):
    return panggil(page, "/sap/fpa/services/rest/epm/contentlib?tenant=O",
                   {"action": action, "data": data})
