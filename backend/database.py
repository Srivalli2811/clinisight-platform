# database.py
# MySQL connection handler for CliniSight

import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    Creates and returns a fresh MySQL connection.
    Uses credentials from .env file.
    Always close connection in finally block after use.
    """
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
