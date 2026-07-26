"""
File: init_db.py
Purpose:
    Database initialization script that builds the required database schemas 
    in PostgreSQL using SQLAlchemy.
Author: Priya Iyer
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import sys
from pathlib import Path
import logging

# Ensure project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from database.connection import engine, Base
from database.models import ETLRun, PaymentRecordModel  # Ensure models are registered

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.database.init_db")


def init_database() -> None:
    """
    Initializes PostgreSQL tables using SQLAlchemy metadata.
    """
    logger.info("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    init_database()
