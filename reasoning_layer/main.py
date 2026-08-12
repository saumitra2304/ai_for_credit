import aiohttp
from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from chat_completion_driver.open_ai import chat_endpoint
from sme_api.insta_summary_f import insta_summary
from pydantic import BaseModel
from mongo_driver.chat_db import get_chat, create_chat, update_chat

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.semaphore_sme_financials = asyncio.Semaphore(10)
    yield

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    cin_list: list[str]
    query: str
    chat_id: int
    user_id: int

@app.post("/chat")
async def chat(request: ChatRequest):
    list_tasks = []
    semaphore = app.state.semaphore_sme_financials
    chat_history = await get_chat(request.user_id, request.chat_id)
    if chat_history == 0:
        chat_history = await create_chat(request.user_id, request.chat_id, request.cin_list, request.query)
    
    for i in request.cin_list:
        list_tasks.append(insta_summary(i, semaphore))
    results = await asyncio.gather(*list_tasks)
    chat_response = await chat_endpoint(request.query, results, chat_history)
    chat_history.message_trail.append({"query": request.query, "response": chat_response})
    chat_history.sme_data.append(results)
    
    if len(chat_history.message_trail) > 5:
        chat_history.message_trail = chat_history.message_trail[-5:]
        chat_history.sme_data = chat_history.sme_data[-5:]
        
    await update_chat(chat_history)
    return chat_response
