import pandas as pd
import matplotlib
# Chuyển sang chế độ không hiển thị cửa sổ (Headless mode) để tránh bị treo
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import seaborn as sns
import os

def perform_eda(file_path="cleaned_data.csv"):
    if not os.path.exists(file_path):
        print(f"Lỗi: Không tìm thấy file {file_path}")
        return

    df = pd.read_csv(file_path)
    
    if not os.path.exists('plots'):
        os.makedirs('plots')
        print("Đã tạo thư mục 'plots/'")

    print("--- Đang xử lý biểu đồ... ---")

    # 1. Phân phối các biến số
    plt.figure(figsize=(15, 10))
    plt.subplot(2, 2, 1); sns.histplot(df['Age'], kde=True, color='blue'); plt.title('Age Distribution')
    plt.subplot(2, 2, 2); sns.histplot(df['Total Spend'], kde=True, color='green'); plt.title('Spend Distribution')
    plt.subplot(2, 2, 3); sns.histplot(df['Tenure'], kde=True, color='orange'); plt.title('Tenure Distribution')
    plt.subplot(2, 2, 4); sns.countplot(x='Gender', data=df, palette='Set2'); plt.title('Gender Count')
    plt.tight_layout()
    plt.savefig('plots/distributions.png')
    plt.close() # Đóng plot để giải phóng bộ nhớ

    # 2. Thống kê Gói cước
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1); sns.countplot(x='Subscription Type', data=df); plt.title('Subscription Type')
    plt.subplot(1, 2, 2); sns.countplot(x='Contract Length', data=df); plt.title('Contract Length')
    plt.tight_layout()
    plt.savefig('plots/categories.png')
    plt.close()

    # 3. Ma trận tương quan
    plt.figure(figsize=(10, 8))
    numeric_df = df.select_dtypes(include=[np.number]) # Đảm bảo chỉ lấy cột số
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')
    plt.savefig('plots/correlation.png')
    plt.close()

    print(f"--- Hoàn tất! Đã lưu 3 ảnh vào thư mục: {os.path.abspath('plots')} ---")

if __name__ == "__main__":
    import numpy as np 
    perform_eda()