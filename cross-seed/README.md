# Home Assistant Add-on: Cross-Seed

![Version](https://img.shields.io/badge/version-1.0.1-blue)
![amd64](https://img.shields.io/badge/amd64-yes-green)
![aarch64](https://img.shields.io/badge/aarch64-yes-green)

[cross-seed](https://www.cross-seed.org/) daemon: automatically detects torrents you are already seeding and re-injects them on your other trackers (via Prowlarr/Torznab), without re-downloading any data.

## Features

- **Always-on daemon** — periodic search (`search_cadence`) + RSS feed (`rss_cadence`)
- **qBittorrent injection** — matches are added directly to the client, with duplicated categories
- **Safe/risky mode** — controls how strict matching must be
- **Multi-tracker** — as many Torznab URLs (Prowlarr) as you want

## Configuration

```yaml
torznab_urls:
  - "http://<ip>:9696/1/api?apikey=<key>"   # Prowlarr → indexer → Torznab
qbittorrent_url: "http://localhost:8080"
qbittorrent_user: "admin"
qbittorrent_pass: ""
link_dirs:
  - "/media/torrents/links"
match_mode: "safe"        # safe | risky
search_cadence: "1d"
rss_cadence: "30m"
log_level: "info"          # info | verbose | debug
```

> **Note**: Torznab URLs contain your Prowlarr API key, and the qBittorrent password ends up in the generated config. These values stay inside the add-on's `/data` and are never printed to the logs.

## Installation

1. Add this repository to the add-on store
2. Install **Cross-Seed**
3. Set at least one Torznab URL and your qBittorrent credentials
4. Start — the daemon listens on port `2468`

## Tech stack

- **App**: cross-seed 6.13.7 (npm)
- **Supported client**: qBittorrent (API ≥ 5.2 handled)
- **Config**: automatically generated at `/config/config.js` from HA options

## License

Add-on: MIT — cross-seed: Apache-2.0.
