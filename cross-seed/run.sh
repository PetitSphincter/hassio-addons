#!/bin/sh
set -e

CONFIG_FILE="/data/options.json"
CS_CONFIG_DIR="/config"
CS_CONFIG="${CS_CONFIG_DIR}/config.js"

mkdir -p "${CS_CONFIG_DIR}"

# Read options from HA
QB_URL=$(jq -r '.qbittorrent_url' "$CONFIG_FILE")
QB_USER=$(jq -r '.qbittorrent_user' "$CONFIG_FILE")
QB_PASS=$(jq -r '.qbittorrent_pass' "$CONFIG_FILE")
MATCH_MODE=$(jq -r '.match_mode' "$CONFIG_FILE")
SEARCH_CADENCE=$(jq -r '.search_cadence' "$CONFIG_FILE")
RSS_CADENCE=$(jq -r '.rss_cadence' "$CONFIG_FILE")

# Build torznab array as JS
TORZNAB_JS=$(jq -r '.torznab_urls | map("    \"" + . + "\"") | join(",\n")' "$CONFIG_FILE")

# Build linkDirs array as JS
LINK_DIRS_JS=$(jq -r '.link_dirs | map("    \"" + . + "\"") | join(",\n")' "$CONFIG_FILE")

# Generate config.js
jq -n \
  --argjson torznab "$(jq '.torznab_urls' "$CONFIG_FILE")" \
  --arg qb_url "qbittorrent:http://${QB_USER}:${QB_PASS}@${QB_URL#http://}" \
  --argjson linkDirs "$(jq '.link_dirs' "$CONFIG_FILE")" \
  --arg matchMode "$MATCH_MODE" \
  --arg searchCadence "$SEARCH_CADENCE" \
  --arg rssCadence "$RSS_CADENCE" \
'{
  torznab: $torznab,
  torrentClients: [$qb_url],
  linkDirs: $linkDirs,
  matchMode: $matchMode,
  searchCadence: $searchCadence,
  rssCadence: $rssCadence,
  action: "inject",
  duplicateCategories: true,
  useClientTorrents: true,
  excludeOlder: "10d",
  excludeRecentSearch: "3d",
  port: 2468
}' > /tmp/cs_config.json

# Convert JSON to JS module
printf "module.exports = %s;\n" "$(cat /tmp/cs_config.json)" > "${CS_CONFIG}"

echo "[cross-seed] Config generated at ${CS_CONFIG}"
echo "[cross-seed] qBittorrent: ${QB_URL}"
echo "[cross-seed] Torznab sources: $(jq -r '.torznab_urls | length' "$CONFIG_FILE")"
echo "[cross-seed] Starting cross-seed daemon..."

export CONFIG_DIR=/config
exec cross-seed daemon
