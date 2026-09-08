# syntax=docker/dockerfile:1

FROM rust:latest AS rust-build
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release -p sme_financial_apis

FROM python:3.12-slim-bookworm
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx gettext-base ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=rust-build /app/target/release/sme_financial_apis /usr/local/bin/sme-api
COPY reasoning_layer /app/reasoning_layer
COPY deploy/nginx /etc/nginx/templates
COPY deploy/entrypoint.sh /entrypoint.sh
COPY deploy/env.example /app/env.example

WORKDIR /app/reasoning_layer
RUN pip install --no-cache-dir -r requirements.txt \
    && chmod +x /entrypoint.sh \
    && mkdir -p /data /var/www/certbot

ENV SQLITE_PATH=/data/credit_ai.db \
    SME_API_BASE=http://127.0.0.1:3000 \
    SME_API_PORT=3000 \
    PYTHONUNBUFFERED=1 \
    OPENAI_MODEL_NAME=gpt-5.4-nano

EXPOSE 80 443
VOLUME ["/data"]
ENTRYPOINT ["/entrypoint.sh"]
