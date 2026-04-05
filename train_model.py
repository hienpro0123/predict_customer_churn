"""
Model training job.

Loads Gold Delta datasets, trains a scikit-learn classifier on the curated
features, evaluates candidate models, and logs the best model to MLflow.
"""

from __future__ import annotations

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, recall_score, roc_auc_score
from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.tree import DecisionTreeClassifier

from pipeline_utils import (
    CATEGORICAL_COLUMNS,
    MLFLOW_MODEL_NAME,
    NUMERIC_COLUMNS,
    get_dataset_paths,
    get_spark,
    get_training_feature_columns,
)


def build_preprocessor() -> ColumnTransformer:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", RobustScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_COLUMNS),
            ("cat", categorical_transformer, CATEGORICAL_COLUMNS),
        ]
    )


def get_candidate_models() -> dict[str, object]:
    return {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            C=0.1,
            penalty="l2",
            class_weight="balanced",
            random_state=42,
        ),
        "decision_tree": DecisionTreeClassifier(
            max_depth=5,
            min_samples_split=10,
            class_weight="balanced",
            random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_split=10,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }


def evaluate_models(X_train: pd.DataFrame, y_train: pd.Series) -> pd.DataFrame:
    preprocessor = build_preprocessor()
    results = []

    for model_name, model in get_candidate_models().items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", model),
            ]
        )
        cv_scores = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=5,
            scoring=["accuracy", "recall", "roc_auc"],
            n_jobs=None,
        )
        results.append(
            {
                "model_name": model_name,
                "accuracy": cv_scores["test_accuracy"].mean(),
                "recall": cv_scores["test_recall"].mean(),
                "roc_auc": cv_scores["test_roc_auc"].mean(),
            }
        )

    return pd.DataFrame(results).sort_values("roc_auc", ascending=False)


def load_gold_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    spark = get_spark("churn-model-training")
    paths = get_dataset_paths()
    feature_columns = get_training_feature_columns()

    train_df = spark.read.format("delta").load(paths["gold"]["train"]).select(
        *(feature_columns + ["churn"])
    )
    test_df = spark.read.format("delta").load(paths["gold"]["test"]).select(
        *(feature_columns + ["churn"])
    )

    return train_df.toPandas(), test_df.toPandas()


def main() -> None:
    train_pdf, test_pdf = load_gold_datasets()

    X_train = train_pdf.drop(columns=["churn"])
    y_train = train_pdf["churn"]
    X_test = test_pdf.drop(columns=["churn"])
    y_test = test_pdf["churn"]

    evaluation_df = evaluate_models(X_train, y_train)
    best_model_name = evaluation_df.iloc[0]["model_name"]
    best_model = get_candidate_models()[best_model_name]

    final_pipeline = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("classifier", best_model),
        ]
    )
    final_pipeline.fit(X_train, y_train)

    y_pred = final_pipeline.predict(X_test)
    y_proba = final_pipeline.predict_proba(X_test)[:, 1]

    test_accuracy = accuracy_score(y_test, y_pred)
    test_recall = recall_score(y_test, y_pred)
    test_roc_auc = roc_auc_score(y_test, y_proba)

    print(evaluation_df.to_string(index=False))
    print(classification_report(y_test, y_pred))

    signature = infer_signature(X_train, final_pipeline.predict(X_train))

    with mlflow.start_run(run_name=best_model_name):
        mlflow.log_param("model_name", best_model_name)
        mlflow.log_metric("cv_accuracy", float(evaluation_df.iloc[0]["accuracy"]))
        mlflow.log_metric("cv_recall", float(evaluation_df.iloc[0]["recall"]))
        mlflow.log_metric("cv_roc_auc", float(evaluation_df.iloc[0]["roc_auc"]))
        mlflow.log_metric("test_accuracy", test_accuracy)
        mlflow.log_metric("test_recall", test_recall)
        mlflow.log_metric("test_roc_auc", test_roc_auc)

        mlflow.sklearn.log_model(
            sk_model=final_pipeline,
            artifact_path="model",
            signature=signature,
            registered_model_name=MLFLOW_MODEL_NAME,
        )

    client = MlflowClient()
    versions = client.search_model_versions(f"name='{MLFLOW_MODEL_NAME}'")
    latest_version = max(int(version.version) for version in versions)
    client.set_registered_model_alias(
        MLFLOW_MODEL_NAME, "champion", str(latest_version)
    )

    print(f"Registered model: {MLFLOW_MODEL_NAME}")
    print(f"Champion alias updated to version: {latest_version}")


if __name__ == "__main__":
    main()
