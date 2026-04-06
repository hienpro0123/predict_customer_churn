from __future__ import annotations

import re
from typing import Dict, Iterable, Tuple

from pyspark.sql import DataFrame, functions as F


REQUIRED_COLUMNS = (
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


def _normalize_column_name(name: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", name.strip().lower())
    cleaned = cleaned.strip("_")
    aliases = {
        "customerid": "customer_id",
    }
    return aliases.get(cleaned, cleaned)


def standardize_columns(df: DataFrame) -> DataFrame:
    """Rename columns to a stable snake_case schema."""
    for current in df.columns:
        renamed = _normalize_column_name(current)
        if renamed != current:
            df = df.withColumnRenamed(current, renamed)
    return df


def validate_required_columns(
    df: DataFrame,
    required_columns: Iterable[str] = REQUIRED_COLUMNS,
) -> None:
    missing = sorted(set(required_columns) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def missing_value_counts(df: DataFrame) -> Dict[str, int]:
    """Return null counts for each column as a plain Python dictionary."""
    row = df.select(
        [
            F.sum(F.when(F.col(column).isNull(), 1).otherwise(0)).alias(column)
            for column in df.columns
        ]
    ).collect()[0]
    return row.asDict()


def clean_customer_data(
    df: DataFrame,
    *,
    drop_nulls: bool = True,
    drop_duplicates: bool = True,
) -> DataFrame:
    """Apply the notebook's cleaning logic with schema normalization."""
    df = standardize_columns(df)
    validate_required_columns(df)

    if drop_nulls:
        df = df.dropna()
    if drop_duplicates:
        df = df.dropDuplicates()

    return df


def clean_train_test(
    train_df: DataFrame,
    test_df: DataFrame,
) -> Tuple[DataFrame, DataFrame]:
    """Clean train and test data and align them to the same column order."""
    clean_train = clean_customer_data(train_df)
    clean_test = clean_customer_data(test_df)

    ordered_columns = [column for column in clean_train.columns if column in clean_test.columns]
    clean_train = clean_train.select(ordered_columns)
    clean_test = clean_test.select(ordered_columns)
    return clean_train, clean_test
