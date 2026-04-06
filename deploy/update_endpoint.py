from __future__ import annotations

import json
from typing import Dict, Optional

import requests
from mlflow import MlflowClient


def latest_model_version(client: MlflowClient, model_name: str) -> str:
    versions = client.search_model_versions(f"name='{model_name}'")
    if not versions:
        raise ValueError(f"No registered versions found for model {model_name}")
    return str(max(int(version.version) for version in versions))


def build_endpoint_payload(
    *,
    model_name: str,
    model_version: str,
    served_entity_name: str = "current_model",
    workload_size: str = "Small",
    scale_to_zero_enabled: bool = True,
) -> Dict[str, object]:
    """Create the Databricks serving endpoint update payload."""
    return {
        "served_entities": [
            {
                "name": served_entity_name,
                "entity_name": model_name,
                "entity_version": str(model_version),
                "scale_to_zero_enabled": scale_to_zero_enabled,
                "workload_size": workload_size,
            }
        ]
    }


def update_serving_endpoint(
    *,
    workspace_url: str,
    token: str,
    endpoint_name: str,
    payload: Dict[str, object],
    timeout: int = 60,
) -> Dict[str, object]:
    """Push a serving endpoint config update to Databricks."""
    normalized_url = workspace_url.rstrip("/")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    endpoint_url = f"{normalized_url}/api/2.0/serving-endpoints/{endpoint_name}/config"
    response = requests.put(
        endpoint_url,
        headers=headers,
        data=json.dumps(payload),
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json() if response.content else {"status_code": response.status_code}


def promote_latest_model_to_endpoint(
    *,
    model_name: str,
    endpoint_name: str,
    workspace_url: str,
    token: str,
    model_version: Optional[str] = None,
    served_entity_name: str = "current_model",
    workload_size: str = "Small",
    scale_to_zero_enabled: bool = True,
) -> Dict[str, object]:
    """Point an existing serving endpoint at the latest registered model version."""
    client = MlflowClient()
    version = model_version or latest_model_version(client, model_name)
    payload = build_endpoint_payload(
        model_name=model_name,
        model_version=version,
        served_entity_name=served_entity_name,
        workload_size=workload_size,
        scale_to_zero_enabled=scale_to_zero_enabled,
    )
    return update_serving_endpoint(
        workspace_url=workspace_url,
        token=token,
        endpoint_name=endpoint_name,
        payload=payload,
    )
