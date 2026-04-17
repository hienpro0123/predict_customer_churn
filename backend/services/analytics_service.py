from typing import Any

from utils.constants import CONTRACT_RISK_MAP, RISK_THRESHOLDS, SUBSCRIPTION_RISK_MAP


def normalize(base_inputs: dict[str, Any]) -> dict[str, Any]:
    return {k.strip().lower().replace(" ", "_"): v for k, v in base_inputs.items()}


def format_feature_label(label: str) -> str:
    return " ".join(part.capitalize() for part in label.split("_"))


def get_risk_level(probability: float) -> str:
    if probability >= RISK_THRESHOLDS["high"]:
        return "HIGH"
    if probability >= RISK_THRESHOLDS["low"]:
        return "MEDIUM"
    return "LOW"


def get_top_risk_drivers(base_inputs: dict[str, Any], top_n: int = 5) -> list[dict[str, Any]]:
    x = normalize(base_inputs)

    payment_delay = float(x["payment_delay"])
    support_calls = float(x["support_calls"])
    last_interaction = float(x["last_interaction"])
    usage = float(x["usage_frequency"])
    tenure = float(x["tenure"])
    total_spend = float(x["total_spend"])
    subscription = str(x["subscription_type"])
    contract = str(x["contract_length"])

    candidates = [
        {
            "label": format_feature_label("payment_delay"),
            "score": min(payment_delay / 30.0, 1.0),
            "reason": f"{int(payment_delay)} days delayed payment behavior.",
        },
        {
            "label": format_feature_label("support_calls"),
            "score": min(support_calls / 20.0, 1.0),
            "reason": f"{int(support_calls)} support interactions in this period.",
        },
        {
            "label": format_feature_label("last_interaction"),
            "score": min(last_interaction / 30.0, 1.0),
            "reason": f"{int(last_interaction)} days since most recent interaction.",
        },
        {
            "label": format_feature_label("usage_frequency"),
            "score": max(0.0, 1.0 - min(usage / 30.0, 1.0)),
            "reason": f"Usage level is {int(usage)} sessions.",
        },
        {
            "label": format_feature_label("tenure"),
            "score": max(0.0, 1.0 - min(tenure / 60.0, 1.0)),
            "reason": f"Tenure is {int(tenure)} months.",
        },
        {
            "label": format_feature_label("total_spend"),
            "score": max(0.0, 1.0 - min(total_spend / 10000.0, 1.0)),
            "reason": f"Total spend is {total_spend:,.0f}.",
        },
        {
            "label": format_feature_label("subscription_type"),
            "score": SUBSCRIPTION_RISK_MAP.get(subscription, 0.5),
            "reason": f"Current plan is {subscription}.",
        },
        {
            "label": format_feature_label("contract_length"),
            "score": CONTRACT_RISK_MAP.get(contract, 0.5),
            "reason": f"Contract is {contract}.",
        },
    ]

    return sorted(candidates, key=lambda item: item["score"], reverse=True)[:top_n]
