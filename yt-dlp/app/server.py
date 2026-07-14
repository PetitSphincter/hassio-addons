"""yt-dlp addon web server."""

import os
import json
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

import downloader

app = Flask(__name__)
app.config["SECRET_KEY"] = "ytdlp-addon-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")

# Config from environment (set by run.sh from HA options)
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/media/videos")
DEFAULT_QUALITY = os.environ.get("DEFAULT_QUALITY", "1080p")
JELLYFIN_NAMING = os.environ.get("JELLYFIN_NAMING", "true").lower() == "true"
EMBED_THUMBNAIL = os.environ.get("EMBED_THUMBNAIL", "true").lower() == "true"
EMBED_METADATA = os.environ.get("EMBED_METADATA", "true").lower() == "true"
PREFERRED_CODEC = os.environ.get("PREFERRED_CODEC", "av1")
INGRESS_PATH = os.environ.get("INGRESS_PATH", "")


@app.route("/")
def index():
    """Serve the main UI."""
    return render_template(
        "index.html",
        ingress_path=INGRESS_PATH,
        output_dir=OUTPUT_DIR,
        default_quality=DEFAULT_QUALITY,
        jellyfin_naming=JELLYFIN_NAMING,
        embed_thumbnail=EMBED_THUMBNAIL,
        embed_metadata=EMBED_METADATA,
        preferred_codec=PREFERRED_CODEC,
    )


@app.route("/api/info", methods=["POST"])
def api_info():
    """Fetch video/playlist metadata."""
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        info = downloader.fetch_info(url)
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download", methods=["POST"])
def api_download():
    """Start a download."""
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    quality = data.get("quality", DEFAULT_QUALITY)
    codec = data.get("codec", PREFERRED_CODEC)
    output_dir = data.get("output_dir", OUTPUT_DIR)
    jellyfin_naming = data.get("jellyfin_naming", JELLYFIN_NAMING)
    embed_thumbnail = data.get("embed_thumbnail", EMBED_THUMBNAIL)
    embed_metadata = data.get("embed_metadata", EMBED_METADATA)
    custom_name = data.get("custom_name", "")
    is_series = data.get("is_series", False)
    series_name = data.get("series_name", "")
    season = data.get("season", 1)
    split_chapters = data.get("split_chapters", False)

    dl_id = downloader.start_download(
        url=url,
        quality=quality,
        codec=codec,
        output_dir=output_dir,
        jellyfin_naming=jellyfin_naming,
        embed_thumbnail=embed_thumbnail,
        embed_metadata=embed_metadata,
        custom_name=custom_name,
        is_series=is_series,
        series_name=series_name,
        season=season,
        split_chapters=split_chapters,
        socketio=socketio,
    )

    return jsonify({"id": dl_id, "status": "started"})


@app.route("/api/downloads")
def api_downloads():
    """Get all downloads."""
    return jsonify(downloader.get_all_downloads())


@app.route("/api/downloads/<dl_id>")
def api_download_status(dl_id):
    """Get single download status."""
    dl = downloader.get_download(dl_id)
    if not dl:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dl)


@socketio.on("connect")
def handle_connect():
    """Send current state on connect."""
    socketio.emit("all_downloads", downloader.get_all_downloads())


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8099)
