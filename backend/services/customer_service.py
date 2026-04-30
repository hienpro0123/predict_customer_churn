import json
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status

from database.redis_client import redis_client
from models.customer import Customer
from models.prediction import Prediction
from schemas.customer import CustomerUpdate
from utils.constants import CONTRACT_LABEL_MAPPING


CUSTOMER_KEY_PREFIX = "customer:"
PREDICTION_KEY_PREFIX = "prediction_history:"
GENDER_MAPPING = {0: "Female", 1: "Male", 2: "Other"}
SUBSCRIPTION_TYPE_MAPPING = {0: "Basic", 1: "Premium", 2: "Standard"}
CONTRACT_LENGTH_MAPPING = {0: "12 months", 1: "1 month", 2: "3 months"}


def map_customer_to_base_inputs(customer: Customer) -> dict[str, Any]:
    return {
        "customer_id": customer.id,
        "age": int(customer.age),
        "gender": customer.gender,
        "tenure": int(customer.tenure),
        "usage_frequency": int(customer.usage_frequency),
        "support_calls": int(customer.support_calls),
        "payment_delay": int(customer.payment_delay),
        "subscription_type": customer.subscription_type,
        "contract_length": customer.contract_length,
        "total_spend": float(customer.total_spend),
        "last_interaction": int(customer.last_interaction),
    }


def get_contract_label(contract_length: str) -> str:
    return CONTRACT_LABEL_MAPPING.get(contract_length, "Monthly")


def _customer_key(customer_id: str) -> str:
    return f"{CUSTOMER_KEY_PREFIX}{customer_id}"


def prediction_history_key(customer_id: str) -> str:
    return f"{PREDICTION_KEY_PREFIX}{customer_id}"


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(float(value))


def _decode_label(value: Any, mapping: dict[int, str]) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip().isdigit():
        return value
    return mapping.get(int(float(value)), str(value))


def _customer_timestamp(value: Any) -> Any:
    return value or datetime.now(timezone.utc)


def _parse_datetime(value: Any) -> Any:
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def _deserialize_customer(raw_customer: str, customer_id: str | None = None) -> Customer:
    try:
        raw_data = json.loads(raw_customer)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Customer data is not valid JSON.") from exc

    if not isinstance(raw_data, dict):
        raise HTTPException(status_code=500, detail="Customer data must be a JSON object.")

    data = {key.strip().lower().replace(" ", "_"): value for key, value in raw_data.items()}
    if customer_id is not None:
        data.setdefault("id", customer_id)
    if "id" not in data and "customer_id" in data:
        data["id"] = data["customer_id"]
    if "id" not in data and "customerid" in data:
        data["id"] = data["customerid"]

    customer = Customer(
        id=data["id"],
        age=_to_int(data.get("age")),
        gender=_decode_label(data.get("gender"), GENDER_MAPPING),
        tenure=_to_int(data.get("tenure")),
        usage_frequency=_to_int(data.get("usage_frequency")),
        support_calls=_to_int(data.get("support_calls")),
        payment_delay=_to_int(data.get("payment_delay")),
        subscription_type=_decode_label(data.get("subscription_type"), SUBSCRIPTION_TYPE_MAPPING),
        contract_length=_decode_label(data.get("contract_length"), CONTRACT_LENGTH_MAPPING),
        total_spend=data.get("total_spend"),
        last_interaction=_to_int(data.get("last_interaction")),
        created_at=_parse_datetime(_customer_timestamp(data.get("created_at"))),
        updated_at=_parse_datetime(_customer_timestamp(data.get("updated_at"))),
    )
    return customer


def _serialize_customer(customer: Customer) -> str:
    return json.dumps(
        {
            "id": customer.id,
            "age": customer.age,
            "gender": customer.gender,
            "tenure": customer.tenure,
            "usage_frequency": customer.usage_frequency,
            "support_calls": customer.support_calls,
            "payment_delay": customer.payment_delay,
            "subscription_type": customer.subscription_type,
            "contract_length": customer.contract_length,
            "total_spend": customer.total_spend,
            "last_interaction": customer.last_interaction,
            "created_at": (
                customer.created_at.isoformat()
                if hasattr(customer.created_at, "isoformat")
                else customer.created_at
            ),
            "updated_at": (
                customer.updated_at.isoformat()
                if hasattr(customer.updated_at, "isoformat")
                else customer.updated_at
            ),
        }
    )


def cache_customer(customer: Customer) -> Customer:
    customer.updated_at = datetime.now(timezone.utc)
    redis_client.set(_customer_key(customer.id), _serialize_customer(customer))
    return customer


def list_customers() -> list[Customer]:
    customers: list[Customer] = []
    for key in redis_client.scan_iter(f"{CUSTOMER_KEY_PREFIX}*"):
        raw_customer = redis_client.get(key)
        if raw_customer is None:
            continue
        customer_id = key.removeprefix(CUSTOMER_KEY_PREFIX)
        customers.append(_deserialize_customer(raw_customer, customer_id))
    return sorted(customers, key=lambda customer: customer.id)


def get_customer_or_404(customer_id: str) -> Customer:
    raw_customer = redis_client.get(_customer_key(customer_id))
    if raw_customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    return _deserialize_customer(raw_customer, customer_id)


def update_customer(customer_id: str, payload: CustomerUpdate) -> Customer:
    customer = get_customer_or_404(customer_id)
    apply_customer_update(customer, payload)
    return cache_customer(customer)


def apply_customer_update(customer: Customer, payload: CustomerUpdate) -> Customer:
    for key, value in payload.model_dump().items():
        setattr(customer, key, value)
    return customer


def _deserialize_prediction(raw_prediction: str) -> Prediction:
    data = json.loads(raw_prediction)
    return Prediction(
        prediction_id=int(data["prediction_id"]),
        customer_id=data["customer_id"],
        predicted_label=int(data["predicted_label"]),
        churn_probability=float(data["churn_probability"]),
        model_input_snapshot=data.get("model_input_snapshot"),
        created_at=_parse_datetime(data.get("created_at")),
    )


def get_prediction_history(customer_id: str) -> list[Prediction]:
    get_customer_or_404(customer_id)
    return sorted(
        (
            _deserialize_prediction(raw_prediction)
            for raw_prediction in redis_client.lrange(prediction_history_key(customer_id), 0, -1)
        ),
        key=lambda prediction: (prediction.created_at, prediction.prediction_id),
        reverse=True,
    )
