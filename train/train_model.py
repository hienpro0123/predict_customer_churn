from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd
from mlflow.models import infer_signature
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import FunctionTransformer, Pipeline
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from etl.feature_engineering import engineer_features_pandas
from train.evaluate import (
    build_preprocessor,
    evaluate_candidate_models,
    evaluate_holdout_model,
    split_features_and_target,
)


@dataclass
class TrainingArtifacts:
    best_model_name: str
    model: Pipeline
    cv_results: pd.DataFrame
    test_metrics: Dict[str, object]
    X_signature_sample: pd.DataFrame
    signature: object


def build_model_candidates(random_state: int = 42) -> Dict[str, object]:
    """Return the candidate models used during model selection."""
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            C=0.1,
            penalty="l2",
            class_weight="balanced",
            random_state=random_state,
        ),
        "Naive Bayes": GaussianNB(),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=5,
            min_samples_split=10,
            class_weight="balanced",
            random_state=random_state,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_split=10,
            class_weight="balanced",
            n_jobs=-1,
            random_state=random_state,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=random_state,
        ),
    }


def train_best_model(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    *,
    target_col: str = "churn",
    id_column: str = "customer_id",
    cv: int = 5,
    random_state: int = 42,
) -> TrainingArtifacts:
    """Train the best-scoring model using the cleaned raw schema."""
    X_train, y_train = split_features_and_target(
        train_df,
        target_col=target_col,
        drop_columns=(id_column,),
    )
    X_test, y_test = split_features_and_target(
        test_df,
        target_col=target_col,
        drop_columns=(id_column,),
    )

    feature_transformer = FunctionTransformer(engineer_features_pandas, validate=False)
    transformed_sample = engineer_features_pandas(X_train)
    preprocessor, _, _ = build_preprocessor(transformed_sample)

    candidate_models = build_model_candidates(random_state=random_state)
    cv_results = evaluate_candidate_models(
        X_train,
        y_train,
        candidate_models=candidate_models,
        feature_transformer=feature_transformer,
        preprocessor=preprocessor,
        cv=cv,
        random_state=random_state,
    )

    best_model_name = str(cv_results.index[0])
    best_model = candidate_models[best_model_name]
    pipeline = Pipeline(
        steps=[
            ("feature_engineering", feature_transformer),
            ("preprocessor", preprocessor),
            ("classifier", best_model),
        ]
    )
    pipeline.fit(X_train, y_train)

    test_metrics = evaluate_holdout_model(pipeline, X_test, y_test)
    signature_sample = X_train.head(min(len(X_train), 100)).copy()
    signature = infer_signature(signature_sample, pipeline.predict(signature_sample))

    return TrainingArtifacts(
        best_model_name=best_model_name,
        model=pipeline,
        cv_results=cv_results,
        test_metrics=test_metrics,
        X_signature_sample=signature_sample,
        signature=signature,
    )
