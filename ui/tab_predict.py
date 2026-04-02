import streamlit as st
from db.repository import (
    get_all_customers,
    get_customer_by_id,
    get_predictions_by_customer,
    save_prediction,
    update_customer,
)
from data_processing.csv_parser import parse_batch_csv
from services.batch_service import prepare_batch_prediction_features, run_batch_prediction
from services.customer_db_service import (
    build_customer_option_label,
    format_prediction_history,
    map_base_inputs_to_customer,
    map_customer_to_base_inputs,
)
from services.gemini import generate_retention_insight
from utils.constants import BATCH_COLUMNS
from services.prediction_service import prepare_single_prediction_features, run_single_prediction
from ui.components import collect_inputs, render_prediction_history, render_result

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
    base_inputs = collect_inputs(key_prefix="manual")

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
                insight = generate_retention_insight(base_inputs, probability)
                st.session_state["baseline_result"] = (prediction, probability)
                st.session_state["baseline_inputs"] = dict(base_inputs)
                st.session_state["baseline_insight"] = insight

    baseline_result = st.session_state.get("baseline_result")
    baseline_inputs = st.session_state.get("baseline_inputs")
    baseline_insight = st.session_state.get("baseline_insight")
    if baseline_result is not None and baseline_inputs is not None:
        prediction, probability = baseline_result
        render_result(prediction, probability, baseline_inputs, baseline_insight)


def render_database_prediction_tab() -> None:
    st.markdown("#### Predict From Database")
    st.caption("Chọn khách hàng đã lưu trong database, kiểm tra lại dữ liệu và chạy dự đoán.")

    try:
        customers = get_all_customers()
    except Exception as exc:
        st.error("Không thể tải danh sách khách hàng từ database.")
        st.code(str(exc))
        return

    if not customers:
        st.info("Hiện chưa có khách hàng nào trong database.")
        return

    selected_label = st.selectbox(
        "Customer in database",
        [customer["id"] for customer in customers],
        format_func=lambda customer_id: build_customer_option_label(
            next(customer for customer in customers if customer["id"] == customer_id)
        ),
        key="database_customer_selector",
    )
    selected_customer_id = selected_label

    customer = get_customer_by_id(selected_customer_id)
    if customer is None:
        st.warning("Không tìm thấy dữ liệu khách hàng được chọn.")
        return

    st.markdown(
        f"**Customer ID:** `{customer['id']}` | "
        f"**Subscription:** `{customer['subscription_type']}` | "
        f"**Contract:** `{customer['contract_length']}`"
    )

    base_inputs = map_customer_to_base_inputs(customer)
    edited_inputs = collect_inputs(base_inputs, key_prefix=f"db_{selected_customer_id}")

    latest_prediction = None
    prediction_history_rows: list[dict[str, object]] = []

    try:
        latest_prediction = get_predictions_by_customer(selected_customer_id)
        prediction_history_rows = format_prediction_history(latest_prediction)
    except Exception as exc:
        st.warning("Không thể tải lịch sử dự đoán từ database.")
        st.code(str(exc))

    if st.button("Run Prediction From Database", key="run_db_prediction"):
        features, missing_fields = prepare_single_prediction_features(edited_inputs)

        if missing_fields:
            st.warning(f"Missing required fields: {', '.join(missing_fields)}")
        else:
            try:
                update_customer(
                    selected_customer_id,
                    map_base_inputs_to_customer(selected_customer_id, edited_inputs),
                )
            except Exception as exc:
                st.error("Không thể cập nhật dữ liệu khách hàng trước khi dự đoán.")
                st.code(str(exc))
                return

            with st.spinner("Calling Databricks Model Serving..."):
                ok, error_message, technical_detail, result = run_single_prediction(edited_inputs)

            if not ok:
                st.error(error_message)
                if technical_detail:
                    with st.expander("Technical details"):
                        st.code(technical_detail)
            elif result is not None:
                prediction, probability = result
                insight = generate_retention_insight(edited_inputs, probability)
                try:
                    save_prediction(
                        selected_customer_id,
                        prediction,
                        probability,
                        edited_inputs,
                        insight.get("recommended_action"),
                    )
                except Exception as exc:
                    st.warning("Dự đoán thành công nhưng chưa lưu được kết quả vào database.")
                    st.code(str(exc))

                st.session_state["db_prediction_result"] = (prediction, probability)
                st.session_state["db_prediction_inputs"] = dict(edited_inputs)
                st.session_state["db_prediction_customer_id"] = selected_customer_id
                st.session_state["db_prediction_insight"] = insight

    saved_result = st.session_state.get("db_prediction_result")
    saved_inputs = st.session_state.get("db_prediction_inputs")
    saved_customer_id = st.session_state.get("db_prediction_customer_id")
    saved_insight = st.session_state.get("db_prediction_insight")

    if saved_result is not None and saved_inputs is not None and saved_customer_id == selected_customer_id:
        prediction, probability = saved_result
        st.success(f"Đã lưu kết quả dự đoán cho khách hàng {selected_customer_id}.")
        render_result(prediction, probability, saved_inputs, saved_insight)

        try:
            updated_history = get_predictions_by_customer(selected_customer_id)
            render_prediction_history(format_prediction_history(updated_history))
        except Exception as exc:
            st.warning("Không thể tải lại lịch sử dự đoán mới nhất.")
            st.code(str(exc))
    else:
        render_prediction_history(prediction_history_rows)
