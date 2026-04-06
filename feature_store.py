from pyspark.sql.functions import col, when

SILVER_TRAIN_PATH = "/Volumes/workspace/default/data_customers/silver/train"
SILVER_TEST_PATH = "/Volumes/workspace/default/data_customers/silver/test"

GOLD_TRAIN_PATH = "/Volumes/workspace/default/data_customers/gold/train"
GOLD_TEST_PATH = "/Volumes/workspace/default/data_customers/gold/test"


df_train = spark.read.format("delta").load(SILVER_TRAIN_PATH)
df_test = spark.read.format("delta").load(SILVER_TEST_PATH)

df_train = df_train.drop("CustomerID")
df_test = df_test.drop("CustomerID")

df_train = df_train.withColumn(
    "Age_group",
    when(col("Age") < 30, "Young (<30)")
    .when((col("Age") >= 30) & (col("Age") < 50), "Adult (30-50)")
    .otherwise("Senior (50+)")
)

df_test = df_test.withColumn(
    "Age_group",
    when(col("Age") < 30, "Young (<30)")
    .when((col("Age") >= 30) & (col("Age") < 50), "Adult (30-50)")
    .otherwise("Senior (50+)")
)

df_train = df_train \
    .withColumn("Usage_Per_Tenure",
                col("Usage Frequency") / (col("Tenure") + 1)) \
    .withColumn("Spend_Per_Usage",
                col("Total Spend") / (col("Usage Frequency") + 1)) \
    .withColumn("Spend_Per_Tenure",
                col("Total Spend") / (col("Tenure") + 1)) \
    .withColumn("Payment_Delay_Ratio",
                col("Payment Delay") / 30) \
    .withColumn("Engagement_Score",
                (col("Usage Frequency") * col("Total Spend")) / 1000)

df_test = df_test \
    .withColumn("Usage_Per_Tenure",
                col("Usage Frequency") / (col("Tenure") + 1)) \
    .withColumn("Spend_Per_Usage",
                col("Total Spend") / (col("Usage Frequency") + 1)) \
    .withColumn("Spend_Per_Tenure",
                col("Total Spend") / (col("Tenure") + 1)) \
    .withColumn("Payment_Delay_Ratio",
                col("Payment Delay") / 30) \
    .withColumn("Engagement_Score",
                (col("Usage Frequency") * col("Total Spend")) / 1000)

df_train.write.format("delta").mode("overwrite").save(GOLD_TRAIN_PATH)
df_test.write.format("delta").mode("overwrite").save(GOLD_TEST_PATH)
