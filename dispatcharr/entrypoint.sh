#!/bin/sh
set -e

OPTIONS=/data/options.json

echo "[dispatcharr-addon] Initializing..."

# ── Read HA addon options ──
if [ -f "$OPTIONS" ]; then
    export TZ=$(jq -r '.TZ // "Europe/Paris"' "$OPTIONS")
    export DISPATCHARR_LOG_LEVEL=$(jq -r '.log_level // "info"' "$OPTIONS")
    echo "[dispatcharr-addon] TZ=${TZ} LOG_LEVEL=${DISPATCHARR_LOG_LEVEL}"
fi

# ── Dispatcharr environment (AIO mode: Redis + Celery + Web in one container) ──
export DISPATCHARR_ENV=aio
export REDIS_HOST=localhost
export CELERY_BROKER_URL=redis://localhost:6379/0

# /data is already persistent in HA addons — Dispatcharr writes directly here
# options.json coexists fine alongside Dispatcharr's own data files

echo "[dispatcharr-addon] Starting Dispatcharr (AIO mode)..."
echo "[dispatcharr-addon] Web UI: port 9191"
echo "[dispatcharr-addon] HDHomeRun API: port 9191/hdhr"

# ── Hand off to Dispatcharr's original entrypoint ──
if [ -f /app/docker/entrypoint.sh ]; then
    exec /app/docker/entrypoint.sh
elif [ -f /entrypoint.sh ]; then
    exec /entrypoint.sh
else
    echo "[dispatcharr-addon] ERROR: Could not find Dispatcharr entrypoint"
    echo "[dispatcharr-addon] Trying default supervisord..."
    exec supervisord -n 2>/dev/null || exec python3 /app/manage.py runserver 0.0.0.0:9191
fi
