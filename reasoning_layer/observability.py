"""Prometheus metrics for HTTP, chats, memos, logs, and exceptions."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

HTTP_REQUESTS = Counter(
    "kuber_http_requests_total",
    "HTTP requests",
    ["method", "path", "status"],
)
HTTP_LATENCY = Histogram(
    "kuber_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "path"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120, 300, 600),
)
EXCEPTIONS = Counter(
    "kuber_exceptions_total",
    "Unhandled exceptions by type and route",
    ["type", "path"],
)
LOG_EVENTS = Counter(
    "kuber_log_events_total",
    "Application log events",
    ["level", "source"],
)
LLM_ERRORS = Counter("kuber_llm_errors_total", "LLM call failures")
PROBE_ERRORS = Counter("kuber_probe_errors_total", "Probe / SME upstream failures")
CHAT_IN_FLIGHT = Gauge("kuber_chat_in_flight", "Chat streams currently running")
LLM_IN_FLIGHT = Gauge("kuber_llm_in_flight", "LLM generations currently running")
MEMO_IN_FLIGHT = Gauge("kuber_memo_in_flight", "Memo renders currently running")
PROBE_IN_FLIGHT = Gauge("kuber_probe_in_flight", "Probe company-detail fetches in this process")
PROBE_LATENCY = Histogram(
    "kuber_probe_request_duration_seconds",
    "Python-to-SME probe call duration",
    ["route"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120),
)


def env_int(name: str, default: int, *, minimum: int = 1, maximum: int = 256) -> int:
    raw = os.getenv(name, "").strip()
    try:
        value = int(raw) if raw else default
    except ValueError:
        value = default
    return max(minimum, min(maximum, value))


def prometheus_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def observe_request(method: str, path: str, status: int, duration_s: float) -> None:
    from sql_db import ops_store

    route = normalize_path(path)
    HTTP_REQUESTS.labels(method=method, path=route, status=str(status)).inc()
    HTTP_LATENCY.labels(method=method, path=route).observe(duration_s)
    ops_store.record_sample(route, method, status, duration_s * 1000, status >= 400)


def record_llm_error() -> None:
    LLM_ERRORS.inc()


def record_probe_error() -> None:
    PROBE_ERRORS.inc()


def record_exception(exc_type: str, path: str) -> None:
    EXCEPTIONS.labels(type=(exc_type or "Exception")[:80], path=normalize_path(path)).inc()


def record_log_event(level: str, source: str) -> None:
    LOG_EVENTS.labels(level=(level or "info")[:16], source=(source or "app")[:32]).inc()


def normalize_path(path: str) -> str:
    if path.startswith("/chat/"):
        return "/chat/{id}" if "/memo" not in path else "/chat/{id}/memo"
    if path.startswith("/chat"):
        return "/chat"
    if path.startswith("/news"):
        return "/news"
    if path.startswith("/credit"):
        return "/credit"
    if path.startswith("/admin"):
        return "/admin"
    if path.startswith("/auth"):
        return "/auth"
    if path.startswith("/chat_history"):
        return "/chat_history"
    return path.split("?")[0][:80]


@asynccontextmanager
async def track_in_flight(gauge: Gauge):
    gauge.inc()
    try:
        yield
    finally:
        gauge.dec()


def metrics_allowed(request: Request) -> bool:
    token = os.getenv("INTERNAL_TOKEN", "").strip()
    got = (request.headers.get("x-internal-token") or "").strip()
    if token and got == token:
        return True
    client = request.client.host if request.client else ""
    return client in {"127.0.0.1", "::1"} or client.startswith("172.") or client.startswith("10.")
