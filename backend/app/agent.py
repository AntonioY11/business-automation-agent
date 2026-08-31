import os

from dotenv import load_dotenv
from google import genai
from pathlib import Path

from app.schemas import AIRequestAnalysis, AIMultiRequestAnalysis

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)


def analyze_request(text: str) -> AIRequestAnalysis:
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=f"""
Analyze this customer request.

Determine:
- the customer's intent
- the priority
- the account ID if one is provided
- the new address if the customer is requesting an address change
Customer request:
{text}
""",
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": AIRequestAnalysis.model_json_schema(),
        },
    )

    return AIRequestAnalysis.model_validate_json(
        interaction.output_text
    )


def analyze_multiple_operations(
    text: str,
) -> AIMultiRequestAnalysis:
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=f"""
Analyze this customer request.

A customer may be asking for one or more operations.

Identify every operation requested.

For each operation determine:
- the customer's intent
- the account ID if one is provided
- the new address if this is an address change
- the refund reason if this is a refund request

The supported intents are:
- refund_request
- cancel_subscription
- address_change
- account_question
- create_support_ticket

Also determine the overall priority.

Customer request:
{text}
""",
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": AIMultiRequestAnalysis.model_json_schema(),
        },
    )

    return AIMultiRequestAnalysis.model_validate_json(
        interaction.output_text
    )

