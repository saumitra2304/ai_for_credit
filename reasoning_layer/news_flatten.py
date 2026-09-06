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


def _merge_articles(*payloads):
    seen = set()
    out = []
    for payload in payloads:
        for row in _articles(payload):
            key = row.get("link") or row.get("title")
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(row)
    return out


async def fetch_topic_news(client, queries, semaphore):
    """Follow-up keyword search. Does not replace fetch_company_news."""
    news = await fetch_news(client, queries, semaphore, engine="google_news")
    pairs = list(zip(queries, news))
    if sum(len(_articles(payload)) for _, payload in pairs) >= 3:
        return pairs
    web = await fetch_news(client, queries, semaphore, engine="google")
    merged = []
    for query, news_payload, web_payload in zip(queries, news, web):
        merged.append(
            (query, {"organic_results": _merge_articles(news_payload, web_payload)})
        )
    return merged


def flatten_topic_news(pairs, per_query=8):
    lines = []
    for query, payload in pairs:
        articles = _articles(payload)[:per_query]
        lines.append(f"Search: {query}")
        if not articles:
            lines.append("  (no articles)")
            lines.append("")
            continue
        for i, row in enumerate(articles, 1):
            title = row.get("title") or "(untitled)"
            meta = " · ".join(x for x in (row.get("source"), row.get("date")) if x)
            lines.append(f"{i}. {title}" + (f" ({meta})" if meta else ""))
            if row.get("snippet"):
                lines.append(f"   {row['snippet']}")
            if row.get("link"):
                lines.append(f"   {row['link']}")
        lines.append("")
    return "\n".join(lines).strip()
