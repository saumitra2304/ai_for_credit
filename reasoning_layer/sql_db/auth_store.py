"""User registration, login, and session management backed by SQLite."""

import hashlib
import os
import re
import secrets
import time
from datetime import datetime, timedelta, timezone

from sql_db.db import open_db

HASH_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = int(os.getenv("AUTH_PBKDF2_ITERATIONS", "600000"))
SESSION_DAYS = int(os.getenv("SESSION_DAYS", "7"))
MIN_PASSWORD_LEN = int(os.getenv("AUTH_MIN_PASSWORD_LEN", "8"))
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")
_TOKEN_CACHE_TTL = 8.0
_token_cache: dict[str, tuple[float, dict]] = {}


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_email(email: str, *, validate: bool = False) -> str:
    value = (email or "").strip().lower()
    if validate and (not _EMAIL_RE.match(value) or len(value) > 254):
        raise AuthError("Enter a valid email address.", status_code=400)
    if not value:
        raise AuthError("Invalid email or password.", status_code=401)
    return value


def _cache_user(token: str, user: dict) -> None:
    if len(_token_cache) > 2048:
        _token_cache.clear()
    _token_cache[token] = (time.monotonic() + _TOKEN_CACHE_TTL, user)


def _cached_user(token: str) -> dict | None:
    hit = _token_cache.get(token)
    if not hit:
        return None
    expires, user = hit
    if expires <= time.monotonic():
        _token_cache.pop(token, None)
        return None
    return user


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return f"{HASH_ALGORITHM}${PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algo, iterations, salt, expected_hex = stored_hash.split("$", 3)
        if algo != HASH_ALGORITHM:
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        )
        return secrets.compare_digest(digest.hex(), expected_hex)
    except (ValueError, TypeError):
        return False


def _validate_password(password: str) -> None:
    if len(password) < MIN_PASSWORD_LEN:
        raise AuthError(
            f"Password must be at least {MIN_PASSWORD_LEN} characters.",
            status_code=400,
        )


def _user_row(row) -> dict:
    try:
        is_admin = bool(row["is_admin"])
    except (IndexError, KeyError):
        is_admin = False
    return {
        "id": row["id"],
        "email": row["email"],
        "display_name": row["display_name"],
        "created_at": row["created_at"],
        "is_admin": is_admin,
    }


async def register_user(email: str, password: str, display_name: str | None = None) -> dict:
    email = _normalize_email(email, validate=True)
    _validate_password(password)

    db = await open_db()
    try:
        existing = await db.execute_fetchall(
            "SELECT id FROM users WHERE email = ?",
            (email,),
        )
        if existing:
            raise AuthError("An account with this email already exists.", status_code=409)

        now = _utcnow().isoformat()
        password_hash = hash_password(password)
        existing_users = await db.execute_fetchall("SELECT COUNT(*) AS count FROM users")
        is_admin = 1 if not existing_users[0]["count"] else 0
        cursor = await db.execute(
            """
            INSERT INTO users (email, password_hash, display_name, created_at, is_admin)
            VALUES (?, ?, ?, ?, ?)
            """,
            (email, password_hash, display_name, now, is_admin),
        )
        user_id = cursor.lastrowid
        token, expires_at = await _create_session(db, user_id)
        await db.commit()
        user = {
            "id": user_id,
            "email": email,
            "display_name": display_name,
            "created_at": now,
            "is_admin": bool(is_admin),
        }
        return {
            "token": token,
            "expires_at": expires_at,
            "user": user,
        }
    finally:
        await db.close()


async def login_user(email: str, password: str) -> dict:
    email = _normalize_email(email)

    db = await open_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id, email, password_hash, display_name, created_at, COALESCE(is_admin, 0) AS is_admin FROM users WHERE email = ?",
            (email,),
        )
        if not rows:
            raise AuthError("Invalid email or password.", status_code=401)

        row = rows[0]
        if not verify_password(password, row["password_hash"]):
            raise AuthError("Invalid email or password.", status_code=401)

        token, expires_at = await _create_session(db, row["id"])
        await db.commit()
        return {
            "token": token,
            "expires_at": expires_at,
            "user": _user_row(row),
        }
    finally:
        await db.close()


async def logout_user(token: str) -> None:
    _token_cache.pop(token, None)
    db = await open_db()
    try:
        await db.execute("DELETE FROM sessions WHERE token = ?", (token,))
        await db.commit()
    finally:
        await db.close()


async def get_user_for_token(token: str) -> dict | None:
    if not token:
        return None
    cached = _cached_user(token)
    if cached:
        return cached

    db = await open_db()
    try:
        rows = await db.execute_fetchall(
            """
            SELECT u.id, u.email, u.display_name, u.created_at, COALESCE(u.is_admin, 0) AS is_admin, s.expires_at
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
            """,
            (token,),
        )
        if not rows:
            return None

        row = rows[0]
        expires_at = datetime.fromisoformat(row["expires_at"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= _utcnow():
            _token_cache.pop(token, None)
            await db.execute("DELETE FROM sessions WHERE token = ?", (token,))
            await db.commit()
            return None

        user = _user_row(row)
        _cache_user(token, user)
        return user
    finally:
        await db.close()


async def get_user_id_for_token(token: str) -> int | None:
    user = await get_user_for_token(token)
    return user["id"] if user else None


async def bootstrap_user(email: str, password: str, display_name: str | None = None) -> None:
    """Create the first admin user when the database has no users."""
    db = await open_db()
    try:
        rows = await db.execute_fetchall("SELECT COUNT(*) AS count FROM users")
        if rows[0]["count"]:
            return
    finally:
        await db.close()

    await register_user(email, password, display_name)


async def _create_session(db, user_id: int) -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    now = _utcnow()
    expires_at = (now + timedelta(days=SESSION_DAYS)).isoformat()
    await db.execute(
        """
        INSERT INTO sessions (token, user_id, expires_at, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (token, user_id, expires_at, now.isoformat()),
    )
    return token, expires_at
