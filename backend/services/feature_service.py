from typing import Any

from utils.constants import FEATURE_COLUMNS


def get_age_group(age: int) -> str:
    if age < 30:
        return "Young"
    if age < 50:
        return "Adult"
    return "Senior"


def create_features(base_inputs: dict[str, Any]) -> dict[str, Any]:
    tenure = base_inputs["Tenure"]
    usage = base_inputs["Usage Frequency"]
    payment_delay = base_inputs["Payment Delay"]
    total_spend = base_inputs["Total Spend"]

    engineered_features = {
        "Age_group": get_age_group(base_inputs["Age"]),
        "Usage_Per_Tenure": usage / (tenure + 1),
        "Spend_Per_Usage": total_spend / (usage + 1),
        "Spend_Per_Tenure": total_spend / (tenure + 1),
        "Payment_Delay_Ratio": payment_delay / 30,
        "Engagement_Score": (usage * total_spend) / 1000,
    }
    full_features = {**base_inputs, **engineered_features}
    return {column: full_features[column] for column in FEATURE_COLUMNS}


def validate_inputs(features: dict[str, Any]) -> list[str]:
    return [field for field in FEATURE_COLUMNS if features.get(field) is None or features.get(field) == ""]
