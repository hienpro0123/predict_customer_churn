from pathlib import Path
from typing import Any

import plotly.graph_objects as go
import streamlit as st

from config.settings import CONTRACT_LENGTH_MAPPING
from services.customer_db_service import get_contract_label
from utils.helpers import get_risk_badge, get_top_risk_drivers


def inject_styles() -> None:
    css_path = Path(__file__).resolve().parents[1] / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        """
        <section class="hero-shell">
            <div class="hero-topline">
                <span class="hero-chip">Churn Intelligence</span>
                <span class="hero-status">Production Ready</span>
            </div>
            <div class="main-title">Customer Churn System</div>
            <div class="sub-title">Advanced Machine Learning Dashboard for Churn Prediction</div>
            <div class="hero-meta">
                <span>Real-time scoring</span>
                <span>Feature-driven analysis</span>
                <span>Decision-ready insights</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def collect_inputs(
    default_values: dict[str, Any] | None = None,
    key_prefix: str = "manual",
) -> dict[str, Any]:
    default_values = default_values or {}

    gender_options = ["Male", "Female"]
    subscription_options = ["Basic", "Standard", "Premium"]
    contract_options = ["Monthly", "Quarterly", "Annual"]

    default_gender = default_values.get("Gender", "Male")
    default_subscription = default_values.get("Subscription Type", "Basic")
    default_contract_label = get_contract_label(default_values.get("Contract Length", "1 month"))

    st.markdown("#### Customer Profile Inputs")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Information")
        age = st.number_input(
            "Age",
            min_value=18,
            max_value=80,
            value=int(default_values.get("Age", 30)),
            key=f"{key_prefix}_age",
        )
        tenure = st.number_input(
            "Tenure (months)",
            min_value=1,
            max_value=60,
            value=int(default_values.get("Tenure", 12)),
            key=f"{key_prefix}_tenure",
        )
        usage = st.number_input(
            "Usage Frequency",
            min_value=1,
            max_value=30,
            value=int(default_values.get("Usage Frequency", 10)),
            key=f"{key_prefix}_usage",
        )
        support_calls = st.number_input(
            "Support Calls",
            min_value=0,
            max_value=20,
            value=int(default_values.get("Support Calls", 1)),
            key=f"{key_prefix}_support_calls",
        )
        gender = st.selectbox(
            "Gender",
            gender_options,
            index=gender_options.index(default_gender) if default_gender in gender_options else 0,
            key=f"{key_prefix}_gender",
        )

    with col2:
        st.subheader("Subscription Details")
        payment_delay = st.number_input(
            "Payment Delay",
            min_value=0,
            max_value=30,
            value=int(default_values.get("Payment Delay", 0)),
            key=f"{key_prefix}_payment_delay",
        )
        total_spend = st.number_input(
            "Total Spend",
            min_value=0.0,
            max_value=10000.0,
            value=float(default_values.get("Total Spend", 500.0)),
            key=f"{key_prefix}_total_spend",
        )
        last_interaction = st.number_input(
            "Last Interaction",
            min_value=0,
            max_value=30,
            value=int(default_values.get("Last Interaction", 5)),
            key=f"{key_prefix}_last_interaction",
        )
        subscription = st.selectbox(
            "Subscription Type",
            subscription_options,
            index=subscription_options.index(default_subscription)
            if default_subscription in subscription_options
            else 0,
            key=f"{key_prefix}_subscription_type",
        )
        contract_label = st.selectbox(
            "Contract Length",
            contract_options,
            index=contract_options.index(default_contract_label)
            if default_contract_label in contract_options
            else 0,
            key=f"{key_prefix}_contract_length",
        )

    st.divider()

    return {
        "Age": int(age),
        "Gender": gender,
        "Tenure": int(tenure),
        "Usage Frequency": int(usage),
        "Support Calls": int(support_calls),
        "Payment Delay": int(payment_delay),
        "Subscription Type": subscription,
        "Contract Length": CONTRACT_LENGTH_MAPPING[contract_label],
        "Total Spend": float(total_spend),
        "Last Interaction": int(last_interaction),
    }


# Hiển thị lịch sử dự đoán ngắn gọn của một khách hàng.
def render_prediction_history(history_rows: list[dict[str, Any]]) -> None:
    st.markdown("#### Prediction History")
    if not history_rows:
        st.info("Khách hàng này chưa có lịch sử dự đoán.")
        return

    st.dataframe(history_rows, width="stretch")


def render_result(
    prediction: int,
    probability: float,
    base_inputs: dict[str, Any],
    insight: dict[str, str] | None = None,
) -> None:
    st.divider()
    st.markdown("#### Model Decision")
    st.subheader("Prediction Result")

    col_gauge, col_summary = st.columns([1, 2])

    with col_gauge:
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=probability * 100,
                title={"text": "Churn Risk (%)", "font": {"size": 24, "color": "#eaf2ff"}},
                number={"font": {"size": 62, "color": "#7dd3fc"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#dbeafe", "tickfont": {"color": "#dbeafe"}},
                    "bar": {"color": "#38bdf8", "thickness": 0.26},
                    "bgcolor": "#0b1324",
                    "steps": [
                        {"range": [0, 30], "color": "#22c55e"},
                        {"range": [30, 70], "color": "#f59e0b"},
                        {"range": [70, 100], "color": "#ef4444"},
                    ],
                },
            )
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#ffffff"},
        )
        st.plotly_chart(fig, width="stretch")

    with col_summary:
        badge_color, risk_label = get_risk_badge(probability)
        top_drivers = get_top_risk_drivers(base_inputs, top_n=5)

        st.markdown(
            f'<div class="score-text">{probability * 100:.2f}%</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="badge" style="background:{badge_color};">{risk_label}</div>',
            unsafe_allow_html=True,
        )

        if prediction == 1:
            st.markdown(
                '<div class="status-banner danger">Customer is likely to churn.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-banner safe">Customer is likely to stay.</div>',
                unsafe_allow_html=True,
            )

        recommended_action = (
            insight.get("recommended_action", "").strip()
            if insight is not None
            else ""
        )
        if recommended_action:
            st.markdown(
                f"""
                <div class="insight-box">
                    <h3>Recommended Action</h3>
                    <p>{recommended_action}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        drivers_html = "".join(
            [
                (
                    f'<li><span class="driver-name">{item["label"]}</span>'
                    f'<span class="driver-score">{item["score"] * 100:.0f}%</span>'
                    f'<div class="driver-reason">{item["reason"]}</div></li>'
                )
                for item in top_drivers
            ]
        )
        st.markdown(
            f"""
            <div class="insight-box driver-box">
                <h3>Top Risk Drivers</h3>
                <p>Strongest factors currently pushing churn risk up:</p>
                <ul class="driver-list">{drivers_html}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
