from typing import Any


def clamp_probability(value: float) -> float:
    return max(0.0, min(float(value), 1.0))


def normalize_prediction_value(value: Any) -> int:
    return int(float(value))
