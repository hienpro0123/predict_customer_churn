from typing import Any

import requests
from fastapi import HTTPException

from core.config import settings
from utils.constants import FEATURE_COLUMNS
from utils.helpers import clamp_probability, normalize_prediction_value


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


def _post_payload(records: list[dict[str, Any]]) -> list[tuple[int, float]]:
    payload = {"dataframe_records": [{column: row[column] for column in FEATURE_COLUMNS} for row in records]}
    try:
        response = _create_session().post(
            settings.DATABRICKS_URL,
            headers=_build_headers(),
            json=payload,
            timeout=settings.DATABRICKS_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise HTTPException(status_code=504, detail="Databricks request timed out.") from exc
    except requests.exceptions.ConnectionError as exc:
        raise HTTPException(status_code=502, detail=f"Could not connect to Databricks: {exc}") from exc
    except requests.exceptions.HTTPError as exc:
        raise HTTPException(status_code=response.status_code, detail=response.text or "Databricks API error.") from exc
    except requests.exceptions.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Databricks request failed: {exc}") from exc

    try:
        predictions = response.json().get("predictions")
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
