try:
    from db.connection import get_connection
except ModuleNotFoundError:
    from connection import get_connection


def create_tables() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id VARCHAR(10) PRIMARY KEY,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.execute(
        """
        ALTER TABLE customers
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            prediction_id SERIAL PRIMARY KEY,
            customer_id VARCHAR(10) NOT NULL,
            predicted_label INTEGER NOT NULL,
            churn_probability FLOAT NOT NULL,
            model_input_snapshot JSONB,
            recommended_action TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_predictions_customer
                FOREIGN KEY (customer_id)
                REFERENCES customers(id)
                ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        ALTER TABLE predictions
        ADD COLUMN IF NOT EXISTS recommended_action TEXT
        """
    )

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    create_tables()