from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import mlflow
import mlflow.sklearn
from mlflow import MlflowClient


@dataclass
class ModelRegistrationResult:
    run_id: str
    model_name: str
    model_version: str
    alias: Optional[str]


def _latest_model_version(client: MlflowClient, model_name: str) -> str:
    versions = client.search_model_versions(f"name='{model_name}'")
    if not versions:
        raise ValueError(f"No registered model versions found for {model_name}")
    return str(max(int(version.version) for version in versions))


def log_and_register_model(
    *,
    model,
    signature,
    input_example,
    model_name: str,
    run_name: str,
    params: Dict[str, object],
    metrics: Dict[str, float],
    alias: Optional[str] = "champion",
    experiment_name: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
) -> ModelRegistrationResult:
    """Log a model to MLflow, register it, and optionally assign an alias."""
    if experiment_name:
        mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        if tags:
            mlflow.set_tags(tags)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=input_example,
            registered_model_name=model_name,
        )

    client = MlflowClient()
    version = _latest_model_version(client, model_name)
    if alias:
        client.set_registered_model_alias(model_name, alias, version)

    return ModelRegistrationResult(
        run_id=run.info.run_id,
        model_name=model_name,
        model_version=version,
        alias=alias,
    )
