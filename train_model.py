import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.model_selection import cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from mlflow.models import infer_signature
import mlflow
import mlflow.sklearn
from mlflow import MlflowClient
from sklearn.ensemble import RandomForestClassifier

GOLD_TRAIN_PATH = "/Volumes/workspace/default/data_customers/gold/train"
GOLD_TEST_PATH = "/Volumes/workspace/default/data_customers/gold/test"


df_train = spark.read.format("delta").load(GOLD_TRAIN_PATH).toPandas()
df_test = spark.read.format("delta").load(GOLD_TEST_PATH).toPandas()

X_train = df_train.drop(columns=["Churn"])
y_train = df_train["Churn"]

numeric_features = X_train.select_dtypes(include=["int64", "float64"]).columns.tolist()
categorical_features = X_train.select_dtypes(include=["object"]).columns.tolist()

X_test = df_test.drop(columns=["Churn"])
y_test = df_test["Churn"]

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", RobustScaler())
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ])

raw_models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, C=0.1, penalty="l2", class_weight="balanced", random_state=42),
    "Naive Bayes": GaussianNB(),
    "Decision Tree": DecisionTreeClassifier(max_depth=5, min_samples_split=10, class_weight="balanced", random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=5, class_weight='balanced', random_state=42, n_jobs=-1),
    "XGBoost": XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, random_state=42)
}

results = {}

for name, model in raw_models.items():
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", model)
    ])

    cv_results = cross_validate(pipeline, X_train, y_train, cv=5, scoring=["accuracy", "recall", "roc_auc"])

    results[name] = {
        "AUC": cv_results["test_roc_auc"].mean(),
        "Recall": cv_results["test_recall"].mean(),
        "Accuracy": cv_results["test_accuracy"].mean()
    }

results_df = pd.DataFrame(results).T.sort_values(by="AUC", ascending=False)
print(results_df)

best_model_name = results_df.index[0]
final_pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", raw_models[best_model_name])])

final_pipeline.fit(X_train, y_train)

y_test_pred = final_pipeline.predict(X_test)
print(classification_report(y_test, y_test_pred))

signature = infer_signature(X_train, final_pipeline.predict(X_train))

model_registry_name = "workspace.default.customer_churn_model"
with mlflow.start_run(run_name=best_model_name):
    mlflow.log_param("model_name", best_model_name)

    mlflow.log_metric("accuracy", results_df.loc[best_model_name, "Accuracy"])
    mlflow.log_metric("auc", results_df.loc[best_model_name, "AUC"])
    mlflow.log_metric("recall", results_df.loc[best_model_name, "Recall"])

    mlflow.sklearn.log_model(
        sk_model=final_pipeline,
        artifact_path="model",
        signature=signature,
        registered_model_name=model_registry_name
    )

print("Model logged to MLflow!")

client = MlflowClient()
versions = client.search_model_versions(f"name='{model_registry_name}'")
latest_version = versions[0].version
client.set_registered_model_alias(model_registry_name, "champion", latest_version)

print(f"Đã dán nhãn @champion cho Version {latest_version} thành công!")
