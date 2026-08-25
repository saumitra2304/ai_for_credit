import os

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from sql_db import auth_store

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=120)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class AuthResponse(BaseModel):
    token: str
    expires_at: str
    user: dict


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


async def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")
    user = await auth_store.get_user_for_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return user


async def get_current_user_id(user: dict = Depends(get_current_user)) -> int:
    return user["id"]


@router.post("/register", response_model=AuthResponse)
async def register(body: RegisterRequest):
    allow_register = os.getenv("AUTH_ALLOW_REGISTER", "true").lower() in ("1", "true", "yes")
    if not allow_register:
        raise HTTPException(status_code=403, detail="Registration is disabled.")
    try:
        return await auth_store.register_user(
            body.email, body.password, body.display_name
        )
    except auth_store.AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest):
    try:
        return await auth_store.login_user(body.email, body.password)
    except auth_store.AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/logout")
async def logout(authorization: str | None = Header(default=None)):
    token = _extract_bearer_token(authorization)
    if token:
        await auth_store.logout_user(token)
    return {"ok": True}


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return {"user": user}
