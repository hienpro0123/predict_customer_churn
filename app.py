import streamlit as st

from ui.batch_tab import render_batch_prediction_tab
from ui.components import inject_styles, render_header
from ui.single_tab import render_single_prediction_tab

st.set_page_config(page_title="Customer Churn", layout="wide")


def main() -> None:
    inject_styles()
    render_header()
    tab_manual, tab_batch = st.tabs(["Single Prediction", "Batch Prediction (CSV)"])

    with tab_manual:
        render_single_prediction_tab()

    with tab_batch:
        render_batch_prediction_tab()


if __name__ == "__main__":
    main()
