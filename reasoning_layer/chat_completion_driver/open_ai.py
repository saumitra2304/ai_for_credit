import asyncio
import os
import re
import sys
import json

from dotenv import load_dotenv
load_dotenv()

from openai import AsyncOpenAI
from sql_db.settings_store import get_setting

_llm_client = None
_llm_sig = None


def _llm_client_and_model():
    global _llm_client, _llm_sig
    api_key = get_setting("OPENAI_API_KEY")
    if not api_key or api_key == "ollama":
        api_key = os.getenv("OPENAI_API_KEY", "")
    model = get_setting("OPENAI_MODEL_NAME", "gpt-5.4-nano") or "gpt-5.4-nano"
    base_url = (get_setting("OPENAI_BASE_URL") or "").strip()
    if "11434" in base_url or api_key == "ollama":
        base_url = ""
    sig = (base_url, api_key, model)
    if _llm_client is None or _llm_sig != sig:
        kwargs = {"api_key": api_key or "missing", "timeout": 1800.0}
        if base_url:
            kwargs["base_url"] = base_url
        _llm_client = AsyncOpenAI(**kwargs)
        _llm_sig = sig
    return _llm_client, model

# Output caps. GPT-5.4 nano has a large context window; one pass is enough.
MAX_TOKENS_EXTRACT = 1200
MAX_TOKENS_AGENT = 8000
MAX_TOKENS_FINAL = 16000
MAX_TOKENS_PLAN = 400

# ~4 chars per token. 400k context leaves ample room for filings + web search.
CHAR_BUDGET = 1_200_000
HISTORY_CHARS_PER_MSG = 4000

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        print(text.encode(encoding, errors="replace").decode(encoding))


def _log(msg):
    print(msg, file=sys.stderr, flush=True)


def strip_thinking(text):
    """Remove Qwen3 reasoning blocks. /no_think is a soft switch and is not
    always honoured, so strip defensively rather than trusting it."""
    if not text:
        return ""
    return _THINK_RE.sub("", text).strip()


def _join_information(company_information_list):
    """Join without json.dumps when the items are already strings.

    json.dumps on a list of JSON strings escapes every quote, inflating the
    payload 20-30% for no benefit.
    """
    if not company_information_list:
        return ""
    if all(isinstance(x, str) for x in company_information_list):
        return "\n\n".join(company_information_list)
    return json.dumps(company_information_list, separators=(",", ":"))


def _build_history(chat_history):
    lines = []
    trail = getattr(chat_history, "message_trail", None) or []
    for msg in trail:
        query = (msg.get("query") or "")[:400]
        response = (msg.get("response") or "")[:HISTORY_CHARS_PER_MSG]
        lines.append(f"User: {query}")
        lines.append(f"Assistant: {response}")
    return "\n".join(lines)


EXTRACT_INSTRUCTION = (
    "You are a data reduction utility working on Indian MCA company filings.\n"
    "Output ONLY the figures a credit analyst needs, one per line, as "
    "`label: value`. Keep labels and values exactly as given.\n"
    "Include: revenue, operating profit, PAT, total equity, total debt, "
    "current and quick ratio, debt/equity, interest coverage, inventory / "
    "debtor / payable days, operating cash flow.\n"
    "Skip: document ids, auditor addresses, PANs, registration numbers, "
    "director details, and any field whose value is null or zero.\n"
    "No introduction, no analysis, no conclusion, no commentary. "
    "If a figure is absent, omit the line rather than writing 'not available'.\n"
    "/no_think"
)


FOLLOWUP_INSTRUCTION = (
    "You are a credit analyst answering ONE follow-up question about Indian "
    "corporates already analysed in this chat.\n"
    "Answer that question only. Be direct. Cite figures only when the question "
    "needs them.\n\n"
    "Do not restart a full credit report. Do not paste FINANCIAL SUMMARY TABLES, "
    "trend write-ups, rating dumps, or news recaps unless the user asked for "
    "that specific thing.\n"
    "Standalone filings are tables only. They do not contain news, corporate "
    "actions, board or management changes, or annual-report commentary.\n"
    "Use web search for recent news or public facts. Summarise what you find "
    "and cite title, source, and date. Do not invent headlines.\n"
    "Do not open with the company name or CIN."
)


