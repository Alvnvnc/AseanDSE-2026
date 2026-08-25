#!/usr/bin/env bash
# Jalankan satu instance Edge terpisah (profil sendiri) dengan port debug CDP 9222.
# Browser Edge Anda yang biasa tidak terganggu.
set -u
D=/home/alvn/.cache/edge-sac
S=/home/alvn/.config/microsoft-edge
LOG=${LOG:-/tmp/edge-sac.log}

if [ "${1:-}" = "--reset" ]; then
  for pid in $(pgrep -x msedge); do
    tr "\0" " " < /proc/$pid/cmdline 2>/dev/null | grep -q "edge-sac" && kill "$pid"
  done
  sleep 2
  rm -rf "$D"
fi

if [ ! -d "$D/Default" ]; then
  mkdir -p "$D/Default"
  cp -f "$S/Local State" "$D/" 2>/dev/null
  cp -f "$S/Default/Cookies" "$D/Default/" 2>/dev/null
  cp -f "$S/Default/Cookies-journal" "$D/Default/" 2>/dev/null
  cp -rf "$S/Default/Local Storage" "$D/Default/" 2>/dev/null
fi

if curl -sS --max-time 3 http://127.0.0.1:9222/json/version >/dev/null 2>&1; then
  echo "sudah jalan"; exit 0
fi

nohup /usr/bin/microsoft-edge-stable \
  --user-data-dir="$D" \
  --remote-debugging-port=9222 \
  --remote-allow-origins='*' \
  --disable-extensions \
  --no-first-run --no-default-browser-check --disable-sync \
  --window-size=1920,1200 \
  about:blank > "$LOG" 2>&1 &

for i in $(seq 1 30); do
  sleep 1
  curl -sS --max-time 2 http://127.0.0.1:9222/json/version >/dev/null 2>&1 && { echo "siap"; exit 0; }
done
echo "gagal siap"; exit 1
