# fastapi_project/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .base import Base

# Load from env or fallback to your local URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:root@localhost:5432/fastapi_db?client_encoding=utf8"
)

# Set up the engine & session factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    """
    FastAPI dependency that yields a database session, then closes it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
