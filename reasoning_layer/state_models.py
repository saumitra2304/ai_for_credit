from typing import List
from pydantic import BaseModel

class chat_memory(BaseModel):
    user_id: int
    chat_id: str | int
    sme_data: dict
    message_trail: List[dict]
    company_cache: dict = {}