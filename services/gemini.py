from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

import requests

from config.settings import DISABLE_OUTBOUND_PROXY, GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TIMEOUT_SECONDS


INSIGHT_PROMPT_TEMPLATE = """You are a customer retention specialist working for a subscription-based digital service company (e.g., telecom or SaaS platform).

Your goal is to reduce customer churn and maximize customer lifetime value (CLV).

Customer behavior insights:

* Low Usage Frequency indicates low engagement and higher churn risk
* High Support Calls may indicate dissatisfaction or unresolved issues
* Payment Delay reflects financial or commitment issues
* Short Contract Length (e.g., monthly) indicates lower commitment
* Low Tenure means the customer is still new and less loyal
* High Total Spend indicates a high-value customer that should be prioritized
* Long time since Last Interaction indicates disengagement

Business strategy:

* High-value customers (Total Spend > 1000) should receive personalized and premium retention actions (e.g., direct call, VIP support)
* Low-value customers should receive cost-effective actions (e.g., email, discount)
* Avoid unnecessary discounts for low-risk customers

Risk-based actions:

* High risk -> immediate retention (discount, direct contact, support)
* Medium risk -> engagement (email, reminder, personalized offer)
* Low risk -> upsell, cross-sell, or loyalty reward

Customer data:
{customer_json}

Churn Probability: {probability}

Instructions:

* Recommend 1-2 specific and practical actions
* Prioritize business value and cost efficiency
* Do NOT explain reasoning

Return ONLY JSON:
{{
  "recommended_action": "..."
}}"""

FALLBACK_ACTIONS = {
    "high": "Offer an immediate retention call with a targeted incentive and assign priority support follow-up within 24 hours.",
    "medium": "Send a personalized engagement email with a limited-time offer and remind the customer of key product value this week.",
    "low": "Send a loyalty or upsell message tailored to the current plan without offering a discount.",
}


def _create_gemini_session() -> requests.Session:
    session = requests.Session()
    if DISABLE_OUTBOUND_PROXY:
        session.trust_env = False
    return session


def build_insight_prompt(base_inputs: dict[str, Any], probability: float) -> str:
    customer_json = json.dumps(base_inputs, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return INSIGHT_PROMPT_TEMPLATE.format(
        customer_json=customer_json,
        probability=round(float(probability), 4),
    )


def _get_fallback_action(base_inputs: dict[str, Any], probability: float) -> str:
    total_spend = float(base_inputs.get("Total Spend", 0.0))
    if probability >= 0.7:
        if total_spend > 1000:
            return (
                "Arrange a direct retention call with a personalized offer and provide VIP support assistance within 24 hours."
            )
        return FALLBACK_ACTIONS["high"]

    if probability >= 0.3:
        if total_spend > 1000:
            return (
                "Send a personalized check-in from the account team and include a premium feature reminder or tailored offer."
            )
        return FALLBACK_ACTIONS["medium"]

    if total_spend > 1000:
        return "Offer a loyalty reward and a personalized upsell conversation focused on premium plan benefits."
    return FALLBACK_ACTIONS["low"]


def _extract_text_from_candidate(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini response does not contain candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text_fragments = [part.get("text", "") for part in parts if isinstance(part, dict) and part.get("text")]
    if not text_fragments:
        raise ValueError("Gemini response does not contain text parts.")

    return "".join(text_fragments).strip()


def _parse_insight_response(raw_text: str) -> dict[str, str]:
    cleaned_text = raw_text.strip()
    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.removeprefix("```json").removeprefix("```").strip()
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3].strip()

    payload = json.loads(cleaned_text)
    recommended_action = str(payload.get("recommended_action", "")).strip()
    if not recommended_action:
        raise ValueError("Missing recommended_action in Gemini response.")

    return {
        "recommended_action": recommended_action,
        "insight_source": "AI",
        "insight_error": "",
    }


@lru_cache(maxsize=256)
def _generate_retention_insight_cached(base_inputs_json: str, probability: float) -> dict[str, str]:
    base_inputs = json.loads(base_inputs_json)
    fallback_payload = {
        "recommended_action": _get_fallback_action(base_inputs, probability),
        "insight_source": "Fallback",
        "insight_error": "",
    }

    if not GEMINI_API_KEY:
        fallback_payload["insight_error"] = "Missing GEMINI_API_KEY."
        return fallback_payload

    prompt = build_insight_prompt(base_inputs, probability)
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    request_payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt,
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }

    try:
        response = _create_gemini_session().post(
            url,
            headers={"Content-Type": "application/json"},
            json=request_payload,
            timeout=GEMINI_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        response_payload = response.json()
        raw_text = _extract_text_from_candidate(response_payload)
        return _parse_insight_response(raw_text)
    except (requests.RequestException, ValueError, json.JSONDecodeError) as exc:
        fallback_payload["insight_error"] = str(exc)
        return fallback_payload


def generate_retention_insight(base_inputs: dict[str, Any], probability: float) -> dict[str, str]:
    cache_key = json.dumps(base_inputs, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return dict(_generate_retention_insight_cached(cache_key, round(float(probability), 4)))
