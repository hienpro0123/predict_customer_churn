"""
Bronze layer job.

Reads raw customer churn CSV files and writes them to Delta without applying
business transformations. This preserves the raw source exactly as ingested.
"""

from pipeline_utils import (
    RAW_TEST_PATH,
    RAW_TRAIN_PATH,
    get_dataset_paths,
    get_spark,
)


def write_raw_dataset(spark, input_path: str, output_path: str) -> None:
    raw_df = spark.read.csv(input_path, header=True, inferSchema=True)
    raw_df.write.format("delta").mode("overwrite").save(output_path)


def main() -> None:
    spark = get_spark("churn-bronze-ingestion")
    paths = get_dataset_paths()

    write_raw_dataset(spark, RAW_TRAIN_PATH, paths["bronze"]["train"])
    write_raw_dataset(spark, RAW_TEST_PATH, paths["bronze"]["test"])


if __name__ == "__main__":
    main()
