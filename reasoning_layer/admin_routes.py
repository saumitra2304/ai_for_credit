import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query

from auth_routes import require_admin
from sme_api.base import sme_headers, sme_url
from sql_db import ops_store, settings_store

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/settings")
async def get_settings(_user: dict = Depends(require_admin)):
    return {"settings": await settings_store.list_settings()}


@router.put("/settings")
async def put_settings(body: dict, _user: dict = Depends(require_admin)):
    values = body.get("values")
    if not isinstance(values, dict):
        raise HTTPException(status_code=400, detail="values required")
    settings = await settings_store.save_settings(
        {str(key): "" if value is None else str(value) for key, value in values.items()}
    )
    asyncio.create_task(_notify_rust())
    await ops_store.add_log("info", "python", "admin updated settings")
    return {"settings": settings}


@router.get("/logs")
async def get_logs(
    _user: dict = Depends(require_admin),
    level: str | None = None,
    source: str | None = None,
    q: str | None = None,
    limit: int = Query(default=200, ge=1, le=500),
):
    return {"logs": await ops_store.list_logs(level=level, source=source, q=q, limit=limit)}


@router.get("/traces")
async def get_traces(
    _user: dict = Depends(require_admin),
    limit: int = Query(default=50, ge=1, le=200),
):
    return {"traces": await ops_store.list_traces(limit=limit)}


@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str, _user: dict = Depends(require_admin)):
    spans = await ops_store.get_trace(trace_id)
    if not spans:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return {"trace_id": trace_id, "spans": spans}


@router.get("/metrics")
async def get_metrics_json(
    _user: dict = Depends(require_admin),
    minutes: int = Query(default=15, ge=1, le=1440),
):
    return ops_store.metrics_summary(minutes=minutes)


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