ANALYSIS_INSTRUCTION = (
    "You are an expert financial analyst specialising in SME and corporate "
    "credit risk assessment for Indian companies.\n\n"
    "The user message contains filings, credit/legal/MSME extracts, and the "
    "question. Use the web_search tool for recent news, litigation, ratings "
    "actions, and market context.\n\n"
    "Write ONE complete credit assessment with these sections:\n\n"
    "1. FINANCIAL SUMMARY TABLES\n"
    "   Markdown tables with years as columns. One table for P&L, one for "
    "the balance sheet, one for key ratios. Reproduce values exactly as "
    "supplied; do not recalculate or round. Include only line items present "
    "in the data.\n\n"
    "2. TREND ANALYSIS\n"
    "   Revenue and profitability direction, liquidity (current/quick), "
    "solvency (debt/equity, interest coverage), and working-capital "
    "efficiency across the years given. Cite the specific numbers.\n\n"
    "3. CREDIT, LEGAL AND MSME\n"
    "   Ratings, distress markers, supplier delays, and material cases from "
    "the filings.\n\n"
    "4. NEWS AND MARKET CONTEXT\n"
    "   From web search. Cite title, source, and date. Do not invent stories. "
    "If search finds nothing material, say so once.\n\n"
    "5. CREDIT STRENGTHS AND RED FLAGS\n"
    "   Bullet points, each anchored to a figure or a cited article.\n\n"
    "6. RISK CONCLUSION\n"
    "   A short verdict with the two or three factors that drive it.\n\n"
    "If several companies are in the packet, cover each, then a short "
    "comparison. Analyse whatever is provided. Do not restate the raw input.\n\n"
    "Do not open with the legal name, the CIN, or a "
    "'Company (Standalone) — Credit Assessment (FY…)' banner. The desk "
    "already knows the borrower. Start at FINANCIAL SUMMARY TABLES. Use "
    "normal section headings, not all caps."
)


MEMO_INSTRUCTION = (
    "You are writing a credit-committee memo for Indian corporates.\n"
    "This is a fresh underwriting document, not a chat reply and not a "
    "summary of a prior assistant message. Do not mention the chat, "
    "follow-up questions, or that you are an AI.\n\n"
    "Use every block in the company packet: identity and capital/charges, "
    "P&L, balance sheet, cash flow, ratios, Probe scores, peers and "
    "industry medians, related-party amounts, shareholders above 5%, "
    "credit ratings and rationale, legal/NCLT/DRT cases, MSME delays, "
    "and governance where it affects credit. Convert rupees to crore "
    "(1 crore = 10 million) or lakh, with Indian grouping "
    "(e.g. Rs 1,234.5 crore). Never write raw millions or ungrouped "
    "8-digit rupee amounts. Do not invent figures. If a line is absent, "
    "say it is not in the filings.\n\n"
    "You MUST call web_search before writing the news section. Run "
    "separate searches for each company covering:\n"
    "- latest ICRA / CRISIL / CARE / India Ratings action\n"
    "- NCLT, CIRP, default, SMA, or DRT developments\n"
    "- promoter or group stress, pledges, or SEBI/MCA actions\n"
    "- material business news in the last 12-18 months "
    "(order book, refinancing, stake sale, project delays)\n"
    "Cite title, publisher, and date. If a search is empty, say so once. "
    "Do not invent headlines.\n\n"
    "Charts for revenue/PAT, equity vs debt, cash flow, margins, and "
    "peers will be attached after your text. Refer to them in prose; "
    "do not draw ASCII charts.\n\n"
    "Structure:\n"
    "1. Cover — legal name, CIN, incorporation, one-line recommendation "
    "(advance / caution / decline) and the assignment if one is given.\n"
    "2. Executive summary — 8 to 12 lines covering scale, leverage, "
    "cash conversion, ratings, legal, and the recommendation.\n"
    "3. Financial position — markdown tables with years as columns for "
    "P&L, balance sheet, cash flow, and key ratios. Then trend commentary "
    "on growth, margins, liquidity, solvency, and working-capital days.\n"
    "4. Peer and industry comparison — scale vs named peers; margins/ROE "
    "vs industry medians when the packet has them.\n"
    "5. Capital structure, charges, related parties, and shareholding.\n"
    "6. Credit ratings, legal, and MSME — rating migration, material "
    "pending cases, supplier delays.\n"
    "7. News and market context — only from web search, cited.\n"
    "8. Strengths and red flags — bullets, each tied to a figure or source.\n"
    "9. Recommendation and conditions — facility view if the officer named one, "
    "security/monitoring, and what to obtain next.\n"
    "10. Macro and sector outlook — only from web search the officer asked for "
    "(policy, demand, rates, input costs, regulation). Cite and date. "
    "Do not invent a house view.\n"
    "11. User documents and chat — if the packet includes CMA, sanction notes, "
    "Excel, Word, or the live chat, use them as evidence. Quote figures from "
    "those files; do not invent rows that are not there.\n"
    "If extra peer companies are in the packet with filings, treat them as "
    "full comparables (scale, margins, leverage, WC), not name-only.\n"
)


