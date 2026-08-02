"""
File: main.py
Purpose:
    Main command-line orchestrator entrypoint for the SentinelX Trust AI backend services.
    Enables database initialization and ETL pipeline execution via simple flags.
Author: Priya Iyer
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import sys
import argparse
import logging
from pathlib import Path

# Ensure backend/app/ is in the python path
sys.path.append(str(Path(__file__).resolve().parent))

from database.init_db import init_database
# run_pipeline is imported dynamically inside the run-etl CLI branch to prevent PySpark dependency errors on API containers.

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("backend.main")


def main() -> None:
    """
    Parses CLI args and triggers database setup or ETL pipeline execution.
    """
    parser = argparse.ArgumentParser(description="SentinelX Trust AI Backend Ingestion Service")
    
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initializes the database schema and builds staging and curated tables."
    )
    
    parser.add_argument(
        "--run-etl",
        action="store_true",
        help="Processes any raw scraped snapshots that have not been ingested."
    )

    args = parser.parse_args()

    # Show help if no flags are provided
    if not (args.init_db or args.run_etl):
        parser.print_help()
        sys.exit(0)

    if args.init_db:
        logger.info("Starting database schema initialization...")
        init_database()
        logger.info("Database schema setup complete.")

    if args.run_etl:
        logger.info("Checking for unprocessed scraper outputs and launching ETL pipeline...")
        from services.etl.spark_etl import run_pipeline
        run_pipeline()
        logger.info("ETL pipeline execution complete.")


if __name__ == "__main__":
    main()
