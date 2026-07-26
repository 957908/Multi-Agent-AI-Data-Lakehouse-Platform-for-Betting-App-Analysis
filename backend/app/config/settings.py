"""
File: settings.py
Purpose:
    Centralized configuration management for the SentinelX Trust AI backend and ETL pipeline.
Author: Priya Iyer
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project Root Directory
BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """
    Configuration settings loaded from environment variables and the root .env file.
    """
    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""  # Default to empty, must be supplied in .env for production
    DB_NAME: str = "sentinelx_trust_ai"

    # Data Lakehouse Layer Paths
    RAW_DATA_DIR: str = str(BASE_DIR / "data" / "raw")
    BRONZE_DATA_DIR: str = str(BASE_DIR / "data" / "bronze")
    SILVER_DATA_DIR: str = str(BASE_DIR / "data" / "silver")
    DLQ_DIR: str = str(BASE_DIR / "output" / "dlq")
    REPORTS_DIR: str = str(BASE_DIR / "output" / "reports" / "etl")

    # Logging
    LOG_LEVEL: str = "INFO"

    # JWT & Role Authentication Configuration
    JWT_SECRET_KEY: str = "sentinelx_super_secure_jwt_secret_key_123"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ADMIN_EMAIL: str = "admin@sentinelx.com"
    ADMIN_PASSWORD: str = "AdminPassword123"
    ANALYST_EMAIL: str = "analyst@sentinelx.com"
    ANALYST_PASSWORD: str = "AnalystPassword123"
    READER_EMAIL: str = "reader@sentinelx.com"
    READER_PASSWORD: str = "ReaderPassword123"

    # Load configuration from the root .env
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        """Constructs the standard PostgreSQL connection string."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Instantiated globally
settings = Settings()
