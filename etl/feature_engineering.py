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
        "Age_group",
        when(col("Age") < 30, "Young (<30)")
        .when((col("Age") >= 30) & (col("Age") < 50), "Adult (30-50)")
        .otherwise("Senior (50+)"),
    )

    df = (
        df.withColumn("Usage_Per_Tenure", col("Usage Frequency") / (col("Tenure") + 1))
        .withColumn("Spend_Per_Usage", col("Total Spend") / (col("Usage Frequency") + 1))
        .withColumn("Spend_Per_Tenure", col("Total Spend") / (col("Tenure") + 1))
        .withColumn("Payment_Delay_Ratio", col("Payment Delay") / 30)
        .withColumn("Engagement_Score", (col("Usage Frequency") * col("Total Spend")) / 1000)
    )
    return df


def save_gold_data(df_train, df_test) -> None:
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
