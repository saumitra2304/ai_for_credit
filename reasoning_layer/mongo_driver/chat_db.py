import os
from pymongo import AsyncMongoClient
from state_models import chat_memory

mongo_url = os.getenv("mongo_url") or "mongodb://localhost:27017"

client = AsyncMongoClient(
    mongo_url,
    maxPoolSize=100,
    minPoolSize=0,
    maxIdleTimeMS=30000,
    maxConnecting=2,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    waitQueueTimeoutMS=5000,
)

db = client["chat_db"]
collection = db["chat_history"]

async def get_chat(user_id, chat_id):
    chat = await collection.find_one({"user_id": user_id, "chat_id": chat_id})
    if chat is None:
        return 0
    return chat_memory(**chat)

async def create_chat(user_id, chat_id, cin_list, query):
    chat = chat_memory(
        user_id=user_id,
        chat_id=chat_id,
        sme_data=[],
        message_trail=[]
    )
    await collection.insert_one(chat.model_dump())
    return chat

async def update_chat(chat: chat_memory):
    await collection.replace_one(
        {"user_id": chat.user_id, "chat_id": chat.chat_id},
        chat.model_dump()
    )