from datetime import datetime
from typing import Any


class Prediction:
    def __init__(
        self,
        *,
        prediction_id: int,
        customer_id: str,
        predicted_label: int,
        churn_probability: float,
        model_input_snapshot: dict[str, Any] | None = None,
        created_at: datetime | str | None = None,
    ) -> None:
        self.prediction_id = prediction_id
        self.customer_id = customer_id
        self.predicted_label = predicted_label
        self.churn_probability = churn_probability
        self.model_input_snapshot = model_input_snapshot
        self.created_at = created_at
