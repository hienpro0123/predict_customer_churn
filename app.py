import csv
import io
from typing import Any

import streamlit as st

from features.feature_engineering import create_features, validate_inputs
from services.databricks_api import query_databricks, query_databricks_batch
from ui.components import collect_inputs, inject_styles, render_header, render_result

st.set_page_config(page_title="Customer Churn", layout="wide")

BATCH_COLUMNS = [
    "Age",
    "Gender",
    "Tenure",
    "Usage Frequency",
    "Support Calls",
    "Payment Delay",
    "Subscription Type",
    "Contract Length",
    "Total Spend",
    "Last Interaction",
]

CONTRACT_MAP = {
    "monthly": "1 month",
    "1 month": "1 month",
    "quarterly": "3 months",
    "3 months": "3 months",
    "annual": "12 months",
    "yearly": "12 months",
    "12 months": "12 months",
}

VALID_GENDER = {"Male", "Female"}
VALID_SUBSCRIPTION = {"Basic", "Standard", "Premium"}


def _normalize_contract(value: str) -> str | None:
    key = value.strip().lower()
    return CONTRACT_MAP.get(key)


def _parse_batch_csv(uploaded_file: Any) -> tuple[list[dict[str, Any]], list[str]]:
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
            contract_value = _normalize_contract(row["Contract Length"])
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


def _render_batch_predict_section() -> None:
    st.divider()
    st.markdown("#### Batch Predict (CSV)")
    st.caption("Upload CSV with required columns to run prediction for multiple customers at once.")

    with st.expander("Required CSV columns"):
        st.code(", ".join(BATCH_COLUMNS))

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], key="batch_csv")

    if uploaded_file is None:
        st.session_state.pop("batch_output_rows", None)
        st.session_state.pop("batch_output_csv", None)
        return

    if st.button("Run Batch Prediction", key="run_batch_prediction"):
        parsed_rows, parse_errors = _parse_batch_csv(uploaded_file)
        if parse_errors:
            st.error(f"Found {len(parse_errors)} data validation error(s) in the CSV file.")
            with st.expander("Error details"):
                for msg in parse_errors[:50]:
                    st.write(f"- {msg}")
            return

        features_list: list[dict[str, Any]] = []
        for idx, base_input in enumerate(parsed_rows, start=1):
            feature_row = create_features(base_input)
            missing_fields = validate_inputs(feature_row)
            if missing_fields:
                st.error(f"Row {idx} is missing engineered features: {', '.join(missing_fields)}")
                return
            features_list.append(feature_row)

        with st.spinner("Running batch prediction on Databricks..."):
            ok, error_message, technical_detail, results = query_databricks_batch(features_list)

        if not ok:
            st.error(error_message)
            if technical_detail:
                with st.expander("Batch technical details"):
                    st.code(technical_detail)
            return

        assert results is not None

        output_rows: list[dict[str, Any]] = []
        for row_idx, (base_row, prediction_result) in enumerate(zip(parsed_rows, results), start=1):
            prediction, probability = prediction_result
            output_rows.append(
                {
                    "Row": row_idx,
                    "Prediction": prediction,
                    "Churn Probability (%)": round(probability * 100, 2),
                    "Risk Level": "HIGH" if probability >= 0.7 else "MEDIUM" if probability >= 0.3 else "LOW",
                    **base_row,
                }
            )

        st.success(f"Batch prediction completed for {len(output_rows)} rows.")
        st.dataframe(output_rows, width="stretch")

        output_buffer = io.StringIO()
        writer = csv.DictWriter(output_buffer, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

        st.session_state["batch_output_rows"] = output_rows
        st.session_state["batch_output_csv"] = output_buffer.getvalue().encode("utf-8")

    saved_rows = st.session_state.get("batch_output_rows")
    saved_csv = st.session_state.get("batch_output_csv")
    if saved_rows and saved_csv:
        st.success(f"Batch prediction completed for {len(saved_rows)} rows.")
        st.dataframe(saved_rows, width="stretch")
        st.download_button(
            label="Download Batch Result CSV",
            data=saved_csv,
            file_name="batch_prediction_results.csv",
            mime="text/csv",
        )


def main() -> None:
    inject_styles()
    render_header()
    base_inputs = collect_inputs()

    if st.button("Run Prediction"):
        features = create_features(base_inputs)
        missing_fields = validate_inputs(features)

        if missing_fields:
            st.warning(f"Missing required fields: {', '.join(missing_fields)}")
        else:
            with st.spinner("Calling Databricks Model Serving..."):
                ok, error_message, technical_detail, result = query_databricks(features)

            if not ok:
                st.error(error_message)
                if technical_detail:
                    with st.expander("Xem chi tiet ky thuat"):
                        st.code(technical_detail)
            elif result is not None:
                prediction, probability = result
                st.session_state["baseline_result"] = (prediction, probability)
                st.session_state["baseline_inputs"] = dict(base_inputs)

    baseline_result = st.session_state.get("baseline_result")
    baseline_inputs = st.session_state.get("baseline_inputs")
    if baseline_result is not None and baseline_inputs is not None:
        prediction, probability = baseline_result
        render_result(prediction, probability, baseline_inputs)

    _render_batch_predict_section()


if __name__ == "__main__":
    main()
