from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when


SILVER_BASE_PATH = "/Volumes/workspace/default/data_customers/silver"
SILVER_TRAIN_PATH = f"{SILVER_BASE_PATH}/train"
SILVER_TEST_PATH = f"{SILVER_BASE_PATH}/test"

GOLD_BASE_PATH = "/Volumes/workspace/default/data_customers/gold"
GOLD_TRAIN_PATH = f"{GOLD_BASE_PATH}/train"
GOLD_TEST_PATH = f"{GOLD_BASE_PATH}/test"


def get_spark() -> SparkSession:
    spark = SparkSession.getActiveSession()
    if spark is not None:
        return spark
    return SparkSession.builder.appName("customer-churn-feature-engineering").getOrCreate()


def load_silver_data(spark: SparkSession):
    df_train = spark.read.format("delta").load(SILVER_TRAIN_PATH)
    df_test = spark.read.format("delta").load(SILVER_TEST_PATH)
    return df_train, df_test


def add_features(df):
    df = df.withColumn(
        "age_group",
        when(col("age") < 30, "young")
        .when((col("age") >= 30) & (col("age") < 50), "adult")
        .otherwise("senior"),
    )

    df = (
        df.withColumn("usage_per_tenure", col("usage_frequency") / (col("tenure") + 1))
        .withColumn("spend_per_usage", col("total_spend") / (col("usage_frequency") + 1))
        .withColumn("spend_per_tenure", col("total_spend") / (col("tenure") + 1))
        .withColumn("payment_delay_ratio", col("payment_delay") / 30)
        .withColumn("engagement_score", (col("usage_frequency") * col("total_spend")) / 1000)
    )
    return df


def save_gold_data(df_train, df_test):
    df_train.write.format("delta").mode("overwrite").save(GOLD_TRAIN_PATH)
    df_test.write.format("delta").mode("overwrite").save(GOLD_TEST_PATH)


def main() -> None:
    spark = get_spark()
    df_train, df_test = load_silver_data(spark)

    df_train = add_features(df_train)
    df_test = add_features(df_test)

    save_gold_data(df_train, df_test)
    print(f"Saved gold train to {GOLD_TRAIN_PATH}")
    print(f"Saved gold test to {GOLD_TEST_PATH}")


if __name__ == "__main__":
    main()
