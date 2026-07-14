FROM lscr.io/linuxserver/heimdall:latest

# Add jq for parsing HA options
RUN apk add --no-cache jq

# Wrapper entrypoint for HA integration
COPY entrypoint.sh /ha-entrypoint.sh
RUN chmod a+x /ha-entrypoint.sh

# Nginx config for ingress support
COPY nginx-ingress.conf /defaults/nginx-ingress.conf

ENTRYPOINT ["/ha-entrypoint.sh"]
