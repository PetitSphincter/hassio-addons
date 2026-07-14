# Home Assistant Add-on: Dispatcharr

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![amd64](https://img.shields.io/badge/amd64-yes-green)
![aarch64](https://img.shields.io/badge/aarch64-yes-green)

IPTV manager and HDHomeRun emulator integrated into Home Assistant. Exposes your IPTV streams to Jellyfin, Plex or Emby as a Live TV source.

## Features

- **M3U / Xtream Codes import** — bring in your IPTV playlists
- **HDHomeRun emulation** — Jellyfin/Plex/Emby detect Dispatcharr as a TV tuner
- **EPG auto-match** — automatic program-to-channel mapping
- **Streaming proxy** — stream relaying with automatic failover
- **FFmpeg transcoding** — stream optimization for different clients
- **Real-time monitoring** — bandwidth and stream health stats
- **VOD** — Video on Demand support with TMDB/IMDB metadata

## Installation

1. Add this repository to the add-on store (**⋮ → Repositories**)
2. Install **Dispatcharr**
3. Start it (first startup can take a while)

## Access

- **HA sidebar** (ingress): click "Dispatcharr" in the sidebar
- **Direct port**: `http://<home-assistant-ip>:9191`

> **Important**: port 9191 must be directly reachable for Jellyfin to hit the HDHomeRun API. Ingress alone is not enough for the Live TV integration.

## Jellyfin setup

Once Dispatcharr is running and your channels are imported:

1. Jellyfin → Dashboard → **Live TV**
2. Add a tuner → **HDHomeRun**
3. Tuner URL: `http://<home-assistant-ip>:9191/hdhr`
4. Add a guide → **XMLTV**
5. Guide URL: `http://<home-assistant-ip>:9191/epg`

## Configuration

```yaml
TZ: "Europe/Paris"      # Timezone
log_level: "info"        # debug | info | warning | error
```

## AIO mode

The add-on runs in All-in-One mode: Redis, Celery and the web server share a single container. This is Dispatcharr's recommended mode for simple setups.

## Persistence

Data (channels, EPG, configuration) is stored in `/data/`, which persists across add-on restarts and updates.

## Tech stack

- **Base**: [ghcr.io/dispatcharr/dispatcharr](https://github.com/Dispatcharr/Dispatcharr)
- **Mode**: AIO (All-in-One) with bundled Redis + Celery
- **Streaming**: FFmpeg, Streamlink, VLC backends
- **HA integration**: `init: false` + wrapper entrypoint

## License

AGPL v3.0 (Dispatcharr) — add-on wrapper MIT.
