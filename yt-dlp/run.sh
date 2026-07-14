#!/bin/sh
set -e

CONFIG=/data/options.json

export OUTPUT_DIR=$(jq -r '.output_dir' $CONFIG)
export DEFAULT_QUALITY=$(jq -r '.default_quality' $CONFIG)
export JELLYFIN_NAMING=$(jq -r '.jellyfin_naming' $CONFIG)
export EMBED_THUMBNAIL=$(jq -r '.embed_thumbnail' $CONFIG)
export EMBED_METADATA=$(jq -r '.embed_metadata' $CONFIG)
export PREFERRED_CODEC=$(jq -r '.preferred_codec' $CONFIG)
export INGRESS_PATH=""

echo "[ytdlp] Starting yt-dlp Downloader..."
echo "[ytdlp] Output: ${OUTPUT_DIR}"

cd /app
exec python3 server.py
