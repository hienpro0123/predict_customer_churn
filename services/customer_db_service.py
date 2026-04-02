from __future__ import annotations

from typing import Any


CONTRACT_LABEL_MAPPING = {
    "1 month": "Monthly",
    "3 months": "Quarterly",
    "12 months": "Annual",
}


# Chuyển một bản ghi khách hàng trong database sang format input của model.
def map_customer_to_base_inputs(customer: dict[str, Any]) -> dict[str, Any]:
    return {
        "Age": int(customer["age"]),
        "Gender": customer["gender"],
        "Tenure": int(customer["tenure"]),
        "Usage Frequency": int(customer["usage_frequency"]),
        "Support Calls": int(customer["support_calls"]),
        "Payment Delay": int(customer["payment_delay"]),
        "Subscription Type": customer["subscription_type"],
        "Contract Length": customer["contract_length"],
        "Total Spend": float(customer["total_spend"]),
        "Last Interaction": int(customer["last_interaction"]),
    }


# Chuyển dữ liệu từ form dự đoán về format lưu trong bảng customers.
def map_base_inputs_to_customer(customer_id: str, base_inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": customer_id,
        "age": int(base_inputs["Age"]),
        "gender": base_inputs["Gender"],
        "tenure": int(base_inputs["Tenure"]),
        "usage_frequency": int(base_inputs["Usage Frequency"]),
        "support_calls": int(base_inputs["Support Calls"]),
        "payment_delay": int(base_inputs["Payment Delay"]),
        "subscription_type": base_inputs["Subscription Type"],
        "contract_length": base_inputs["Contract Length"],
        "total_spend": float(base_inputs["Total Spend"]),
        "last_interaction": int(base_inputs["Last Interaction"]),
    }


# Tạo nhãn hiển thị gọn cho dropdown chọn khách hàng từ database.
def build_customer_option_label(customer: dict[str, Any]) -> str:
    return (
        f'{customer["id"]} | {customer["gender"]} | '
        f'{customer["subscription_type"]} | Tenure {customer["tenure"]}m'
    )


# Đổi giá trị contract length lưu trong database sang nhãn dễ hiểu trên giao diện.
def get_contract_label(contract_length: str) -> str:
    return CONTRACT_LABEL_MAPPING.get(contract_length, "Monthly")


# Chuẩn hóa lịch sử dự đoán để hiển thị lên bảng Streamlit.
def format_prediction_history(predictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    formatted_rows: list[dict[str, Any]] = []
    for item in predictions:
        formatted_rows.append(
            {
                "Prediction ID": item["prediction_id"],
                "Customer ID": item["customer_id"],
                "Predicted Label": item["predicted_label"],
                "Churn Probability": round(float(item["churn_probability"]), 4),
                "Recommended Action": item.get("recommended_action") or "",
                "Created At": item["created_at"],
            }
        )
    return formatted_rows
