#!/bin/sh
set -e

OPTIONS=/data/options.json
HEIMDALL_DATA=/data/heimdall

echo "[heimdall-addon] Initializing..."

# ── Read HA addon options ──
if [ -f "$OPTIONS" ]; then
    export TZ=$(jq -r '.TZ // "Europe/Paris"' "$OPTIONS")
    export PUID=$(jq -r '.PUID // 0' "$OPTIONS")
    export PGID=$(jq -r '.PGID // 0' "$OPTIONS")
    echo "[heimdall-addon] TZ=${TZ} PUID=${PUID} PGID=${PGID}"
fi

# ── Persistent data ──
# On restore /data/heimdall → /config au boot
# Et on sauvegarde /config → /data/heimdall à l'arrêt
if [ -d "$HEIMDALL_DATA" ] && [ "$(ls -A "$HEIMDALL_DATA" 2>/dev/null)" ]; then
    echo "[heimdall-addon] Restoring data from previous run..."
    cp -a "$HEIMDALL_DATA"/. /config/ 2>/dev/null || true
else
    echo "[heimdall-addon] First run — will persist on shutdown"
    mkdir -p "$HEIMDALL_DATA"
fi

# ── Background sync: /config → /data/heimdall every 60s ──
(
    while true; do
        sleep 60
        cp -a /config/. "$HEIMDALL_DATA/" 2>/dev/null || true
    done
) &

# ── Inject ingress-aware nginx config ──
NGINX_CONF_DIR="/config/nginx/site-confs"
mkdir -p "$NGINX_CONF_DIR"
cp /defaults/nginx-ingress.conf "$NGINX_CONF_DIR/default.conf"
echo "[heimdall-addon] Nginx ingress config injected"

echo "[heimdall-addon] Starting Heimdall..."

# ── Hand off to linuxserver's s6-overlay init ──
exec /init