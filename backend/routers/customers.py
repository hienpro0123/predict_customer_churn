from fastapi import APIRouter, HTTPException

from schemas.customer import CustomerResponse, CustomerUpdate
from schemas.prediction import CustomerPredictionRequest, CustomerPredictionResponse, StoredPredictionResponse
from services.customer_service import (
    apply_customer_update,
    cache_customer,
    get_customer_or_404,
    get_prediction_history,
    list_customers,
    update_customer,
)
from services.prediction_service import run_single_prediction, save_prediction_record


router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerResponse])
def get_customers() -> list[CustomerResponse]:
    return list_customers()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str) -> CustomerResponse:
    return get_customer_or_404(customer_id.upper())


@router.put("/{customer_id}", response_model=CustomerResponse)
def put_customer(customer_id: str, payload: CustomerUpdate) -> CustomerResponse:
    return update_customer(customer_id.upper(), payload)


@router.get("/{customer_id}/predictions", response_model=list[StoredPredictionResponse])
def get_customer_predictions(customer_id: str) -> list[StoredPredictionResponse]:
    return get_prediction_history(customer_id.upper())


@router.post("/{customer_id}/predict", response_model=CustomerPredictionResponse)
def predict_for_customer(
    customer_id: str,
    payload: CustomerPredictionRequest,
) -> CustomerPredictionResponse:
    customer = get_customer_or_404(customer_id.upper())
    customer = apply_customer_update(
        customer,
        CustomerUpdate(
            age=payload.inputs.age,
            gender=payload.inputs.gender,
            tenure=payload.inputs.tenure,
            usage_frequency=payload.inputs.usage_frequency,
            support_calls=payload.inputs.support_calls,
            payment_delay=payload.inputs.payment_delay,
            subscription_type=payload.inputs.subscription_type,
            contract_length=payload.inputs.contract_length,
            total_spend=payload.inputs.total_spend,
            last_interaction=payload.inputs.last_interaction,
        ),
    )
    base_inputs = payload.inputs.to_base_inputs()
    try:
        result = run_single_prediction(base_inputs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    cache_customer(customer)
    save_prediction_record(customer, result, base_inputs, commit=False)
    history = get_prediction_history(customer.id)
    return CustomerPredictionResponse(
        customer=CustomerResponse.model_validate(customer),
        result=result,
        history=history,
    )
