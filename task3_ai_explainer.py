from groq import Groq
import json
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(portfolio, tone="beginner"):
    portfolio_text = json.dumps(portfolio, indent=2)

    tone_instruction = {
        "beginner":    "Use very simple language. Avoid jargon. Explain everything as if talking to someone who has never invested before.",
        "experienced": "Assume the investor understands basic finance. Use standard financial terms.",
        "expert":      "Use technical financial language. Be concise and precise."
    }[tone]

    prompt = f"""
You are a professional financial advisor. {tone_instruction}

Your task is to analyze the portfolio using clear reasoning based on:
- Asset allocation percentages
- Expected crash impact
- Diversification and concentration risk
- Cash buffer and safety

Follow these strict rules:
- Be specific and avoid generic statements
- Use numbers from the portfolio when relevant
- Do NOT hallucinate data
- Keep explanations practical and actionable

Output format (STRICT):

SUMMARY:
Write 3–4 sentences explaining overall risk level.

DOING_WELL:
Write ONE specific strength with reasoning.

SHOULD_CHANGE:
Write ONE actionable improvement and WHY it matters.

VERDICT:
Choose exactly one: Aggressive / Balanced / Conservative

Portfolio data:
{portfolio_text}

Return ONLY the structured output. No extra text.
"""
    return prompt


def call_groq(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant" ,   # free, fast, good quality
        messages=[
            {
                "role": "system",
                "content": "You are a helpful financial advisor. Always follow the exact output format given to you. Never add extra text."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=1024,
        temperature=0.4,
    )
    return response.choices[0].message.content


def parse_response(raw_response):
    """
    Extracts structured sections from the response.
    Cleans markdown formatting just in case.
    """
    sections = {}
    current_key = None
    current_lines = []

    for line in raw_response.strip().split("\n"):
        line = line.strip()
        line = line.replace("**", "").replace("*", "")

        if line.endswith(":") and line.isupper():
            if current_key:
                sections[current_key] = " ".join(current_lines).strip()
            current_key = line[:-1]
            current_lines = []
        elif line:
            current_lines.append(line)

    if current_key:
        sections[current_key] = " ".join(current_lines).strip()

    return sections


def explain_portfolio(portfolio, tone="beginner"):
    print(f"\n Generating AI explanation (tone: {tone})...\n")

    prompt = build_prompt(portfolio, tone)

    print("--- PROMPT SENT TO GROQ ---")
    print(prompt)
    print("---------------------------\n")

    raw_response = call_groq(prompt)

    print("--- RAW API RESPONSE ---")
    print(raw_response)
    print("------------------------\n")

    structured = parse_response(raw_response)

    print("--- STRUCTURED OUTPUT ---")
    for key, value in structured.items():
        print(f"\n✅ {key}:\n   {value}")
    print("-------------------------\n")

    return structured


if __name__ == "__main__":
    portfolio = {
        "total_value_inr": 10_000_000,
        "monthly_expenses_inr": 80_000,
        "assets": [
            {"name": "BTC",     "allocation_pct": 30, "expected_crash_pct": -80},
            {"name": "NIFTY50", "allocation_pct": 40, "expected_crash_pct": -40},
            {"name": "GOLD",    "allocation_pct": 20, "expected_crash_pct": -15},
            {"name": "CASH",    "allocation_pct": 10, "expected_crash_pct":   0},
        ]
    }

    explain_portfolio(portfolio, tone="beginner")
    explain_portfolio(portfolio, tone="experienced")
    explain_portfolio(portfolio, tone="expert")