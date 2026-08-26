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


def _row_to_chat(row) -> chat_memory:
    return chat_memory(
        user_id=row["user_id"],
        chat_id=row["chat_id"],
        sme_data=json.loads(row["sme_data"] or "{}"),
        message_trail=json.loads(row["message_trail"] or "[]"),
        company_cache=json.loads(row["company_cache"] or "{}"),
    )


async def get_chat(user_id, chat_id):
    db = await open_db()
    try:
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
    finally:
        await db.close()


async def create_chat(user_id, chat_id, _cin_list, _query):
    chat = chat_memory(
        user_id=user_id,
        chat_id=_chat_id_key(chat_id),
        sme_data={},
        message_trail=[],
        company_cache={},
    )
    db = await open_db()
    try:
        await db.execute(
            """
            INSERT INTO chats (
                user_id, chat_id, sme_data, message_trail, company_cache, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                chat.chat_id,
                _dumps(chat.sme_data),
                _dumps(chat.message_trail),
                _dumps(chat.company_cache),
                _utcnow(),
            ),
        )
        await db.commit()
    finally:
        await db.close()
    return chat


async def update_chat(chat: chat_memory):
    db = await open_db()
    try:
        await db.execute(
            """
            UPDATE chats
            SET sme_data = ?, message_trail = ?, company_cache = ?, updated_at = ?
            WHERE user_id = ? AND chat_id = ?
            """,
            (
                _dumps(chat.sme_data),
                _dumps(chat.message_trail),
                _dumps(chat.company_cache),
                _utcnow(),
                chat.user_id,
                _chat_id_key(chat.chat_id),
            ),
        )
        await db.commit()
    finally:
        await db.close()


async def get_chat_history(user_id):
    db = await open_db()
    try:
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
    finally:
        await db.close()
