import aiohttp

from sme_api.base import sme_headers, sme_url


async def insta_summary(client: aiohttp.ClientSession, cin: str, semaphore):
    async with semaphore:
        async with client.get(
            sme_url("/insta_summary"),
            params={"cin": cin},
            headers=sme_headers(),
        ) as resp:
            return await resp.json()
