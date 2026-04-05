"""
Deployment job.

Updates an existing Databricks Model Serving endpoint so it serves the latest
registered version of the MLflow model produced by the training pipeline.
"""

from __future__ import annotations

import json

import requests
from mlflow import MlflowClient

from pipeline_utils import MLFLOW_MODEL_NAME, SERVING_ENDPOINT_NAME, get_spark


def get_workspace_url(spark) -> str:
    return "https://" + spark.conf.get("spark.databricks.workspaceUrl")


def get_api_token() -> str:
    return (
        dbutils.notebook.entry_point.getDbutils()
        .notebook()
        .getContext()
        .apiToken()
        .get()
    )


def get_latest_model_version(client: MlflowClient, model_name: str) -> str:
    versions = client.search_model_versions(f"name='{model_name}'")
    if not versions:
        raise ValueError(f"No registered versions found for model: {model_name}")
    return str(max(int(version.version) for version in versions))


def build_update_payload(model_name: str, model_version: str) -> dict:
    return {
        "served_entities": [
            {
                "name": "current_model",
                "entity_name": model_name,
                "entity_version": model_version,
                "scale_to_zero_enabled": True,
                "workload_size": "Small",
            }
        ]
    }


def main() -> None:
    spark = get_spark("churn-update-serving-endpoint")
    client = MlflowClient()

    workspace_url = get_workspace_url(spark)
    token = get_api_token()
    latest_version = get_latest_model_version(client, MLFLOW_MODEL_NAME)

    print(
        f"Updating endpoint '{SERVING_ENDPOINT_NAME}' "
        f"to model version {latest_version}"
    )

    endpoint_url = (
        f"{workspace_url}/api/2.0/serving-endpoints/"
        f"{SERVING_ENDPOINT_NAME}/config"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = build_update_payload(MLFLOW_MODEL_NAME, latest_version)

    response = requests.put(
        endpoint_url,
        headers=headers,
        data=json.dumps(payload),
        timeout=60,
    )
    response.raise_for_status()

    print("Serving endpoint updated successfully.")
    print(response.text)


if __name__ == "__main__":
    main()
