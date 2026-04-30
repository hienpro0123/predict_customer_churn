from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from schemas.customer import CustomerResponse


class BaseInputSchema(BaseModel):
    customer_id: int = Field(
        default=0,
        validation_alias=AliasChoices("customer_id", "customerid", "CustomerID", "Customer Id", "Customer ID"),
    )
    age: int = Field(validation_alias=AliasChoices("age", "Age"))
    gender: str = Field(validation_alias=AliasChoices("gender", "Gender"))
    tenure: int = Field(validation_alias=AliasChoices("tenure", "Tenure"))
    usage_frequency: int = Field(
        validation_alias=AliasChoices("usage_frequency", "Usage Frequency"),
    )
    support_calls: int = Field(
        validation_alias=AliasChoices("support_calls", "Support Calls"),
    )
    payment_delay: int = Field(
        validation_alias=AliasChoices("payment_delay", "Payment Delay"),
    )
    subscription_type: str = Field(
        validation_alias=AliasChoices("subscription_type", "Subscription Type"),
    )
    contract_length: str = Field(
        validation_alias=AliasChoices("contract_length", "Contract Length"),
    )
    total_spend: float = Field(
        validation_alias=AliasChoices("total_spend", "Total Spend"),
    )
    last_interaction: int = Field(
        validation_alias=AliasChoices("last_interaction", "Last Interaction"),
    )

    model_config = ConfigDict(populate_by_name=True)

    def to_base_inputs(self) -> dict[str, Any]:
        return self.model_dump()


class PredictionRequest(BaseModel):
    inputs: BaseInputSchema


class RiskDriver(BaseModel):
    label: str
    score: float
    reason: str


class PredictionResultResponse(BaseModel):
    prediction: int
    probability: float
    risk_level: str
    top_risk_drivers: list[RiskDriver]


class StoredPredictionResponse(BaseModel):
    prediction_id: int
    customer_id: str
    predicted_label: int
    churn_probability: float
    model_input_snapshot: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerPredictionRequest(BaseModel):
    inputs: BaseInputSchema


class CustomerPredictionResponse(BaseModel):
    customer: CustomerResponse
    result: PredictionResultResponse
    history: list[StoredPredictionResponse]


class BatchPredictionItem(BaseModel):
    row: int
    prediction: int
    churn_probability_percent: float
    risk_level: str
    inputs: dict[str, Any]


class BatchPredictionResponse(BaseModel):
    count: int
    rows: list[BatchPredictionItem]
    csv_content: str
