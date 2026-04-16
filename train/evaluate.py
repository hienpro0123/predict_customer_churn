import mlflow
from sklearn.metrics import classification_report

from pyspark.sql import SparkSession


GOLD_BASE_PATH = "/Volumes/workspace/default/data_customers/gold"
GOLD_TEST_PATH = f"{GOLD_BASE_PATH}/test"
MODEL_REGISTRY_NAME = "workspace.default.customer_churn_model"


def get_spark() -> SparkSession:
    spark = SparkSession.getActiveSession()
    if spark is not None:
        return spark
    return SparkSession.builder.appName("customer-churn-evaluate").getOrCreate()


def load_gold_test_data(spark: SparkSession):
    return spark.read.format("delta").load(GOLD_TEST_PATH).toPandas()


def evaluate_latest_model(df_test) -> None:
    model = mlflow.sklearn.load_model(f"models:/{MODEL_REGISTRY_NAME}@champion")

    X_test = df_test.drop(columns=["churn"])
    y_test = df_test["churn"]

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))


def main() -> None:
    spark = get_spark()
    df_test = load_gold_test_data(spark)
    evaluate_latest_model(df_test)


if __name__ == "__main__":
    main()
