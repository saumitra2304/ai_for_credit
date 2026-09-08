import aiohttp
import os
import sys
import time
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
load_dotenv()
from auth_routes import get_current_user_id, router as auth_router
from chat_completion_driver.open_ai import (
    chat_endpoint_stream, FOLLOWUP_INSTRUCTION, ANALYSIS_INSTRUCTION,
)
from sql_db.chat_store import get_chat, create_chat, update_chat, list_chat_summaries
from pydantic import BaseModel, Field, field_validator
from state_models import chat_memory
from sme_api.probe24_comp_details import company_details
from financial_flatten import flatten_company
from credit_flatten import flatten_credit
from sql_db import auth_store
from sql_db.db import close_db, init_db_sync
from sql_db import ops_store, settings_store
from admin_routes import router as admin_router, observe_request
from request_ctx import bind_request_id, log_event, span, agen_span

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_sync()
    await ops_store.start_writer()
    await settings_store.load_cache()
    auth_store.warm_password_hasher()
    bootstrap_email = os.getenv("AUTH_BOOTSTRAP_EMAIL")
    bootstrap_password = os.getenv("AUTH_BOOTSTRAP_PASSWORD")
    if bootstrap_email and bootstrap_password:
        await auth_store.bootstrap_user(
            bootstrap_email,
            bootstrap_password,
            os.getenv("AUTH_BOOTSTRAP_NAME", "Admin"),
        )
    app.state.semaphore_sme_financials = asyncio.Semaphore(10)
    app.state.client = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=120, connect=15, sock_read=90)
    )
    yield
    await app.state.client.close()
    await ops_store.stop_writer()
    await close_db()

app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENABLE_API_DOCS", "").lower() in ("1", "true", "yes") else None,
    redoc_url="/redoc" if os.getenv("ENABLE_API_DOCS", "").lower() in ("1", "true", "yes") else None,
    openapi_url="/openapi.json" if os.getenv("ENABLE_API_DOCS", "").lower() in ("1", "true", "yes") else None,
)

_cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=os.getenv(
        "CORS_ORIGIN_REGEX",
        r"https://.*\.vercel\.app",
    ),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-Id"],
)
app.include_router(auth_router)
app.include_router(admin_router)


def _friendly_validation_message(exc) -> str:
    for err in exc.errors():
        loc = [str(part) for part in err.get("loc", []) if part != "body"]
        field = loc[-1] if loc else "field"
        kind = err.get("type") or ""
        if field == "password" and ("too_short" in kind or "at least" in (err.get("msg") or "").lower()):
            return "Password must be at least 8 characters."
        if field == "email":
            return "Enter a valid email address."
        if kind == "missing":
            return f"Please fill in {field.replace('_', ' ')}."
        msg = err.get("msg") or ""
        if msg.lower().startswith("value error,"):
            return msg.split(",", 1)[-1].strip()
        if msg:
            return msg
    return "Please check the form and try again."


@app.exception_handler(RequestValidationError)
async def validation_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse({"detail": _friendly_validation_message(exc)}, status_code=422)


_NOISY_PATHS = ("/admin/logs", "/admin/traces", "/admin/metrics", "/health")


@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    rid = bind_request_id(request.headers.get("x-request-id"))
    started = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["x-request-id"] = rid
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store"
        return response
    except Exception as exc:
        await log_event("error", "http", f"{request.method} {request.url.path} crashed: {exc}")
        raise
    finally:
        duration = time.perf_counter() - started
        path = request.url.path
        observe_request(request.method, path, status, duration)
        if not path.startswith(_NOISY_PATHS) and request.method != "OPTIONS":
            level = "error" if status >= 400 else "info"
            await log_event(
                level,
                "http",
                f"{request.method} {path} {status} ({duration * 1000:.0f}ms)",
            )


@app.get("/health")
async def health():
    return {"ok": True}

class ChatRequest(BaseModel):
    cin_list: list[str] = Field(min_length=1, max_length=8)
    query: str = Field(min_length=1, max_length=4000)
    chat_id: str | int
    stream: bool = True

    @field_validator("query")
    @classmethod
    def _strip_query(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("query required")
        return text

    @field_validator("chat_id")
    @classmethod
    def _chat_id(cls, value):
        key = str(value).strip()
        if not key or len(key) > 80:
            raise ValueError("invalid chat_id")
        return key

    @field_validator("cin_list")
    @classmethod
    def _clean_cins(cls, value: list[str]) -> list[str]:
        seen = set()
        out = []
        for cin in value:
            item = (cin or "").strip()
            if not item or item in seen:
                continue
            if len(item) > 40:
                raise ValueError("invalid CIN")
            seen.add(item)
            out.append(item)
        if not out:
            raise ValueError("cin_list required")
        return out


STREAM_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}


