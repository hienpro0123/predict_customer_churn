import streamlit as st

from services.prediction_service import prepare_single_prediction_features, run_single_prediction
from ui.components import collect_inputs, render_result


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
