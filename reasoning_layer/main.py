import aiohttp
import json
import os
import sys
import time
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
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
from sql_db.chat_store import (
    cins_needing_fetch,
    create_chat,
    get_chat,
    list_chat_summaries,
    update_chat,
)
from probe_errors import ProbeError
from pydantic import AfterValidator, BaseModel, BeforeValidator, Field
from typing import Annotated
from state_models import chat_memory
from sme_api.probe24_comp_details import company_details
from financial_flatten import flatten_company
from credit_flatten import flatten_credit
from sql_db import auth_store
from sql_db.db import close_db, init_db_sync
from sql_db import ops_store, settings_store
from admin_routes import router as admin_router
from observability import (
    CHAT_IN_FLIGHT,
    LLM_IN_FLIGHT,
    MEMO_IN_FLIGHT,
    env_int,
    metrics_allowed,
    observe_request,
    prometheus_response,
    record_exception,
    track_in_flight,
)
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
    app.state.semaphore_sme_financials = asyncio.Semaphore(
        env_int("PROBE_CONCURRENCY", 16, maximum=64)
    )
    app.state.semaphore_llm = asyncio.Semaphore(
        env_int("CHAT_LLM_CONCURRENCY", 8, maximum=32)
    )
    app.state.semaphore_memo = asyncio.Semaphore(
        env_int("MEMO_CONCURRENCY", 2, maximum=8)
    )
    app.state.client = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=120, connect=15, sock_read=90),
        connector=aiohttp.TCPConnector(
            limit=64,
            limit_per_host=24,
            ttl_dns_cache=300,
            enable_cleanup_closed=True,
        ),
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


_NOISY_PATHS = ("/admin/logs", "/admin/traces", "/admin/metrics", "/health", "/metrics")


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
        record_exception(type(exc).__name__, request.url.path)
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


@app.get("/metrics")
async def metrics(request: Request):
    if not metrics_allowed(request):
        raise HTTPException(status_code=404, detail="Not found")
    return prometheus_response()

def strip_query(value: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError("query required")
    return text


def as_chat_id(value) -> str:
    key = str(value).strip()
    if not key or len(key) > 80:
        raise ValueError("invalid chat_id")
    return key


def clean_cin_list(value: list[str]) -> list[str]:
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


def extra_cins_from_body(value) -> list[str]:
    from memo_attachments import parse_extra_cins

    if isinstance(value, str):
        return parse_extra_cins(value)
    return parse_extra_cins(" ".join(str(item) for item in (value or []) if item))


def extra_searches_from_body(value) -> list[str]:
    from memo_attachments import parse_search_lines

    if isinstance(value, str):
        return parse_search_lines(value)
    return parse_search_lines("\n".join(str(item) for item in (value or []) if item))


def drop_client_attachments(_value):
    return []


class ChatRequest(BaseModel):
    cin_list: Annotated[list[str], AfterValidator(clean_cin_list)] = Field(
        min_length=1, max_length=12
    )
    query: Annotated[str, AfterValidator(strip_query)] = Field(min_length=1, max_length=4000)
    chat_id: Annotated[str, AfterValidator(as_chat_id)]
    stream: bool = True
    extra_cins: Annotated[list[str], BeforeValidator(extra_cins_from_body)] = Field(
        default_factory=list
    )
    extra_searches: Annotated[list[str], BeforeValidator(extra_searches_from_body)] = Field(
        default_factory=list
    )
    attachments: Annotated[list[tuple[str, str]], BeforeValidator(drop_client_attachments)] = (
        Field(default_factory=list)
    )


STREAM_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}


def _merged_cins(request: ChatRequest) -> ChatRequest:
    seen = []
    for cin in list(request.cin_list) + list(request.extra_cins):
        item = (cin or "").strip()
        if not item or item in seen:
            continue
        seen.append(item)
        if len(seen) >= 12:
            break
    return request.model_copy(update={"cin_list": seen})


async def _uploaded_attachments(form) -> list[tuple[str, str]]:
    from memo_attachments import extract_attachment

    attachments = []
    uploads = form.getlist("files")
    if len(uploads) > 6:
        raise HTTPException(status_code=400, detail="Attach at most 6 files.")
    for item in uploads:
        filename = getattr(item, "filename", None) or "upload"
        reader = getattr(item, "read", None)
        if not callable(reader):
            continue
        data = await reader()
        try:
            text = extract_attachment(filename, data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        attachments.append((filename, text))
    return attachments


async def parse_chat_request(request: Request) -> ChatRequest:
    content_type = request.headers.get("content-type") or ""
    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        try:
            cin_list = json.loads(str(form.get("cin_list") or "[]"))
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="invalid cin_list") from exc
        if not isinstance(cin_list, list):
            raise HTTPException(status_code=400, detail="invalid cin_list")
        attachments = await _uploaded_attachments(form)
        chat_req = ChatRequest.model_validate(
            {
                "cin_list": cin_list,
                "query": str(form.get("query") or ""),
                "chat_id": form.get("chat_id"),
                "stream": str(form.get("stream") or "true").strip().lower()
                not in {"0", "false", "no"},
                "extra_cins": str(form.get("extra_cins") or ""),
                "extra_searches": str(form.get("extra_searches") or ""),
            }
        )
        return _merged_cins(chat_req.model_copy(update={"attachments": attachments}))
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="invalid JSON") from exc
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="invalid JSON")
    body.pop("attachments", None)
    return _merged_cins(ChatRequest.model_validate(body))


