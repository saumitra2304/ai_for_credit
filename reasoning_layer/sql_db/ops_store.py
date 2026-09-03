"""Logs, traces, and in-memory metric samples for the admin dashboard."""

import asyncio
import json
from collections import deque
from datetime import datetime, timezone
from threading import Lock

from sql_db.db import open_db

LOG_CAP = 20_000
SPAN_CAP = 10_000
SAMPLE_CAP = 2_000
_QUEUE_MAX = 4_000
_BATCH_SIZE = 40
_TRIM_EVERY = 80
_SECRET_FRAGMENTS = ("key", "token", "password", "secret", "authorization", "cookie")

_samples: deque[dict] = deque(maxlen=SAMPLE_CAP)
_samples_lock = Lock()
_queue: asyncio.Queue | None = None
_writer_task: asyncio.Task | None = None
_writes_since_trim = 0


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_extra(extra: dict | None) -> dict | None:
    if not extra:
        return None
    clean = {}
    for key, value in extra.items():
        name = str(key)[:40]
        lowered = name.lower()
        if any(fragment in lowered for fragment in _SECRET_FRAGMENTS):
            continue
        if isinstance(value, str):
            if len(value) > 400:
                value = value[:400] + "…"
        elif isinstance(value, (list, dict)):
            try:
                dumped = json.dumps(value, default=str)
            except (TypeError, ValueError):
                continue
            value = dumped[:800] + "…" if len(dumped) > 800 else value
        clean[name] = value
        if len(clean) >= 24:
            break
    return clean or None


def _clip_message(message: str) -> str:
    text = str(message or "")
    return text if len(text) <= 2000 else text[:2000] + "…"


def _ensure_queue() -> asyncio.Queue:
    global _queue
    if _queue is None:
        _queue = asyncio.Queue(maxsize=_QUEUE_MAX)
    return _queue


def _enqueue(item: tuple | None) -> None:
    global _writer_task
    queue = _ensure_queue()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    if _writer_task is None or _writer_task.done():
        _writer_task = loop.create_task(_writer_loop())
    try:
        queue.put_nowait(item)
    except asyncio.QueueFull:
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            return
        try:
            queue.put_nowait(item)
        except asyncio.QueueFull:
            pass


async def _flush_batch(db, batch: list) -> None:
    global _writes_since_trim
    for kind, payload in batch:
        if kind == "log":
            await db.execute(
                """
                INSERT INTO app_logs (ts, level, source, message, request_id, extra_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                payload,
            )
        elif kind == "span":
            await db.execute(
                """
                INSERT INTO app_spans (
                    trace_id, span_id, parent_id, name, start_ts, end_ts, status, attrs_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                payload,
            )
        else:
            continue
        _writes_since_trim += 1
    await db.commit()
    if _writes_since_trim >= _TRIM_EVERY:
        _writes_since_trim = 0
        await db.execute(
            f"""
            DELETE FROM app_logs
            WHERE id NOT IN (SELECT id FROM app_logs ORDER BY id DESC LIMIT {LOG_CAP})
            """
        )
        await db.execute(
            f"""
            DELETE FROM app_spans
            WHERE id NOT IN (SELECT id FROM app_spans ORDER BY id DESC LIMIT {SPAN_CAP})
            """
        )
        await db.commit()


async def _writer_loop() -> None:
    queue = _ensure_queue()
    db = await open_db()
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        batch = [item]
        while len(batch) < _BATCH_SIZE:
            try:
                nxt = queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            if nxt is None:
                queue.task_done()
                try:
                    await _flush_batch(db, batch)
                except Exception:
                    pass
                for _ in batch:
                    queue.task_done()
                return
            batch.append(nxt)
        try:
            await _flush_batch(db, batch)
        except Exception:
            pass
        for _ in batch:
            queue.task_done()


async def start_writer() -> None:
    global _writer_task
    _ensure_queue()
    if _writer_task is None or _writer_task.done():
        _writer_task = asyncio.create_task(_writer_loop())


async def stop_writer() -> None:
    global _writer_task
    if _writer_task is None:
        return
    _enqueue(None)
    try:
        await asyncio.wait_for(_writer_task, timeout=2)
    except (asyncio.TimeoutError, asyncio.CancelledError):
        _writer_task.cancel()
    _writer_task = None


async def add_log(level: str, source: str, message: str, request_id: str | None = None, extra: dict | None = None) -> None:
    extra = _safe_extra(extra)
    _enqueue(
        (
            "log",
            (
                _utcnow(),
                (level or "info")[:16],
                (source or "app")[:64],
                _clip_message(message),
                request_id,
                json.dumps(extra) if extra else None,
            ),
        )
    )


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
    attrs = _safe_extra(attrs)
    _enqueue(
        (
            "span",
            (
                trace_id,
                span_id,
                parent_id,
                (name or "span")[:120],
                start_ts,
                end_ts,
                status,
                json.dumps(attrs) if attrs else None,
            ),
        )
    )


async def list_traces(limit: int = 50) -> list[dict]:
    limit = max(1, min(limit, 200))
    db = await open_db()
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


async def get_trace(trace_id: str) -> list[dict]:
    db = await open_db()
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
