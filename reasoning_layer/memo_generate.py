from datetime import datetime, timezone
import hashlib
import json

from chat_completion_driver.open_ai import MEMO_INSTRUCTION, chat_endpoint, strip_thinking
from credit_flatten import flatten_credit
from financial_flatten import flatten_company, flatten_legal_history
from memo_attachments import attachment_blocks
from memo_charts import (
    extract_memo_charts,
    flatten_memo_extras,
    select_peer_cins_from_charts,
    standalone_year_labels,
)
from memo_document import memo_filename, render_docx, render_pdf
from probe_errors import ProbeError
from sme_api.probe24_comp_details import company_details
from state_models import chat_memory

MEMO_CACHE_VERSION = 5


def company_slots(cache: dict) -> list[tuple[str, dict]]:
    out = []
    for cin, slot in (cache or {}).items():
        if str(cin).startswith("_") or not isinstance(slot, dict):
            continue
        out.append((cin, slot))
    return out


def _assignment(chat) -> str:
    trail = chat.message_trail if isinstance(chat.message_trail, list) else []
    if not trail:
        return ""
    return str((trail[0] or {}).get("query") or "").strip()[:800]


def _context_from_cache(cache: dict) -> str:
    parts = []
    for cin, slot in company_slots(cache):
        label = slot.get("label") or cin
        chunks = [
            f"### {label}",
            f"#### Filings\n{slot.get('flat') or '(none)'}",
            f"#### Credit / legal / MSME\n{slot.get('credit_flat') or '(none)'}",
        ]
        extras = (slot.get("extras_flat") or "").strip()
        if extras:
            chunks.append(f"#### Peers, related parties, shareholding\n{extras}")
        legal_extra = (slot.get("legal_flat") or "").strip()
        if legal_extra:
            chunks.append(f"#### Litigation detail\n{legal_extra}")
        parts.append("\n\n".join(chunks))
    return "\n\n".join(parts)


def memo_brief(
    notes="",
    extra_cins=None,
    extra_searches=None,
    include_chat=True,
    auto_peers=True,
    attachments=None,
):
    return {
        "notes": notes or "",
        "extra_cins": list(extra_cins or []),
        "extra_searches": list(extra_searches or []),
        "include_chat": bool(include_chat),
        "auto_peers": bool(auto_peers),
        "attachments": list(attachments or []),
    }


def brief_fingerprint(brief: dict) -> str:
    payload = {
        "notes": (brief.get("notes") or "").strip(),
        "cins": list(brief.get("extra_cins") or []),
        "searches": list(brief.get("extra_searches") or []),
        "chat": bool(brief.get("include_chat", True)),
        "auto": bool(brief.get("auto_peers", True)),
        "files": [
            (name, hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16])
            for name, text in (brief.get("attachments") or [])
        ],
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:24]


def flatten_chat_trail(chat, *, limit: int = 12, each: int = 700) -> str:
    trail = chat.message_trail if isinstance(getattr(chat, "message_trail", None), list) else []
    blocks = []
    for idx, item in enumerate(trail[-limit:], start=1):
        if not isinstance(item, dict):
            continue
        query = str(item.get("query") or "").strip()[:each]
        response = str(item.get("response") or "").strip()[:each]
        if not query and not response:
            continue
        piece = [f"Turn {idx}"]
        if query:
            piece.append(f"Officer: {query}")
        if response:
            piece.append(f"Kuber: {response}")
        blocks.append("\n".join(piece))
    return "\n\n".join(blocks)


def _brief_context(chat, brief: dict) -> str:
    parts = []
    notes = (brief.get("notes") or "").strip()[:4000]
    if notes:
        parts.append("### Officer notes, facility terms, and revisions\n" + notes)
    if brief.get("include_chat", True):
        trail = flatten_chat_trail(chat)
        if trail:
            parts.append("### Chat with the officer\n" + trail)
    uploaded = attachment_blocks(brief.get("attachments") or [])
    if uploaded:
        parts.append(uploaded)
    return "\n\n".join(parts)


def _cached_markdown(cache: dict, fingerprint: str = "") -> str:
    existing = (cache or {}).get("__memo__")
    if isinstance(existing, str) and existing.strip():
        return ""
    if isinstance(existing, dict):
        if existing.get("version") != MEMO_CACHE_VERSION:
            return ""
        if (existing.get("fingerprint") or "") != (fingerprint or ""):
            return ""
        return (existing.get("markdown") or "").strip()
    return ""


def merge_extra_companies(chat, extra_cins: list[str]):
    cache = dict(chat.company_cache or {})
    for cin in extra_cins or []:
        if not cin or str(cin).startswith("_"):
            continue
        if cin in cache and isinstance(cache[cin], dict):
            continue
        cache[cin] = {"label": cin, "flat": "", "credit_flat": ""}
    chat.company_cache = cache


