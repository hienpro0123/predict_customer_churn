from __future__ import annotations

import json
from typing import Any

from db.connection import get_connection


CustomerRecord = dict[str, Any]
PredictionRecord = dict[str, Any]


def _normalize_customer_row(row: tuple[Any, ...]) -> CustomerRecord:
    return {
        "id": row[0],
        "age": row[1],
        "gender": row[2],
        "tenure": row[3],
        "usage_frequency": row[4],
        "support_calls": row[5],
        "payment_delay": row[6],
        "subscription_type": row[7],
        "contract_length": row[8],
        "total_spend": float(row[9]) if row[9] is not None else None,
        "last_interaction": row[10],
        "created_at": row[11],
        "updated_at": row[12],
    }


def _normalize_prediction_row(row: tuple[Any, ...]) -> PredictionRecord:
    return {
        "prediction_id": row[0],
        "customer_id": row[1],
        "predicted_label": row[2],
        "churn_probability": float(row[3]) if row[3] is not None else None,
        "model_input_snapshot": row[4],
        "recommended_action": row[5],
        "created_at": row[6],
    }


# Tạo mới một khách hàng trong bảng customers.
def create_customer(customer_data: CustomerRecord) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO customers (
            id,
            age,
            gender,
            tenure,
            usage_frequency,
            support_calls,
            payment_delay,
            subscription_type,
            contract_length,
            total_spend,
            last_interaction
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            customer_data["id"],
            customer_data["age"],
            customer_data["gender"],
            customer_data["tenure"],
            customer_data["usage_frequency"],
            customer_data["support_calls"],
            customer_data["payment_delay"],
            customer_data["subscription_type"],
            customer_data["contract_length"],
            customer_data["total_spend"],
            customer_data["last_interaction"],
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()


# Lấy toàn bộ danh sách khách hàng để hiển thị lên giao diện.
def get_all_customers() -> list[CustomerRecord]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            age,
            gender,
            tenure,
            usage_frequency,
            support_calls,
            payment_delay,
            subscription_type,
            contract_length,
            total_spend,
            last_interaction,
            created_at,
            updated_at
        FROM customers
        ORDER BY id
        """
    )
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return [_normalize_customer_row(row) for row in rows]


# Lấy chi tiết một khách hàng theo id.
def get_customer_by_id(customer_id: str) -> CustomerRecord | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            age,
            gender,
            tenure,
            usage_frequency,
            support_calls,
            payment_delay,
            subscription_type,
            contract_length,
            total_spend,
            last_interaction,
            created_at,
            updated_at
        FROM customers
        WHERE id = %s
        """,
        (customer_id,),
    )
    row = cursor.fetchone()

    cursor.close()
    conn.close()
    return _normalize_customer_row(row) if row else None


# Cập nhật thông tin khách hàng đã có trong database.
def update_customer(customer_id: str, customer_data: CustomerRecord) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE customers
        SET
            age = %s,
            gender = %s,
            tenure = %s,
            usage_frequency = %s,
            support_calls = %s,
            payment_delay = %s,
            subscription_type = %s,
            contract_length = %s,
            total_spend = %s,
            last_interaction = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (
            customer_data["age"],
            customer_data["gender"],
            customer_data["tenure"],
            customer_data["usage_frequency"],
            customer_data["support_calls"],
            customer_data["payment_delay"],
            customer_data["subscription_type"],
            customer_data["contract_length"],
            customer_data["total_spend"],
            customer_data["last_interaction"],
            customer_id,
        ),
    )
    updated = cursor.rowcount > 0

    conn.commit()
    cursor.close()
    conn.close()
    return updated


# Lưu kết quả dự đoán của một khách hàng vào bảng predictions.
def save_prediction(
    customer_id: str,
    predicted_label: int,
    churn_probability: float,
    model_input_snapshot: dict[str, Any],
    recommended_action: str | None = None,
) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions (
            customer_id,
            predicted_label,
            churn_probability,
            model_input_snapshot,
            recommended_action
        )
        VALUES (%s, %s, %s, %s::jsonb, %s)
        RETURNING prediction_id
        """,
        (
            customer_id,
            predicted_label,
            churn_probability,
            json.dumps(model_input_snapshot),
            recommended_action,
        ),
    )
    prediction_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()
    return prediction_id


# Lấy kết quả dự đoán mới nhất của một khách hàng.
def get_latest_prediction(customer_id: str) -> PredictionRecord | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            prediction_id,
            customer_id,
            predicted_label,
            churn_probability,
            model_input_snapshot,
            recommended_action,
            created_at
        FROM predictions
        WHERE customer_id = %s
        ORDER BY created_at DESC, prediction_id DESC
        LIMIT 1
        """,
        (customer_id,),
    )
    row = cursor.fetchone()

    cursor.close()
    conn.close()
    return _normalize_prediction_row(row) if row else None


# Lấy toàn bộ lịch sử dự đoán của một khách hàng.
def get_predictions_by_customer(customer_id: str) -> list[PredictionRecord]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            prediction_id,
            customer_id,
            predicted_label,
            churn_probability,
            model_input_snapshot,
            recommended_action,
            created_at
        FROM predictions
        WHERE customer_id = %s
        ORDER BY created_at DESC, prediction_id DESC
        """,
        (customer_id,),
    )
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return [_normalize_prediction_row(row) for row in rows]
