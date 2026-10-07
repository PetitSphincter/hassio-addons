# Changelog

## 0.2.2 (2026-10-07)

- Playlists: skip unavailable videos (private, deleted...) instead of failing the whole download
- Show the number of skipped videos in the UI (list in tooltip and add-on logs)
- Title prefetch uses flat extraction (faster on playlists)
- Silence pip warnings at startup

## 0.2.1 (2026-10-07)

- Fix HTTP 403 on YouTube downloads: install Node.js and yt-dlp-ejs (JS challenge solving)
- Enable the node JS runtime for every yt-dlp call
- Update yt-dlp at add-on startup

## 0.2.0 (2026-04-06)

- YouTube chapter detection and display in preview
- Split by chapters option (creates one file per chapter via FFmpegSplitChapters)
- MP3 download mode (320kbps via FFmpegExtractAudio)
- Chapter toggle auto-shown when video has chapters

## 0.1.0 (2026-03-29)

- Initial release
- Video and playlist downloads
- Quality selection (audio, 720p, 1080p, 4K)
- Codec preference (AV1, VP9, H.264)
- Jellyfin series naming (S01E01)
- Embedded thumbnails and metadata
- Real-time progress via WebSocket
- Home Assistant ingress support
