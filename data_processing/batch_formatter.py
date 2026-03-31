import csv
import io
from typing import Any

from utils.helpers import get_risk_level


def format_batch_output_rows(
    parsed_rows: list[dict[str, Any]],
    results: list[tuple[int, float]],
) -> list[dict[str, Any]]:
    output_rows: list[dict[str, Any]] = []
    for row_idx, (base_row, prediction_result) in enumerate(zip(parsed_rows, results), start=1):
        prediction, probability = prediction_result
        output_rows.append(
            {
                "Row": row_idx,
                "Prediction": prediction,
                "Churn Probability (%)": round(probability * 100, 2),
                "Risk Level": get_risk_level(probability),
                **base_row,
            }
        )

    return output_rows


def build_batch_output_csv(output_rows: list[dict[str, Any]]) -> bytes:
    output_buffer = io.StringIO()
    writer = csv.DictWriter(output_buffer, fieldnames=list(output_rows[0].keys()))
    writer.writeheader()
    writer.writerows(output_rows)
    return output_buffer.getvalue().encode("utf-8")
