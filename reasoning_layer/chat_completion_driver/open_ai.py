import asyncio
from dotenv import load_dotenv
load_dotenv()

from openai import AsyncOpenAI

client = AsyncOpenAI()

import json

async def chat_endpoint(query, company_information_list, chat_history):
    company_information = json.dumps(company_information_list, indent=2)
    
    developer_prompt = (
        f"this is the previous chat history {chat_history}\n\n"
        "You are an expert financial analyst specializing in SME (Small and Medium Enterprises) "
        "and corporate credit risk analysis. Your goal is to analyze the provided company information "
        "(containing Company Master details, Charges/Debts, Credit Ratings, and Director information) "
        "and perform a comprehensive risk assessment.\n\n"
        "Focus on evaluating:\n"
        "1. Financial & Solvency Risk: Analyze Paid-up vs. Authorized Capital, age/vintage, and MCA status.\n"
        "2. Debt & Charge Profile: Assess total active (open) charges vs. satisfied charges, key lenders, and security details.\n"
        "3. Credit Rating Strength: Evaluate historical and current ratings from rating agencies (e.g., CRISIL, ICRA) and their trends.\n"
        "4. Management & Directorship Risk: Check director profiles, their other directorships, and potential conflict/stability indicators.\n"
        "5. Risk Synthesis: Identify key red flags, strengths, and provide a concluding credit risk assessment."
    )
    
    completion = await client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=[
            {"role": "developer", "content": developer_prompt},
            {"role": "user", "content": f"User Query: {query}\n\nCompany Data:\n{company_information}"}
        ]
    )
    
    response_content = completion.choices[0].message.content
    print(response_content)
    return response_content
