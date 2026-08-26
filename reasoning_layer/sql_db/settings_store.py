"""Runtime settings: SQLite overrides, then process env / bundled.env."""

import os
from datetime import datetime, timezone

from sql_db.db import open_db

SETTING_KEYS = [
    "probe_api_key",
    "INSTA_API_KEY",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL_NAME",
    "SEARCH_API_KEY",
]

SECRET_KEYS = {
    "probe_api_key",
    "INSTA_API_KEY",
    "OPENAI_API_KEY",
    "SEARCH_API_KEY",
}

ENV_DEFAULTS = {
    "OPENAI_API_KEY": "ollama",
    "OPENAI_BASE_URL": "http://127.0.0.1:11434/v1",
    "OPENAI_MODEL_NAME": "qwen3:8b",
}

_cache: dict[str, str] = {}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _env_fallback(key: str) -> str:
    if key in os.environ and os.environ[key]:
        return os.environ[key]
    alt = key.lower() if key != key.lower() else None
    if alt and os.getenv(alt):
        return os.environ[alt]
    return ENV_DEFAULTS.get(key, "")


def get_setting(key: str, default: str | None = None) -> str:
    cached = _cache.get(key)
    if cached:
        return cached
    value = _env_fallback(key)
    if value:
        return value
    return default or ""


async def load_cache() -> None:
    db = await open_db()
    try:
        rows = await db.execute_fetchall("SELECT key, value FROM app_settings")
        _cache.clear()
        for row in rows:
            if row["value"]:
                _cache[row["key"]] = row["value"]
    finally:
        await db.close()


def mask_value(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "••••"
    return f"••••{value[-4:]}"


async def list_settings() -> list[dict]:
    await load_cache()
    out = []
    for key in SETTING_KEYS:
        raw = get_setting(key)
        secret = key in SECRET_KEYS
        out.append(
            {
                "key": key,
                "secret": secret,
                "has_value": bool(raw),
                "value": "" if secret else raw,
                "masked": mask_value(raw) if secret else raw,
            }
        )
    return out


async def save_settings(updates: dict[str, str]) -> list[dict]:
    db = await open_db()
    try:
        now = _utcnow()
        for key, value in updates.items():
            if key not in SETTING_KEYS:
                continue
            if value is None:
                continue
            value = str(value).strip()
            if not value:
                await db.execute("DELETE FROM app_settings WHERE key = ?", (key,))
                _cache.pop(key, None)
                continue
            await db.execute(
                """
                INSERT INTO app_settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                (key, value, now),
            )
            _cache[key] = value
        await db.commit()
    finally:
        await db.close()
    return await list_settings()