FOLLOWUP_WEB_NOTE = (
    "\n\nWeb search results are included below. Queries were planned from "
    "the meaning of this follow-up. Use those articles as the main evidence. "
    "Do not claim there were no search results.\n"
)


SEARCH_PLAN_INSTRUCTION = (
    "You plan web searches for a follow-up question about named companies.\n"
    "Understand the user's intent — what they actually want to know. Then write "
    "1 to 3 short search queries that would retrieve recent news or pages about "
    "that intent. Each query is a company name plus the topic, 3 to 8 words.\n"
    "Never copy the user's question. Never write a full sentence. "
    "Do not use a canned industry list. Derive topics only from this question.\n"
    "Set search=false only if they ask solely for a figure already in filings.\n\n"
    "Output ONLY JSON, no markdown:\n"
    '{"search": true, "queries": ["<Company> <topic>", "<Company> <topic two>"]}\n'
    "or\n"
    '{"search": false, "queries": []}\n'
    "/no_think"
)


SEARCH_PLAN_RETRY = (
    "Your last reply was not usable. Infer the topics from the question's "
    "meaning and output ONLY JSON with 1 to 3 short search queries. Include "
    "the company name in each query. Do not copy the question.\n"
    '{"search": true, "queries": ["..."]}\n'
    "/no_think"
)


def _normalize_query(item) -> str:
    if not isinstance(item, str):
        return ""
    return " ".join(item.split())[:160]


def _parse_search_plan(raw: str, user_question: str, company_names: list[str]) -> list[str]:
    text = strip_thinking(raw)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return []
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return []
    question = " ".join((user_question or "").split()).lower()
    names = [n for n in company_names if n]
    items = list(data.get("queries") or []) + list(data.get("keywords") or [])
    out = []
    seen = set()
    for item in items:
        query = _normalize_query(item)
        if len(query) < 3:
            continue
        low = query.lower()
        if question and (low == question or (len(question) > 24 and question in low)):
            continue
        if names and not any(name.lower() in low for name in names):
            query = f"{names[0]} {query}"[:160]
            low = query.lower()
        if low in seen:
            continue
        seen.add(low)
        out.append(query)
        if len(out) >= 3:
            break
    if data.get("search") is False and not out:
        return []
    return out


async def _llm_plan_once(messages) -> str:
    llm, model_name = _llm_client_and_model()
    response = await llm.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=MAX_TOKENS_PLAN,
        temperature=0.1,
        stream=False,
    )
    if not response.choices:
        return ""
    return response.choices[0].message.content or ""


