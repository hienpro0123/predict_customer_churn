import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder

def preprocess_data(input_file="sample_batch_input.csv", output_file="cleaned_data.csv"):
    if not os.path.exists(input_file):
        print(f"Lỗi: Không tìm thấy file {input_file}")
        return None

    df = pd.read_csv(input_file)
    print(f"--- Bat dau Preprocessing ---")

    # 1. Xóa trùng lặp
    df = df.drop_duplicates(subset=['CustomerID'], keep='last')

    # 2. Danh sách các cột cần chuẩn hóa chữ (Categorical columns)
    cat_cols = ['Gender', 'Subscription Type', 'Contract Length']
    
    # 3. Xử lý giá trị thiếu
    for col in df.columns:
        if col in cat_cols:
            if not df[col].empty:
                df[col] = df[col].fillna(df[col].mode()[0])
        else:
            if df[col].dtype in [np.float64, np.int64]:
                df[col] = df[col].fillna(df[col].median())

    # 4. CHUẨN HÓA CHỮ (Normalization)
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower().str.capitalize()

    # 5. MÃ HÓA CÁC CỘT PHÂN LOẠI (Encoding - LEGIT WAY)
    # Sử dụng LabelEncoder để chuyên nghiệp hơn
    le = LabelEncoder()
    for col in cat_cols:
        if col in df.columns:
            print(f"Encoding column: {col}")
            df[col] = le.fit_transform(df[col])
            # Lưu ý: Trong thực tế bạn nên lưu 'le' lại để dùng cho inference sau này


    # 6. Xử lý Outliers cho các cột số
    num_cols = ['Age', 'Total Spend', 'Tenure', 'Usage Frequency', 'Payment Delay']
    for col in num_cols:
        if col in df.columns:
            # Ép về kiểu số
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].median())
            
            if col == 'Age':
                df.loc[df[col] > 90, col] = 90
                df.loc[df[col] < 18, col] = 18
            if col == 'Total Spend':
                df.loc[df[col] < 0, col] = 0
            if col == 'Payment Delay':
                # Giả sử delay không quá 120 ngày
                df.loc[df[col] < 0, col] = 0
                df.loc[df[col] > 120, col] = 120

    # 6. Lưu dữ liệu
    df.to_csv(output_file, index=False)
    print(f"Da luu du lieu sach vao: {output_file}")
    print(f"--- Hoan thanh Preprocessing ---")
    
    return df

if __name__ == "__main__":
    preprocess_data()