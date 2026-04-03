import streamlit as st
from db.schema import create_tables
from ui.tab_predict import (
    render_batch_prediction_tab,
    render_database_prediction_tab,
    render_single_prediction_tab,
)
from ui.components import inject_styles, render_header
st.set_page_config(page_title="Customer Churn", layout="wide")


def main() -> None:
    # Create table if 
    create_tables()
    inject_styles()
    render_header()
    tab_manual, tab_database, tab_batch = st.tabs(
        ["Single Prediction", "Predict From Database", "Batch Prediction (CSV)"]
    )

    with tab_manual:
        render_single_prediction_tab()

    with tab_database:
        render_database_prediction_tab()

    with tab_batch:
        render_batch_prediction_tab()


if __name__ == "__main__":
    main()
