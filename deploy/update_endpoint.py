import json
import os

import requests
from mlflow import MlflowClient
from pyspark.sql import SparkSession


MODEL_NAME = "workspace.default.customer_churn_model"
ENDPOINT_NAME = "customer-churn-endpoint"


def get_spark() -> SparkSession:
    spark = SparkSession.getActiveSession()
    if spark is not None:
        return spark
    return SparkSession.builder.appName("customer-churn-update-endpoint").getOrCreate()


def get_workspace_url(spark: SparkSession) -> str:
    return "https://" + spark.conf.get("spark.databricks.workspaceUrl")


def get_token() -> str | None:
    return os.environ.get("DATABRICKS_TOKEN")


def build_update_payload(model_version: str):
    return {
        "served_entities": [
            {
                "name": "current_model",
                "entity_name": MODEL_NAME,
                "entity_version": str(model_version),
                "scale_to_zero_enabled": True,
                "workload_size": "Small",
            }
        ]
    }


def update_endpoint(mock: bool = False) -> None:
    spark = get_spark()
    client = MlflowClient()

    versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    latest_version = versions[0].version
    print(f"Đang tiến hành cập nhật Endpoint lên Version mới nhất: {latest_version}")

    update_payload = build_update_payload(latest_version)

    if mock:
        print("Mock update payload:")
        print(json.dumps(update_payload, indent=2))
        return

    token = get_token()
    if not token:
        print("DATABRICKS_TOKEN not found. Running in mock mode.")
        print(json.dumps(update_payload, indent=2))
        return

    workspace_url = get_workspace_url(spark)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    endpoint_url = f"{workspace_url}/api/2.0/serving-endpoints/{ENDPOINT_NAME}/config"
    response = requests.put(endpoint_url, headers=headers, data=json.dumps(update_payload), timeout=60)

    print(response.status_code)
    print(response.text)


def main() -> None:
    update_endpoint(mock=False)


if __name__ == "__main__":
    main()
