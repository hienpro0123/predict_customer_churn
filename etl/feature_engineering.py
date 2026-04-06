from __future__ import annotations

from typing import Iterable

import pandas as pd
from pyspark.sql import DataFrame, functions as F


BASE_COLUMNS = (
    "customer_id",
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
    "churn",
)

ENGINEERED_COLUMNS = (
    "age_group",
    "usage_per_tenure",
    "spend_per_usage",
    "spend_per_tenure",
    "payment_delay_ratio",
    "engagement_score",
)


def _age_group_expr(age_col: F.Column) -> F.Column:
    return (
        F.when(age_col < 30, F.lit("Young (<30)"))
        .when(age_col < 50, F.lit("Adult (30-50)"))
        .otherwise(F.lit("Senior (50+)"))
    )


def engineer_features_spark(df: DataFrame) -> DataFrame:
    """Apply notebook feature engineering with a stable snake_case schema."""
    return (
        df.withColumn("age_group", _age_group_expr(F.col("age")))
        .withColumn("usage_per_tenure", F.col("usage_frequency") / (F.col("tenure") + F.lit(1.0)))
        .withColumn(
            "spend_per_usage",
            F.col("total_spend") / (F.col("usage_frequency") + F.lit(1.0)),
        )
        .withColumn("spend_per_tenure", F.col("total_spend") / (F.col("tenure") + F.lit(1.0)))
        .withColumn("payment_delay_ratio", F.col("payment_delay") / F.lit(30.0))
        .withColumn(
            "engagement_score",
            (F.col("usage_frequency") * F.col("total_spend")) / F.lit(1000.0),
        )
    )


def engineer_features_pandas(df: pd.DataFrame) -> pd.DataFrame:
    """Pandas equivalent of the Spark feature engineering step."""
    required = set(BASE_COLUMNS) - {"churn"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing columns for feature engineering: {missing}")

    frame = df.copy()
    frame["age_group"] = pd.Series(index=frame.index, dtype="object")
    frame.loc[frame["age"] < 30, "age_group"] = "Young (<30)"
    frame.loc[(frame["age"] >= 30) & (frame["age"] < 50), "age_group"] = "Adult (30-50)"
    frame.loc[frame["age"] >= 50, "age_group"] = "Senior (50+)"

    frame["usage_per_tenure"] = frame["usage_frequency"] / (frame["tenure"] + 1.0)
    frame["spend_per_usage"] = frame["total_spend"] / (frame["usage_frequency"] + 1.0)
    frame["spend_per_tenure"] = frame["total_spend"] / (frame["tenure"] + 1.0)
    frame["payment_delay_ratio"] = frame["payment_delay"] / 30.0
    frame["engagement_score"] = (frame["usage_frequency"] * frame["total_spend"]) / 1000.0
    return frame


def feature_columns(include_label: bool = True) -> Iterable[str]:
    """Return the base and engineered columns in their expected order."""
    columns = [column for column in BASE_COLUMNS if include_label or column != "churn"]
    return columns + list(ENGINEERED_COLUMNS)
