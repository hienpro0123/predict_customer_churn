RAW_TRAIN_PATH = "/Volumes/workspace/default/data_customers/raw/customer_churn_dataset-training-master.csv"
RAW_TEST_PATH = "/Volumes/workspace/default/data_customers/raw/customer_churn_dataset-testing-master.csv"

BRONZE_TRAIN_PATH = "/Volumes/workspace/default/data_customers/bronze/train"
BRONZE_TEST_PATH = "/Volumes/workspace/default/data_customers/bronze/test"


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

df_train.write.format("delta").mode("overwrite").save(BRONZE_TRAIN_PATH)
df_test.write.format("delta").mode("overwrite").save(BRONZE_TEST_PATH)
