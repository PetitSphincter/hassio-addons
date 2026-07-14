# Home Assistant Add-on: Heimdall

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![amd64](https://img.shields.io/badge/amd64-yes-green)
![aarch64](https://img.shields.io/badge/aarch64-yes-green)

Application dashboard and service launcher, integrated straight into Home Assistant.

Heimdall centralizes links to all your services (Jellyfin, Sonarr, Radarr, Grafana, Prowlarr, etc.) in a clean, fast interface.

## Features

- **Full dashboard** — add apps, links and bookmarks with icons
- **Enhanced apps** — live stats for some services (Sonarr, Radarr, Plex, etc.)
- **Tags** — organize by category
- **Multi-user** — each user can have their own dashboard
- **Built-in search** — Google, DuckDuckGo or custom
- **HA sidebar** — direct access from Home Assistant via ingress
- **Direct access** — also available on port 6610

## Installation

1. Add this repository to the add-on store (**⋮ → Repositories**)
2. Install **Heimdall**
3. Start the add-on

## Access

Two access modes:

- **HA sidebar** (ingress): click "Heimdall" in the sidebar
- **Direct port**: `http://<home-assistant-ip>:6610`

> Note: ingress can occasionally struggle with some CSS/JS assets. If the layout looks broken from the sidebar, use the direct port (6610), which always works fine.

## Configuration

```yaml
TZ: "Europe/Paris"    # Timezone
PUID: 0               # User ID (0 = root, fine inside a container)
PGID: 0               # Group ID
```

## Persistence

Data (configured apps, settings, users) is stored in `/data/heimdall/`, which persists across add-on restarts and updates.

## Tech stack

- **Base**: [linuxserver/heimdall](https://docs.linuxserver.io/images/docker-heimdall/)
- **App**: Laravel/PHP + SQLite
- **Web**: Nginx
- **Init**: s6-overlay (linuxserver)
- **HA integration**: `init: false` + wrapper entrypoint

## License

MIT (add-on wrapper) — Heimdall is MIT-licensed.
