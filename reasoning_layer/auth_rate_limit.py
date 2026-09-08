"""In-memory login/register throttling for a single-process API."""

from __future__ import annotations

import threading
import time

from fastapi import HTTPException, Request

_WINDOW_SECONDS = 15 * 60
_LOGIN_LIMIT = 8
_REGISTER_LIMIT = 5
_MAX_KEYS = 8000
_lock = threading.Lock()
_hits: dict[str, list[float]] = {}


def _prune_locked(now: float) -> None:
    if len(_hits) < _MAX_KEYS:
        return
    stale = [key for key, times in _hits.items() if not times or now - times[-1] >= _WINDOW_SECONDS]
    for key in stale:
        _hits.pop(key, None)
    if len(_hits) >= _MAX_KEYS:
        _hits.clear()


def _allow(key: str, limit: int) -> bool:
    now = time.monotonic()
    with _lock:
        times = [stamp for stamp in _hits.get(key, []) if now - stamp < _WINDOW_SECONDS]
        if len(times) >= limit:
            _hits[key] = times
            return False
        times.append(now)
        _hits[key] = times
        _prune_locked(now)
        return True


def client_ip(request: Request) -> str:
    forwarded = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    if forwarded:
        return forwarded[:64]
    if request.client and request.client.host:
        return request.client.host[:64]
    return "unknown"


def enforce(request: Request, action: str, email: str) -> None:
    ip = client_ip(request)
    identity = (email or "").strip().lower()[:254]
    ip_limit = _REGISTER_LIMIT if action == "register" else _LOGIN_LIMIT
    if not _allow(f"{action}:ip:{ip}", ip_limit) or not _allow(f"{action}:id:{identity}", ip_limit):
        raise HTTPException(
            status_code=429,
            detail="Too many attempts. Wait a few minutes and try again.",
        )
