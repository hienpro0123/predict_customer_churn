from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.customer import Customer
from models.prediction import Prediction
from schemas.customer import CustomerUpdate
from utils.constants import CONTRACT_LABEL_MAPPING



def map_customer_to_base_inputs(customer: Customer) -> dict[str, Any]:
    return {
        "customerid": customer.id,
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


def list_customers(db: Session) -> list[Customer]:
    return list(db.scalars(select(Customer).order_by(Customer.id)).all())


def get_customer_or_404(db: Session, customer_id: str) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    return customer


def update_customer(db: Session, customer_id: str, payload: CustomerUpdate) -> Customer:
    customer = get_customer_or_404(db, customer_id)
    apply_customer_update(customer, payload)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def apply_customer_update(customer: Customer, payload: CustomerUpdate) -> Customer:
    for key, value in payload.model_dump().items():
        setattr(customer, key, value)
    return customer


def get_prediction_history(db: Session, customer_id: str) -> list[Prediction]:
    customer = get_customer_or_404(db, customer_id)
    return sorted(customer.predictions, key=lambda item: (item.created_at, item.prediction_id), reverse=True)
