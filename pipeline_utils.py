"""
Shared helpers for the churn ETL + ML pipeline.

This module centralizes path management, schema normalization, cleaning,
feature engineering, and feature selection so the Bronze/Silver/Gold and
ML jobs stay small and consistent.
"""

from __future__ import annotations

import os
import re
from typing import Dict, List

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, StringType


RAW_TRAIN_PATH = os.getenv(
    "RAW_TRAIN_PATH",
    "/Volumes/workspace/default/data_customers/customer_churn_dataset-training-master.csv",
)
RAW_TEST_PATH = os.getenv(
    "RAW_TEST_PATH",
    "/Volumes/workspace/default/data_customers/customer_churn_dataset-testing-master.csv",
)
BRONZE_BASE_PATH = os.getenv(
    "BRONZE_BASE_PATH", "/Volumes/workspace/default/churn/bronze"
)
SILVER_BASE_PATH = os.getenv(
    "SILVER_BASE_PATH", "/Volumes/workspace/default/churn/silver"
)
GOLD_BASE_PATH = os.getenv("GOLD_BASE_PATH", "/Volumes/workspace/default/churn/gold")
MLFLOW_MODEL_NAME = os.getenv(
    "MLFLOW_MODEL_NAME", "workspace.default.customer_churn_model"
)
SERVING_ENDPOINT_NAME = os.getenv(
    "SERVING_ENDPOINT_NAME", "customer-churn-endpoint"
)


EXPECTED_COLUMN_ORDER = [
    "age",
    "gender",
    "tenure",
    "usage_frequency",
    "support_calls",
    "payment_delay",
    "subscription_type",
    "contract_length",
    "total_spend",
    "last_interaction",
    "age_group",
    "usage_per_tenure",
    "spend_per_usage",
    "spend_per_tenure",
    "payment_delay_ratio",
    "engagement_score",
    "churn",
]


NUMERIC_COLUMNS = [
    "age",
    "tenure",
    "usage_frequency",
    "support_calls",
    "payment_delay",
    "total_spend",
    "last_interaction",
    "usage_per_tenure",
    "spend_per_usage",
    "spend_per_tenure",
    "payment_delay_ratio",
    "engagement_score",
]


CATEGORICAL_COLUMNS = [
    "gender",
    "subscription_type",
    "contract_length",
    "age_group",
]


def get_spark(app_name: str) -> SparkSession:
    return SparkSession.builder.appName(app_name).getOrCreate()


def layer_path(base_path: str, dataset_name: str) -> str:
    return f"{base_path.rstrip('/')}/{dataset_name}"


def normalize_column_name(column_name: str) -> str:
    normalized = re.sub(r"[^0-9a-zA-Z]+", "_", column_name.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized


def normalize_schema(df: DataFrame) -> DataFrame:
    result = df
    for source_name in df.columns:
        result = result.withColumnRenamed(source_name, normalize_column_name(source_name))
    return result


def clean_customer_data(df: DataFrame) -> DataFrame:
    """
    Apply Silver-layer cleanup only:
    - normalize column names
    - drop notebook-only identifier columns
    - remove nulls and duplicates
    - enforce stable types for downstream ML
    """
    cleaned_df = normalize_schema(df)

    if "customerid" in cleaned_df.columns:
        cleaned_df = cleaned_df.drop("customerid")

    cleaned_df = cleaned_df.dropna().dropDuplicates()

    type_map = {
        "age": IntegerType(),
        "gender": StringType(),
        "tenure": IntegerType(),
        "usage_frequency": IntegerType(),
        "support_calls": IntegerType(),
        "payment_delay": IntegerType(),
        "subscription_type": StringType(),
        "contract_length": StringType(),
        "total_spend": DoubleType(),
        "last_interaction": IntegerType(),
        "churn": IntegerType(),
    }

    for column_name, data_type in type_map.items():
        if column_name in cleaned_df.columns:
            cleaned_df = cleaned_df.withColumn(
                column_name, F.col(column_name).cast(data_type)
            )

    return cleaned_df


def add_feature_columns(df: DataFrame) -> DataFrame:
    """
    Apply shared feature engineering used by Silver, Gold, and inference.
    """
    return (
        df.withColumn(
            "age_group",
            F.when(F.col("age") < 30, F.lit("Young (<30)"))
            .when((F.col("age") >= 30) & (F.col("age") < 50), F.lit("Adult (30-50)"))
            .otherwise(F.lit("Senior (50+)")),
        )
        .withColumn("usage_per_tenure", F.col("usage_frequency") / (F.col("tenure") + 1))
        .withColumn("spend_per_usage", F.col("total_spend") / (F.col("usage_frequency") + 1))
        .withColumn("spend_per_tenure", F.col("total_spend") / (F.col("tenure") + 1))
        .withColumn("payment_delay_ratio", F.col("payment_delay") / F.lit(30.0))
        .withColumn(
            "engagement_score",
            (F.col("usage_frequency") * F.col("total_spend")) / F.lit(1000.0),
        )
    )


def select_gold_features(df: DataFrame) -> DataFrame:
    available_columns = [column for column in EXPECTED_COLUMN_ORDER if column in df.columns]
    return df.select(*available_columns)


def get_training_feature_columns() -> List[str]:
    return [column for column in EXPECTED_COLUMN_ORDER if column != "churn"]


def get_dataset_paths() -> Dict[str, Dict[str, str]]:
    return {
        "bronze": {
            "train": layer_path(BRONZE_BASE_PATH, "train"),
            "test": layer_path(BRONZE_BASE_PATH, "test"),
        },
        "silver": {
            "train": layer_path(SILVER_BASE_PATH, "train"),
            "test": layer_path(SILVER_BASE_PATH, "test"),
        },
        "gold": {
            "train": layer_path(GOLD_BASE_PATH, "train"),
            "test": layer_path(GOLD_BASE_PATH, "test"),
        },
    }