def _emit(text: str) -> str:
    """Mirror streamed chunks to the server terminal."""
    print(text, end="", file=sys.stderr, flush=True)
    return text


async def _traced_stream(name: str, request: ChatRequest, agen):
    async with span(
        name,
        query=(request.query or "")[:180],
        cins=",".join(request.cin_list),
        chat_id=str(request.chat_id),
    ):
        await log_event(
            "info",
            "agent",
            f"{name} started: {(request.query or '')[:160]}",
            extra={"cins": request.cin_list, "chat_id": str(request.chat_id)},
        )
        try:
            async for chunk in agen:
                yield chunk
            await log_event("info", "agent", f"{name} completed")
        except Exception as exc:
            await log_event("error", "agent", f"{name} failed: {type(exc).__name__}: {exc}")
            raise


async def _collect(gen):
    parts = []
    async for chunk in gen:
        parts.append(chunk)
    return "".join(parts)


async def _load_results(request, chat_history, client, semaphore):
    cins_to_fetch = [
        cin for cin in request.cin_list if cin not in chat_history.sme_data
    ]

    if cins_to_fetch:
        fetched = await asyncio.gather(
            *[company_details(client, cin, semaphore) for cin in cins_to_fetch]
        )
        for cin, res in zip(cins_to_fetch, fetched):
            chat_history.sme_data[cin] = res

    return [chat_history.sme_data[cin] for cin in request.cin_list if cin in chat_history.sme_data]


def _cin(entry: dict) -> str:
    company = (entry.get("data", {}) or {}).get("company", {}) or {}
    return company.get("cin") or "?"


def _ensure_cache(chat_history):
    if not isinstance(chat_history.company_cache, dict):
        chat_history.company_cache = {}


def _is_followup(chat_history, cache: dict, cin_list: list[str]) -> bool:
    if not chat_history.message_trail or not cin_list:
        return False
    return all((cache.get(cin) or {}).get("flat") for cin in cin_list)


def _followup_context(cin_list, cache):
    """Filings tables only. Full prior write-ups make the model ignore the new question."""
    parts = []
    for cin in cin_list:
        slot = cache.get(cin, {})
        label = slot.get("label", cin)
        flat = (slot.get("flat") or "").strip()
        if flat:
            parts.append(f"### {label} — standalone filings\n{flat}")
        else:
            parts.append(f"### {label}\nCIN {cin}. No standalone tables in cache.")
    return "\n\n".join(parts)


def _slim_followup_history(chat_history):
    trail = []
    for item in (chat_history.message_trail or [])[-2:]:
        trail.append(
            {
                "query": (item.get("query") or "")[:400],
                "response": (item.get("response") or "")[:2500],
            }
        )
    return chat_memory(
        user_id=chat_history.user_id,
        chat_id=chat_history.chat_id,
        sme_data={},
        message_trail=trail,
        company_cache={},
    )


def _answer_header(cin_list, cache, results) -> str:
    if len(cin_list) == 1 and results:
        cin = cin_list[0]
        slot = cache.get(cin, {})
        label = slot.get("label") or _company_label(results[0])
        return f"## {label}\n\n"
    return "# Answer\n\n"