def _with_chat_extras(query: str, context: str, request: ChatRequest) -> tuple[str, str]:
    from memo_attachments import attachment_blocks, required_search_suffix

    extra_docs = attachment_blocks(request.attachments)
    if extra_docs:
        context = "\n\n".join(part for part in (context, extra_docs) if part.strip())
    return query + required_search_suffix(request.extra_searches), context


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


def _probe_http_error(cin, result):
    if isinstance(result, ProbeError):
        raise HTTPException(status_code=502, detail=str(result)) from result
    if isinstance(result, Exception):
        raise HTTPException(
            status_code=502, detail=f"Could not load filings for {cin}"
        ) from result


async def _load_results(request, chat_history, client, semaphore):
    to_fetch = cins_needing_fetch(chat_history, request.cin_list)
    if to_fetch:
        fetched = await asyncio.gather(
            *[company_details(client, cin, semaphore) for cin in to_fetch],
            return_exceptions=True,
        )
        for cin, res in zip(to_fetch, fetched):
            _probe_http_error(cin, res)
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


def _prepare_chat(request: ChatRequest, user_id: int):
    semaphore = app.state.semaphore_sme_financials
    client = app.state.client
    chat_history = await get_chat(user_id, request.chat_id)
    if chat_history is None:
        chat_history = await create_chat(
            user_id, request.chat_id, request.cin_list, request.query
        )
    if not isinstance(chat_history.sme_data, dict):
        chat_history.sme_data = {}
    _ensure_cache(chat_history)
    results = await _load_results(request, chat_history, client, semaphore)
    return chat_history, results


async def _chat_stream(request: ChatRequest, chat_history, results):
    yield _emit("Loading company data...\n")
    await log_event("info", "agent", f"Loading company data for {len(request.cin_list)} CIN(s)")
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
            credit_flat = flatten_credit(entry)
            if credit_flat.strip():
                slot["credit_flat"] = credit_flat

        context = _followup_context(request.cin_list, cache)
        instruction = FOLLOWUP_INSTRUCTION
        followup_query = (
            f"Answer only this follow-up:\n{request.query}\n\n"
            "Use the reference data below only where this question needs it. "
            "Use web search when the question needs recent news or public facts. "
            "Do not retell the first credit analysis."
        )
        followup_query, context = _with_chat_extras(followup_query, context, request)
        body = ""
        async with app.state.semaphore_llm, track_in_flight(LLM_IN_FLIGHT):
            async for chunk in agen_span(
                "followup.answer",
                chat_endpoint_stream(
                    followup_query, [context], _slim_followup_history(chat_history),
                    is_final=True,
                    instruction=instruction,
                    web_search=True,
                ),
            ):
                body += chunk
                yield _emit(chunk)
        chat_history.message_trail.append(
            {"query": request.query, "response": body}
        )
        await update_chat(chat_history)
        print("", file=sys.stderr, flush=True)
        return

    packets = []
    for entry in results:
        label = _company_label(entry)
        cin = _cin(entry)
        slot = cache.setdefault(cin, {"label": label})
        slot["label"] = label
        flat = flatten_company(entry)
        credit_flat = flatten_credit(entry)
        slot["flat"] = flat
        slot["credit_flat"] = credit_flat
        packets.append(
            f"### {label}\n\n#### Filings\n{flat or '(no standalone tables)'}\n\n"
            f"#### Credit / legal / MSME\n{credit_flat or '(none)'}"
        )

    if not packets:
        for cin in request.cin_list:
            slot = cache.get(cin) or {}
            flat = (slot.get("flat") or "").strip()
            if not flat:
                continue
            label = slot.get("label") or cin
            packets.append(
                f"### {label}\n\n#### Filings\n{flat}\n\n"
                f"#### Credit / legal / MSME\n{slot.get('credit_flat') or '(none)'}"
            )

    if not packets:
        raise ValueError(f"No usable data for {request.cin_list}")

    context = "\n\n".join(packets)
    analysis_query, context = _with_chat_extras(request.query, context, request)
    await log_event("info", "agent", "Writing one-pass credit assessment with web search")
    body = ""
    async with app.state.semaphore_llm, track_in_flight(LLM_IN_FLIGHT):
        async for chunk in agen_span(
            "analysis",
            chat_endpoint_stream(
                analysis_query,
                [context],
                chat_history,
                is_final=True,
                instruction=ANALYSIS_INSTRUCTION,
                web_search=True,
            ),
        ):
            body += chunk
            yield _emit(chunk)

    chat_history.message_trail.append(
        {"query": request.query, "response": body}
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
    request: Request,
    user_id: int = Depends(get_current_user_id),
):
    try:
        chat_request = await parse_chat_request(request)
        async with span("load_company_data", cins=",".join(chat_request.cin_list)):
            chat_history, results = await _prepare_chat(chat_request, user_id)
    except HTTPException:
        raise
    except ProbeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    async def stream():
        async with track_in_flight(CHAT_IN_FLIGHT):
            try:
                async for chunk in _traced_stream(
                    "chat", chat_request, _chat_stream(chat_request, chat_history, results)
                ):
                    yield chunk
            except Exception as e:
                record_exception(type(e).__name__, "/chat")
                import traceback
                with open("error.log", "a", encoding="utf-8") as f:
                    traceback.print_exc(file=f)
                raise e

    if chat_request.stream:
        return StreamingResponse(
            stream(), media_type="text/plain; charset=utf-8", headers=STREAM_HEADERS
        )
    try:
        return await _collect(_chat_stream(chat_request, chat_history, results))
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
        if not str(cin).startswith("_") and isinstance(slot, dict)
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
    if chat is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "user_id": chat.user_id,
        "chat_id": chat.chat_id,
        "message_trail": chat.message_trail,
        "preview": (chat.message_trail[0].get("query") if chat.message_trail else "") or "",
        "message_count": len(chat.message_trail or []),
        "company_cache": _public_company_cache(chat.company_cache),
    }


