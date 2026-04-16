from fastapi import APIRouter, File, HTTPException, UploadFile

from schemas.prediction import BatchPredictionResponse, PredictionRequest, PredictionResultResponse
from services.csv_service import parse_batch_csv
from services.prediction_service import run_batch_prediction, run_single_prediction


router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/single", response_model=PredictionResultResponse)
def predict_single_endpoint(payload: PredictionRequest) -> PredictionResultResponse:
    try:
        return run_single_prediction(payload.inputs.to_base_inputs())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch_endpoint(file: UploadFile = File(...)) -> BatchPredictionResponse:
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Batch prediction requires a CSV file.")
    rows, errors = parse_batch_csv(await file.read())
    if errors:
        raise HTTPException(status_code=400, detail={"message": "CSV validation failed.", "errors": errors})
    try:
        response_rows, csv_content = run_batch_prediction(rows)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BatchPredictionResponse(count=len(response_rows), rows=response_rows, csv_content=csv_content)
