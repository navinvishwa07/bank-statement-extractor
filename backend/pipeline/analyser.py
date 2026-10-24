import os
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])


def analyse(transactions: list[dict]) -> dict:
    transaction_text = "\n".join([
        f"{t['date']} | {t['type'].upper():6} | {t['amount']:>10.2f} | {t['description']}"
        for t in transactions
    ])

    prompt = f"""You are a financial analyst reviewing an Indian bank statement.

Here are the transactions:

{transaction_text}

Analyse these transactions and return a JSON object with exactly these fields:
{{
    "avg_monthly_income": <average monthly credit amount as a number>,
    "emis": [
        {{"name": "<description>", "amount": <number>}}
    ],
    "irregular_credits": [
        {{"date": "<date>", "description": "<description>", "amount": <number>}}
    ],
    "cash_flow": {{
        "<month-year>": {{
            "income": <total credits that month>,
            "expenses": <total debits that month>
        }}
    }},
    "summary": "<2-3 sentence plain English summary of this person financial health>"
}}

Rules:
- EMIs are recurring debits of the same amount appearing monthly — list max 3
- Irregular credits: one-off large deposits — list max 2
- cash_flow: include only the months present in the data, max 5 months
- avg_monthly_income: only regular recurring credits
- Be concise. Return only valid JSON, no explanation, no markdown.
"""

    response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    max_tokens=900,
)

    raw = response.choices[0].message.content.strip()
    print("RAW:", repr(raw[:200]))

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)
