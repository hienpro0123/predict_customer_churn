from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    age: int
    gender: str
    tenure: int
    usage_frequency: int
    support_calls: int
    payment_delay: int
    subscription_type: str
    contract_length: str
    total_spend: float
    last_interaction: int


class CustomerUpdate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