def merge_auto_peer_cins(user_cins, chart_sets, exclude=(), auto=True, limit=3, cap=8):
    blocked = {str(cin).strip().upper() for cin in exclude if cin}
    out = []
    for cin in user_cins or []:
        item = str(cin).strip().upper()
        if not item or item in blocked or item in out:
            continue
        out.append(item)
        if len(out) >= cap:
            return out
    if auto and not out:
        for cin in select_peer_cins_from_charts(chart_sets, exclude=blocked, limit=limit):
            if cin in out or cin in blocked:
                continue
            out.append(cin)
            if len(out) >= cap:
                break
    return out


async def write_memo_markdown(chat, brief: dict | None = None) -> str:
    brief = brief or memo_brief()
    fingerprint = brief_fingerprint(brief)
    cached = _cached_markdown(chat.company_cache, fingerprint)
    if cached:
        return cached

    merge_extra_companies(chat, brief.get("extra_cins") or [])
    packet = _context_from_cache(chat.company_cache)
    extra = _brief_context(chat, brief)
    context = "\n\n".join(part for part in (packet, extra) if part.strip())
    if not packet.strip():
        raise ValueError("No company filings in this chat to build a memo from.")

    names = [slot.get("label") or cin for cin, slot in company_slots(chat.company_cache)]
    assignment = _assignment(chat)
    search_lines = []
    for name in names:
        short = name.split("(")[0].strip()
        search_lines.append(f"- {short} ICRA CRISIL CARE rating action")
        search_lines.append(f"- {short} NCLT CIRP default DRT")
        search_lines.append(f"- {short} latest news promoter")
    for topic in brief.get("extra_searches") or []:
        search_lines.append(f"- {topic}")
    notes = (brief.get("notes") or "").strip()
    query = (
        "Write a complete credit committee memo for "
        + ", ".join(names)
        + ".\n"
        + (f"Assignment from the officer: {assignment}\n" if assignment else "")
        + (f"Officer revision notes: {notes[:800]}\n" if notes else "")
        + "Use the full company packet, any uploaded documents, and the chat if present. "
        "Convert figures to Rs crore. You must web_search each of:\n"
        + "\n".join(search_lines)
        + "\nCharts will be attached after your text."
    )
    fresh = chat_memory(
        user_id=chat.user_id,
        chat_id=chat.chat_id,
        sme_data={},
        message_trail=[],
        company_cache={},
    )
    raw = await chat_endpoint(
        query,
        [context],
        fresh,
        is_final=True,
        instruction=MEMO_INSTRUCTION,
        web_search=True,
    )
    markdown = strip_thinking(raw or "").strip()
    if not markdown:
        raise ValueError("Memo generation returned an empty document.")
    cache = dict(chat.company_cache or {})
    cache["__memo__"] = {
        "markdown": markdown,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": MEMO_CACHE_VERSION,
        "fingerprint": fingerprint,
    }
    chat.company_cache = cache
    return markdown


async def collect_chart_sets(chat, client, semaphore, only_cins=None) -> list[dict]:
    cache = dict(chat.company_cache or {})
    sets = []
    slots = company_slots(cache)
    if only_cins is not None:
        wanted = {str(cin).strip().upper() for cin in only_cins}
        slots = [(cin, slot) for cin, slot in slots if str(cin).strip().upper() in wanted]
    for cin, slot in slots:
        slot = dict(slot)
        try:
            payload = await company_details(client, cin, semaphore)
        except ProbeError:
            payload = None
        if payload:
            years = standalone_year_labels(payload)
            flat = flatten_company(payload, years=years)
            credit_flat = flatten_credit(payload)
            extras = flatten_memo_extras(payload)
            legal = "\n".join(flatten_legal_history(payload.get("data") or {}, max_cases=20))
            if flat.strip():
                slot["flat"] = flat
            if credit_flat.strip():
                slot["credit_flat"] = credit_flat
            if extras.strip():
                slot["extras_flat"] = extras
            if legal.strip():
                slot["legal_flat"] = legal
            cache[cin] = slot
            sets.append(extract_memo_charts(payload))
        else:
            sets.append(
                {
                    "company_name": slot.get("label") or cin,
                    "cin": cin,
                    "pnl": [],
                    "balance_sheet": [],
                    "cash_flow": [],
                    "margins": [],
                    "peers": [],
                    "peer_bench": [],
                }
            )
    chat.company_cache = cache
    return sets


def render_memo_bytes(markdown: str, chart_sets: list[dict], fmt: str, company_name: str) -> tuple[bytes, str, str]:
    fmt = (fmt or "pdf").lower()
    if fmt not in ("pdf", "docx"):
        raise ValueError("format must be pdf or docx")
    if fmt == "pdf":
        body = render_pdf(markdown, chart_sets, company_name)
        media = "application/pdf"
    else:
        body = render_docx(markdown, chart_sets, company_name)
        media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return body, media, memo_filename(company_name, fmt)
