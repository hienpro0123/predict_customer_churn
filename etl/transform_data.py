from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, when


BRONZE_BASE_PATH = "/Volumes/workspace/default/data_customers/bronze"
BRONZE_TRAIN_PATH = f"{BRONZE_BASE_PATH}/train"
BRONZE_TEST_PATH = f"{BRONZE_BASE_PATH}/test"

SILVER_BASE_PATH = "/Volumes/workspace/default/data_customers/silver"
SILVER_TRAIN_PATH = f"{SILVER_BASE_PATH}/train"
SILVER_TEST_PATH = f"{SILVER_BASE_PATH}/test"


def get_spark() -> SparkSession:
    spark = SparkSession.getActiveSession()
    if spark is not None:
        return spark
    return SparkSession.builder.appName("customer-churn-cleaning").getOrCreate()



def load_bronze_data(spark: SparkSession):
    df_train = spark.read.format("delta").load(BRONZE_TRAIN_PATH)
    df_test = spark.read.format("delta").load(BRONZE_TEST_PATH)
    return df_train, df_test


def get_missing_counts(df):
    return df.select(
        [
            sum(when(col(c).isNull(), 1).otherwise(0)).alias(c)
            for c in df.columns
        ]
    )


def clean_data(df_train, df_test):
    missing_df_train = get_missing_counts(df_train)
    missing_df_test = get_missing_counts(df_test)

    df_train = df_train.dropna()
    df_test = df_test.dropna()

    df_train = df_train.dropDuplicates()
    df_test = df_test.dropDuplicates()

    return df_train, df_test, missing_df_train, missing_df_test


def save_silver_data(df_train, df_test) -> None:
    df_train.write.format("delta").mode("overwrite").save(SILVER_TRAIN_PATH)
    df_test.write.format("delta").mode("overwrite").save(SILVER_TEST_PATH)


def main() -> None:
    spark = get_spark()

    df_train, df_test = load_bronze_data(spark)
    df_train, df_test, missing_df_train, missing_df_test = clean_data(df_train, df_test)

    print("Missing values in train before cleaning:")
    missing_df_train.show()

    print("Missing values in test before cleaning:")
    missing_df_test.show()

    print("Missing values in train after dropna:")
    get_missing_counts(df_train).show()

    save_silver_data(df_train, df_test)

    print(f"Saved silver train (DELTA) to {SILVER_TRAIN_PATH}")
    print(f"Saved silver test (DELTA) to {SILVER_TEST_PATH}")


if __name__ == "__main__":
    main()