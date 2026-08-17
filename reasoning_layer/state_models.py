from typing import List
from pydantic import BaseModel

class chat_memory(BaseModel):
    user_id: int
    chat_id: int
    sme_data: dict
    message_trail: List[dict]