import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder

def preprocess_data(data):
    # Check if the input data is empty
    if not data:
        print("Error: Input data is empty")
        return []

    # Convert the data into a pandas DataFrame
    df = pd.DataFrame(data)
    print(f"--- Starting Preprocessing ---")

    # 1. Remove duplicate records based on CustomerID, keeping the last occurrence
    df = df.drop_duplicates(subset=['CustomerID'], keep='last')

    # 2. Define list of categorical columns to be normalized
    cat_cols = ['Gender', 'Subscription Type', 'Contract Length']
    
    # 3. Handle missing values
    for col in df.columns:
        if col in cat_cols:
            # Fill missing categorical values with the mode
            if not df[col].empty:
                df[col] = df[col].fillna(df[col].mode()[0])
        else:
            # Fill missing numerical values with the median
            if df[col].dtype in [np.float64, np.int64]:
                df[col] = df[col].fillna(df[col].median())

    # 4. TEXT NORMALIZATION
    for col in cat_cols:
        if col in df.columns:
            # Strip whitespace, convert to lowercase, and capitalize the first letter
            df[col] = df[col].astype(str).str.strip().str.lower().str.capitalize()

    # 5. ENCODE CATEGORICAL COLUMNS
    # Initialize and apply LabelEncoder
    le = LabelEncoder()
    for col in cat_cols:
        if col in df.columns:
            print(f"Encoding column: {col}")
            df[col] = le.fit_transform(df[col])

    # 6. Handle Outliers for numerical columns
    num_cols = ['Age', 'Total Spend', 'Tenure', 'Usage Frequency', 'Payment Delay']
    for col in num_cols:
        if col in df.columns:
            # Force conversion to numeric, coercing errors to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Fill resulting NaNs with the median
            df[col] = df[col].fillna(df[col].median())
            
            # Cap Age between 18 and 90
            if col == 'Age':
                df.loc[df[col] > 90, col] = 90
                df.loc[df[col] < 18, col] = 18
            # Ensure Total Spend is not negative
            if col == 'Total Spend':
                df.loc[df[col] < 0, col] = 0
            # Cap Payment Delay between 0 and 120 days
            if col == 'Payment Delay':
                df.loc[df[col] < 0, col] = 0
                df.loc[df[col] > 120, col] = 120

    print(f"--- Preprocessing Complete ---")
    
    # Return the processed data as a list of dictionaries
    return df.to_dict(orient='records')