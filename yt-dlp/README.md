# Home Assistant Add-on: yt-dlp Downloader

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![amd64](https://img.shields.io/badge/amd64-yes-green)
![aarch64](https://img.shields.io/badge/aarch64-yes-green)

Download YouTube videos and playlists straight from Home Assistant, with automatic Jellyfin-friendly naming.

## Features

- **Video or playlist** — automatic detection, preview before downloading
- **Quality selection** — audio only, 720p, 1080p, 4K
- **Smart codec choice** — AV1 > VP9 > H.264 preference (configurable)
- **Jellyfin naming** — automatic `Show - S01E01.mp4` for playlists
- **Chapters** — detection, display, and optional one-file-per-chapter splitting
- **MP3 mode** — 320 kbps audio extraction
- **Thumbnail + metadata** — embedded in the file
- **Real-time progress** — via WebSocket, right in the UI

## Installation

1. Add this repository to the add-on store (**⋮ → Repositories**)
2. Install **yt-dlp Downloader**
3. Start — the panel shows up in the HA sidebar

## Configuration

```yaml
output_dir: "/media/videos"       # Output folder (mapped for Jellyfin)
default_quality: "1080p"           # audio | mp3 | 720p | 1080p | 4k
jellyfin_naming: true              # S01E01 naming for shows
embed_thumbnail: true              # Embed the thumbnail
embed_metadata: true               # Embed metadata
preferred_codec: "av1"             # av1 | vp9 | h264 | any
```

## Usage

1. Open the **yt-dlp** panel in the HA sidebar
2. Paste a YouTube URL
3. Click **Fetch** to preview
4. Adjust quality / codec / folder
5. Click **Download**
6. Follow the progress in real time

For a series: enable **Jellyfin series naming**, set the show name and season → episodes get named automatically.

## Tech stack

- **Backend**: Python / Flask / Flask-SocketIO
- **Download**: yt-dlp + ffmpeg
- **Container**: Alpine Linux (HA base image)
- **UI**: vanilla HTML/CSS/JS, WebSocket for progress

## License

MIT
