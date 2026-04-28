from typing import Any

from utils.constants import FEATURE_COLUMNS


def normalize_key(key: str) -> str:
    return key.strip().lower().replace(" ", "_")


def normalize_customerid(value: Any) -> int:
    if value in (None, ""):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    digits = "".join(char for char in str(value) if char.isdigit())
    return int(digits) if digits else 0


def get_age_group(age: int) -> str:
    if age < 30:
        return "Young"
    if age < 50:
        return "Adult"
    return "Senior"


def create_features(base_inputs: dict[str, Any]) -> dict[str, Any]:
    x = {normalize_key(key): value for key, value in base_inputs.items()}

    # đảm bảo có customerid
    x["customerid"] = normalize_customerid(x.get("customerid"))

    # feature engineering
    tenure = x["tenure"]
    usage = x["usage_frequency"]
    spend = x["total_spend"]
    delay = x["payment_delay"]

    x.update(
        {
            "age_group": get_age_group(x["age"]),
            "usage_per_tenure": usage / (tenure + 1),
            "spend_per_usage": spend / (usage + 1),
            "spend_per_tenure": spend / (tenure + 1),
            "payment_delay_ratio": delay / 30,
            "engagement_score": (usage * spend) / 1000,
        }
    )

    # Đảm bảo tất cả các key trả về đều được chuẩn hóa (viết thường, replace space bằng _)
    # để khớp với schema mà model yêu cầu
    return {column: x.get(column) for column in FEATURE_COLUMNS}


def validate_inputs(features: dict[str, Any]) -> list[str]:
    # Kiểm tra tính hợp lệ dựa trên key đã chuẩn hóa
    return [field for field in FEATURE_COLUMNS if features.get(field) in (None, "")]
