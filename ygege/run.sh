#!/usr/bin/with-contenv bashio

# Récupérer les options depuis config.yaml
RELAY_URL=$(bashio::config 'relay_url')
LOG_LEVEL=$(bashio::config 'log_level')

# Exporter les variables d'environnement
export RELAY_URL="${RELAY_URL}"
export LOG_LEVEL="${LOG_LEVEL}"

bashio::log.info "Starting Ygege with relay: ${RELAY_URL}"

# Lancer ygege
exec /app/ygege