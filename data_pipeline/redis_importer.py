import redis
import json
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

def get_redis_client():
    """
    Initializes and returns a Redis client using environment variables.
    """
    try:
        return redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            username=os.getenv('REDIS_USERNAME', 'default'),
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True
        )
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        return None

def import_to_redis(data_list: list):
    """
    Imports a list of customer data into Redis, skipping existing IDs.
    """
    r = get_redis_client()
    if r is None:
        print("Skipping Redis import due to connection failure.")
        return

    imported_count = 0
    skipped_count = 0

    for row in data_list:
        customer_id = row['CustomerID']
        
        # Check if customerId already exists in Redis to prevent overwriting
        if r.exists(f"customer:{customer_id}"):
            print(f"Customer {customer_id} already exists. Skipping.")
            skipped_count += 1
            continue
        
        # Copy the row data and prepare for JSON serialization
        customer_data = row.copy()
                
        # Store the data in Redis as a JSON string using the customer key
        try:
            r.set(f"customer:{customer_id}", json.dumps(customer_data))
            imported_count += 1
        except Exception as e:
            print(f"Error importing {customer_id}: {e}")

    # Final summary of the import process
    print(f"Import complete: {imported_count} imported, {skipped_count} skipped.")