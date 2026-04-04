import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import cross_validate
import pandas as pd
from sklearn.metrics import classification_report
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from etl import feature_engineering
from pyspark.sql.functions import col, when

def get_models():
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            C=0.1,
            penalty='l2',
            class_weight='balanced',
            random_state=42
        ),

        "Naive Bayes": GaussianNB(),

        "Decision Tree": DecisionTreeClassifier(
            max_depth=5,
            min_samples_split=10,
            class_weight='balanced',
            random_state=42
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
            random_state=42
        )
    }

def build_preprocessor(X_train):
    numeric_features = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X_train.select_dtypes(include=['object']).columns.tolist()

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', RobustScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    return preprocessor

def train_and_evaluate(X_train, y_train, preprocessor):
    models = get_models()
    results = {}

    for name, model in models.items():
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])

        cv_results = cross_validate(
            pipeline, X_train, y_train,
            cv=5,
            scoring=['accuracy', 'recall', 'roc_auc']
        )

        results[name] = {
            'AUC': cv_results['test_roc_auc'].mean(),
            'Recall': cv_results['test_recall'].mean(),
            'Accuracy': cv_results['test_accuracy'].mean()
        }

    results_df = pd.DataFrame(results).T.sort_values(by='AUC', ascending=False)
    best_model_name = results_df.index[0]

    return results_df, best_model_name, models[best_model_name]

def train_final_model(X_train, y_train, preprocessor, best_model):
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', best_model)
    ])

    pipeline.fit(X_train, y_train)
    return pipeline



def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred)
    mlflow.log_text(report, "classification_report.txt")
    return report



def log_model_mlflow(model, X_train, results_df, best_model_name):

    import mlflow
    if mlflow.active_run():
        mlflow.end_run()

    signature = infer_signature(X_train, model.predict(X_train))

    with mlflow.start_run(run_name=best_model_name):
        mlflow.log_param("model_name", best_model_name)
        mlflow.log_metric("auc", results_df.loc[best_model_name, "AUC"])
        mlflow.log_metric("recall", results_df.loc[best_model_name, "Recall"])
        mlflow.log_metric("accuracy", results_df.loc[best_model_name, "Accuracy"])

        mlflow.sklearn.log_model(model, "model", signature=signature)

def run_training(df_train, df_test):

    df_train = df_train.drop("CustomerID")
    df_test = df_test.drop("CustomerID")

    df_train = df_train.dropna()
    df_test = df_test.dropna()

    df_train = df_train.dropDuplicates()
    df_test = df_test.dropDuplicates()

    df_train = feature_engineering(df_train)
    df_test = feature_engineering(df_test)

    df_train = df_train.toPandas()
    df_test = df_test.toPandas()

    X_train = df_train.drop(columns=['Churn'])
    y_train = df_train['Churn']

    X_test = df_test.drop(columns=['Churn'])
    y_test = df_test['Churn']

    preprocessor = build_preprocessor(X_train)

    results_df, best_model_name, best_model = train_and_evaluate(
        X_train, y_train, preprocessor
    )

    final_model = train_final_model(
        X_train, y_train, preprocessor, best_model
    )

    evaluate_model(final_model, X_test, y_test)

    log_model_mlflow(final_model, X_train, results_df, best_model_name)

    return final_model, results_df