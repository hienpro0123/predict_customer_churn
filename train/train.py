 import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_validate
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from pyspark.sql import SparkSession
from databricks.feature_engineering import FeatureEngineeringClient, FeatureLookup
from sklearn.model_selection import train_test_split
import logging
import warnings
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("databricks").setLevel(logging.ERROR)

GOLD_BASE_PATH = "/Volumes/workspace/default/data_customers/gold"
GOLD_TRAIN_PATH = f"{GOLD_BASE_PATH}/train"
MODEL_REGISTRY_NAME = "workspace.default.customer_churn_model"
FEATURE_TABLE_NAME = "workspace.default.customer_features"

fs = FeatureEngineeringClient()

def get_spark() -> SparkSession:
    spark = SparkSession.getActiveSession()
    if spark is not None:
        return spark
    return SparkSession.builder.appName("customer-churn-train-model").getOrCreate()


def load_training_data(spark: SparkSession):
    df = spark.read.format("delta").load(GOLD_TRAIN_PATH)
    label_df = df.select("customerid", "churn")
    feature_lookups = [
        FeatureLookup(
            table_name=FEATURE_TABLE_NAME,
            lookup_key="customerid"
        )
    ]

    training_set = fs.create_training_set(
        df=label_df,
        feature_lookups=feature_lookups,
        label="churn"
    )

    return training_set


def build_preprocessor(X_train: pd.DataFrame):
    numeric_features = X_train.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features = X_train.select_dtypes(include=["object"]).columns.tolist()

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

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )
    return preprocessor


def build_candidate_models():
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            C=0.1,
            penalty="l2",
            class_weight="balanced",
            random_state=42,
        ),
        "Naive Bayes": GaussianNB(),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=5,
            min_samples_split=10,
            class_weight="balanced",
            random_state=42,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ),

        "XGBoost": XGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42,
        ),
    }


def train_and_select_model(df_train: pd.DataFrame, df_test: pd.DataFrame):
    X_train = df_train.drop(columns=["churn"])
    y_train = df_train["churn"]

    X_test = df_test.drop(columns=["churn"])
    y_test = df_test["churn"]

    preprocessor = build_preprocessor(X_train)
    raw_models = build_candidate_models()

    results = {}

    for name, model in raw_models.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", model),
            ]
        )

        cv_results = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=5,
            scoring=["accuracy", "recall", "roc_auc"],
        )

        results[name] = {
            "AUC": cv_results["test_roc_auc"].mean(),
            "Recall": cv_results["test_recall"].mean(),
            "Accuracy": cv_results["test_accuracy"].mean(),
        }

    results_df = pd.DataFrame(results).T.sort_values(by="AUC", ascending=False)
    print(results_df)

    best_model_name = results_df.index[0]
    final_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", raw_models[best_model_name]),
        ]
    )

    final_pipeline.fit(X_train, y_train)

    y_test_pred = final_pipeline.predict(X_test)
    print(classification_report(y_test, y_test_pred))

    signature = infer_signature(X_train, final_pipeline.predict(X_train))
    return final_pipeline, best_model_name, results_df, signature

def log_model(final_pipeline, best_model_name, results_df, signature) -> str:
    spark = SparkSession.getActiveSession()
    user = spark.sql("SELECT current_user()").collect()[0][0]
    mlflow.set_experiment(f"/Users/{user}/churn_experiment")
    with mlflow.start_run(run_name=best_model_name, nested=True):
        mlflow.log_param("model_name", best_model_name)

        mlflow.log_metric("accuracy", results_df.loc[best_model_name, "Accuracy"])
        mlflow.log_metric("auc", results_df.loc[best_model_name, "AUC"])
        mlflow.log_metric("recall", results_df.loc[best_model_name, "Recall"])

        mlflow.sklearn.log_model(
            sk_model=final_pipeline,
            artifact_path="model",
            signature=signature,
            registered_model_name=MODEL_REGISTRY_NAME,
        )

    print("Model logged to MLflow!")

    client = MlflowClient()
    versions = client.search_model_versions(f"name='{MODEL_REGISTRY_NAME}'")
    latest_version = versions[0].version
    client.set_registered_model_alias(MODEL_REGISTRY_NAME, "champion", latest_version)

    print(f"Đã dán nhãn @champion cho Version {latest_version} thành công!")
    return str(latest_version)



def main() -> None:
    spark = get_spark()

    training_set = load_training_data(spark)

    df = training_set.load_df().toPandas()

    df_train, df_test = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["churn"]
    )

    final_pipeline, best_model_name, results_df, signature = train_and_select_model(df_train, df_test)

    log_model(final_pipeline, best_model_name, results_df, signature)


if __name__ == "__main__":
    main()
