from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from schemas.customer import CustomerResponse


class BaseInputSchema(BaseModel):
    age: int = Field(validation_alias="Age", serialization_alias="Age")
    gender: str = Field(validation_alias="Gender", serialization_alias="Gender")
    tenure: int = Field(validation_alias="Tenure", serialization_alias="Tenure")
    usage_frequency: int = Field(
        validation_alias="Usage Frequency",
        serialization_alias="Usage Frequency",
    )
    support_calls: int = Field(
        validation_alias="Support Calls",
        serialization_alias="Support Calls",
    )
    payment_delay: int = Field(
        validation_alias="Payment Delay",
        serialization_alias="Payment Delay",
    )
    subscription_type: str = Field(
        validation_alias="Subscription Type",
        serialization_alias="Subscription Type",
    )
    contract_length: str = Field(
        validation_alias="Contract Length",
        serialization_alias="Contract Length",
    )
    total_spend: float = Field(
        validation_alias="Total Spend",
        serialization_alias="Total Spend",
    )
    last_interaction: int = Field(
        validation_alias="Last Interaction",
        serialization_alias="Last Interaction",
    )

    model_config = ConfigDict(populate_by_name=True)

    def to_base_inputs(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True)


class PredictionRequest(BaseModel):
    inputs: BaseInputSchema


class InsightResponse(BaseModel):
    recommended_action: str
    insight_source: str
    insight_error: str = ""


class RiskDriver(BaseModel):
    label: str
    score: float
    reason: str


class PredictionResultResponse(BaseModel):
    prediction: int
    probability: float
    risk_level: str
    insight: InsightResponse
    top_risk_drivers: list[RiskDriver]


class StoredPredictionResponse(BaseModel):
    prediction_id: int
    customer_id: str
    predicted_label: int
    churn_probability: float
    model_input_snapshot: dict[str, Any] | None = None
    recommended_action: str | None = None
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
