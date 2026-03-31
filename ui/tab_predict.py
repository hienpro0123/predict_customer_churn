import streamlit as st
from data_processing.csv_parser import parse_batch_csv
from services.batch_service import prepare_batch_prediction_features, run_batch_prediction
from utils.constants import BATCH_COLUMNS
from services.prediction_service import prepare_single_prediction_features, run_single_prediction
from ui.components import collect_inputs, render_result

def render_batch_prediction_tab() -> None:
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
        parsed_rows, parse_errors = parse_batch_csv(uploaded_file)
        if parse_errors:
            st.error(f"Found {len(parse_errors)} data validation error(s) in the CSV file.")
            with st.expander("Error details"):
                for msg in parse_errors[:50]:
                    st.write(f"- {msg}")
            return

        ok, error_message, _ = prepare_batch_prediction_features(parsed_rows)
        if not ok:
            st.error(error_message)
            return

        with st.spinner("Running batch prediction on Databricks..."):
            ok, error_message, technical_detail, output_rows, output_csv = run_batch_prediction(parsed_rows)

        if not ok:
            st.error(error_message)
            if technical_detail:
                with st.expander("Batch technical details"):
                    st.code(technical_detail)
            return

        assert output_rows is not None
        assert output_csv is not None

        st.success(f"Batch prediction completed for {len(output_rows)} rows.")
        st.dataframe(output_rows, width="stretch")

        st.session_state["batch_output_rows"] = output_rows
        st.session_state["batch_output_csv"] = output_csv

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


def render_single_prediction_tab() -> None:
    base_inputs = collect_inputs()

    if st.button("Run Prediction", key="run_single_prediction"):
        features, missing_fields = prepare_single_prediction_features(base_inputs)

        if missing_fields:
            st.warning(f"Missing required fields: {', '.join(missing_fields)}")
        else:
            with st.spinner("Calling Databricks Model Serving..."):
                ok, error_message, technical_detail, result = run_single_prediction(base_inputs)

            if not ok:
                st.error(error_message)
                if technical_detail:
                    with st.expander("Technical details"):
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
