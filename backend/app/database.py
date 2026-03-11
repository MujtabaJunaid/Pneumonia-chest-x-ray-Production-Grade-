"""

Database Configuration and Session Management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get DATABASE_URL from environment or use SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./medical_ai.db"
)

print(f"Database connection: {DATABASE_URL}")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True to log SQL queries
)

# Create SessionLocal for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Session:
    """
    Database session provider for dependency injection
    
    Yields:
    -------
    Session
        SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables at application startup
    """
    print("ðŸ“ ÚˆÛŒÙ¹Ø§Ø¨ÛŒØ³ Ù¹ÛŒØ¨Ù„Ø² Ø¨Ù†Ø§Ø¦Û’ Ø¬Ø§ Ø±ÛÛ’ ÛÛŒÚº...")
    Base.metadata.create_all(bind=engine)
    print("âœ“ Ù¹ÛŒØ¨Ù„Ø² Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø¨Ù†Ø§Ø¦Û’ Ú¯Ø¦Û’")
