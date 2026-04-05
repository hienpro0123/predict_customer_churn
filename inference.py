"""
Inference job.

Loads the champion model from MLflow, prepares new records with the same
Gold feature logic used during training, and writes predictions to Delta.
"""

from __future__ import annotations

import os

import mlflow.sklearn
from pyspark.sql import functions as F

from pipeline_utils import (
    MLFLOW_MODEL_NAME,
    get_spark,
    get_training_feature_columns,
    normalize_schema,
    add_feature_columns,
)


INFERENCE_INPUT_PATH = os.getenv(
    "INFERENCE_INPUT_PATH", "/Volumes/workspace/default/churn/inference/input"
)
INFERENCE_OUTPUT_PATH = os.getenv(
    "INFERENCE_OUTPUT_PATH", "/Volumes/workspace/default/churn/inference/output"
)


def main() -> None:
    spark = get_spark("churn-model-inference")
    feature_columns = get_training_feature_columns()

    input_df = spark.read.format("delta").load(INFERENCE_INPUT_PATH)
    prepared_df = normalize_schema(input_df)

    if "customerid" in prepared_df.columns:
        prepared_df = prepared_df.drop("customerid")

    prepared_df = prepared_df.dropDuplicates()
    prepared_df = add_feature_columns(prepared_df).select(*feature_columns)

    model = mlflow.sklearn.load_model(f"models:/{MLFLOW_MODEL_NAME}@champion")

    scored_pdf = prepared_df.toPandas()
    scored_pdf["prediction"] = model.predict(scored_pdf)

    if hasattr(model, "predict_proba"):
        scored_pdf["prediction_probability"] = model.predict_proba(scored_pdf)[:, 1]

    prediction_df = spark.createDataFrame(scored_pdf).withColumn(
        "scored_at", F.current_timestamp()
    )
    prediction_df.write.format("delta").mode("overwrite").save(INFERENCE_OUTPUT_PATH)


if __name__ == "__main__":
    main()
