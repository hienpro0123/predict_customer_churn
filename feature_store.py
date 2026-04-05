"""
Gold layer job.

Selects the final model-ready features from the Silver layer and persists
the curated datasets to Delta for training and inference workloads.
"""

from pipeline_utils import get_dataset_paths, get_spark, select_gold_features


def build_gold_dataset(spark, input_path: str, output_path: str) -> None:
    silver_df = spark.read.format("delta").load(input_path)
    gold_df = select_gold_features(silver_df)
    gold_df.write.format("delta").mode("overwrite").save(output_path)


def main() -> None:
    spark = get_spark("churn-gold-feature-store")
    paths = get_dataset_paths()

    build_gold_dataset(spark, paths["silver"]["train"], paths["gold"]["train"])
    build_gold_dataset(spark, paths["silver"]["test"], paths["gold"]["test"])


if __name__ == "__main__":
    main()
