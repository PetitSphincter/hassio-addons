"""S3 Browser addon web server."""

import os
import base64
from flask import Flask, render_template, request, jsonify, Response

import s3client

app = Flask(__name__)

DEFAULT_BUCKET = os.environ.get("S3_DEFAULT_BUCKET", "")

# Extensions we can preview inline
PREVIEWABLE_TEXT = {"txt", "log", "json", "xml", "csv", "yaml", "yml", "md",
                    "ini", "cfg", "conf", "py", "sh", "bash", "html", "css",
                    "js", "toml", "env", "properties", "sql", "geojson"}
PREVIEWABLE_IMAGE = {"jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "ico"}


@app.route("/")
def index():
    return render_template(
        "index.html",
        default_bucket=DEFAULT_BUCKET,
        endpoint=os.environ.get("S3_ENDPOINT", ""),
    )


@app.route("/api/buckets")
def api_buckets():
    return jsonify(s3client.list_buckets())


@app.route("/api/browse/<bucket>")
def api_browse(bucket):
    prefix = request.args.get("prefix", "")
    token = request.args.get("token", "")
    return jsonify(s3client.list_objects(
        bucket, prefix=prefix,
        continuation_token=token if token else None,
    ))


@app.route("/api/info/<bucket>")
def api_info(bucket):
    key = request.args.get("key", "")
    if not key:
        return jsonify({"error": "No key provided"}), 400
    return jsonify(s3client.get_object_info(bucket, key))


@app.route("/api/preview/<bucket>")
def api_preview(bucket):
    key = request.args.get("key", "")
    if not key:
        return jsonify({"error": "No key provided"}), 400

    ext = key.rsplit(".", 1)[-1].lower() if "." in key else ""

    # Determine preview type
    if ext in PREVIEWABLE_TEXT:
        result = s3client.get_object_content(bucket, key, max_size=2 * 1024 * 1024)
        if result.get("error"):
            return jsonify(result), 500
        if result.get("too_large"):
            return jsonify({"type": "too_large", "size": result["size"]})

        try:
            text = result["body"].decode("utf-8")
        except UnicodeDecodeError:
            text = result["body"].decode("latin-1")

        return jsonify({
            "type": "text",
            "content": text[:500000],  # Cap at 500k chars
            "size": result["size"],
            "content_type": result["content_type"],
            "truncated": len(text) > 500000,
        })

    elif ext in PREVIEWABLE_IMAGE:
        result = s3client.get_object_content(bucket, key, max_size=10 * 1024 * 1024)
        if result.get("error"):
            return jsonify(result), 500
        if result.get("too_large"):
            return jsonify({"type": "too_large", "size": result["size"]})

        b64 = base64.b64encode(result["body"]).decode("ascii")
        mime = result["content_type"]
        if ext == "svg":
            mime = "image/svg+xml"
        elif ext in ("jpg", "jpeg"):
            mime = "image/jpeg"
        elif ext == "png":
            mime = "image/png"

        return jsonify({
            "type": "image",
            "data": f"data:{mime};base64,{b64}",
            "size": result["size"],
        })

    else:
        info = s3client.get_object_info(bucket, key)
        return jsonify({
            "type": "binary",
            "size": info.get("size", 0),
            "content_type": info.get("content_type", ""),
        })


@app.route("/api/download/<bucket>")
def api_download(bucket):
    key = request.args.get("key", "")
    if not key:
        return jsonify({"error": "No key"}), 400

    try:
        s3 = s3client.get_client()
        obj = s3.get_object(Bucket=bucket, Key=key)
        filename = key.split("/")[-1]
        content_type = obj.get("ContentType", "application/octet-stream")

        return Response(
            obj["Body"].iter_chunks(1024 * 1024),
            mimetype=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(obj["ContentLength"]),
            },
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restore-status/<bucket>")
def api_restore_status(bucket):
    key = request.args.get("key", "")
    if not key:
        return jsonify({"error": "No key"}), 400
    return jsonify(s3client.get_restore_status(bucket, key))


@app.route("/api/restore/<bucket>", methods=["POST"])
def api_restore(bucket):
    data = request.get_json()
    key = data.get("key", "")
    days = data.get("days", 7)
    tier = data.get("tier", "Standard")
    if not key:
        return jsonify({"error": "No key"}), 400
    return jsonify(s3client.restore_object(bucket, key, days=days, tier=tier))


@app.route("/api/stats/<bucket>")
def api_stats(bucket):
    return jsonify(s3client.get_bucket_stats(bucket))


@app.route("/api/bucket-info/<bucket>")
def api_bucket_info(bucket):
    """Aggregate all bucket metadata in one call."""
    info = {
        "lifecycle": s3client.get_bucket_lifecycle(bucket),
        "policy": s3client.get_bucket_policy(bucket),
        "versioning": s3client.get_bucket_versioning(bucket),
        "object_lock": s3client.get_bucket_object_lock(bucket),
        "tagging": s3client.get_bucket_tagging(bucket),
        "stats": s3client.get_bucket_stats(bucket),
    }
    return jsonify(info)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8099)
