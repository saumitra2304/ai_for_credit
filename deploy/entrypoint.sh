#!/bin/sh
set -eu

export SQLITE_PATH="${SQLITE_PATH:-/data/credit_ai.db}"
export SME_API_BASE="${SME_API_BASE:-http://127.0.0.1:3000}"
export SME_API_PORT="${SME_API_PORT:-3000}"
export DOMAIN="${DOMAIN:-_}"
export INTERNAL_TOKEN="${INTERNAL_TOKEN:-}"

mkdir -p /data /var/www/certbot /var/log/nginx

if [ -f /app/.env ]; then
  cp /app/.env /app/reasoning_layer/.env 2>/dev/null || true
fi

CERT="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"
if [ -n "${DOMAIN}" ] && [ "${DOMAIN}" != "_" ] && [ -f "${CERT}" ]; then
  TEMPLATE=/etc/nginx/templates/ssl.conf.template
else
  TEMPLATE=/etc/nginx/templates/http.conf.template
fi

envsubst '${DOMAIN} ${INTERNAL_TOKEN}' \
  < /etc/nginx/templates/kuber-proxy.conf.template \
  > /etc/nginx/kuber-proxy.conf
envsubst '${DOMAIN} ${INTERNAL_TOKEN}' < "$TEMPLATE" > /etc/nginx/conf.d/default.conf
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

echo "starting sme-api on :${SME_API_PORT}"
sme-api &

echo "starting reasoning layer on :8001"
cd /app/reasoning_layer
uvicorn main:app --host 127.0.0.1 --port 8001 --workers 1 --timeout-keep-alive 75 &

echo "starting nginx ($(basename "$TEMPLATE"))"
exec nginx -g "daemon off;"
