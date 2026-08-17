import aiohttp


async def insta_summary(client: aiohttp.ClientSession, cin: str, semaphore):
    async with semaphore:
        async with client.get(f"http://localhost:3000/insta_summary?cin={cin}") as resp:
            return await resp.json()