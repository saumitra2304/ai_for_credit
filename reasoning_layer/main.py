import aiohttp
from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from chat_completion_driver.open_ai import chat_endpoint
from sme_api.insta_summary_f import insta_summary
from pydantic import BaseModel
from mongo_driver.chat_db import get_chat, create_chat, update_chat
from sme_api.probe24_comp_details import company_details
from financial_flatten import flatten_all

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

        # Deterministic flattening replaces the map/reduce LLM passes.
        #
        # The old pipeline sent ~9k tokens of JSON to the model and asked it to
        # transcribe every one of ~730 labelled fields, then asked a second call
        # to compress that transcription. Both steps were output-bound: roughly
        # 7000 generated tokens each, at ~7 tokens/sec, before the analysis had
        # even started. This does the same reduction in Python, exactly, and
        # leaves a single LLM call to do the only thing it is actually needed
        # for -- the credit judgement.
        #
        # Note this receives `results`, NOT a filtered copy. flatten_all reads
        # probe_financial_score, msme_supplier_payment_delays, legal_history and
        # credit_ratings, all of which the old filter_company_details discarded.
        flat = flatten_all(results)

        if not flat.strip():
            raise ValueError(
                f"No STANDALONE 2023-2025 financials found for {request.cin_list}. "
                "Check the API response shape before blaming the model."
            )

        chat_response = await chat_endpoint(request.query, [flat], chat_history, is_final=True)

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