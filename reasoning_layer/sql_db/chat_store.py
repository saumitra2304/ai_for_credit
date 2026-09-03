"""Chat history backed by the same SQLite file as auth."""

import json
from datetime import datetime, timezone

from sql_db.db import open_db
from state_models import chat_memory


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _chat_id_key(chat_id) -> str:
    return str(chat_id)


def _dumps(value) -> str:
    return json.dumps(value, default=str)


def _index_fields(chat: chat_memory) -> tuple[str, str, int]:
    trail = chat.message_trail if isinstance(chat.message_trail, list) else []
    cache = chat.company_cache if isinstance(chat.company_cache, dict) else {}
    preview = ""
    if trail:
        preview = str((trail[-1] or {}).get("query") or "")[:240]
    labels = [
        {"cin": cin, "label": (slot or {}).get("label") or cin}
        for cin, slot in cache.items()
    ]
    return preview, _dumps(labels), len(trail)


def _row_to_chat(row) -> chat_memory:
    return chat_memory(
        user_id=row["user_id"],
        chat_id=row["chat_id"],
        sme_data=json.loads(row["sme_data"] or "{}"),
        message_trail=json.loads(row["message_trail"] or "[]"),
        company_cache=json.loads(row["company_cache"] or "{}"),
    )


def _labels_to_cache(raw: str | None) -> dict:
    try:
        items = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return {}
    out = {}
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            cin = item.get("cin")
            if cin:
                out[cin] = {"label": item.get("label") or cin}
    return out


async def get_chat(user_id, chat_id):
    db = await open_db()
    rows = await db.execute_fetchall(
        """
        SELECT user_id, chat_id, sme_data, message_trail, company_cache
        FROM chats
        WHERE user_id = ? AND chat_id = ?
        """,
        (user_id, _chat_id_key(chat_id)),
    )
    if not rows:
        return 0
    return _row_to_chat(rows[0])


async def create_chat(user_id, chat_id, _cin_list, _query):
    chat = chat_memory(
        user_id=user_id,
        chat_id=_chat_id_key(chat_id),
        sme_data={},
        message_trail=[],
        company_cache={},
    )
    preview, labels, count = _index_fields(chat)
    db = await open_db()
    await db.execute(
        """
        INSERT INTO chats (
            user_id, chat_id, sme_data, message_trail, company_cache, updated_at,
            preview_query, company_labels, message_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            chat.chat_id,
            _dumps(chat.sme_data),
            _dumps(chat.message_trail),
            _dumps(chat.company_cache),
            _utcnow(),
            preview,
            labels,
            count,
        ),
    )
    await db.commit()
    return chat


async def update_chat(chat: chat_memory):
    preview, labels, count = _index_fields(chat)
    db = await open_db()
    await db.execute(
        """
        UPDATE chats
        SET sme_data = ?, message_trail = ?, company_cache = ?, updated_at = ?,
            preview_query = ?, company_labels = ?, message_count = ?
        WHERE user_id = ? AND chat_id = ?
        """,
        (
            _dumps(chat.sme_data),
            _dumps(chat.message_trail),
            _dumps(chat.company_cache),
            _utcnow(),
            preview,
            labels,
            count,
            chat.user_id,
            _chat_id_key(chat.chat_id),
        ),
    )
    await db.commit()


async def list_chat_summaries(user_id):
    db = await open_db()
    rows = await db.execute_fetchall(
        """
        SELECT user_id, chat_id, preview_query, company_labels, message_count, updated_at
        FROM chats
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (user_id,),
    )
    return [
        {
            "user_id": row["user_id"],
            "chat_id": row["chat_id"],
            "preview": row["preview_query"] or "",
            "message_count": row["message_count"] or 0,
            "updated_at": row["updated_at"],
            "company_cache": _labels_to_cache(row["company_labels"]),
        }
        for row in rows
    ]


async def get_chat_history(user_id):
    db = await open_db()
    rows = await db.execute_fetchall(
        """
        SELECT user_id, chat_id, sme_data, message_trail, company_cache
        FROM chats
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (user_id,),
    )
    return [_row_to_chat(row) for row in rows]
