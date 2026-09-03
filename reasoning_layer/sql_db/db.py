"""SQLite setup for auth and chat history."""

import json
import os
import sqlite3
from pathlib import Path

import aiosqlite

DB_PATH = os.getenv(
    "SQLITE_PATH",
    str(Path(__file__).resolve().parent.parent / "credit_ai_db.db"),
)

_SCHEMA = """
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS user_features (
    user_id       INTEGER NOT NULL,
    cin           TEXT    NOT NULL,
    brisk         BOOLEAN,
    insta_summary BOOLEAN,
    credit        BOOLEAN,
    PRIMARY KEY (user_id, cin)
);

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT    NOT NULL,
    display_name  TEXT,
    created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token         TEXT    PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at    TEXT    NOT NULL,
    created_at    TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

CREATE TABLE IF NOT EXISTS chats (
    user_id        INTEGER NOT NULL,
    chat_id        TEXT    NOT NULL,
    sme_data       TEXT    NOT NULL DEFAULT '{}',
    message_trail  TEXT    NOT NULL DEFAULT '[]',
    company_cache  TEXT    NOT NULL DEFAULT '{}',
    updated_at     TEXT    NOT NULL,
    PRIMARY KEY (user_id, chat_id)
);

CREATE INDEX IF NOT EXISTS idx_chats_user_updated
    ON chats(user_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS app_settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS app_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT    NOT NULL,
    level       TEXT    NOT NULL,
    source      TEXT    NOT NULL,
    message     TEXT    NOT NULL,
    request_id  TEXT,
    extra_json  TEXT
);

CREATE TABLE IF NOT EXISTS app_spans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id    TEXT    NOT NULL,
    span_id     TEXT    NOT NULL,
    parent_id   TEXT,
    name        TEXT    NOT NULL,
    start_ts    TEXT    NOT NULL,
    end_ts      TEXT    NOT NULL,
    status      TEXT    NOT NULL,
    attrs_json  TEXT
);

CREATE INDEX IF NOT EXISTS idx_app_logs_ts ON app_logs(id DESC);
CREATE INDEX IF NOT EXISTS idx_app_spans_trace ON app_spans(trace_id);
CREATE INDEX IF NOT EXISTS idx_app_spans_start ON app_spans(start_ts DESC);
CREATE INDEX IF NOT EXISTS idx_app_logs_request ON app_logs(request_id);
CREATE INDEX IF NOT EXISTS idx_app_logs_level ON app_logs(level, id DESC);
"""

_shared = None
_wrapper = None
_init_lock = None


class _SharedConnection:
    """Shared aiosqlite connection; close() is a no-op so existing callers stay safe."""

    def __init__(self, inner: aiosqlite.Connection):
        self._inner = inner

    def __getattr__(self, name):
        return getattr(self._inner, name)

    async def close(self):
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc):
        return False


def _apply_runtime_pragmas(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA cache_size = -8000")


def _add_column(conn: sqlite3.Connection, sql: str) -> None:
    try:
        conn.execute(sql)
    except sqlite3.OperationalError:
        pass


def _backfill_chat_index(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT user_id, chat_id, message_trail, company_cache
        FROM chats
        WHERE IFNULL(message_count, 0) = 0
        """
    ).fetchall()
    for user_id, chat_id, trail_raw, cache_raw in rows:
        try:
            trail = json.loads(trail_raw or "[]")
        except json.JSONDecodeError:
            trail = []
        try:
            cache = json.loads(cache_raw or "{}")
        except json.JSONDecodeError:
            cache = {}
        preview = ""
        if isinstance(trail, list) and trail:
            preview = str((trail[-1] or {}).get("query") or "")[:240]
        labels = []
        if isinstance(cache, dict):
            for cin, slot in cache.items():
                label = cin
                if isinstance(slot, dict):
                    label = slot.get("label") or cin
                labels.append({"cin": cin, "label": label})
        conn.execute(
            """
            UPDATE chats
            SET preview_query = ?, company_labels = ?, message_count = ?
            WHERE user_id = ? AND chat_id = ?
            """,
            (preview, json.dumps(labels), len(trail) if isinstance(trail, list) else 0, user_id, chat_id),
        )


def init_db_sync() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        _apply_runtime_pragmas(conn)
        conn.executescript(_SCHEMA)
        _add_column(conn, "ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")
        _add_column(conn, "ALTER TABLE chats ADD COLUMN preview_query TEXT NOT NULL DEFAULT ''")
        _add_column(conn, "ALTER TABLE chats ADD COLUMN company_labels TEXT NOT NULL DEFAULT '[]'")
        _add_column(conn, "ALTER TABLE chats ADD COLUMN message_count INTEGER NOT NULL DEFAULT 0")
        conn.execute(
            """
            UPDATE users
            SET is_admin = 1
            WHERE id = (SELECT MIN(id) FROM users)
              AND NOT EXISTS (SELECT 1 FROM users WHERE is_admin = 1)
            """
        )
        _backfill_chat_index(conn)
        conn.commit()
    finally:
        conn.close()


async def open_db() -> aiosqlite.Connection:
    global _shared, _wrapper, _init_lock
    if _wrapper is not None:
        return _wrapper
    import asyncio

    if _init_lock is None:
        _init_lock = asyncio.Lock()
    async with _init_lock:
        if _wrapper is not None:
            return _wrapper
        conn = await aiosqlite.connect(DB_PATH)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys = ON")
        await conn.execute("PRAGMA journal_mode = WAL")
        await conn.execute("PRAGMA busy_timeout = 5000")
        await conn.execute("PRAGMA synchronous = NORMAL")
        await conn.execute("PRAGMA temp_store = MEMORY")
        await conn.execute("PRAGMA cache_size = -8000")
        _shared = conn
        _wrapper = _SharedConnection(conn)
        return _wrapper


async def close_db() -> None:
    global _shared, _wrapper
    if _shared is not None:
        await _shared.close()
    _shared = None
    _wrapper = None
