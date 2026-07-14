# Home Assistant Add-on: S3 Browser

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![amd64](https://img.shields.io/badge/amd64-yes-green)
![aarch64](https://img.shields.io/badge/aarch64-yes-green)

Read-only S3 browser integrated into Home Assistant. Compatible with AWS S3, Scality, MinIO, and any S3-compatible endpoint.

## Features

- **Bucket listing** — sidebar with every accessible bucket
- **Navigation** — folder browsing with a clickable breadcrumb
- **Built-in preview** — text, JSON, YAML, CSV, images (PNG, JPG, SVG)
- **Metadata** — size, type, date, ETag, storage class, custom metadata
- **Download** — presigned URL generation for direct downloads
- **Read-only** — no write operations, safe for external access

## Installation

1. Add this repository to the add-on store (**⋮ → Repositories**)
2. Install **S3 Browser**
3. Set your credentials in the Configuration tab
4. Start

## Configuration

```yaml
endpoint_url: "https://s3.example.com"   # S3 endpoint
access_key: "AKIA..."                     # Access key
secret_key: "..."                         # Secret key
region: "us-east-1"                       # Region
verify_ssl: true                          # SSL verification
default_bucket: "my-bucket"               # Default bucket (optional)
```

Credentials are stored encrypted by HA (`password` type in the schema).

## Previewable formats

- **Text**: txt, log, json, xml, csv, yaml, yml, md, py, sh, sql, geojson, toml, html, css, js
- **Images**: jpg, jpeg, png, gif, webp, svg, bmp

Files > 5 MB (images > 10 MB) show metadata only.

## Tech stack

- **Backend**: Python / Flask / boto3
- **Frontend**: vanilla HTML/CSS/JS
- **Container**: Python 3.12 Alpine
- **Auth**: Signature V4, path-style addressing

## License

MIT
