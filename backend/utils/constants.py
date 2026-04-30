FEATURE_COLUMNS = [
    "customer_id",
    "age",
    "gender",
    "tenure",
    "usage_frequency",
    "support_calls",
    "payment_delay",
    "subscription_type",
    "contract_length",
    "total_spend",
    "last_interaction",
    "age_group",
    "usage_per_tenure",
    "spend_per_usage",
    "spend_per_tenure",
    "payment_delay_ratio",
    "engagement_score",
]

BATCH_COLUMNS = [
    "age",
    "gender",
    "tenure",
    "usage_frequency",
    "support_calls",
    "payment_delay",
    "subscription_type",
    "contract_length",
    "total_spend",
    "last_interaction",
]

CONTRACT_LENGTH_MAPPING = {
    "Monthly": "1 month",
    "Quarterly": "3 months",
    "Annual": "12 months",
}

CONTRACT_LABEL_MAPPING = {
    "1 month": "Monthly",
    "3 months": "Quarterly",
    "12 months": "Annual",
}

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

RISK_THRESHOLDS = {
    "low": 0.3,
    "high": 0.7,
}

CONTRACT_RISK_MAP = {"1 month": 1.0, "3 months": 0.55, "12 months": 0.2}
SUBSCRIPTION_RISK_MAP = {"Basic": 1.0, "Standard": 0.55, "Premium": 0.2}
