import asyncio
import os
import sys
from dotenv import load_dotenv
load_dotenv()

from openai import AsyncOpenAI

# Default to local vLLM instance on port 8000
client = AsyncOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "EMPTY")
)

import json

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or 'utf-8'
        print(text.encode(encoding, errors='replace').decode(encoding))

async def chat_endpoint(query, company_information_list, chat_history, is_final=False):
    if is_final:
        # For the final summary, it's a list of strings. Join them cleanly.
        company_information = "\n".join(company_information_list)
    else:
        # For the chunks, it's a list of dicts. Use extremely compact JSON to save tokens.
        company_information = json.dumps(company_information_list, separators=(',', ':'))
    # Format message trail cleanly to avoid passing the massive raw sme_data dictionary in chat_history
    history_lines = []
    if chat_history and hasattr(chat_history, "message_trail") and chat_history.message_trail:
        for msg in chat_history.message_trail:
            history_lines.append(f"User: {msg.get('query', '')}")
            history_lines.append(f"Assistant: {msg.get('response', '')}")
    history_str = "\n".join(history_lines)
    
    if is_final:
        developer_instruction = (
            f"This is the previous chat history:\n{history_str}\n\n"
            "You are an expert financial analyst specializing in SME (Small and Medium Enterprises) "
            "and corporate credit risk analysis. Your goal is to perform a comprehensive financial analysis and credit risk assessment based on the provided company data.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. ANALYZE WHAT IS PRESENT: Focus on the actual numbers and data provided. If some elements (like credit ratings, director profiles, or certain financial schedules) are missing, briefly note it as a data limitation, but DO NOT stop, complain, or ask the user for more information. You MUST analyze whatever data is given to the absolute best of your ability.\n"
            "2. TABULATE AND SHOW DATA: You MUST present the financial figures, including Balance Sheet items (Assets & Liabilities), Profit & Loss details, and key financial ratios, in clear, well-structured Markdown tables. Make sure every table is complete and contains the exact values and labels.\n"
            "3. FINANCIAL RISK ASSESSMENT: Provide a detailed, quantitative analysis based on the tabulated data. Evaluate Revenue & Profitability trends, Liquidity (current/quick ratios), Solvency (debt/equity ratios), and Operational Efficiency (inventory/receivable days) across the available years (e.g., 2023, 2024, 2025).\n"
            "4. CREDIT RISK SYNTHESIS: Provide a clear synthesis highlighting the key credit strengths, red flags/weaknesses, and a final risk conclusion."
        )
    else:
        developer_instruction = (
            "You are a precise data extraction utility. Your task is to extract and list the financial numbers, ratios, and items present in the company data, ALONG WITH THEIR EXACT LABELS.\n"
            "Do not analyze, do not discuss weaknesses, do not write introduction or conclusion. Keep your output extremely brief and focused."
        )
    
    model_name = os.getenv("OPENAI_MODEL_NAME", "google/gemma-2-2b-it")
    
    # Use a single "user" role content because local vLLM running Gemma does not support "system" / "developer" role
    combined_content = f"{developer_instruction}\n\nUser Query: {query}\n\nCompany Data:\n{company_information}"
    
    completion = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": combined_content}
        ]
    )
    
    response_content = completion.choices[0].message.content
    safe_print(response_content)
    return response_content
