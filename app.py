import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Customer Churn",
    layout="wide"
)

# ==============================
# LOAD MODEL (CACHE)
# ==============================
@st.cache_resource
def load_model():
    return joblib.load("model.pkl")

model = load_model()

# ==============================
# ADVANCED UI STYLE
# ==============================
st.markdown("""
<style>

/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Main container */
.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* Glass card */
.glass {
    background: rgba(255, 255, 255, 0.07);
    padding: 10px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

/* Title */
.main-title {
    text-align: center;
    font-size: 60px;
    font-weight: 900;
    margin-bottom: 10px;
}

/* Subtitle */
.sub-title {
    text-align: center;
    font-size: 22px;
    opacity: 0.8;
    margin-bottom: 50px;
}

/* Button */
.stButton>button {
    width: 100%;
    height: 60px;
    font-size: 22px;
    font-weight: bold;
    border-radius: 12px;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.03);
}

/* Score text */
.score-text {
    font-size: 48px;
    font-weight: 800;
}

/* Risk badge */
.badge {
    padding: 8px 18px;
    border-radius: 20px;
    font-weight: bold;
    display: inline-block;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# TITLE
# ==============================
st.markdown('<div class="main-title">Customer Churn System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Advanced Machine Learning Dashboard for Churn Prediction</div>', unsafe_allow_html=True)

# ==============================
# INPUT SECTION
# ==============================
st.markdown('<div class="glass">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Customer Information")
    age = st.number_input("Age", 18, 80, 30)
    tenure = st.number_input("Tenure (months)", 1, 60, 12)
    usage = st.number_input("Usage Frequency", 1, 30, 10)
    support_calls = st.number_input("Support Calls", 0, 20, 1)
    gender = st.selectbox("Gender", ["Male", "Female"])

with col2:
    st.markdown("### Subscription Details")
    payment_delay = st.number_input("Payment Delay", 0, 30, 0)
    total_spend = st.number_input("Total Spend", 0.0, 10000.0, 500.0)
    last_interaction = st.number_input("Last Interaction", 0, 30, 5)
    subscription = st.selectbox("Subscription Type", ["Basic", "Standard", "Premium"])
    contract = st.selectbox("Contract Length", ["Monthly", "Quarterly", "Annual"])

st.divider()

# ==============================
# FEATURE ENGINEERING
# ==============================
def create_features():

    usage_per_tenure = usage / (tenure + 1)
    spend_per_usage = total_spend / (usage + 1)
    spend_per_tenure = total_spend / (tenure + 1)
    payment_delay_ratio = payment_delay / 30
    engagement_score = (usage * total_spend) / 1000

    if age < 30:
        age_group = "Young"
    elif age < 50:
        age_group = "Adult"
    else:
        age_group = "Senior"

    return pd.DataFrame([{
        "Age": age,
        "Gender": gender,
        "Tenure": tenure,
        "Usage Frequency": usage,
        "Support Calls": support_calls,
        "Payment Delay": payment_delay,
        "Subscription Type": subscription,
        "Contract Length": contract,
        "Total Spend": total_spend,
        "Last Interaction": last_interaction,
        "Age_group": age_group,
        "Usage_Per_Tenure": usage_per_tenure,
        "Spend_Per_Usage": spend_per_usage,
        "Spend_Per_Tenure": spend_per_tenure,
        "Payment_Delay_Ratio": payment_delay_ratio,
        "Engagement_Score": engagement_score
    }])

# ==============================
# PREDICT BUTTON
# ==============================
predict = st.button("Run Prediction")

# ==============================
# RESULT SECTION
# ==============================
if predict:

    input_data = create_features()
    prediction = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0][1]

    st.divider()
    st.markdown("## Prediction Result")

    col_gauge, col_summary = st.columns([1,2])

 # ==========================
# GAUGE (Light Blue Theme)
# ==========================
    with col_gauge:

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob * 100,
            title={"text": "Churn Risk (%)", "font": {"size": 22, "color": "#ffffff"}},
            number={"font": {"size": 60, "color": "#1e3a8a"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#1e3a8a"},
                "bar": {"color": "#2563eb", "thickness": 0.25},
                "bgcolor": "#e0f2fe",
                "steps": [
                    {"range": [0, 30], "color": "#86efac"},
                    {"range": [30, 70], "color": "#fde68a"},
                    {"range": [70, 100], "color": "#fca5a5"},
                ],
            }
        ))

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",   # trong suốt
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#ffffff"}
        )

        st.plotly_chart(fig, use_container_width=True)

    # Summary
    with col_summary:

        st.markdown(f'<div class="score-text">{prob*100:.2f}%</div>', unsafe_allow_html=True)

        if prob < 0.3:
            badge_color = "#2ecc71"
            risk = "LOW RISK"
        elif prob < 0.7:
            badge_color = "#f39c12"
            risk = "MEDIUM RISK"
        else:
            badge_color = "#e74c3c"
            risk = "HIGH RISK"

        st.markdown(
            f'<div class="badge" style="background:{badge_color};">{risk}</div>',
            unsafe_allow_html=True
        )

        if prediction == 1:
            st.error("Customer is likely to churn.")
        else:
            st.success("Customer is likely to stay.")

        st.markdown("""
        ### Insight

        The AI model evaluates:
        - Payment delay behavior
        - Customer engagement
        - Spending patterns
        - Subscription characteristics
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)