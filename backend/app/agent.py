import os
import time


from dotenv import load_dotenv
import httpx

from google import genai
from google.genai import errors
from pydantic import ValidationError
from pathlib import Path

from app.schemas import AIRequestAnalysis, AIMultiRequestAnalysis

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)



def call_gemini(input_text: str, schema):
    try:
        return client.interactions.create(
            model="gemini-3.6-flash",
            input=input_text,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": schema,
            },
        )

    except errors.APIError as e:
        if e.code == 429:
            raise RuntimeError(
                "AI service rate limit exceeded. Please try again later."
            )

        raise RuntimeError(
            "AI service is currently unavailable."
        )

    except httpx.HTTPError:
        raise RuntimeError(
            "AI service is currently unreachable."
        )




def _parse(schema, output_text: str | None):
    if not output_text:
        raise RuntimeError("AI service returned an empty response.")

    try:
        return schema.model_validate_json(output_text)
    except ValidationError:
        raise RuntimeError(
            "AI service returned a response that could not be understood."
        )


def analyze_request(text: str) -> AIRequestAnalysis:
    interaction = call_gemini(
        input_text=f"""
Analyze this customer request.

Determine:
- the customer's intent
- the priority
- the account ID if one is provided
- the new address if the customer is requesting an address change

Customer request:
{text}
""",
        schema=AIRequestAnalysis.model_json_schema(),
    )

    return _parse(AIRequestAnalysis, interaction.output_text)


def analyze_multiple_operations(
    text: str,
) -> AIMultiRequestAnalysis:
    interaction = call_gemini(
        input_text=f"""
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
        schema=AIMultiRequestAnalysis.model_json_schema(),
    )

    return _parse(AIMultiRequestAnalysis, interaction.output_text)

