from typing import Any

from data_processing.batch_formatter import build_batch_output_csv, format_batch_output_rows
from features.feature_engineering import create_features, validate_inputs
from services.databricks_api import query_databricks_batch


def prepare_batch_prediction_features(
    parsed_rows: list[dict[str, Any]],
) -> tuple[bool, str, list[dict[str, Any]] | None]:
    features_list: list[dict[str, Any]] = []
    for idx, base_input in enumerate(parsed_rows, start=1):
        feature_row = create_features(base_input)
        missing_fields = validate_inputs(feature_row)
        if missing_fields:
            return False, f"Row {idx} is missing engineered features: {', '.join(missing_fields)}", None
        features_list.append(feature_row)

    return True, "", features_list


def run_batch_prediction(
    parsed_rows: list[dict[str, Any]],
) -> tuple[bool, str, str | None, list[dict[str, Any]] | None, bytes | None]:
    ok, error_message, features_list = prepare_batch_prediction_features(parsed_rows)
    if not ok or features_list is None:
        return False, error_message, None, None, None

    ok, error_message, technical_detail, results = query_databricks_batch(features_list)
    if not ok or results is None:
        return False, error_message, technical_detail, None, None

    output_rows = format_batch_output_rows(parsed_rows, results)
    output_csv = build_batch_output_csv(output_rows)
    return True, "", None, output_rows, output_csv
