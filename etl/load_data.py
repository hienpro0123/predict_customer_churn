from pyspark.sql import SparkSession


RAW_BASE_PATH = "/Volumes/workspace/default/data_customers/raw"
RAW_TRAIN_PATH = f"{RAW_BASE_PATH}/customer_churn_dataset-training-master.csv"
RAW_TEST_PATH = f"{RAW_BASE_PATH}/customer_churn_dataset-testing-master.csv"

BRONZE_BASE_PATH = "/Volumes/workspace/default/data_customers/bronze"
BRONZE_TRAIN_PATH = f"{BRONZE_BASE_PATH}/train"
BRONZE_TEST_PATH = f"{BRONZE_BASE_PATH}/test"


def get_spark() -> SparkSession:
    spark = SparkSession.getActiveSession()
    if spark is not None:
        return spark
    return SparkSession.builder.appName("customer-churn-load-data").getOrCreate()


def read_raw_data(spark: SparkSession):
    df_train = spark.read.csv(
        RAW_TRAIN_PATH,
        header=True,
        inferSchema=True,
    )

    df_test = spark.read.csv(
        RAW_TEST_PATH,
        header=True,
        inferSchema=True,
    )

    return df_train, df_test


def save_bronze_data(df_train, df_test) -> None:
    df_train.write.mode("overwrite").parquet(BRONZE_TRAIN_PATH)
    df_test.write.mode("overwrite").parquet(BRONZE_TEST_PATH)


def main() -> None:
    spark = get_spark()
    df_train, df_test = read_raw_data(spark)
    save_bronze_data(df_train, df_test)

    print(f"Saved bronze train to {BRONZE_TRAIN_PATH}")
    print(f"Saved bronze test to {BRONZE_TEST_PATH}")


if __name__ == "__main__":
    main()
