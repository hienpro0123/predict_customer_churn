from connection import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id SERIAL PRIMARY KEY,
        age INTEGER,
        gender VARCHAR(10),
        tenure INTEGER,
        usage_frequency INTEGER,
        support_calls INTEGER,
        payment_delay INTEGER,
        subscription_type VARCHAR(20),
        contract_length VARCHAR(20),
        total_spend FLOAT,
        last_interaction INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

create_tables()