async def _chat_stream(request: ChatRequest, user_id: int):
    semaphore = app.state.semaphore_sme_financials
    client = app.state.client

    chat_history = await get_chat(user_id, request.chat_id)
    if chat_history == 0:
        chat_history = await create_chat(
            user_id, request.chat_id, request.cin_list, request.query
        )
    if not isinstance(chat_history.sme_data, dict):
        chat_history.sme_data = {}
    _ensure_cache(chat_history)

    yield _emit("Loading company data...\n")
    await log_event("info", "agent", f"Loading company data for {len(request.cin_list)} CIN(s)")
    async with span("load_company_data", cins=",".join(request.cin_list)):
        results = await _load_results(request, chat_history, client, semaphore)
    cache = chat_history.company_cache

    # Follow-up: all companies cached + prior messages — answer only the new question.
    if _is_followup(chat_history, cache, request.cin_list):
        print("[followup] one-pass answer", file=sys.stderr, flush=True)
        await log_event("info", "agent", "Follow-up: one GPT call with web search")
        for entry in results:
            cin = _cin(entry)
            slot = cache.get(cin, {})
            flat = flatten_company(entry)
            if flat.strip():
                slot["flat"] = flat

        header = _answer_header(request.cin_list, cache, results)
        context = _followup_context(request.cin_list, cache)
        instruction = FOLLOWUP_INSTRUCTION
        followup_query = (
            f"Answer only this follow-up:\n{request.query}\n\n"
            "Use the reference data below only where this question needs it. "
            "Use web search when the question needs recent news or public facts. "
            "Do not retell the first credit analysis."
        )
        body = ""
        started = False
        async for chunk in agen_span(
            "followup.answer",
            chat_endpoint_stream(
                followup_query, [context], _slim_followup_history(chat_history),
                is_final=True,
                instruction=instruction,
                web_search=True,
            ),
        ):
            if not started:
                yield _emit(header)
                started = True
            body += chunk
            yield _emit(chunk)
        chat_response = header + body
        chat_history.message_trail.append(
            {"query": request.query, "response": chat_response}
        )
        await update_chat(chat_history)
        print("", file=sys.stderr, flush=True)
        return

    packets = []
    for entry in results:
        label = _company_label(entry)
        cin = _cin(entry)
        slot = cache.setdefault(cin, {"label": label})
        flat = flatten_company(entry)
        credit_flat = flatten_credit(entry)
        slot["flat"] = flat
        packets.append(
            f"### {label}\n\n#### Filings\n{flat or '(no standalone tables)'}\n\n"
            f"#### Credit / legal / MSME\n{credit_flat or '(none)'}"
        )

    if not packets:
        raise ValueError(f"No usable data for {request.cin_list}")

    header = _answer_header(request.cin_list, cache, results)
    context = "\n\n".join(packets)
    await log_event("info", "agent", "Writing one-pass credit assessment with web search")
    body = ""
    started = False
    async for chunk in agen_span(
        "analysis",
        chat_endpoint_stream(
            request.query,
            [context],
            chat_history,
            is_final=True,
            instruction=ANALYSIS_INSTRUCTION,
            web_search=True,
        ),
    ):
        if not started:
            yield _emit(header)
            started = True
        body += chunk
        yield _emit(chunk)

    report = header + body
    chat_response = report

    chat_history.message_trail.append(
        {"query": request.query, "response": chat_response}
    )
    await update_chat(chat_history)
    print("", file=sys.stderr, flush=True)


def _company_label(entry: dict) -> str:
    """Pull a display name for headers without depending on flatten_company's
    text output."""
    company = (entry.get("data", {}) or {}).get("company", {}) or {}
    name = company.get("legal_name") or "Unknown company"
    cin = company.get("cin") or "?"
    return f"{name} (CIN {cin})"


@app.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
):
    async def stream():
        try:
            async for chunk in _traced_stream("chat", request, _chat_stream(request, user_id)):
                yield chunk
        except Exception as e:
            import traceback
            with open("error.log", "a", encoding="utf-8") as f:
                traceback.print_exc(file=f)
            raise e

    if request.stream:
        return StreamingResponse(
            stream(), media_type="text/plain; charset=utf-8", headers=STREAM_HEADERS
        )
    try:
        return await _collect(_chat_stream(request, user_id))
    except Exception as e:
        import traceback
        with open("error.log", "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise e


def _public_company_cache(cache: dict | None) -> dict:
    return {
        cin: {
            key: val
            for key, val in (slot or {}).items()
            if key in ("label", "flat")
        }
        for cin, slot in (cache or {}).items()
    }


@app.get("/chat_history")
async def chat_history(user_id: int = Depends(get_current_user_id)):
    try:
        return await list_chat_summaries(user_id)
    except Exception as e:
        import traceback
        with open("error.log", "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise e


@app.get("/chat_history/{chat_id}")
async def chat_history_one(chat_id: str, user_id: int = Depends(get_current_user_id)):
    if not chat_id or len(chat_id) > 80:
        raise HTTPException(status_code=404, detail="Not found")
    chat = await get_chat(user_id, chat_id)
    if chat == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "user_id": chat.user_id,
        "chat_id": chat.chat_id,
        "message_trail": chat.message_trail,
        "preview": (chat.message_trail[0].get("query") if chat.message_trail else "") or "",
        "message_count": len(chat.message_trail or []),
        "company_cache": _public_company_cache(chat.company_cache),
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("REASONING_PORT", "8001")))
    uvicorn.run(app, host=host, port=port, log_level="info")