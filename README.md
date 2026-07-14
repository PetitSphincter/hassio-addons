# PetitSphincter Home Assistant Add-ons

![Add repository on my Home Assistant][repository-badge]][repository-url]
![Addons](https://img.shields.io/badge/addons-7-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A Home Assistant add-on repository focused on **media stack & self-hosting**: IPTV, downloading, seedbox tooling, dashboards and S3 utilities.

## Installation

Click the button above, or manually:

1. **Settings → Add-ons → Add-on Store**
2. **⋮** menu (top right) → **Repositories**
3. Add: `https://github.com/PetitSphincter/hassio-addons`
4. The add-ons appear at the bottom of the store.

## Add-ons

| Add-on | Version | Description | Arch |
|---|---|---|---|
| [Cross-Seed](cross-seed/) | ![v](https://img.shields.io/badge/1.0.1-blue) | Automatic cross-seeding daemon across trackers via Prowlarr + qBittorrent | ![a](https://img.shields.io/badge/amd64%20%7C%20aarch64-lightgrey) |
| [Dispatcharr](dispatcharr/) | ![v](https://img.shields.io/badge/0.1.0-blue) | IPTV stream manager & HDHomeRun emulator for Jellyfin/Plex/Emby | ![a](https://img.shields.io/badge/amd64%20%7C%20aarch64-lightgrey) |
| [Heimdall](heimdall/) | ![v](https://img.shields.io/badge/0.1.0-blue) | Application dashboard and service launcher | ![a](https://img.shields.io/badge/amd64%20%7C%20aarch64-lightgrey) |
| [S3 Browser](s3-browser/) | ![v](https://img.shields.io/badge/0.2.0-blue) | Read-only S3 browser (AWS, Scality, MinIO…) | ![a](https://img.shields.io/badge/amd64%20%7C%20aarch64-lightgrey) |
| [Traffic Map](traffic-map/) | ![v](https://img.shields.io/badge/1.0.0-blue) | Generates a road traffic map image (CartoDB basemap + Azure Maps overlay) | ![a](https://img.shields.io/badge/multi--arch-lightgrey) |
| [Ygege](ygege/) | ![v](https://img.shields.io/badge/1.0.0-blue) | YGG Torrent indexer via Nostr relay, for Prowlarr | ![a](https://img.shields.io/badge/amd64%20%7C%20aarch64%20%7C%20armv7-lightgrey) |
| [yt-dlp Downloader](yt-dlp/) | ![v](https://img.shields.io/badge/0.2.0-blue) | YouTube video/playlist downloads, Jellyfin naming, chapters, MP3 | ![a](https://img.shields.io/badge/amd64%20%7C%20aarch64-lightgrey) |

## Philosophy

- **Thin wrappers**: when an official image exists (Dispatcharr, Heimdall), the add-on wraps it with the bare minimum (ingress, HA options, `/data` persistence).
- **Ingress first**: sidebar access whenever possible, direct ports when required (HDHomeRun API, daemons…).
- **No secrets in the repo**: all keys/credentials go through add-on options (`password` schema).

## Support

Having an issue? Open an [issue](https://github.com/PetitSphincter/hassio-addons/issues) with the add-on logs (**Settings → Add-ons → [add-on] → Log**).

## License

MIT — bundled applications keep their respective licenses (see each add-on's README).