async def plan_followup_web_search(query: str, company_names: list[str]) -> list[str]:
    """Model infers search topics from the question; those queries are searched."""
    names = [n for n in company_names if n]
    listed = ", ".join(names) or "(none)"
    user_content = f"Companies: {listed}\nQuestion: {query}"
    messages = [
        {"role": "system", "content": SEARCH_PLAN_INSTRUCTION},
        {"role": "user", "content": user_content},
    ]
    try:
        from request_ctx import span, log_event

        _log(f"[search-plan] {user_content}")
        async with span("search.plan", question=query[:160]):
            raw = await _llm_plan_once(messages)
            queries = _parse_search_plan(raw, query, names)
            if not queries:
                _log("[search-plan] first pass unused; retrying model")
                messages = [
                    {"role": "system", "content": SEARCH_PLAN_RETRY},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": raw or "(empty)"},
                    {
                        "role": "user",
                        "content": "Rewrite as the JSON search plan only.",
                    },
                ]
                raw = await _llm_plan_once(messages)
                queries = _parse_search_plan(raw, query, names)
            _log(f"[search-plan] queries={queries}")
            if queries:
                await log_event("info", "search", f"planned searches: {queries}")
            return queries
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        _log(f"[search-plan error {type(exc).__name__}: {exc}]")
        try:
            from request_ctx import log_event

            await log_event("error", "search", f"search plan failed: {exc}")
        except Exception:
            pass
        return []


def _final_instruction(history_str):
    return (
        "You are an expert financial analyst specialising in SME and corporate "
        "credit risk assessment.\n\n"
        + (f"Previous conversation:\n{history_str}\n\n" if history_str else "")
        + "Produce a credit assessment with these four sections:\n\n"
        "1. FINANCIAL SUMMARY TABLES\n"
        "   Markdown tables with years as columns. One table for P&L, one for "
        "the balance sheet, one for key ratios. Reproduce values exactly as "
        "supplied; do not recalculate or round. Include only line items present "
        "in the data.\n\n"
        "2. TREND ANALYSIS\n"
        "   Revenue and profitability direction, liquidity (current/quick), "
        "solvency (debt/equity, interest coverage), and working-capital "
        "efficiency (inventory/debtor/payable days) across the years given. "
        "Cite the specific numbers you are reasoning from.\n\n"
        "3. CREDIT STRENGTHS AND RED FLAGS\n"
        "   Bullet points. Each one anchored to a figure. Include MSME payment "
        "delays and material litigation from the data when present.\n\n"
        "4. RISK CONCLUSION\n"
        "   A short verdict with the two or three factors that drive it.\n\n"
        "Analyse whatever is provided. If credit ratings, director profiles or "
        "schedules are absent, note it once as a data limitation and move on — "
        "do not stop or ask for more data. Do not restate the raw input; the "
        "tables plus your analysis are the whole deliverable."
    )


NEWS_INSTRUCTION = (
    "You are a news analyst covering Indian corporates.\n"
    "The user message contains Google News results in three buckets: "
    "general_news, financial_news, legal_news.\n"
    "Write a clear summary of what IS in the articles — headline themes, "
    "dates, sources, and credit-relevant signals (litigation, fraud claims, "
    "earnings misses, rating actions, management issues).\n\n"
    "Separate your answer into three short sections: General, Financial, Legal. "
    "If a bucket has no articles, say so once. Do not invent stories.\n"
    "/no_think"
)


CREDIT_INSTRUCTION = (
    "You are a credit-rating and distress analyst for Indian corporates.\n"
    "The user message contains the full credit/distress JSON for one company. "
    "Write a clear prose summary of everything that IS in the payload — "
    "do not reply with a blank template or say 'none' for fields that have "
    "values (e.g. struckoff248_details, key_indicators, debt figures).\n\n"
    "Where data exists, discuss: rating migration, agency divergence, "
    "withdrawn/unaccepted ratings, rated quantum vs latest_standalone_debt, "
    "and any mismatch between key_indicators.credit_rating and credit_ratings. "
    "Also cover defaulter_list, bifr_history, cdr_history, "
    "legal_cases_of_financial_disputes, legal_history (individual court cases), "
    "and msme_supplier_payment_delays (trend and supplier-level delays).\n\n"
    "Only note 'not in payload' for arrays/objects that are literally empty or "
    "null. Do not invent ratings. Quote agency, instrument, date, grade, "
    "outlook, and amounts when present.\n"
    "/no_think"
)


