import mlflow
import numpy as np
import pandas as pd

from mlflow import MlflowClient

SILVER_TEST_PATH = "/Volumes/workspace/default/data_customers/silver/test"
INFERENCE_OUTPUT_PATH = "/Volumes/workspace/default/data_customers/inference/output/"


def feature_engineering(df):
    df = df.copy()

    tenure_safe = df["Tenure"].clip(lower=1)
    usage_safe = df["Usage Frequency"].clip(lower=1)

    df["Usage_Per_Tenure"] = df["Usage Frequency"] / tenure_safe
    df["Spend_Per_Usage"] = df["Total Spend"] / usage_safe
    df["Spend_Per_Tenure"] = df["Total Spend"] / tenure_safe
    df["Payment_Delay_Ratio"] = df["Payment Delay"] / 30
    df["Engagement_Score"] = (
        df["Usage Frequency"] * df["Total Spend"]
    ) / 1000

    df["Age_group"] = np.where(
        df["Age"] < 30, "Young (<30)",
        np.where(
            df["Age"] < 50, "Adult (30-50)",
            "Senior (50+)"
        )
    )

    return df


model_registry_name = "workspace.default.customer_churn_model"
client = MlflowClient()
versions = client.search_model_versions(f"name='{model_registry_name}'")
latest_version = versions[0].version

model = mlflow.sklearn.load_model(f"models:/{model_registry_name}/{latest_version}")

df_test = spark.read.format("delta").load(SILVER_TEST_PATH).toPandas()
df_features = df_test.drop(columns=["CustomerID"])
df_features = feature_engineering(df_features)

predictions = model.predict(df_features)

results = df_test.copy()
results["Prediction"] = predictions

spark.createDataFrame(results).write.format("delta").mode("overwrite").save(INFERENCE_OUTPUT_PATH)
