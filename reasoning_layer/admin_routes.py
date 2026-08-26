import asyncio
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel

from auth_routes import get_current_user
from sme_api.base import sme_headers, sme_url
from sql_db import ops_store, settings_store

router = APIRouter(prefix="/admin", tags=["admin"])

HTTP_REQUESTS = Counter(
    "kuber_http_requests_total",
    "HTTP requests",
    ["method", "path", "status"],
)
HTTP_LATENCY = Histogram(
    "kuber_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "path"],
)
LLM_ERRORS = Counter("kuber_llm_errors_total", "LLM call failures")


class SettingsUpdate(BaseModel):
    values: dict[str, str]


@router.get("/settings")
async def get_settings(_user: dict = Depends(get_current_user)):
    return {"settings": await settings_store.list_settings()}


@router.put("/settings")
async def put_settings(body: SettingsUpdate, _user: dict = Depends(get_current_user)):
    settings = await settings_store.save_settings(body.values)
    asyncio.create_task(_notify_rust())
    await ops_store.add_log("info", "python", "admin updated settings")
    return {"settings": settings}


@router.get("/logs")
async def get_logs(
    _user: dict = Depends(get_current_user),
    level: str | None = None,
    source: str | None = None,
    q: str | None = None,
    limit: int = Query(default=200, ge=1, le=500),
):
    return {"logs": await ops_store.list_logs(level=level, source=source, q=q, limit=limit)}


@router.get("/traces")
async def get_traces(
    _user: dict = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=200),
):
    return {"traces": await ops_store.list_traces(limit=limit)}


@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str, _user: dict = Depends(get_current_user)):
    spans = await ops_store.get_trace(trace_id)
    if not spans:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return {"trace_id": trace_id, "spans": spans}


@router.get("/metrics")
async def get_metrics_json(
    _user: dict = Depends(get_current_user),
    minutes: int = Query(default=15, ge=1, le=1440),
):
    return ops_store.metrics_summary(minutes=minutes)


def prometheus_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def observe_request(method: str, path: str, status: int, duration_s: float) -> None:
    route = _normalize_path(path)
    HTTP_REQUESTS.labels(method=method, path=route, status=str(status)).inc()
    HTTP_LATENCY.labels(method=method, path=route).observe(duration_s)
    ops_store.record_sample(route, method, status, duration_s * 1000, status >= 400)


def record_llm_error() -> None:
    LLM_ERRORS.inc()


def _normalize_path(path: str) -> str:
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
    return path.split("?")[0][:80]


async def _notify_rust() -> None:
    try:
        import aiohttp

        from sme_api.base import SME_API_BASE

        if not SME_API_BASE:
            return
        timeout = aiohttp.ClientTimeout(total=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                sme_url("/internal/reload-settings"),
                headers=sme_headers(),
            ):
                pass
    except Exception:
        pass


def new_ids() -> tuple[str, str]:
    return uuid.uuid4().hex[:16], uuid.uuid4().hex[:16]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
