import time
from fake_data import generate_fake_data
from processed import preprocess_data
from redis_importer import import_to_redis

def run_pipeline():
    print("--- Starting Data Pipeline ---")
    i = 100
    # 1. Generate Fake Data
    print(f"Step 1: Generating {i} samples of fake data...")
    raw_data = generate_fake_data(i)
    print(f"Generated {len(raw_data)} samples.")
    
    # 2. Preprocess Data
    print("Step 2: Preprocessing and Encoding data...")
    cleaned_data = preprocess_data(raw_data)
    print(f"Cleaned {len(cleaned_data)} samples.")

    # 3. Import Data to Redis
    print("Step 3: Importing data to Redis...")
    import_to_redis(cleaned_data)
    
    print("--- Pipeline completed successfully ---")

if __name__ == "__main__":
    run_pipeline()