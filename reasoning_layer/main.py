import aiohttp
import json
from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from chat_completion_driver.open_ai import chat_endpoint
from sme_api.insta_summary_f import insta_summary
from pydantic import BaseModel
from mongo_driver.chat_db import get_chat, create_chat, update_chat
from sme_api.probe24_comp_details import company_details

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

def filter_company_details(res: dict) -> dict:
    if not isinstance(res, dict) or "data" not in res:
        return res
    
    data = res["data"]
    filtered_data = {}
    
    # Keep only the company identification/info and detailed financials
    if "company" in data:
        filtered_data["company"] = data["company"]
        
    if "financials" in data and isinstance(data["financials"], list):
        # Keep stand-alone and consolidated financials for the last 3 years
        filtered_data["financials"] = [
            f for f in data["financials"]
            if isinstance(f, dict) and any(str(f.get("year", "")).startswith(y) for y in ["2025", "2024", "2023"])
        ]
        
    return {
        "metadata": res.get("metadata", {}),
        "data": filtered_data
    }

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

        # Filter results before passing to LLM to keep only the relevant parts
        filtered_results = [filter_company_details(res) for res in results]
        results_text = json.dumps(filtered_results, indent=2)
        
        # 6000 characters fits easily within Gemma's context limit
        max_chars = 6000
        chunks = []
        current_chunk = []
        current_length = 0
        for line in results_text.splitlines():
            if current_length + len(line) + 1 > max_chars:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_length = len(line) + 1
            else:
                current_chunk.append(line)
                current_length += len(line) + 1
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        # Run summaries sequentially to avoid overloading the local model
        summaries = []
        for idx, chunk in enumerate(chunks, 1):
            batch_query = (
                f"Extract and list the financial numbers, ratios, balance sheet items, and P&L figures present in this JSON batch ({idx}/{len(chunks)}). "
                "Output them in a very compact bulleted list. YOU MUST INCLUDE THE EXACT LABEL FOR EVERY NUMBER (e.g., 'Paid-up Capital: 1996972240', 'Revenue Growth: 44.85'). "
                "Do not write any introduction, analysis, weaknesses, recommendations, or filler text. "
                "Your entire response must be extremely brief and contain only the labels and their corresponding numbers."
            )
            # Await each request sequentially
            summary = await chat_endpoint(batch_query, [chunk], chat_history, is_final=False)
            summaries.append(summary)

        # Recursive reduce: if the combined summaries are too long, summarize them further in batches
        while True:
            combined_length = sum(len(s) for s in summaries)
            # 10000 characters is roughly 2500 tokens, leaving room for instructions, history, and output
            if combined_length < 10000: 
                break
            
            new_summaries = []
            # Group summaries in batches of 2 to reduce them
            for i in range(0, len(summaries), 2):
                chunk_group = summaries[i:i+2]
                reduce_query = "Combine and summarize these extracted financial details compactly. Keep all exact numbers and labels, but remove any duplicate information or filler."
                reduced = await chat_endpoint(reduce_query, chunk_group, chat_history, is_final=False)
                new_summaries.append(reduced)
            summaries = new_summaries

        chat_response = await chat_endpoint(request.query, summaries, chat_history, is_final=True)

        chat_history.message_trail.append({"query": request.query, "response": chat_response})

        # Keep only the last 2 messages to prevent chat history from bloating the context
        if len(chat_history.message_trail) > 2:
            chat_history.message_trail = chat_history.message_trail[-2:]
            
        await update_chat(chat_history)
        return chat_response
    except Exception as e:
        import traceback
        with open("error.log", "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise e
