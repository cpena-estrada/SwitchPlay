# database.py
import os
import psycopg2
from dotenv import load_dotenv

# Load the DATABASE_URL from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """
    Opens a connection to the Postgres database (Supabase).
    Close when done.
    """
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f'Error connecting to database {e}')
        raise e