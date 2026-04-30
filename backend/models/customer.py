from datetime import datetime


class Customer:
    def __init__(
        self,
        *,
        id: str,
        age: int | None = None,
        gender: str | None = None,
        tenure: int | None = None,
        usage_frequency: int | None = None,
        support_calls: int | None = None,
        payment_delay: int | None = None,
        subscription_type: str | None = None,
        contract_length: str | None = None,
        total_spend: float | None = None,
        last_interaction: int | None = None,
        created_at: datetime | str | None = None,
        updated_at: datetime | str | None = None,
    ) -> None:
        self.id = id
        self.age = age
        self.gender = gender
        self.tenure = tenure
        self.usage_frequency = usage_frequency
        self.support_calls = support_calls
        self.payment_delay = payment_delay
        self.subscription_type = subscription_type
        self.contract_length = contract_length
        self.total_spend = total_spend
        self.last_interaction = last_interaction
        self.created_at = created_at
        self.updated_at = updated_at
