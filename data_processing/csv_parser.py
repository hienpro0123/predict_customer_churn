import csv
import io
from typing import Any

from utils.constants import BATCH_COLUMNS, CONTRACT_MAP, VALID_GENDER, VALID_SUBSCRIPTION


def normalize_contract(value: str) -> str | None:
    key = value.strip().lower()
    return CONTRACT_MAP.get(key)


def parse_batch_csv(uploaded_file: Any) -> tuple[list[dict[str, Any]], list[str]]:
    content = uploaded_file.getvalue().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    if reader.fieldnames is None:
        return [], ["CSV does not contain a valid header."]

    missing_columns = [col for col in BATCH_COLUMNS if col not in reader.fieldnames]
    if missing_columns:
        return [], [f"Missing required columns: {', '.join(missing_columns)}"]

    rows: list[dict[str, Any]] = []
    errors: list[str] = []

    for row_index, row in enumerate(reader, start=2):
        if not any((row.get(col) or "").strip() for col in BATCH_COLUMNS):
            continue

        try:
            contract_value = normalize_contract(row["Contract Length"])
            if contract_value is None:
                raise ValueError("Contract Length must be Monthly/Quarterly/Annual or 1 month/3 months/12 months.")

            gender = (row["Gender"] or "").strip()
            if gender not in VALID_GENDER:
                raise ValueError("Gender must be Male or Female.")

            subscription = (row["Subscription Type"] or "").strip()
            if subscription not in VALID_SUBSCRIPTION:
                raise ValueError("Subscription Type must be Basic/Standard/Premium.")

            parsed = {
                "Age": int(float((row["Age"] or "0").strip())),
                "Gender": gender,
                "Tenure": int(float((row["Tenure"] or "0").strip())),
                "Usage Frequency": int(float((row["Usage Frequency"] or "0").strip())),
                "Support Calls": int(float((row["Support Calls"] or "0").strip())),
                "Payment Delay": int(float((row["Payment Delay"] or "0").strip())),
                "Subscription Type": subscription,
                "Contract Length": contract_value,
                "Total Spend": float((row["Total Spend"] or "0").strip()),
                "Last Interaction": int(float((row["Last Interaction"] or "0").strip())),
            }
        except ValueError as exc:
            errors.append(f"Row {row_index}: {exc}")
            continue

        rows.append(parsed)

    if not rows and not errors:
        errors.append("CSV does not contain any valid data rows.")

    return rows, errors
