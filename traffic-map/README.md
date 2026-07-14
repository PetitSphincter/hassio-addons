# Home Assistant Add-on: Traffic Map Generator

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![amd64](https://img.shields.io/badge/amd64-yes-green)
![aarch64](https://img.shields.io/badge/aarch64-yes-green)
![armv7](https://img.shields.io/badge/armv7-yes-green)

Periodically generates a road traffic map image: dark CartoDB basemap + **Azure Maps** traffic overlay. Great for a `camera`/`picture` card on a Lovelace dashboard (home-to-work commute, etc.).

## Features

- **CartoDB dark basemap** — label-free tiles, clean dashboard rendering
- **Azure Maps traffic overlay** — real-time relative flow (green/orange/red)
- **Configurable refresh** — from 60 s to 1 h
- **Image output** — written to `/config` / `/share`, consumable by a `local_file` camera entity

## Prerequisites

An **Azure Maps** key (the free tier is plenty for a 5-minute refresh): Azure portal → create an *Azure Maps Account* resource → Authentication → primary key.

## Configuration

```yaml
latitude: 43.604500        # Map center
longitude: 1.444200
zoom: 15                   # 1-20
width: 1000                # px
height: 640
update_interval: 300       # seconds
azure_key: ""              # Your Azure Maps key (required)
```

> The key uses the `password` schema type: never shown in plain text in the UI or the logs. Never commit a key to a repository.

## Lovelace usage

```yaml
camera:
  - platform: local_file
    name: Traffic Map
    file_path: /config/www/traffic_map.png
```

Then a `picture-entity` card pointing at `camera.traffic_map`.

## License

MIT. Tiles © CartoDB / OpenStreetMap contributors — traffic © Microsoft Azure Maps (subject to their terms of use).
