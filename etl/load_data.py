from __future__ import annotations

from typing import Tuple

from pyspark.sql import DataFrame, SparkSession


def load_csv_dataset(
    spark: SparkSession,
    path: str,
    *,
    header: bool = True,
    infer_schema: bool = True,
) -> DataFrame:
    """Load a raw CSV dataset into a Spark DataFrame."""
    return spark.read.csv(path, header=header, inferSchema=infer_schema)


def load_raw_train_test(
    spark: SparkSession,
    train_path: str,
    test_path: str,
) -> Tuple[DataFrame, DataFrame]:
    """Load the raw training and testing datasets."""
    return (
        load_csv_dataset(spark, train_path),
        load_csv_dataset(spark, test_path),
    )


def write_dataset(
    df: DataFrame,
    path: str,
    *,
    fmt: str = "delta",
    mode: str = "overwrite",
) -> None:
    """Persist a DataFrame in the configured storage format."""
    df.write.format(fmt).mode(mode).save(path)


def ingest_raw_to_bronze(
    spark: SparkSession,
    train_path: str,
    test_path: str,
    bronze_train_path: str,
    bronze_test_path: str,
    *,
    fmt: str = "delta",
) -> Tuple[DataFrame, DataFrame]:
    """Load raw CSV data and persist it as the bronze layer."""
    train_df, test_df = load_raw_train_test(spark, train_path, test_path)
    write_dataset(train_df, bronze_train_path, fmt=fmt)
    write_dataset(test_df, bronze_test_path, fmt=fmt)
    return train_df, test_df
