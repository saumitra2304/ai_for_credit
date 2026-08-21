import asyncio
import os
import re
import sys
import json

from dotenv import load_dotenv
load_dotenv()

from openai import AsyncOpenAI

# Local Ollama, OpenAI-compatible endpoint. The api_key is required by the
# client but ignored by Ollama.
client = AsyncOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:11434/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "ollama"),
    timeout=1800.0,          # 30 min: a long final call must not be cut off mid-stream
)

MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "qwen3:8b")

# Output caps. Without these a confused model generates until it hits the
# context ceiling, which is what turned one extraction call into 16 minutes.
MAX_TOKENS_EXTRACT = 1200
MAX_TOKENS_FINAL = 4000

# ~4 chars per token. 32k context minus room for the response.
CHAR_BUDGET = 100_000

# Each prior turn's response is a full analysis with tables. Left untrimmed,
# two of them alone can eat half the context window.
HISTORY_CHARS_PER_MSG = 1500

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
        "   Bullet points. Each one anchored to a figure.\n\n"
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
    "legal_cases_of_financial_disputes.\n\n"
    "Only note 'not in payload' for arrays/objects that are literally empty or "
    "null. Do not invent ratings. Quote agency, instrument, date, grade, "
    "outlook, and amounts when present.\n"
    "/no_think"
)


async def chat_endpoint_stream(query, company_information_list, chat_history, is_final=False,
                               instruction=None):
    company_information = _join_information(company_information_list)
    history_str = _build_history(chat_history) if is_final else ""

    if instruction:
        developer_instruction = instruction
        if history_str:
            developer_instruction += f"\n\nPrevious conversation:\n{history_str}"
        max_tokens = MAX_TOKENS_FINAL
        temperature = 0.3
    elif is_final:
        developer_instruction = _final_instruction(history_str)
        max_tokens = MAX_TOKENS_FINAL
        temperature = 0.4
    else:
        developer_instruction = EXTRACT_INSTRUCTION
        max_tokens = MAX_TOKENS_EXTRACT
        temperature = 0.1

    user_content = f"{query}\n\nCompany Data:\n{company_information}"

    total_chars = len(developer_instruction) + len(user_content)
    _log(f"[llm final={is_final} chars={total_chars} ~tokens={total_chars // 4} "
         f"max_out={max_tokens}]")
    if total_chars > CHAR_BUDGET:
        _log(f"[llm WARNING payload exceeds {CHAR_BUDGET} chars; a context "
             f"shift is likely. Reduce the input rather than raising num_ctx.]")

    messages = [
        {"role": "system", "content": developer_instruction},
        {"role": "user", "content": user_content},
    ]

    try:
        stream = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            text = getattr(delta, "content", None)
            if text:
                yield text
    except asyncio.CancelledError:
        _log("[llm cancelled]")
        raise
    except Exception as exc:
        _log(f"[llm error {type(exc).__name__}: {exc}]")
        raise


async def chat_endpoint(query, company_information_list, chat_history, is_final=False,
                        instruction=None):
    pieces = []
    async for text in chat_endpoint_stream(
        query, company_information_list, chat_history, is_final=is_final,
        instruction=instruction,
    ):
        pieces.append(text)

    raw = "".join(pieces)
    response_content = strip_thinking(raw) if not is_final else (raw or "").strip()

    _log(f"[llm done chars_out={len(response_content)} "
         f"~tokens_out={len(response_content) // 4}]")

    if is_final:
        safe_print(response_content)
    return response_content