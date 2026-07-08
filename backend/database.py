# database.py
# MySQL connection handler for CliniSight

import pymysql
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.sql import func

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
class Base(DeclarativeBase):
    pass

def get_db():
    """
    FastAPI dependency providing a SQLAlchemy session.
    Yields the session and always closes it after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_connection():
    """
    Creates and returns a fresh MySQL connection.
    Uses credentials from .env file.
    Always close connection in finally block after use.
    """
    print("DB_USER =", os.getenv("DB_USER"))
    print("DB_PASSWORD =", os.getenv("DB_PASSWORD"))
    
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
