from typing import Any

from utils.constants import CONTRACT_RISK_MAP, RISK_THRESHOLDS, SUBSCRIPTION_RISK_MAP


def get_risk_level(probability: float) -> str:
    if probability >= RISK_THRESHOLDS["high"]:
        return "HIGH"
    if probability >= RISK_THRESHOLDS["low"]:
        return "MEDIUM"
    return "LOW"


def get_top_risk_drivers(base_inputs: dict[str, Any], top_n: int = 5) -> list[dict[str, Any]]:
    payment_delay = float(base_inputs["Payment Delay"])
    support_calls = float(base_inputs["Support Calls"])
    last_interaction = float(base_inputs["Last Interaction"])
    usage = float(base_inputs["Usage Frequency"])
    tenure = float(base_inputs["Tenure"])
    total_spend = float(base_inputs["Total Spend"])
    subscription = str(base_inputs["Subscription Type"])
    contract = str(base_inputs["Contract Length"])

    candidates = [
        {
            "label": "Payment Delay",
            "score": min(payment_delay / 30.0, 1.0),
            "reason": f"{int(payment_delay)} days delayed payment behavior.",
        },
        {
            "label": "Support Calls",
            "score": min(support_calls / 20.0, 1.0),
            "reason": f"{int(support_calls)} support interactions in this period.",
        },
        {
            "label": "Last Interaction",
            "score": min(last_interaction / 30.0, 1.0),
            "reason": f"{int(last_interaction)} days since most recent interaction.",
        },
        {
            "label": "Usage Frequency",
            "score": max(0.0, 1.0 - min(usage / 30.0, 1.0)),
            "reason": f"Usage level is {int(usage)} sessions.",
        },
        {
            "label": "Tenure",
            "score": max(0.0, 1.0 - min(tenure / 60.0, 1.0)),
            "reason": f"Tenure is {int(tenure)} months.",
        },
        {
            "label": "Total Spend",
            "score": max(0.0, 1.0 - min(total_spend / 10000.0, 1.0)),
            "reason": f"Total spend is {total_spend:,.0f}.",
        },
        {
            "label": "Subscription Type",
            "score": SUBSCRIPTION_RISK_MAP.get(subscription, 0.5),
            "reason": f"Current plan is {subscription}.",
        },
        {
            "label": "Contract Length",
            "score": CONTRACT_RISK_MAP.get(contract, 0.5),
            "reason": f"Contract is {contract}.",
        },
    ]
    return sorted(candidates, key=lambda item: item["score"], reverse=True)[:top_n]