@app.post("/chat/{chat_id}/memo")
async def download_memo(
    request: Request,
    chat_id: str,
    format: str = Query("pdf"),
    user_id: int = Depends(get_current_user_id),
):
    if not chat_id or len(chat_id) > 80:
        raise HTTPException(status_code=404, detail="Not found")
    chat = await get_chat(user_id, chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Not found")

    from memo_attachments import parse_extra_cins, parse_search_lines
    from memo_generate import (
        collect_chart_sets,
        company_slots,
        memo_brief,
        merge_auto_peer_cins,
        merge_extra_companies,
        render_memo_bytes,
        write_memo_markdown,
    )

    brief = memo_brief()
    content_type = request.headers.get("content-type") or ""
    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        format = str(form.get("format") or format)
        include_raw = str(form.get("include_chat") or "true").strip().lower()
        auto_raw = str(form.get("auto_peers") or "true").strip().lower()
        attachments = await _uploaded_attachments(form)
        brief = memo_brief(
            notes=str(form.get("notes") or "")[:4000],
            extra_cins=parse_extra_cins(str(form.get("extra_cins") or "")),
            extra_searches=parse_search_lines(str(form.get("extra_searches") or "")),
            include_chat=include_raw not in {"0", "false", "no"},
            auto_peers=auto_raw not in {"0", "false", "no"},
            attachments=attachments,
        )

    slots = company_slots(chat.company_cache)
    if not slots or not any((slot.get("flat") or "").strip() for _, slot in slots):
        raise HTTPException(
            status_code=400,
            detail="Run a credit analysis first, then download the memo.",
        )

    existing = [cin for cin, _ in slots]
    async with app.state.semaphore_memo, track_in_flight(MEMO_IN_FLIGHT):
        try:
            merge_extra_companies(chat, brief["extra_cins"])
            chart_sets = await collect_chart_sets(
                chat, app.state.client, app.state.semaphore_sme_financials
            )
            merged = merge_auto_peer_cins(
                brief["extra_cins"],
                chart_sets,
                exclude=existing,
                auto=brief["auto_peers"],
            )
            already = {str(cin).strip().upper() for cin, _ in company_slots(chat.company_cache)}
            new_peers = [cin for cin in merged if cin not in already]
            brief["extra_cins"] = merged
            if new_peers:
                merge_extra_companies(chat, new_peers)
                chart_sets.extend(
                    await collect_chart_sets(
                        chat,
                        app.state.client,
                        app.state.semaphore_sme_financials,
                        only_cins=new_peers,
                    )
                )
            markdown = await write_memo_markdown(chat, brief)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        await update_chat(chat)
        company_name = slots[0][1].get("label") or slots[0][0]
        try:
            body, media, filename = await asyncio.to_thread(
                render_memo_bytes, markdown, chart_sets, format, company_name
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            record_exception(type(exc).__name__, "/chat/{id}/memo")
            await log_event("error", "memo", f"render failed: {type(exc).__name__}: {exc}")
            raise HTTPException(
                status_code=500,
                detail="Could not build the memo file. Try Word, or run the analysis again.",
            ) from exc

    return Response(
        content=body,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("REASONING_PORT", "8001")))
    uvicorn.run(app, host=host, port=port, log_level="info")