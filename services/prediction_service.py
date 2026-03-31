from typing import Any

from features.feature_engineering import create_features, validate_inputs
from services.databricks_api import query_databricks


def prepare_single_prediction_features(base_inputs: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    features = create_features(base_inputs)
    missing_fields = validate_inputs(features)
    return features, missing_fields


def run_single_prediction(
    base_inputs: dict[str, Any],
) -> tuple[bool, str, str | None, tuple[int, float] | None]:
    features, missing_fields = prepare_single_prediction_features(base_inputs)
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}", None, None

    return query_databricks(features)
