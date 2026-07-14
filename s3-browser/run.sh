#!/bin/sh
set -e

CONFIG=/data/options.json

export S3_ENDPOINT=$(jq -r '.endpoint_url' $CONFIG)
export S3_ACCESS_KEY=$(jq -r '.access_key' $CONFIG)
export S3_SECRET_KEY=$(jq -r '.secret_key' $CONFIG)
export S3_REGION=$(jq -r '.region // "us-east-1"' $CONFIG)
export S3_VERIFY_SSL=$(jq -r '.verify_ssl | tostring' $CONFIG)
export S3_DEFAULT_BUCKET=$(jq -r '.default_bucket // ""' $CONFIG)

# ── Auto-fetch CA chain from endpoint ──
ENDPOINT_HOST=$(echo "$S3_ENDPOINT" | sed 's|https://||' | sed 's|http://||' | sed 's|/.*||' | sed 's|:.*||')
ENDPOINT_PORT=$(echo "$S3_ENDPOINT" | grep -o ':[0-9]*' | tr -d ':')
ENDPOINT_PORT=${ENDPOINT_PORT:-443}

echo "[s3-browser] Fetching CA chain from ${ENDPOINT_HOST}:${ENDPOINT_PORT}..."
if openssl s_client -showcerts -connect "${ENDPOINT_HOST}:${ENDPOINT_PORT}" \
    </dev/null 2>/dev/null | \
    awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/' \
    > /usr/local/share/ca-certificates/s3-endpoint.crt 2>/dev/null; then

    if [ -s /usr/local/share/ca-certificates/s3-endpoint.crt ]; then
        update-ca-certificates 2>/dev/null
        export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
        export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
        export AWS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
        echo "[s3-browser] CA chain injected into trust store"
    else
        echo "[s3-browser] WARNING: Could not extract certs from endpoint"
    fi
else
    echo "[s3-browser] WARNING: Could not connect to endpoint for cert fetch"
fi

# Force disable SSL at env level if requested
if [ "$S3_VERIFY_SSL" = "false" ]; then
    export CURL_CA_BUNDLE=""
    export REQUESTS_CA_BUNDLE=""
    echo "[s3-browser] SSL verification DISABLED"
fi

echo "[s3-browser] Starting S3 Browser..."
echo "[s3-browser] Endpoint: ${S3_ENDPOINT}"
echo "[s3-browser] SSL verify: ${S3_VERIFY_SSL}"

cd /app
exec python3 server.py
