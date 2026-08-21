import asyncio
import json
import os
from typing import Any, Dict, List

import aiohttp
from aiohttp import ClientSession
from dotenv import load_dotenv

load_dotenv()

SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
if not SEARCH_API_KEY:
    raise RuntimeError("SEARCH_API_KEY is not set — check your .env file")

SEARCH_URL = "https://www.searchapi.io/api/v1/search"

# base64 image blobs — multi-KB each, useless downstream
DROP_KEYS = {"favicon", "thumbnail"}


def strip_blobs(obj: Any) -> Any:
    """Recursively remove base64 image fields from the API response."""
    if isinstance(obj, dict):
        return {k: strip_blobs(v) for k, v in obj.items() if k not in DROP_KEYS}
    if isinstance(obj, list):
        return [strip_blobs(item) for item in obj]
    return obj


async def company_details(
    client: ClientSession,
    query: str,
    semaphore: asyncio.Semaphore,
) -> Dict[str, Any]:
    params = {
        "engine": "google_news",
        "q": query,
        "location": "India",
        "gl": "in",
        "hl": "en",
        "api_key": SEARCH_API_KEY,
    }
    async with semaphore:
        try:
            async with client.get(SEARCH_URL, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return strip_blobs(data)
        except aiohttp.ClientResponseError as e:
            print(f"[{query}] HTTP {e.status}: {e.message}")
        except aiohttp.ClientError as e:
            print(f"[{query}] request failed: {e}")
        except asyncio.TimeoutError:
            print(f"[{query}] timed out")
        return {"query": query, "error": True, "organic_results": []}


async def main(queries: List[str]) -> List[Dict[str, Any]]:
    semaphore = asyncio.Semaphore(5)
    timeout = aiohttp.ClientTimeout(total=45)  # cold calls can take ~13s
    async with aiohttp.ClientSession(timeout=timeout) as client:
        tasks = [company_details(client, q, semaphore) for q in queries]
        return await asyncio.gather(*tasks)


def print_results(results: List[Dict[str, Any]]) -> None:
    for res in results:
        if res.get("error"):
            continue
        query = res.get("search_parameters", {}).get("q", "?")
        print(f"\n{'=' * 70}\n{query}\n{'=' * 70}")

        for r in res.get("organic_results", []):
            print(f"\n[{r.get('position')}] {r.get('title')}")
            print(f"    {r.get('source')} · {r.get('date')}")
            print(f"    {r.get('snippet', '(no snippet)')}")
            print(f"    {r.get('link')}")

        stories = res.get("top_stories", [])
        if stories:
            print(f"\n--- top stories ({len(stories)}) ---")
            for s in stories:
                print(f"  • {s.get('title')}  [{s.get('source')}]")


if __name__ == "__main__":
    results = asyncio.run(main(["godrej properties limited"]))

    print_results(results)

    with open("news_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nSaved to news_results.json")