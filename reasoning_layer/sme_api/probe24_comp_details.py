from typing import Dict

from aiohttp import ClientSession

from sme_api.base import sme_headers, sme_url


async def company_details(client: ClientSession, cin: str, semaphore) -> Dict:
    async with semaphore:
        async with client.get(
            sme_url("/company_details"),
            params={"cin": cin},
            headers=sme_headers(),
        ) as resp:
            return await resp.json()
