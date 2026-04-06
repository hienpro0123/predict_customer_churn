from __future__ import annotations

import argparse
from pyspark.sql import SparkSession

from deploy.update_endpoint import promote_latest_model_to_endpoint
from etl.cleaning import clean_train_test
from etl.feature_engineering import engineer_features_spark
from etl.load_data import ingest_raw_to_bronze, write_dataset
from train.save_model import log_and_register_model
from train.train_model import train_best_model


def get_spark_session(app_name: str) -> SparkSession:
    active = SparkSession.getActiveSession()
    if active is not None:
        return active
    return SparkSession.builder.appName(app_name).getOrCreate()


def run_pipeline(args: argparse.Namespace) -> None:
    spark = get_spark_session(args.app_name)

    raw_train_df, raw_test_df = ingest_raw_to_bronze(
        spark,
        train_path=args.raw_train_path,
        test_path=args.raw_test_path,
        bronze_train_path=args.bronze_train_path,
        bronze_test_path=args.bronze_test_path,
        fmt=args.storage_format,
    )

    clean_train_df, clean_test_df = clean_train_test(raw_train_df, raw_test_df)
    write_dataset(clean_train_df, args.silver_train_path, fmt=args.storage_format)
    write_dataset(clean_test_df, args.silver_test_path, fmt=args.storage_format)

    gold_train_df = engineer_features_spark(clean_train_df)
    gold_test_df = engineer_features_spark(clean_test_df)
    write_dataset(gold_train_df, args.gold_train_path, fmt=args.storage_format)
    write_dataset(gold_test_df, args.gold_test_path, fmt=args.storage_format)

    artifacts = train_best_model(
        clean_train_df.toPandas(),
        clean_test_df.toPandas(),
        target_col=args.target_column,
        id_column=args.id_column,
        cv=args.cv_folds,
        random_state=args.random_state,
    )

    metrics_to_log = {
        "cv_accuracy": float(artifacts.cv_results.loc[artifacts.best_model_name, "accuracy"]),
        "cv_recall": float(artifacts.cv_results.loc[artifacts.best_model_name, "recall"]),
        "cv_auc": float(artifacts.cv_results.loc[artifacts.best_model_name, "auc"]),
        "test_accuracy": float(artifacts.test_metrics["test_accuracy"]),
    }
    if artifacts.test_metrics.get("test_recall") is not None:
        metrics_to_log["test_recall"] = float(artifacts.test_metrics["test_recall"])
    if artifacts.test_metrics.get("test_auc") is not None:
        metrics_to_log["test_auc"] = float(artifacts.test_metrics["test_auc"])

    registration = log_and_register_model(
        model=artifacts.model,
        signature=artifacts.signature,
        input_example=artifacts.X_signature_sample,
        model_name=args.model_name,
        run_name=artifacts.best_model_name,
        params={
            "model_name": artifacts.best_model_name,
            "cv_folds": args.cv_folds,
            "random_state": args.random_state,
        },
        metrics=metrics_to_log,
        alias=args.model_alias,
        experiment_name=args.mlflow_experiment,
        tags={"pipeline": "customer_churn"},
    )

    if args.update_endpoint:
        if not args.workspace_url or not args.databricks_token or not args.endpoint_name:
            raise ValueError(
                "workspace_url, databricks_token, and endpoint_name are required "
                "when --update-endpoint is enabled."
            )
        promote_latest_model_to_endpoint(
            model_name=registration.model_name,
            model_version=registration.model_version,
            endpoint_name=args.endpoint_name,
            workspace_url=args.workspace_url,
            token=args.databricks_token,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Customer churn end-to-end pipeline")
    parser.add_argument("--raw-train-path", required=True)
    parser.add_argument("--raw-test-path", required=True)
    parser.add_argument("--bronze-train-path", required=True)
    parser.add_argument("--bronze-test-path", required=True)
    parser.add_argument("--silver-train-path", required=True)
    parser.add_argument("--silver-test-path", required=True)
    parser.add_argument("--gold-train-path", required=True)
    parser.add_argument("--gold-test-path", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--endpoint-name")
    parser.add_argument("--workspace-url")
    parser.add_argument("--databricks-token")
    parser.add_argument("--mlflow-experiment")
    parser.add_argument("--model-alias", default="champion")
    parser.add_argument("--target-column", default="churn")
    parser.add_argument("--id-column", default="customer_id")
    parser.add_argument("--storage-format", default="delta")
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--app-name", default="customer-churn-pipeline")
    parser.add_argument("--update-endpoint", action="store_true")
    return parser


if __name__ == "__main__":
    parser = build_parser()
    run_pipeline(parser.parse_args())
