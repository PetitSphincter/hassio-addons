"""yt-dlp download manager."""

import os
import json
import uuid
import threading
import time
from datetime import datetime
from pathlib import Path

import yt_dlp

# Download state storage
downloads = {}
downloads_lock = threading.Lock()

# Quality to format mapping
FORMAT_MAP = {
    "audio": {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "merge": "m4a",
    },
    "mp3": {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "merge": None,
    },
    "720p": {
        "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
        "merge": "mp4",
    },
    "1080p": {
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
        "merge": "mp4",
    },
    "4k": {
        "format": None,
        "merge": "mkv",
    },
}

CODEC_PRIORITY = {
    "av1": "bestvideo[height<=2160][vcodec^=av01]+bestaudio[ext=m4a]/"
           "bestvideo[height<=2160][vcodec^=vp9]+bestaudio[ext=m4a]/"
           "bestvideo[height<=2160]+bestaudio",
    "vp9": "bestvideo[height<=2160][vcodec^=vp9]+bestaudio[ext=m4a]/"
           "bestvideo[height<=2160]+bestaudio",
    "h264": "bestvideo[height<=2160][vcodec^=avc1]+bestaudio[ext=m4a]/"
            "bestvideo[height<=2160]+bestaudio",
    "any": "bestvideo[height<=2160]+bestaudio",
}


def get_format_string(quality: str, codec: str) -> str:
    """Build yt-dlp format string from quality + codec preference."""
    if quality == "4k":
        return CODEC_PRIORITY.get(codec, CODEC_PRIORITY["any"])
    return FORMAT_MAP[quality]["format"]


def get_merge_format(quality: str) -> str:
    """Get output container format."""
    return FORMAT_MAP[quality]["merge"]


