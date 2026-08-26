"""Logs, traces, and in-memory metric samples for the admin dashboard."""

import json
from collections import deque
from datetime import datetime, timezone
from threading import Lock

from sql_db.db import open_db

LOG_CAP = 20_000
SPAN_CAP = 10_000
SAMPLE_CAP = 2_000

_samples: deque[dict] = deque(maxlen=SAMPLE_CAP)
_samples_lock = Lock()


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


async def add_log(level: str, source: str, message: str, request_id: str | None = None, extra: dict | None = None) -> None:
    db = await open_db()
    try:
        await db.execute(
            """
            INSERT INTO app_logs (ts, level, source, message, request_id, extra_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                _utcnow(),
                level,
                source,
                message,
                request_id,
                json.dumps(extra) if extra else None,
            ),
        )
        await db.execute(
            f"""
            DELETE FROM app_logs
            WHERE id NOT IN (SELECT id FROM app_logs ORDER BY id DESC LIMIT {LOG_CAP})
            """
        )
        await db.commit()
    finally:
        await db.close()


async def list_logs(level: str | None = None, source: str | None = None, q: str | None = None, limit: int = 200) -> list[dict]:
    limit = max(1, min(limit, 500))
    clauses = []
    args: list = []
    if level:
        clauses.append("level = ?")
        args.append(level)
    if source:
        clauses.append("source = ?")
        args.append(source)
    if q:
        clauses.append("(message LIKE ? OR IFNULL(request_id, '') LIKE ?)")
        args.extend([f"%{q}%", f"%{q}%"])
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    db = await open_db()
    try:
        rows = await db.execute_fetchall(
            f"""
            SELECT id, ts, level, source, message, request_id, extra_json
            FROM app_logs
            {where}
            ORDER BY id DESC
            LIMIT ?
            """,
            (*args, limit),
        )
        return [
            {
                "id": row["id"],
                "ts": row["ts"],
                "level": row["level"],
                "source": row["source"],
                "message": row["message"],
                "request_id": row["request_id"],
                "extra": json.loads(row["extra_json"]) if row["extra_json"] else None,
            }
            for row in rows
        ]
    finally:
        await db.close()


async def add_span(
    trace_id: str,
    span_id: str,
    name: str,
    start_ts: str,
    end_ts: str | None = None,
    status: str = "ok",
    parent_id: str | None = None,
    attrs: dict | None = None,
) -> None:
    db = await open_db()
    try:
        await db.execute(
            """
            INSERT INTO app_spans (
                trace_id, span_id, parent_id, name, start_ts, end_ts, status, attrs_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace_id,
                span_id,
                parent_id,
                name,
                start_ts,
                end_ts,
                status,
                json.dumps(attrs) if attrs else None,
            ),
        )
        await db.execute(
            f"""
            DELETE FROM app_spans
            WHERE id NOT IN (SELECT id FROM app_spans ORDER BY id DESC LIMIT {SPAN_CAP})
            """
        )
        await db.commit()
    finally:
        await db.close()


async def list_traces(limit: int = 50) -> list[dict]:
    limit = max(1, min(limit, 200))
    db = await open_db()
    try:
        rows = await db.execute_fetchall(
            """
            SELECT
                trace_id,
                MIN(start_ts) AS start_ts,
                MAX(IFNULL(end_ts, start_ts)) AS end_ts,
                SUM(CASE WHEN status != 'ok' THEN 1 ELSE 0 END) AS errors,
                COUNT(*) AS spans,
                (
                    SELECT name FROM app_spans s2
                    WHERE s2.trace_id = app_spans.trace_id
                    ORDER BY CASE WHEN s2.parent_id IS NULL THEN 0 ELSE 1 END, s2.id ASC
                    LIMIT 1
                ) AS name
            FROM app_spans
            GROUP BY trace_id
            ORDER BY start_ts DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [
            {
                "trace_id": row["trace_id"],
                "name": row["name"],
                "start_ts": row["start_ts"],
                "end_ts": row["end_ts"],
                "errors": row["errors"],
                "spans": row["spans"],
            }
            for row in rows
        ]
    finally:
        await db.close()


async def get_trace(trace_id: str) -> list[dict]:
    db = await open_db()
    try:
        rows = await db.execute_fetchall(
            """
            SELECT id, trace_id, span_id, parent_id, name, start_ts, end_ts, status, attrs_json
            FROM app_spans
            WHERE trace_id = ?
            ORDER BY id ASC
            """,
            (trace_id,),
        )
        return [
            {
                "id": row["id"],
                "trace_id": row["trace_id"],
                "span_id": row["span_id"],
                "parent_id": row["parent_id"],
                "name": row["name"],
                "start_ts": row["start_ts"],
                "end_ts": row["end_ts"],
                "status": row["status"],
                "attrs": json.loads(row["attrs_json"]) if row["attrs_json"] else None,
            }
            for row in rows
        ]
    finally:
        await db.close()


def record_sample(path: str, method: str, status: int, duration_ms: float, error: bool) -> None:
    with _samples_lock:
        _samples.append(
            {
                "ts": datetime.now(timezone.utc).timestamp(),
                "path": path,
                "method": method,
                "status": status,
                "duration_ms": duration_ms,
                "error": error,
            }
        )


def metrics_summary(minutes: int = 15) -> dict:
    cutoff = datetime.now(timezone.utc).timestamp() - minutes * 60
    with _samples_lock:
        window = [s for s in _samples if s["ts"] >= cutoff]
    if not window:
        return {
            "minutes": minutes,
            "count": 0,
            "errors": 0,
            "error_rate": 0,
            "p95_ms": 0,
            "avg_ms": 0,
            "buckets": [],
        }

    durations = sorted(s["duration_ms"] for s in window)
    p95_index = min(len(durations) - 1, int(len(durations) * 0.95))
    errors = sum(1 for s in window if s["error"])
    buckets = []
    start = cutoff
    step = 60
    while start < datetime.now(timezone.utc).timestamp():
        end = start + step
        slice_rows = [s for s in window if start <= s["ts"] < end]
        buckets.append(
            {
                "ts": datetime.fromtimestamp(start, tz=timezone.utc).isoformat(),
                "count": len(slice_rows),
                "errors": sum(1 for s in slice_rows if s["error"]),
            }
        )
        start = end

    return {
        "minutes": minutes,
        "count": len(window),
        "errors": errors,
        "error_rate": round(errors / len(window), 4),
        "p95_ms": round(durations[p95_index], 1),
        "avg_ms": round(sum(durations) / len(durations), 1),
        "buckets": buckets,
    }
