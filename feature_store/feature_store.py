from pyspark.sql import SparkSession
from databricks.feature_engineering import FeatureEngineeringClient

#Path
GOLD_BASE_PATH = "/Volumes/workspace/default/data_customers/gold"
GOLD_TRAIN_PATH = f"{GOLD_BASE_PATH}/train"

FEATURE_TABLE_NAME = "workspace.default.customer_features"

def get_spark() -> SparkSession:
    spark = SparkSession.getActiveSession()
    if spark is not None:
        return spark
    return SparkSession.builder.appName("feature-store").getOrCreate()


def load_gold_data(spark: SparkSession):
    df = spark.read.format("delta").load(GOLD_TRAIN_PATH)
    return df


def prepare_feature_df(df):
    feature_df = df.drop("churn")
    feature_df = feature_df.dropDuplicates(["customerid"])
    return feature_df


def create_or_update_feature_store(df):
    fs = FeatureEngineeringClient()
    try:
        # Create table if not exist
        fs.create_table(
            name=FEATURE_TABLE_NAME,
            primary_keys=["customerid"],
            df=df,
            description="Customer churn features"
        )
        print("Feature table created!")

    except Exception as e:
        print("Table exists, updating instead...")
        fs.write_table(
            name=FEATURE_TABLE_NAME,
            df=df,
            mode="merge"
        )
        print("Feature table updated!")


def main():
    spark = get_spark()

    # Load data from path Gold
    df = load_gold_data(spark)

    # Prepare feature dataframe
    feature_df = prepare_feature_df(df)

    # 3Create / Update Feature Store
    create_or_update_feature_store(feature_df)

if __name__ == "__main__":
    main()