def fetch_info(url: str) -> dict:
    """Fetch video/playlist metadata without downloading."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info is None:
        return {"error": "Could not fetch info"}

    result = {
        "title": info.get("title", "Unknown"),
        "thumbnail": info.get("thumbnail", ""),
        "duration": info.get("duration", 0),
        "uploader": info.get("uploader", "Unknown"),
        "is_playlist": info.get("_type") == "playlist",
        "chapters": [],
    }

    if result["is_playlist"]:
        entries = info.get("entries", [])
        result["count"] = len(entries)
        result["entries"] = [
            {
                "title": e.get("title", f"Video {i+1}"),
                "duration": e.get("duration", 0),
                "url": e.get("url", ""),
            }
            for i, e in enumerate(entries) if e
        ]
    else:
        formats = info.get("formats", [])
        result["available_resolutions"] = sorted(set(
            f.get("height", 0) for f in formats
            if f.get("height") and f.get("vcodec", "none") != "none"
        ))

        # Extract chapters if available
        chapters = info.get("chapters") or []
        result["chapters"] = [
            {
                "title": ch.get("title", f"Chapter {i+1}"),
                "start_time": ch.get("start_time", 0),
                "end_time": ch.get("end_time", 0),
            }
            for i, ch in enumerate(chapters)
        ]

    return result


def start_download(
    url: str,
    quality: str,
    codec: str,
    output_dir: str,
    jellyfin_naming: bool,
    embed_thumbnail: bool,
    embed_metadata: bool,
    custom_name: str = "",
    is_series: bool = False,
    series_name: str = "",
    season: int = 1,
    split_chapters: bool = False,
    socketio=None,
) -> str:
    """Start a download in background thread. Returns download ID."""
    dl_id = str(uuid.uuid4())[:8]

    with downloads_lock:
        downloads[dl_id] = {
            "id": dl_id,
            "url": url,
            "status": "starting",
            "progress": 0,
            "speed": "",
            "eta": "",
            "title": "Fetching info...",
            "thumbnail": "",
            "filename": "",
            "error": "",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "quality": quality,
        }

    thread = threading.Thread(
        target=_download_worker,
        args=(dl_id, url, quality, codec, output_dir, jellyfin_naming,
              embed_thumbnail, embed_metadata, custom_name, is_series,
              series_name, season, split_chapters, socketio),
        daemon=True,
    )
    thread.start()
    return dl_id


def _make_progress_hook(dl_id, socketio=None):
    """Create a progress hook for yt-dlp."""
    def hook(d):
        with downloads_lock:
            dl = downloads.get(dl_id)
            if not dl:
                return

            if d["status"] == "downloading":
                dl["status"] = "downloading"
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                if total > 0:
                    dl["progress"] = round(downloaded / total * 100, 1)
                dl["speed"] = d.get("_speed_str", "")
                dl["eta"] = d.get("_eta_str", "")
                dl["filename"] = d.get("filename", "")

            elif d["status"] == "finished":
                dl["status"] = "processing"
                dl["progress"] = 100

            elif d["status"] == "error":
                dl["status"] = "error"
                dl["error"] = str(d.get("error", "Unknown error"))

        if socketio:
            socketio.emit("progress", _get_download_safe(dl_id))

    return hook


def _download_worker(
    dl_id, url, quality, codec, output_dir, jellyfin_naming,
    embed_thumbnail, embed_metadata, custom_name, is_series,
    series_name, season, split_chapters, socketio
):
    """Background download worker."""
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        is_mp3 = quality == "mp3"

        # Build output template
        if is_series and jellyfin_naming and series_name:
            outtmpl = os.path.join(
                output_dir,
                f"{series_name}",
                f"Season {season:02d}",
                f"{series_name} - S{season:02d}E%(playlist_index)02d.%(ext)s"
            )
        elif custom_name:
            outtmpl = os.path.join(output_dir, f"{custom_name}.%(ext)s")
        else:
            outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")

        # Build yt-dlp options
        ydl_opts = {
            "format": get_format_string(quality, codec),
            "outtmpl": outtmpl,
            "no_overwrites": True,
            "progress_hooks": [_make_progress_hook(dl_id, socketio)],
            "quiet": True,
            "no_warnings": True,
        }

        merge_fmt = get_merge_format(quality)
        if merge_fmt:
            ydl_opts["merge_output_format"] = merge_fmt

        postprocessors = []

        # MP3 conversion via ffmpeg
        if is_mp3:
            postprocessors.append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            })

        # Chapter splitting — yt-dlp native SplitChapters postprocessor
        if split_chapters and not is_series:
            postprocessors.append({
                "key": "FFmpegSplitChapters",
                "force_keyframes": False,
            })
            # Chapter files get their own output template
            chapter_tmpl = outtmpl.replace(
                ".%(ext)s",
                " - %(section_title)s.%(ext)s"
            )
            ydl_opts["outtmpl"] = {
                "default": outtmpl,
                "chapter": chapter_tmpl,
            }

        if embed_thumbnail:
            ydl_opts["writethumbnail"] = True
            postprocessors.append({
                "key": "EmbedThumbnail",
                "already_have_thumbnail": False,
            })

        if embed_metadata:
            postprocessors.append({"key": "FFmpegMetadata"})

        if postprocessors:
            ydl_opts["postprocessors"] = postprocessors

        # Fetch title before download
        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            with downloads_lock:
                dl = downloads[dl_id]
                dl["title"] = info.get("title", "Unknown")
                dl["thumbnail"] = info.get("thumbnail", "")
            if socketio:
                socketio.emit("progress", _get_download_safe(dl_id))

        # Download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with downloads_lock:
            dl = downloads[dl_id]
            dl["status"] = "completed"
            dl["progress"] = 100
            dl["completed_at"] = datetime.now().isoformat()

        if socketio:
            socketio.emit("progress", _get_download_safe(dl_id))

    except Exception as e:
        with downloads_lock:
            dl = downloads.get(dl_id)
            if dl:
                dl["status"] = "error"
                dl["error"] = str(e)
        if socketio:
            socketio.emit("progress", _get_download_safe(dl_id))


def _get_download_safe(dl_id) -> dict:
    """Thread-safe copy of download state."""
    with downloads_lock:
        dl = downloads.get(dl_id)
        return dict(dl) if dl else {}


def get_all_downloads() -> list:
    """Get all downloads, newest first."""
    with downloads_lock:
        return [dict(d) for d in reversed(downloads.values())]


def get_download(dl_id: str) -> dict:
    """Get single download state."""
    return _get_download_safe(dl_id)
