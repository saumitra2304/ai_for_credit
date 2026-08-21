"""Compact news payload for the news agent."""

import json

from scrapper import fetch_news

ARTICLE_KEYS = ("title", "source", "date", "snippet", "link")

NEWS_CATEGORIES = {
    "general_news": lambda name: name,
    "financial_news": lambda name: f"{name} financial earnings revenue profit stock",
    "legal_news": lambda name: f"{name} lawsuit court legal case fraud dispute",
}


def _articles(payload):
    if not payload or payload.get("error"):
        return []
    items = []
    for row in payload.get("organic_results") or []:
        items.append({k: row.get(k) for k in ARTICLE_KEYS if row.get(k)})
    for row in payload.get("top_stories") or []:
        items.append({k: row.get(k) for k in ARTICLE_KEYS if row.get(k)})
    return items


async def fetch_company_news(client, company_name, semaphore):
    queries = {cat: fn(company_name) for cat, fn in NEWS_CATEGORIES.items()}
    results = await fetch_news(client, list(queries.values()), semaphore)
    return dict(zip(queries.keys(), results))


def flatten_news(label, categories):
    block = {"company": label}
    for cat, payload in categories.items():
        block[cat] = _articles(payload)
    return json.dumps(block, indent=2, default=str)
