import aiohttp
import sys
from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from chat_completion_driver.open_ai import chat_endpoint
from sme_api.insta_summary_f import insta_summary
from pydantic import BaseModel
from mongo_driver.chat_db import get_chat, create_chat, update_chat
from sme_api.probe24_comp_details import company_details
from financial_flatten import flatten_company

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


def _company_label(entry: dict) -> str:
    """Pull a display name for headers without depending on flatten_company's
    text output."""
    company = (entry.get("data", {}) or {}).get("company", {}) or {}
    name = company.get("legal_name") or "Unknown company"
    cin = company.get("cin") or "?"
    return f"{name} (CIN {cin})"


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        list_tasks = []
        semaphore = app.state.semaphore_sme_financials
        client = app.state.client

        chat_history = await get_chat(request.user_id, request.chat_id)

        if chat_history == 0:
            chat_history = await create_chat(request.user_id, request.chat_id, request.cin_list, request.query)
        
        if not isinstance(chat_history.sme_data, dict):
            chat_history.sme_data = {}

        results = []
        cins_to_fetch = []
        for i in request.cin_list:
            if i in chat_history.sme_data:
                results.append(chat_history.sme_data[i])
            else:
                cins_to_fetch.append(i)

        if cins_to_fetch:
            list_tasks = []
            for i in cins_to_fetch:
                # list_tasks.append(insta_summary(client, i, semaphore))
                list_tasks.append(company_details(client, i, semaphore))
            fetched = await asyncio.gather(*list_tasks)
            for i, res in zip(cins_to_fetch, fetched):
                chat_history.sme_data[i] = res
                results.append(res)

        # -------------------------------------------------------------------
        # Phase 1: one LLM call per company, run sequentially.
        #
        # Ollama serves one request at a time regardless (OLLAMA_NUM_PARALLEL=1
        # on this box), so sequential vs concurrent costs the same wall clock
        # here -- it just avoids joining every company into one prompt whose
        # context grows with cin_list length.
        # -------------------------------------------------------------------
        sections = []
        flats = []          # (label, flattened_table) for companies with data
        per_company_answers = []

        for entry in results:
            label = _company_label(entry)
            flat = flatten_company(entry)

            if not flat.strip():
                print(f"[skip] no STANDALONE 2023-2025 financials for {label}",
                      file=sys.stderr, flush=True)
                sections.append(f"## {label}\n\nNo 2023-2025 standalone financials on record.")
                continue

            flats.append((label, flat))
            per_company_query = f"{request.query}\n\n(This call covers only: {label}.)"
            response = await chat_endpoint(per_company_query, [flat], chat_history, is_final=True)
            per_company_answers.append(response)
            sections.append(f"## {label}\n\n{response}")

        if not sections:
            raise ValueError(f"No usable data for {request.cin_list}")

        # ---------------------------------------------------------------
        # Phase 2: one final call that actually answers request.query.
        #
        # Each per-company call above was scoped to a single company and
        # forced through the fixed four-section template, so a comparative
        # or cross-company question ("which of these is the safer bet")
        # never got directly answered anywhere. This call sees every
        # company's flattened table together and is asked the user's
        # original question with no per-company framing.
        #
        # Skipped for a single company: re-running the same table through
        # a second ~9-minute generation would just restate the answer
        # already produced in Phase 1.
        # ---------------------------------------------------------------
        if len(flats) > 1:
            combined_tables = "\n\n".join(f"### {label}\n{table}" for label, table in flats)
            synthesis_query = (
                f"{request.query}\n\n"
                f"You have already produced a detailed breakdown for each company "
                f"individually (shown after this answer). Answer the question above "
                f"directly, comparing across all {len(flats)} companies using the "
                f"tables below. Be direct and specific -- name the company where "
                f"relevant rather than describing them abstractly."
            )
            final_answer = await chat_endpoint(synthesis_query, [combined_tables], chat_history, is_final=True)
        else:
            final_answer = per_company_answers[0]

        chat_response = (
            "# Answer\n\n" + final_answer
            + "\n\n---\n\n# Per-Company Detail\n\n"
            + "\n\n---\n\n".join(sections)
        )

        chat_history.message_trail.append({"query": request.query, "response": chat_response})

        # Keep only the last 2 messages to prevent chat history from bloating the context
        if len(chat_history.message_trail) > 2:
            chat_history.message_trail = chat_history.message_trail[-2:]
            
        await update_chat(chat_history)
        return chat_response
    except Exception as e:
        import traceback
        with open("error.log", "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise e