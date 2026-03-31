from pathlib import Path
from typing import Any

import plotly.graph_objects as go
import streamlit as st

from config.settings import CONTRACT_LENGTH_MAPPING
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


def collect_inputs() -> dict[str, Any]:
    st.markdown("#### Customer Profile Inputs")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Information")
        age = st.number_input("Age", min_value=18, max_value=80, value=30)
        tenure = st.number_input("Tenure (months)", min_value=1, max_value=60, value=12)
        usage = st.number_input("Usage Frequency", min_value=1, max_value=30, value=10)
        support_calls = st.number_input("Support Calls", min_value=0, max_value=20, value=1)
        gender = st.selectbox("Gender", ["Male", "Female"])

    with col2:
        st.subheader("Subscription Details")
        payment_delay = st.number_input("Payment Delay", min_value=0, max_value=30, value=0)
        total_spend = st.number_input(
            "Total Spend",
            min_value=0.0,
            max_value=10000.0,
            value=500.0,
        )
        last_interaction = st.number_input("Last Interaction", min_value=0, max_value=30, value=5)
        subscription = st.selectbox("Subscription Type", ["Basic", "Standard", "Premium"])
        contract_label = st.selectbox("Contract Length", ["Monthly", "Quarterly", "Annual"])

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


def render_result(prediction: int, probability: float, base_inputs: dict[str, Any]) -> None:
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

        st.markdown(
            """
            <div class="insight-box">
                <h3>Insight</h3>
                <p>The AI model evaluates:</p>
                <ul>
                    <li>Payment delay behavior</li>
                    <li>Customer engagement</li>
                    <li>Spending patterns</li>
                    <li>Subscription characteristics</li>
                </ul>
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
