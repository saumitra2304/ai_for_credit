import aiohttp
import sys
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from chat_completion_driver.open_ai import chat_endpoint_stream, CREDIT_INSTRUCTION
from sme_api.insta_summary_f import insta_summary
from pydantic import BaseModel
from mongo_driver.chat_db import get_chat, create_chat, update_chat, get_chat_history
from sme_api.probe24_comp_details import company_details
from financial_flatten import flatten_company
from credit_flatten import flatten_credit

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.semaphore_sme_financials = asyncio.Semaphore(10)
    app.state.client = aiohttp.ClientSession() 
    yield
    await app.state.client.close()

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    cin_list: list[str]
    query: str
    chat_id: int
    user_id: int
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
    results = []
    cins_to_fetch = []
    for cin in request.cin_list:
        if cin in chat_history.sme_data:
            results.append(chat_history.sme_data[cin])
        else:
            cins_to_fetch.append(cin)

    if cins_to_fetch:
        fetched = await asyncio.gather(
            *[company_details(client, cin, semaphore) for cin in cins_to_fetch]
        )
        for cin, res in zip(cins_to_fetch, fetched):
            chat_history.sme_data[cin] = res
            results.append(res)
    return results


async def _chat_stream(request: ChatRequest):
    semaphore = app.state.semaphore_sme_financials
    client = app.state.client

    chat_history = await get_chat(request.user_id, request.chat_id)
    if chat_history == 0:
        chat_history = await create_chat(
            request.user_id, request.chat_id, request.cin_list, request.query
        )
    if not isinstance(chat_history.sme_data, dict):
        chat_history.sme_data = {}

    yield _emit("Loading company data...\n")
    results = await _load_results(request, chat_history, client, semaphore)

    sections = []
    flats = []
    per_company_answers = []

    yield _emit("\n# Per-Company Credit Answer\n\n")
    credit_answer = ""
    async for chunk in credit_tool_stream(
        request, results=results, chat_history=chat_history
    ):
        credit_answer += chunk
        yield _emit(chunk)

    detail_started = False
    for entry in results:
        label = _company_label(entry)
        flat = flatten_company(entry)

        if not flat.strip():
            print(
                f"[skip] no STANDALONE 2023-2025 financials for {label}",
                file=sys.stderr, flush=True,
            )
            block = f"## {label}\n\nNo 2023-2025 standalone financials on record."
            sections.append(block)
            if not detail_started:
                yield _emit("\n\n---\n\n# Per-Company Detail\n\n")
                detail_started = True
            yield _emit(block)
            continue

        flats.append((label, flat))
        if not detail_started:
            yield _emit("\n\n---\n\n# Per-Company Detail\n\n")
            detail_started = True

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
        per_company_answers.append(answer)
        sections.append(section)

    if not sections:
        raise ValueError(f"No usable data for {request.cin_list}")

    yield _emit("\n\n---\n\n# Answer\n\n")
    if len(flats) > 1:
        combined_tables = "\n\n".join(
            f"### {label}\n{table}" for label, table in flats
        )
        synthesis_query = (
            f"{request.query}\n\n"
            f"You have already produced a detailed breakdown for each company "
            f"individually (shown after this answer). Answer the question above "
            f"directly, comparing across all {len(flats)} companies using the "
            f"tables below. Be direct and specific -- name the company where "
            f"relevant rather than describing them abstractly."
        )
        final_answer = ""
        async for chunk in chat_endpoint_stream(
            synthesis_query, [combined_tables], chat_history, is_final=True
        ):
            final_answer += chunk
            yield _emit(chunk)
    else:
        final_answer = per_company_answers[0]
        yield _emit(final_answer)

    chat_response = (
        "# Answer\n\n" + final_answer
        + "\n\n---\n\n# Per-Company Credit Answer\n\n"
        + credit_answer
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


async def _credit_stream(request: ChatRequest):
    semaphore = app.state.semaphore_sme_financials
    client = app.state.client

    chat_history = await get_chat(request.user_id, request.chat_id)
    if chat_history == 0:
        chat_history = await create_chat(
            request.user_id, request.chat_id, request.cin_list, request.query
        )
    if not isinstance(chat_history.sme_data, dict):
        chat_history.sme_data = {}

    yield _emit("Loading company data...\n")
    results = await _load_results(request, chat_history, client, semaphore)

    chat_response = ""
    async for chunk in credit_tool_stream(
        request, results=results, chat_history=chat_history
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
async def chat(request: ChatRequest):
    async def stream():
        try:
            async for chunk in _chat_stream(request):
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
        return await _collect(_chat_stream(request))
    except Exception as e:
        import traceback
        with open("error.log", "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise e


@app.post("/credit")
async def credit(request: ChatRequest):
    async def stream():
        try:
            async for chunk in _credit_stream(request):
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
        return await _collect(_credit_stream(request))
    except Exception as e:
        import traceback
        with open("error.log", "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise e

async def credit_tool_stream(request: ChatRequest, results=None, chat_history=None):
    if chat_history is None:
        chat_history = await get_chat(request.user_id, request.chat_id)
        if chat_history == 0:
            chat_history = await create_chat(
                request.user_id, request.chat_id, request.cin_list, request.query
            )
        if not isinstance(chat_history.sme_data, dict):
            chat_history.sme_data = {}

    if results is None:
        semaphore = app.state.semaphore_sme_financials
        client = app.state.client

        results = []
        cins_to_fetch = []
        for cin in request.cin_list:
            if cin in chat_history.sme_data:
                results.append(chat_history.sme_data[cin])
            else:
                cins_to_fetch.append(cin)

        if cins_to_fetch:
            fetched = await asyncio.gather(
                *[company_details(client, cin, semaphore) for cin in cins_to_fetch]
            )
            for cin, res in zip(cins_to_fetch, fetched):
                chat_history.sme_data[cin] = res
                results.append(res)

    if not results:
        raise ValueError(f"No usable data for {request.cin_list}")

    for i, entry in enumerate(results):
        if i:
            yield "\n\n---\n\n"
        label = _company_label(entry)
        flat = flatten_credit(entry)
        query = f"{request.query}\n\n(This call covers only: {label}.)"
        yield f"## {label}\n\n"
        async for chunk in chat_endpoint_stream(
            query, [flat], chat_history, is_final=True,
            instruction=CREDIT_INSTRUCTION,
        ):
            yield chunk


async def credit_tool(request: ChatRequest, results=None, chat_history=None, persist=True):
    try:
        if chat_history is None:
            chat_history = await get_chat(request.user_id, request.chat_id)
            if chat_history == 0:
                chat_history = await create_chat(
                    request.user_id, request.chat_id, request.cin_list, request.query
                )
            if not isinstance(chat_history.sme_data, dict):
                chat_history.sme_data = {}

        pieces = []
        async for chunk in credit_tool_stream(
            request, results=results, chat_history=chat_history
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
async def chat_history(user_id: int):
    try: 
        chat_history = await get_chat_history(user_id)
        return chat_history
    except Exception as e:
        import traceback
        with open("error.log", "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise e