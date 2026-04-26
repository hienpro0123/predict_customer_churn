import time
from fake_data import generate_fake_data
from processed import preprocess_data
# from redis_importer import import_to_redis # Tạm thời bỏ qua import Redis

def run_pipeline():
    print("--- Starting Data Pipeline ---")
    
    # 1. Generate Fake Data
    print("Step 1: Generating 100 samples of fake data...")
    df = generate_fake_data(100)
    print(f"Generated data shape: {df.shape}")
    
    # Save to CSV for inspection (as per image 1)
    input_file = "sample_batch_input.csv"
    df.to_csv(input_file, index=False)
    print(f"Data saved to {input_file}")
    
    # 2. Preprocess Data
    print("Step 2: Preprocessing and Encoding data...")
    cleaned_df = preprocess_data(input_file=input_file, output_file="cleaned_data.csv")
    if cleaned_df is not None:
        print(f"Cleaned data shape: {cleaned_df.shape}")
    
    # 3. Import to Redis
    print("Step 3: [SKIPPED] Importing data to Redis.")
    # import_to_redis(cleaned_df) # Tạm thời comment lại theo yêu cầu
    
    print("--- Pipeline completed successfully ---")

if __name__ == "__main__":
    run_pipeline()
