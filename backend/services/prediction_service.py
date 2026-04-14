from typing import Any

from sqlalchemy.orm import Session

from models.customer import Customer
from models.prediction import Prediction
from schemas.prediction import BatchPredictionItem, PredictionResultResponse
from services.analytics_service import get_risk_level, get_top_risk_drivers
from services.databricks_service import predict_batch, predict_single
from services.external_ai_service import generate_retention_insight
from services.feature_service import create_features, validate_inputs


def prepare_single_prediction_features(base_inputs: dict[str, Any]) -> dict[str, Any]:
    features = create_features(base_inputs)
    missing_fields = validate_inputs(features)
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    return features


def run_single_prediction(base_inputs: dict[str, Any]) -> PredictionResultResponse:
    features = prepare_single_prediction_features(base_inputs)
    prediction, probability = predict_single(features)
    insight = generate_retention_insight(base_inputs, probability)
    return PredictionResultResponse(
        prediction=prediction,
        probability=probability,
        risk_level=get_risk_level(probability),
        insight=insight,
        top_risk_drivers=get_top_risk_drivers(base_inputs, top_n=5),
    )


def save_prediction_record(
    db: Session,
    customer: Customer,
    result: PredictionResultResponse,
    base_inputs: dict[str, Any],
) -> Prediction:
    prediction = Prediction(
        customer_id=customer.id,
        predicted_label=result.prediction,
        churn_probability=result.probability,
        model_input_snapshot=base_inputs,
        recommended_action=result.insight.recommended_action,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def run_batch_prediction(parsed_rows: list[dict[str, Any]]) -> tuple[list[BatchPredictionItem], str]:
    features_list = [prepare_single_prediction_features(base_inputs) for base_inputs in parsed_rows]
    results = predict_batch(features_list)
    output_rows: list[dict[str, Any]] = []
    response_rows: list[BatchPredictionItem] = []

    for row_idx, (base_row, prediction_result) in enumerate(zip(parsed_rows, results), start=1):
        prediction, probability = prediction_result
        risk_level = get_risk_level(probability)
        csv_row = {
            "Row": row_idx,
            "Prediction": prediction,
            "Churn Probability (%)": round(probability * 100, 2),
            "Risk Level": risk_level,
            **base_row,
        }
        output_rows.append(csv_row)
        response_rows.append(
            BatchPredictionItem(
                row=row_idx,
                prediction=prediction,
                churn_probability_percent=round(probability * 100, 2),
                risk_level=risk_level,
                inputs=base_row,
            )
        )

    from services.csv_service import build_batch_output_csv

    return response_rows, build_batch_output_csv(output_rows)
