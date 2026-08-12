import aiohttp


async def insta_summary(cin, semaphore):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://localhost:3000/insta_summary?cin={cin}") as resp:
                return await resp.json()