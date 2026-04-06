from __future__ import annotations

from typing import Dict, Iterable, Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler


def split_features_and_target(
    df: pd.DataFrame,
    *,
    target_col: str = "churn",
    drop_columns: Iterable[str] = ("customer_id",),
) -> Tuple[pd.DataFrame, pd.Series]:
    """Split a DataFrame into features and target."""
    features = df.drop(columns=[target_col, *list(drop_columns)], errors="ignore")
    target = df[target_col]
    return features, target


def build_preprocessor(
    X: pd.DataFrame,
) -> Tuple[ColumnTransformer, list[str], list[str]]:
    """Build a preprocessing transformer from the current schema."""
    numeric_features = X.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", RobustScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )
    return preprocessor, numeric_features, categorical_features


def evaluate_candidate_models(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    candidate_models: Dict[str, object],
    feature_transformer,
    preprocessor: ColumnTransformer,
    cv: int = 5,
    random_state: int = 42,
) -> pd.DataFrame:
    """Cross-validate each candidate model and return a ranked score table."""
    splitter = StratifiedKFold(n_splits=cv, shuffle=True, random_state=random_state)
    results = {}

    for name, model in candidate_models.items():
        pipeline = Pipeline(
            steps=[
                ("feature_engineering", feature_transformer),
                ("preprocessor", preprocessor),
                ("classifier", model),
            ]
        )
        scores = cross_validate(
            pipeline,
            X,
            y,
            cv=splitter,
            scoring=["accuracy", "recall", "roc_auc"],
            error_score="raise",
        )
        results[name] = {
            "accuracy": float(scores["test_accuracy"].mean()),
            "recall": float(scores["test_recall"].mean()),
            "auc": float(scores["test_roc_auc"].mean()),
        }

    return pd.DataFrame(results).T.sort_values(by="auc", ascending=False)


def evaluate_holdout_model(
    fitted_pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> Dict[str, object]:
    """Evaluate a fitted model on the held-out test set."""
    predictions = fitted_pipeline.predict(X_test)
    report = classification_report(y_test, predictions, output_dict=True)

    metrics: Dict[str, object] = {
        "classification_report": report,
        "test_accuracy": float(report["accuracy"]),
        "test_recall": float(report["1"]["recall"]) if "1" in report else None,
    }

    if hasattr(fitted_pipeline, "predict_proba"):
        probabilities = fitted_pipeline.predict_proba(X_test)[:, 1]
        metrics["test_auc"] = float(roc_auc_score(y_test, probabilities))

    return metrics
