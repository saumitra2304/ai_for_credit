import os

SME_API_BASE = os.getenv("SME_API_BASE", "http://127.0.0.1:3000").rstrip("/")
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "")


def sme_headers() -> dict[str, str]:
    if INTERNAL_TOKEN:
        return {"X-Internal-Token": INTERNAL_TOKEN}
    return {}


def sme_url(path: str) -> str:
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{SME_API_BASE}{path}"
