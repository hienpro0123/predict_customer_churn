"""
Silver layer job.

Loads Bronze Delta tables, cleans the raw data, normalizes the schema,
and creates reusable engineered columns for downstream analytics and ML.
"""

from pipeline_utils import (
    add_feature_columns,
    clean_customer_data,
    get_dataset_paths,
    get_spark,
)


def transform_dataset(spark, input_path: str, output_path: str) -> None:
    bronze_df = spark.read.format("delta").load(input_path)
    silver_df = clean_customer_data(bronze_df)
    silver_df = add_feature_columns(silver_df)
    silver_df.write.format("delta").mode("overwrite").save(output_path)


def main() -> None:
    spark = get_spark("churn-silver-transform")
    paths = get_dataset_paths()

    transform_dataset(spark, paths["bronze"]["train"], paths["silver"]["train"])
    transform_dataset(spark, paths["bronze"]["test"], paths["silver"]["test"])


if __name__ == "__main__":
    main()
