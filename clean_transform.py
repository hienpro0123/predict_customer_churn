from pyspark.sql.functions import col, sum, when

BRONZE_TRAIN_PATH = "/Volumes/workspace/default/data_customers/bronze/train"
BRONZE_TEST_PATH = "/Volumes/workspace/default/data_customers/bronze/test"

SILVER_TRAIN_PATH = "/Volumes/workspace/default/data_customers/silver/train"
SILVER_TEST_PATH = "/Volumes/workspace/default/data_customers/silver/test"


df_train = spark.read.format("delta").load(BRONZE_TRAIN_PATH)
df_test = spark.read.format("delta").load(BRONZE_TEST_PATH)

missing_df_train = df_train.select([
    sum(when(col(c).isNull(), 1).otherwise(0)).alias(c)
    for c in df_train.columns
])

display(missing_df_train)

df_train = df_train.dropna()
df_test = df_test.dropna()

df_train.select([
    sum(when(col(c).isNull(), 1).otherwise(0)).alias(c)
    for c in df_train.columns
]).show()

df_train = df_train.dropDuplicates()
df_test = df_test.dropDuplicates()

df_train.write.format("delta").mode("overwrite").save(SILVER_TRAIN_PATH)
df_test.write.format("delta").mode("overwrite").save(SILVER_TEST_PATH)
