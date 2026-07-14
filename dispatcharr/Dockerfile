FROM ghcr.io/dispatcharr/dispatcharr:latest

# Add jq for parsing HA options
RUN apt-get update && apt-get install -y --no-install-recommends jq \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /ha-entrypoint.sh
RUN chmod a+x /ha-entrypoint.sh

ENTRYPOINT ["/ha-entrypoint.sh"]
