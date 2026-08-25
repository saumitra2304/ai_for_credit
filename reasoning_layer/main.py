import aiohttp
import os
import sys
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from auth_routes import get_current_user_id, router as auth_router
from chat_completion_driver.open_ai import (
    chat_endpoint_stream, CREDIT_INSTRUCTION, NEWS_INSTRUCTION, FOLLOWUP_INSTRUCTION,
)
from sme_api.insta_summary_f import insta_summary
from pydantic import BaseModel
from mongo_driver.chat_db import get_chat, create_chat, update_chat, get_chat_history
from sme_api.probe24_comp_details import company_details
from financial_flatten import flatten_company
from credit_flatten import flatten_credit
from news_flatten import fetch_company_news, flatten_news
from sql_db import auth_store
from sql_db.db import init_db_sync

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_sync()
    bootstrap_email = os.getenv("AUTH_BOOTSTRAP_EMAIL")
    bootstrap_password = os.getenv("AUTH_BOOTSTRAP_PASSWORD")
    if bootstrap_email and bootstrap_password:
        await auth_store.bootstrap_user(
            bootstrap_email,
            bootstrap_password,
            os.getenv("AUTH_BOOTSTRAP_NAME", "Admin"),
        )
    app.state.semaphore_sme_financials = asyncio.Semaphore(10)
    app.state.semaphore_news = asyncio.Semaphore(5)
    app.state.client = aiohttp.ClientSession()
    yield
    await app.state.client.close()

app = FastAPI(lifespan=lifespan)

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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)

class ChatRequest(BaseModel):
    cin_list: list[str]
    query: str
    chat_id: str | int
    stream: bool = True


STREAM_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}


def _emit(text: str) -> str:
    """Mirror streamed chunks to the server terminal."""
    print(text, end="", file=sys.stderr, flush=True)
    return text


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


def _company_llm_needed(cache: dict, cin: str) -> bool:
    slot = cache.get(cin, {})
    return not (slot.get("credit") and slot.get("news") and "detail" in slot)


def _join_company_blocks(cin_list, cache, key):
    blocks = [cache[cin][key] for cin in cin_list if cache.get(cin, {}).get(key)]
    return "\n\n---\n\n".join(blocks)


def _all_companies_cached(cache: dict, cin_list: list[str]) -> bool:
    return bool(cin_list) and all(not _company_llm_needed(cache, cin) for cin in cin_list)


def _is_followup(chat_history, cache: dict, cin_list: list[str]) -> bool:
    return bool(chat_history.message_trail) and _all_companies_cached(cache, cin_list)


