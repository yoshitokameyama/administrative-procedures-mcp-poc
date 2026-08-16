FROM caddy:2.11.4-alpine

COPY gateway/Caddyfile /etc/caddy/Caddyfile

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider "http://127.0.0.1:${PORT:-8080}/health" || exit 1
