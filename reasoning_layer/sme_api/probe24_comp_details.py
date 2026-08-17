import aiohttp
from aiohttp import ClientSession
from typing import Dict

async def company_details(client: ClientSession, cin: str, semaphore) -> Dict:
    async with semaphore:
        async with client.get(f"http://localhost:3000/company_details?cin={cin}") as resp:
            return await resp.json()



