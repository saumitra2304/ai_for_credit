import os

SME_API_BASE = os.getenv("SME_API_BASE", "http://127.0.0.1:3000").rstrip("/")
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "")


def sme_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    if INTERNAL_TOKEN:
        headers["X-Internal-Token"] = INTERNAL_TOKEN
    try:
        from request_ctx import request_id_ctx, span_id_ctx

        rid = request_id_ctx.get()
        sid = span_id_ctx.get()
        if rid:
            headers["x-request-id"] = rid
        if sid:
            headers["x-parent-span-id"] = sid
    except Exception:
        pass
    return headers


def sme_url(path: str) -> str:
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{SME_API_BASE}{path}"
