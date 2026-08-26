"""SQLite setup for auth and chat history."""

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
"""


def init_db_sync() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(_SCHEMA)
        try:
            conn.execute(
                "ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0"
            )
        except sqlite3.OperationalError:
            pass
        conn.execute(
            """
            UPDATE users
            SET is_admin = 1
            WHERE id = (SELECT MIN(id) FROM users)
              AND NOT EXISTS (SELECT 1 FROM users WHERE is_admin = 1)
            """
        )
        conn.commit()
    finally:
        conn.close()


async def open_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON")
    return db
