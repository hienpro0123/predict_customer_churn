import time
from fake_data import generate_fake_data
from processed import preprocess_data
# from redis_importer import import_to_redis # Tạm thời bỏ qua import Redis

def run_pipeline():
    print("--- Starting Data Pipeline ---")
    
    # 1. Generate Fake Data
    print("Step 1: Generating 100 samples of fake data...")
    raw_data = generate_fake_data(100)
    print(f"Generated {len(raw_data)} samples.")
    
    # 2. Preprocess Data
    print("Step 2: Preprocessing and Encoding data...")
    cleaned_data = preprocess_data(raw_data)
    print(f"Cleaned {len(cleaned_data)} samples.")
    
    # 3. Import to Redis
    print("Step 3: [SKIPPED] Importing data to Redis.")
    # import_to_redis(cleaned_df) # Tạm thời comment lại theo yêu cầu
    
    print("--- Pipeline completed successfully ---")

if __name__ == "__main__":
    run_pipeline()