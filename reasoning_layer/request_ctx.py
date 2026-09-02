"""Per-request IDs for logs, traces, and downstream SME calls."""

from contextlib import asynccontextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import uuid

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
span_id_ctx: ContextVar[str | None] = ContextVar("span_id", default=None)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return uuid.uuid4().hex[:16]


def current_request_id() -> str | None:
    return request_id_ctx.get()


def bind_request_id(request_id: str | None = None) -> str:
    rid = request_id or request_id_ctx.get() or new_id()
    request_id_ctx.set(rid)
    return rid


async def log_event(level: str, source: str, message: str, extra: dict | None = None) -> None:
    from sql_db import ops_store

    try:
        await ops_store.add_log(level, source, message, request_id_ctx.get(), extra)
    except Exception:
        pass


@asynccontextmanager
async def span(name: str, **attrs):
    from sql_db import ops_store

    trace_id = request_id_ctx.get() or new_id()
    if request_id_ctx.get() is None:
        request_id_ctx.set(trace_id)
    sid = new_id()
    parent = span_id_ctx.get()
    token = span_id_ctx.set(sid)
    start = utcnow()
    status = "ok"
    clean_attrs = {key: value for key, value in attrs.items() if value is not None} or None
    try:
        yield sid
    except Exception:
        status = "error"
        raise
    finally:
        span_id_ctx.reset(token)
        try:
            await ops_store.add_span(
                trace_id,
                sid,
                name,
                start,
                utcnow(),
                status,
                parent,
                clean_attrs,
            )
        except Exception:
            pass


async def agen_span(name, agen, **attrs):
    async with span(name, **attrs):
        async for item in agen:
            yield item
