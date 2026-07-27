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
from services.etl.spark_etl import run_pipeline

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
    
    parser.add_argument(
        "--run-gold",
        action="store_true",
        help="Aggregates curated records to Gold layer Parquet folders and database tables."
    )

    args = parser.parse_args()

    # Show help if no flags are provided
    if not (args.init_db or args.run_etl or args.run_gold):
        parser.print_help()
        sys.exit(0)

    if args.init_db:
        logger.info("Starting database schema initialization...")
        init_database()
        logger.info("Database schema setup complete.")

    if args.run_etl:
        logger.info("Checking for unprocessed scraper outputs and launching ETL pipeline...")
        run_pipeline()
        logger.info("ETL pipeline execution complete.")

    if args.run_gold:
        logger.info("Executing Gold Layer pre-aggregation job...")
        from database.connection import get_db
        from services.etl.gold_pipeline import GoldPipeline
        from datetime import datetime
        with get_db() as db:
            pipeline = GoldPipeline(db)
            run_path_key = datetime.now().strftime("%Y-%m-%d/%H-%M")
            result = pipeline.run_aggregation(run_path_key)
            logger.info(f"Gold Layer aggregation complete: {result}")


if __name__ == "__main__":
    main()