def _response_text_delta(event) -> str:
    etype = getattr(event, "type", "") or ""
    if etype in ("response.output_text.delta", "response.refusal.delta"):
        return getattr(event, "delta", None) or ""
    delta = getattr(event, "delta", None)
    if isinstance(delta, str) and "output_text" in etype:
        return delta
    return ""


async def _stream_responses(llm, model_name, instruction, user_content, max_tokens, web_search):
    kwargs = {
        "model": model_name,
        "instructions": instruction,
        "input": user_content,
        "max_output_tokens": max_tokens,
        "stream": True,
    }
    if web_search:
        kwargs["tools"] = [{"type": "web_search"}]
    stream = await llm.responses.create(**kwargs)
    async for event in stream:
        text = _response_text_delta(event)
        if text:
            yield text


async def _stream_chat_completions(llm, model_name, messages, max_tokens):
    try:
        stream = await llm.chat.completions.create(
            model=model_name,
            messages=messages,
            max_completion_tokens=max_tokens,
            stream=True,
        )
    except TypeError:
        stream = await llm.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )
    async for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        text = getattr(delta, "content", None)
        if text:
            yield text


async def chat_endpoint_stream(query, company_information_list, chat_history, is_final=False,
                               instruction=None, web_search=None):
    company_information = _join_information(company_information_list)
    history_str = _build_history(chat_history) if is_final else ""

    if instruction:
        developer_instruction = instruction
        if history_str:
            developer_instruction += f"\n\nPrevious conversation:\n{history_str}"
        max_tokens = MAX_TOKENS_AGENT if instruction != ANALYSIS_INSTRUCTION else MAX_TOKENS_FINAL
    elif is_final:
        developer_instruction = _final_instruction(history_str)
        max_tokens = MAX_TOKENS_FINAL
    else:
        developer_instruction = EXTRACT_INSTRUCTION
        max_tokens = MAX_TOKENS_EXTRACT

    if web_search is None:
        web_search = bool(is_final or instruction)

    user_content = f"{query}\n\nCompany Data:\n{company_information}"

    total_chars = len(developer_instruction) + len(user_content)
    _log(f"[llm final={is_final} web_search={web_search} chars={total_chars} "
         f"~tokens={total_chars // 4} max_out={max_tokens}]")
    if total_chars > CHAR_BUDGET:
        _log(f"[llm WARNING payload exceeds {CHAR_BUDGET} chars]")

    messages = [
        {"role": "system", "content": developer_instruction},
        {"role": "user", "content": user_content},
    ]

    try:
        llm, model_name = _llm_client_and_model()
        from request_ctx import agen_span

        kind = "llm.agent" if instruction else ("llm.final" if is_final else "llm.extract")

        async def _tokens():
            try:
                async for text in _stream_responses(
                    llm, model_name, developer_instruction, user_content,
                    max_tokens, web_search,
                ):
                    yield text
                return
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log(f"[llm responses fallback to chat.completions: {type(exc).__name__}: {exc}]")
            async for text in _stream_chat_completions(llm, model_name, messages, max_tokens):
                yield text

        async for text in agen_span(kind, _tokens(), chars=total_chars, max_out=max_tokens):
            yield text
    except asyncio.CancelledError:
        _log("[llm cancelled]")
        raise
    except Exception as exc:
        _log(f"[llm error {type(exc).__name__}: {exc}]")
        try:
            from observability import record_llm_error
            from request_ctx import log_event

            record_llm_error()
            await log_event("error", "llm", f"{type(exc).__name__}: {exc}")
        except Exception:
            pass
        raise


async def chat_endpoint(query, company_information_list, chat_history, is_final=False,
                        instruction=None, web_search=None):
    pieces = []
    async for text in chat_endpoint_stream(
        query, company_information_list, chat_history, is_final=is_final,
        instruction=instruction, web_search=web_search,
    ):
        pieces.append(text)

    raw = "".join(pieces)
    response_content = strip_thinking(raw) if not is_final else (raw or "").strip()

    _log(f"[llm done chars_out={len(response_content)} "
         f"~tokens_out={len(response_content) // 4}]")

    if is_final:
        safe_print(response_content)
    return response_content