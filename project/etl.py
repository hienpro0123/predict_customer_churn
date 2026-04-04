import pandas as pd 
from matplotlib import pyplot as plt 
import seaborn as sns 
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
# from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import FunctionTransformer
from mlflow.models import infer_signature
import mlflow
import mlflow.sklearn
import numpy as np
from pyspark.sql.functions import col, when

def load_dataSet(spark, PATH):
    return spark.read.parquet(PATH)

def convertToParquet(df, path):
    df.write.mode("overwrite").parquet(path)

def feature_engineering(df):

    # ===== Age Group =====
    df = df.withColumn(
        "Age_group",
        when(col("Age") < 30, "Young (<30)")
        .when((col("Age") >= 30) & (col("Age") < 50), "Adult (30-50)")
        .otherwise("Senior (50+)")
    )

    # ===== Numeric Features =====
    df = df \
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

    return df