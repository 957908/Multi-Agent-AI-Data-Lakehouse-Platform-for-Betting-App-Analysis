"""
File: connection.py
Purpose:
    Database connection management and session factory utilizing SQLAlchemy.
Author: Priya Iyer
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from config.settings import settings

logger = logging.getLogger("backend.database.connection")

# Create engine with connection pooling settings suitable for production
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verifies connection health before vending
    echo=False           # Set to True only for deep query debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models
Base = declarative_base()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager that yields a database session and ensures it is closed 
    safely and that transactions are rolled back in case of exceptions.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction error: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()


def get_db_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.
    Avoids using @contextmanager decorator directly to prevent Python 3.13 compatibility issues.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