def _followup_context(cin_list, cache):
    parts = []
    for cin in cin_list:
        slot = cache.get(cin, {})
        label = slot.get("label", cin)
        if slot.get("flat"):
            parts.append(f"### {label} — financials\n{slot['flat']}")
        if slot.get("credit"):
            parts.append(f"### {label} — credit (prior analysis)\n{slot['credit']}")
        if slot.get("news"):
            parts.append(f"### {label} — news (prior analysis)\n{slot['news']}")
        if slot.get("detail"):
            parts.append(f"### {label} — prior financial analysis\n{slot['detail']}")
    return "\n\n".join(parts)


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
    results = await _load_results(request, chat_history, client, semaphore)
    cache = chat_history.company_cache

    # Follow-up: all companies cached + prior messages — answer only the new question.
    if _is_followup(chat_history, cache, request.cin_list):
        print("[followup] skipping credit/news/detail; direct answer only",
              file=sys.stderr, flush=True)
        sections = []
        for entry in results:
            cin = _cin(entry)
            slot = cache.get(cin, {})
            if slot.get("detail"):
                sections.append(slot["detail"])
            flat = flatten_company(entry)
            if flat.strip():
                slot["flat"] = flat

        header = _answer_header(request.cin_list, cache, results)
        context = _followup_context(request.cin_list, cache)
        body = ""
        started = False
        async for chunk in chat_endpoint_stream(
            request.query, [context], chat_history, is_final=True,
            instruction=FOLLOWUP_INSTRUCTION,
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
        if len(chat_history.message_trail) > 2:
            chat_history.message_trail = chat_history.message_trail[-2:]
        await update_chat(chat_history)
        print("", file=sys.stderr, flush=True)
        return

    sections = []
    flats = []

    yield _emit("\n# Per-Company Credit Answer\n\n")
    credit_answer = ""
    async for chunk in credit_tool_stream(
        request, user_id, results=results, chat_history=chat_history, company_cache=cache
    ):
        credit_answer += chunk
        yield _emit(chunk)

    yield _emit("\n\n---\n\n# Per-Company News\n\n")
    news_answer = ""
    async for chunk in news_tool_stream(
        request, user_id, results=results, chat_history=chat_history,
        client=client, company_cache=cache,
    ):
        news_answer += chunk
        yield _emit(chunk)

    detail_started = False
    for entry in results:
        label = _company_label(entry)
        cin = _cin(entry)
        slot = cache.setdefault(cin, {"label": label})
        flat = flatten_company(entry)

        if not flat.strip():
            print(
                f"[skip] no STANDALONE 2023-2025 financials for {label}",
                file=sys.stderr, flush=True,
            )
            block = f"## {label}\n\nNo 2023-2025 standalone financials on record."
            if _company_llm_needed(cache, cin):
                slot["detail"] = block
                slot["flat"] = ""
            if not detail_started:
                yield _emit("\n\n---\n\n# Per-Company Detail\n\n")
                detail_started = True
            yield _emit(slot["detail"])
            sections.append(slot["detail"])
            continue

        slot["flat"] = flat
        if not detail_started:
            yield _emit("\n\n---\n\n# Per-Company Detail\n\n")
            detail_started = True

        if slot.get("detail") and not _company_llm_needed(cache, cin):
            print(f"[cache hit] detail for {label}", file=sys.stderr, flush=True)
            yield _emit(slot["detail"])
            sections.append(slot["detail"])
            flats.append((label, flat))
            continue

        header = f"## {label}\n\n"
        yield _emit(header)
        section = header
        per_company_query = f"{request.query}\n\n(This call covers only: {label}.)"
        answer = ""
        async for chunk in chat_endpoint_stream(
            per_company_query, [flat], chat_history, is_final=True
        ):
            answer += chunk
            section += chunk
            yield _emit(chunk)
        slot["detail"] = section
        sections.append(section)
        flats.append((label, flat))

    if not sections:
        raise ValueError(f"No usable data for {request.cin_list}")

    answer_header = _answer_header(request.cin_list, cache, results)
    run_synthesis = len(flats) > 1 or bool(chat_history.message_trail)
    if run_synthesis and flats:
        combined_tables = "\n\n".join(
            f"### {label}\n{table}" for label, table in flats
        )
        synthesis_query = request.query
        if len(flats) > 1:
            synthesis_query += (
                f"\n\nYou have already produced a detailed breakdown for each company "
                f"individually (shown after this answer). Answer the question above "
                f"directly, comparing across all {len(flats)} companies using the "
                f"tables below. Be direct and specific -- name the company where "
                f"relevant rather than describing them abstractly."
            )
        body = ""
        started = False
        async for chunk in chat_endpoint_stream(
            synthesis_query, [combined_tables], chat_history, is_final=True
        ):
            if not started:
                yield _emit("\n\n---\n\n" + answer_header)
                started = True
            body += chunk
            yield _emit(chunk)
        final_answer = body
    elif flats:
        slot0 = cache.get(_cin(results[0]), {})
        detail = slot0.get("detail", sections[0])
        final_answer = detail.split("\n\n", 1)[-1] if detail.startswith("## ") else detail
        yield _emit(final_answer)
    else:
        final_answer = sections[0]
        yield _emit(final_answer)

    credit_answer = _join_company_blocks(request.cin_list, cache, "credit") or credit_answer
    news_answer = _join_company_blocks(request.cin_list, cache, "news") or news_answer

    chat_response = (
        answer_header + final_answer
        + "\n\n---\n\n# Per-Company Credit Answer\n\n"
        + credit_answer
        + "\n\n---\n\n# Per-Company News\n\n"
        + news_answer
        + "\n\n---\n\n# Per-Company Detail\n\n"
        + "\n\n---\n\n".join(sections)
    )

    chat_history.message_trail.append(
        {"query": request.query, "response": chat_response}
    )
    if len(chat_history.message_trail) > 2:
        chat_history.message_trail = chat_history.message_trail[-2:]
    await update_chat(chat_history)
    print("", file=sys.stderr, flush=True)


async def _news_stream(request: ChatRequest, user_id: int):
    semaphore = app.state.semaphore_sme_financials
    client = app.state.client

    chat_history = await get_chat(user_id, request.chat_id)
    if chat_history == 0:
        chat_history = await create_chat(
            user_id, request.chat_id, request.cin_list, request.query
        )
    if not isinstance(chat_history.sme_data, dict):
        chat_history.sme_data = {}

    yield _emit("Loading company data...\n")
    results = await _load_results(request, chat_history, client, semaphore)

    chat_response = ""
    async for chunk in news_tool_stream(
        request, user_id, results=results, chat_history=chat_history, client=client
    ):
        chat_response += chunk
        yield _emit(chunk)

    if not chat_response.strip():
        raise ValueError(f"No usable data for {request.cin_list}")

    chat_history.message_trail.append(
        {"query": request.query, "response": chat_response}
    )
    if len(chat_history.message_trail) > 2:
        chat_history.message_trail = chat_history.message_trail[-2:]
    await update_chat(chat_history)
    print("", file=sys.stderr, flush=True)


async def _credit_stream(request: ChatRequest, user_id: int):
    semaphore = app.state.semaphore_sme_financials
    client = app.state.client

    chat_history = await get_chat(user_id, request.chat_id)
    if chat_history == 0:
        chat_history = await create_chat(
            user_id, request.chat_id, request.cin_list, request.query
        )
    if not isinstance(chat_history.sme_data, dict):
        chat_history.sme_data = {}

    yield _emit("Loading company data...\n")
    results = await _load_results(request, chat_history, client, semaphore)

    chat_response = ""
    async for chunk in credit_tool_stream(
        request, user_id, results=results, chat_history=chat_history
    ):
        chat_response += chunk
        yield _emit(chunk)

    if not chat_response.strip():
        raise ValueError(f"No usable data for {request.cin_list}")

    chat_history.message_trail.append(
        {"query": request.query, "response": chat_response}
    )
    if len(chat_history.message_trail) > 2:
        chat_history.message_trail = chat_history.message_trail[-2:]
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
            async for chunk in _chat_stream(request, user_id):
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


@app.post("/news")
async def news(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
):
    async def stream():
        try:
            async for chunk in _news_stream(request, user_id):
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
        return await _collect(_news_stream(request, user_id))
    except Exception as e:
        import traceback
        with open("error.log", "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise e


@app.post("/credit")
async def credit(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
):
    async def stream():
        try:
            async for chunk in _credit_stream(request, user_id):
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
        return await _collect(_credit_stream(request, user_id))
    except Exception as e:
        import traceback
        with open("error.log", "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise e

async def news_tool_stream(
    request, user_id, results=None, chat_history=None, client=None, company_cache=None,
):
    if chat_history is None:
        chat_history = await get_chat(user_id, request.chat_id)
        if chat_history == 0:
            chat_history = await create_chat(
                user_id, request.chat_id, request.cin_list, request.query
            )
        if not isinstance(chat_history.sme_data, dict):
            chat_history.sme_data = {}
    _ensure_cache(chat_history)
    if company_cache is None:
        company_cache = chat_history.company_cache

    if results is None:
        semaphore = app.state.semaphore_sme_financials
        if client is None:
            client = app.state.client
        results = await _load_results(request, chat_history, client, semaphore)

    if not results:
        raise ValueError(f"No usable data for {request.cin_list}")

    if client is None:
        client = app.state.client
    news_sem = app.state.semaphore_news

    for i, entry in enumerate(results):
        cin = _cin(entry)
        label = _company_label(entry)
        slot = company_cache.setdefault(cin, {"label": label})

        if i:
            yield "\n\n---\n\n"

        if slot.get("news") and not _company_llm_needed(company_cache, cin):
            print(f"[cache hit] news for {label}", file=sys.stderr, flush=True)
            yield slot["news"]
            continue

        company = (entry.get("data", {}) or {}).get("company", {}) or {}
        name = company.get("legal_name") or label

        categories = await fetch_company_news(client, name, news_sem)
        flat = flatten_news(label, categories)
        query = f"{request.query}\n\n(This call covers only: {label}.)"
        header = f"## {label}\n\n"
        yield header
        block = header
        async for chunk in chat_endpoint_stream(
            query, [flat], chat_history, is_final=True,
            instruction=NEWS_INSTRUCTION,
        ):
            block += chunk
            yield chunk
        slot["news"] = block


async def credit_tool_stream(
    request, user_id, results=None, chat_history=None, company_cache=None,
):
    if chat_history is None:
        chat_history = await get_chat(user_id, request.chat_id)
        if chat_history == 0:
            chat_history = await create_chat(
                user_id, request.chat_id, request.cin_list, request.query
            )
        if not isinstance(chat_history.sme_data, dict):
            chat_history.sme_data = {}
    _ensure_cache(chat_history)
    if company_cache is None:
        company_cache = chat_history.company_cache

    if results is None:
        semaphore = app.state.semaphore_sme_financials
        client = app.state.client
        results = await _load_results(request, chat_history, client, semaphore)

    if not results:
        raise ValueError(f"No usable data for {request.cin_list}")

    for i, entry in enumerate(results):
        cin = _cin(entry)
        label = _company_label(entry)
        slot = company_cache.setdefault(cin, {"label": label})

        if i:
            yield "\n\n---\n\n"

        if slot.get("credit") and not _company_llm_needed(company_cache, cin):
            print(f"[cache hit] credit for {label}", file=sys.stderr, flush=True)
            yield slot["credit"]
            continue

        flat = flatten_credit(entry)
        query = f"{request.query}\n\n(This call covers only: {label}.)"
        header = f"## {label}\n\n"
        yield header
        block = header
        async for chunk in chat_endpoint_stream(
            query, [flat], chat_history, is_final=True,
            instruction=CREDIT_INSTRUCTION,
        ):
            block += chunk
            yield chunk
        slot["credit"] = block


async def credit_tool(
    request: ChatRequest, user_id: int, results=None, chat_history=None, persist=True,
):
    try:
        if chat_history is None:
            chat_history = await get_chat(user_id, request.chat_id)
            if chat_history == 0:
                chat_history = await create_chat(
                    user_id, request.chat_id, request.cin_list, request.query
                )
            if not isinstance(chat_history.sme_data, dict):
                chat_history.sme_data = {}

        pieces = []
        async for chunk in credit_tool_stream(
            request, user_id, results=results, chat_history=chat_history
        ):
            pieces.append(chunk)
        chat_response = "".join(pieces)

        if persist:
            chat_history.message_trail.append(
                {"query": request.query, "response": chat_response}
            )
            if len(chat_history.message_trail) > 2:
                chat_history.message_trail = chat_history.message_trail[-2:]
            await update_chat(chat_history)
        return chat_response
    except Exception as e:
        import traceback
        with open("error.log", "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise e

@app.get("/chat_history")
async def chat_history(user_id: int = Depends(get_current_user_id)):
    try:
        history = await get_chat_history(user_id)
        return [
            {
                "user_id": chat.user_id,
                "chat_id": chat.chat_id,
                "message_trail": chat.message_trail,
                "company_cache": {
                    cin: {
                        key: val
                        for key, val in slot.items()
                        if key in ("label", "credit", "news", "detail")
                    }
                    for cin, slot in (chat.company_cache or {}).items()
                },
            }
            for chat in history
        ]
    except Exception as e:
        import traceback
        with open("error.log", "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise e