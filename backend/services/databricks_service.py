from functools import lru_cache
import time
from typing import Any

import requests
from fastapi import HTTPException

from core.config import settings
from utils.constants import FEATURE_COLUMNS
from utils.helpers import clamp_probability, normalize_prediction_value


@lru_cache(maxsize=1)
def _create_session() -> requests.Session:
    session = requests.Session()
    if settings.DISABLE_OUTBOUND_PROXY:
        session.trust_env = False
    return session


def _build_headers() -> dict[str, str]:
    if not settings.DATABRICKS_URL or not settings.DATABRICKS_TOKEN:
        raise HTTPException(status_code=500, detail="Missing Databricks configuration.")
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.DATABRICKS_TOKEN}",
    }


def _extract_prediction(result: Any) -> tuple[int, float]:
    if isinstance(result, dict):
        prediction = next(
            (result.get(key) for key in ("prediction", "predicted_label", "label", "class") if result.get(key) is not None),
            None,
        )
        probability = next(
            (
                result.get(key)
                for key in ("probability", "probabilities", "score", "churn_probability")
                if result.get(key) is not None
            ),
            None,
        )
        if isinstance(probability, list) and probability:
            probability = probability[-1]
        elif isinstance(probability, dict) and probability:
            probability = (
                probability.get("1")
                or probability.get(1)
                or probability.get("true")
                or probability.get(True)
                or max(probability.values())
            )
        if probability is not None:
            probability = clamp_probability(probability)
        if prediction is None and probability is not None:
            return int(probability >= 0.5), probability
        if prediction is not None:
            normalized_prediction = normalize_prediction_value(prediction)
            fallback_probability = clamp_probability(normalized_prediction)
            return normalized_prediction, probability if probability is not None else fallback_probability

    if isinstance(result, (int, float)):
        numeric_value = float(result)
        if 0.0 <= numeric_value <= 1.0:
            return int(numeric_value >= 0.5), numeric_value
        return int(numeric_value), clamp_probability(int(numeric_value))
    raise ValueError("Unexpected prediction format returned by Databricks Model Serving.")


def _should_retry_status_code(status_code: int) -> bool:
    return status_code in {429, 502, 503, 504}


def _sleep_before_retry(attempt_number: int) -> None:
    delay = max(settings.DATABRICKS_RETRY_BACKOFF_SECONDS, 0) * attempt_number
    if delay > 0:
        time.sleep(delay)


def _post_payload(records: list[dict[str, Any]]) -> list[tuple[int, float]]:
    payload = {
        "dataframe_records": [
            {column: row.get(column) for column in FEATURE_COLUMNS}
            for row in records
        ]
    }
    retry_attempts = max(settings.DATABRICKS_RETRY_ATTEMPTS, 0)
    total_attempts = retry_attempts + 1
    response: requests.Response | None = None

    for attempt_number in range(1, total_attempts + 1):
        try:
            response = _create_session().post(
                settings.DATABRICKS_URL,
                headers=_build_headers(),
                json=payload,
                timeout=(5, settings.DATABRICKS_TIMEOUT),
            )
            response.raise_for_status()
            break
        except requests.exceptions.Timeout as exc:
            if attempt_number < total_attempts:
                _sleep_before_retry(attempt_number)
                continue
            raise HTTPException(
                status_code=504,
                detail=(
                    f"Databricks request timed out after {total_attempts} attempt(s). "
                    "The serving endpoint may still be waking up."
                ),
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            if attempt_number < total_attempts:
                _sleep_before_retry(attempt_number)
                continue
            raise HTTPException(status_code=502, detail=f"Could not connect to Databricks: {exc}") from exc
        except requests.exceptions.HTTPError as exc:
            status_code = response.status_code if response is not None else 502
            if attempt_number < total_attempts and _should_retry_status_code(status_code):
                _sleep_before_retry(attempt_number)
                continue
            raise HTTPException(status_code=status_code, detail=response.text or "Databricks API error.") from exc
        except requests.exceptions.RequestException as exc:
            raise HTTPException(status_code=502, detail=f"Databricks request failed: {exc}") from exc

    try:
        predictions = response.json().get("predictions") if response is not None else None
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Databricks returned invalid JSON.") from exc

    if not predictions:
        raise HTTPException(status_code=502, detail="Databricks response does not include predictions.")
    try:
        return [_extract_prediction(item) for item in predictions]
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=502, detail=f"Could not parse Databricks prediction output: {exc}") from exc


def predict_single(features: dict[str, Any]) -> tuple[int, float]:
    return _post_payload([features])[0]


def predict_batch(features_list: list[dict[str, Any]]) -> list[tuple[int, float]]:
    if not features_list:
        raise HTTPException(status_code=400, detail="No rows provided for batch prediction.")
    results = _post_payload(features_list)
    if len(results) != len(features_list):
        raise HTTPException(status_code=502, detail="Prediction count does not match batch input row count.")
    return results
