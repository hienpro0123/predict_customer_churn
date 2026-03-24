from typing import Any

import requests


def clamp_probability(value: float) -> float:
    return max(0.0, min(float(value), 1.0))


def normalize_prediction_value(value: Any) -> int:
    return int(float(value))


def get_error_message(response: requests.Response) -> str:
    response_text = response.text.strip()
    return response_text if response_text else "Unknown Databricks API error."
