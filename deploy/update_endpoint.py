import json
import os
import requests
from mlflow import MlflowClient
from pyspark.sql import SparkSession

# 1. Khởi tạo
client = MlflowClient()
workspace_url = "https://" + spark.conf.get("spark.databricks.workspaceUrl") 
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

model_name = "workspace.default.customer_churn_model"
endpoint_name = "customer-churn-endpoint" # Tên endpoint hiện tại của bạn

# 2. Lấy số Version mới nhất vừa train xong
versions = client.search_model_versions(f"name='{model_name}'")
latest_version = versions[0].version
print(f"🔄 Đang tiến hành cập nhật Endpoint lên Version mới nhất: {latest_version}")

# 3. Cấu hình Payload 
update_payload = {
  "served_entities": [
    {
      "name": "current_model",
      "entity_name": model_name,
      "entity_version": str(latest_version), # Ép kiểu string cho chắc
      "scale_to_zero_enabled": True,
      "workload_size": "Small"
    }
  ]
}

# 4. Gửi lệnh UPDATE
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
endpoint_url = f"{workspace_url}/api/2.0/serving-endpoints/{endpoint_name}/config"
response = requests.put(endpoint_url, headers=headers, data=json.dumps(update_payload))
