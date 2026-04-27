import csv
import io
from typing import Any

from utils.constants import BATCH_COLUMNS, CONTRACT_MAP, VALID_GENDER, VALID_SUBSCRIPTION


def normalize_key(k: str) -> str:
    return k.strip().lower().replace(" ", "_")


def parse_batch_csv(content: bytes) -> tuple[list[dict[str, Any]], list[str]]:
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))

    if reader.fieldnames is None:
        return [], ["CSV does not contain a valid header."]

    # normalize header
    reader.fieldnames = [normalize_key(c) for c in reader.fieldnames]

    missing_columns = [col for col in BATCH_COLUMNS if col not in reader.fieldnames]
    if missing_columns:
        return [], [f"Missing required columns: {', '.join(missing_columns)}"]

    rows: list[dict[str, Any]] = []
    errors: list[str] = []

    for row_index, row in enumerate(reader, start=2):
        try:
            # normalize row keys
            row = {normalize_key(k): v for k, v in row.items()}

            if not any((row.get(col) or "").strip() for col in BATCH_COLUMNS):
                continue

            contract_value = CONTRACT_MAP.get((row["contract_length"] or "").strip().lower())
            if contract_value is None:
                raise ValueError("Contract Length invalid.")

            gender = (row["gender"] or "").strip()
            if gender not in VALID_GENDER:
                raise ValueError("Gender must be Male or Female.")

            subscription = (row["subscription_type"] or "").strip()
            if subscription not in VALID_SUBSCRIPTION:
                raise ValueError("Subscription Type invalid.")

            rows.append(
                {
                    "age": int(float(row["age"] or 0)),
                    "gender": gender,
                    "tenure": int(float(row["tenure"] or 0)),
                    "usage_frequency": int(float(row["usage_frequency"] or 0)),
                    "support_calls": int(float(row["support_calls"] or 0)),
                    "payment_delay": int(float(row["payment_delay"] or 0)),
                    "subscription_type": subscription,
                    "contract_length": contract_value,
                    "total_spend": float(row["total_spend"] or 0),
                    "last_interaction": int(float(row["last_interaction"] or 0)),
                }
            )

        except ValueError as exc:
            errors.append(f"Row {row_index}: {exc}")

    if not rows and not errors:
        errors.append("CSV does not contain any valid data rows.")

    return rows, errors


def build_batch_output_csv(output_rows: list[dict[str, Any]]) -> str:
    output_buffer = io.StringIO()
    writer = csv.DictWriter(output_buffer, fieldnames=list(output_rows[0].keys()))
    writer.writeheader()
    writer.writerows(output_rows)
    return output_buffer.getvalue()
