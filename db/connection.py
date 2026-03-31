from dotenv import load_dotenv
import psycopg2
import os
load_dotenv()


def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT")
        )
        return conn
    except Exception as e:
        print("Database connection error:", e)
        raise
