"""
File: spark_etl.py
Purpose:
    PySpark based ETL pipeline for ingesting, validating, transforming, 
    and staging scraper payment datasets.
Author: Priya Iyer
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import sys
import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Third Party
import os
import sys
from pathlib import Path

# Project root path for environment configuration
PROJECT_ROOT = Path(__file__).resolve().parents[4]

# Force Spark/Hadoop configurations on Windows
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ["HADOOP_HOME"] = str(PROJECT_ROOT / "hadoop")
os.environ["PATH"] = str(PROJECT_ROOT / "hadoop" / "bin") + os.pathsep + os.environ.get("PATH", "")

# Create dummy hadoop files on Windows to satisfy Hadoop static initializer checks
if os.name == "nt":
    hadoop_bin = PROJECT_ROOT / "hadoop" / "bin"
    hadoop_bin.mkdir(parents=True, exist_ok=True)
    for mock_file in ("winutils.exe", "hadoop.dll"):
        mock_path = hadoop_bin / mock_file
        if not mock_path.exists():
            with open(mock_path, "wb") as f:
                pass

from sqlalchemy import text
from sqlalchemy.orm import Session
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, MapType
from pyspark.sql.functions import col
from services.etl.gold_pipeline import GoldPipeline

# Ensure root is on sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from config.settings import settings
from database.connection import get_db, engine
from database.models import ETLRun
from services.validation.validator import DataValidator
from services.quality.monitor import QualityMonitor

logger = logging.getLogger("backend.services.etl.spark_etl")


class SparkETLPipeline:
    """
    Orchestrates the PySpark ETL process from Raw JSON to Bronze/Silver Parquet 
    and Curated PostgreSQL tables.
    """

    def __init__(self) -> None:
        """Initializes Spark Session and Validation layer."""
        self.spark = SparkSession.builder \
            .appName("SentinelX-Trust-AI-ETL") \
            .master("local[*]") \
            .config("spark.driver.memory", "512m") \
            .config("spark.executor.memory", "512m") \
            .config("spark.driver.extraJavaOptions", "-Djava.security.manager=allow") \
            .config("spark.executor.extraJavaOptions", "-Djava.security.manager=allow") \
            .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem") \
            .config("spark.sql.warehouse.dir", str(Path(settings.SILVER_DATA_DIR).parent / "spark-warehouse")) \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .getOrCreate()
        
        self.validator = DataValidator()
        logger.info("SparkETLPipeline initialized successfully.")

    def shutdown(self) -> None:
        """Closes the Spark Session."""
        if self.spark:
            self.spark.stop()
            logger.info("Spark Session terminated.")

    def find_unprocessed_runs(self) -> List[str]:
        """
        Scans data/raw/ directory to identify YYYY-MM-DD/HH-MM paths 
        that have not been successfully processed.
        """
        raw_base = Path(settings.RAW_DATA_DIR)
        if not raw_base.exists():
            logger.warning(f"Raw data directory does not exist: {raw_base}")
            return []

        # Find leaf paths like YYYY-MM-DD/HH-MM
        all_candidate_paths: List[str] = []
        for date_dir in raw_base.iterdir():
            if date_dir.is_dir() and len(date_dir.name) == 10:  # Format YYYY-MM-DD
                for time_dir in date_dir.iterdir():
                    if time_dir.is_dir() and len(time_dir.name) == 5:  # Format HH-MM
                        # Verify it has JSON files before adding
                        if list(time_dir.glob("*.json")):
                            rel_path = f"{date_dir.name}/{time_dir.name}"
                            all_candidate_paths.append(rel_path)

        if not all_candidate_paths:
            return []

        # Compare with DB logs
        unprocessed: List[str] = []
        with get_db() as db:
            for rel_path in all_candidate_paths:
                run = db.query(ETLRun).filter(ETLRun.run_path == rel_path, ETLRun.status == "SUCCESS").first()
                if not run:
                    unprocessed.append(rel_path)

        # Sort paths chronologically
        unprocessed.sort()
        logger.info(f"Found {len(unprocessed)} unprocessed runs: {unprocessed}")
        return unprocessed

    def load_raw_json_files(self, run_path_key: str) -> List[Dict[str, Any]]:
        """Loads and parses raw JSON files from a target run directory."""
        run_dir = Path(settings.RAW_DATA_DIR) / run_path_key
        raw_records: List[Dict[str, Any]] = []

        for json_file in run_dir.glob("*.json"):
            logger.info(f"Reading file: {json_file}")
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        raw_records.extend(data)
                    elif isinstance(data, dict):
                        raw_records.append(data)
            except Exception as e:
                logger.error(f"Failed to read JSON file {json_file}: {str(e)}")
        
        return raw_records

    def write_to_dlq(self, date_str: str, invalid_records: List[Dict[str, Any]]) -> None:
        """
        Writes validation-failed records containing error summaries to the structured DLQ:
        output/dlq/YYYY-MM-DD/invalid_records.json
        """
        if not invalid_records:
            return

        dlq_dir = Path(settings.DLQ_DIR) / date_str
        dlq_dir.mkdir(parents=True, exist_ok=True)
        dlq_file = dlq_dir / "invalid_records.json"

        # Load existing DLQ if exists
        existing_records: List[Dict[str, Any]] = []
        if dlq_file.exists():
            try:
                with open(dlq_file, "r", encoding="utf-8") as f:
                    existing_records = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read existing DLQ file, overwriting: {str(e)}")

        existing_records.extend(invalid_records)

        try:
            with open(dlq_file, "w", encoding="utf-8") as f:
                json.dump(existing_records, f, indent=4, ensure_ascii=False)
            logger.info(f"Wrote {len(invalid_records)} records to DLQ: {dlq_file}")
        except Exception as e:
            logger.error(f"Failed to write to DLQ file: {str(e)}")

    def normalize_and_hash_records(self, valid_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalizes payment types, currencies, and countries.
        Generates unique row hashes for each record.
        """
        processed: List[Dict[str, Any]] = []
        
        for rec in valid_records:
            # 1. Normalize site/platform name
            site = str(rec.get("site", "")).lower().strip()
            
            # 2. Normalize Payment Type
            p_type_raw = str(rec.get("payment_type", "")).lower().strip()
            if any(x in p_type_raw for x in ["upi", "instant", "netbanking-upi"]):
                payment_type = "UPI"
            elif any(x in p_type_raw for x in ["bank_transfer", "netbanking", "bank transfer", "net banking"]):
                payment_type = "Bank Transfer"
            elif any(x in p_type_raw for x in ["crypto", "cryptocurrency", "bitcoin", "tether", "usdt", "eth"]):
                payment_type = "Cryptocurrency"
            elif any(x in p_type_raw for x in ["wallet", "ewallet", "skrill", "neteller", "astropay", "paytm", "phonepe"]):
                payment_type = "E-Wallet"
            elif any(x in p_type_raw for x in ["card", "debit", "credit", "visa", "mastercard"]):
                payment_type = "Card"
            else:
                payment_type = "Other"

            # 3. Normalize Currency
            currency_raw = str(rec.get("currency", "INR")).upper().strip()
            if currency_raw in ("₹", "RS", "INR"):
                currency = "INR"
            elif currency_raw in ("$", "USD"):
                currency = "USD"
            elif currency_raw in ("€", "EUR"):
                currency = "EUR"
            else:
                currency = currency_raw

            # 4. Normalize Country
            country_raw = str(rec.get("country", "IN")).upper().strip()
            if country_raw in ("IN", "IND"):
                country = "IN"
            elif country_raw in ("BG", "BGR"):
                country = "BG"
            else:
                country = country_raw

            # 5. Re-standardize status
            status = str(rec.get("status", "active")).lower().strip()
            status = "active" if status in ("active", "success", "available") else "inactive"

            # 6. Generate Row Hash based on composite keys
            # key = site + payment_type + payment_name + currency + country + source_url
            payment_name = str(rec.get("payment_name", "")).strip()
            source_url = str(rec.get("source_url", "")).strip()
            key_str = f"{site}_{payment_type}_{payment_name}_{currency}_{country}_{source_url}"
            row_hash = hashlib.sha256(key_str.encode("utf-8")).hexdigest()

            # Build clean dictionary compatible with DB and Parquet
            clean_rec = {
                "schema_version": rec.get("schema_version", "1.1"),
                "scraper_version": rec.get("scraper_version", "1.0.0"),
                "source_platform": rec.get("source_platform", site),
                "extraction_status": rec.get("extraction_status", "success"),
                "extraction_method": rec.get("extraction_method", "playwright_sync"),
                "site": site,
                "page_type": rec.get("page_type", "deposit_page"),
                "payment_type": payment_type,
                "payment_name": payment_name,
                "currency": currency,
                "country": country,
                "bonus_name": rec.get("bonus_name"),
                "support_type": rec.get("support_type"),
                "support_value": rec.get("support_value"),
                "status": status,
                "source_url": source_url,
                "scraped_at": rec["scraped_at"],  # String for Spark loading
                "extracted_data": json.dumps(rec.get("extracted_data", {})),  # Serialized for Spark / DB JSONB
                "row_hash": row_hash
            }
            processed.append(clean_rec)
            
        return processed

    def write_to_postgresql(self, records: List[Dict[str, Any]]) -> int:
        """
        Executes a bulk upsert (insert on conflict update) into PostgreSQL.
        Returns count of inserted/updated records.
        """
        if not records:
            return 0

        upsert_sql = text("""
            INSERT INTO payment_records (
                schema_version, scraper_version, source_platform, extraction_status,
                extraction_method, site, page_type, payment_type, payment_name,
                currency, country, bonus_name, support_type, support_value,
                status, source_url, scraped_at, extracted_data, row_hash,
                created_at, updated_at
            ) VALUES (
                :schema_version, :scraper_version, :source_platform, :extraction_status,
                :extraction_method, :site, :page_type, :payment_type, :payment_name,
                :currency, :country, :bonus_name, :support_type, :support_value,
                :status, :source_url, CAST(:scraped_at AS TIMESTAMP), CAST(:extracted_data AS JSONB), :row_hash,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            ON CONFLICT (row_hash) DO UPDATE SET
                extraction_status = EXCLUDED.extraction_status,
                status = EXCLUDED.status,
                scraped_at = EXCLUDED.scraped_at,
                extracted_data = EXCLUDED.extracted_data,
                updated_at = CURRENT_TIMESTAMP;
        """)

        with get_db() as db:
            for rec in records:
                db.execute(upsert_sql, rec)
            db.commit()
            
        return len(records)

    def process_run(self, run_path_key: str) -> bool:
        """
        Ingests, validates, transforms, deduplicates, and saves datasets for a run.
        """
        logger.info(f"=== Starting ETL process for run: {run_path_key} ===")
        date_str, time_str = run_path_key.split("/")

        # Initialize run status in DB
        with get_db() as db:
            run_log = db.query(ETLRun).filter(ETLRun.run_path == run_path_key).first()
            if not run_log:
                run_log = ETLRun(run_path=run_path_key, status="PROCESSING")
                db.add(run_log)
                db.commit()

        # Initialize quality monitor
        monitor = QualityMonitor(run_path_key)

        try:
            # 1. Load Raw JSON
            raw_records = self.load_raw_json_files(run_path_key)
            total_raw = len(raw_records)
            if total_raw == 0:
                logger.warning(f"No records loaded for run {run_path_key}.")
                with get_db() as db:
                    run_log = db.query(ETLRun).filter(ETLRun.run_path == run_path_key).first()
                    run_log.status = "SUCCESS"
                    run_log.records_scraped = 0
                    db.commit()
                return True

            # 2. Write Bronze Parquet Layer (Raw Backup)
            import pandas as pd
            bronze_target_path = Path(settings.BRONZE_DATA_DIR) / run_path_key
            bronze_target_path.mkdir(parents=True, exist_ok=True)
            bronze_file = bronze_target_path / "raw_backup.parquet"
            raw_pdf = pd.DataFrame(raw_records)
            raw_pdf.to_parquet(str(bronze_file), index=False)
            logger.info(f"Saved Bronze Parquet backup to: {bronze_file}")

            # 3. Validate Schema & Core Data Contracts
            valid_records, invalid_records = self.validator.validate_batch(raw_records)
            
            # 4. Route invalid records to DLQ
            self.write_to_dlq(date_str, invalid_records)

            if not valid_records:
                logger.warning("All records failed validation. No silver records generated.")
                metrics = monitor.calculate_metrics(total_raw, 0, 0, 0, invalid_records)
                monitor.generate_report(metrics, invalid_records)
                
                with get_db() as db:
                    run_log = db.query(ETLRun).filter(ETLRun.run_path == run_path_key).first()
                    run_log.status = "FAILED"
                    run_log.records_scraped = total_raw
                    run_log.records_failed = len(invalid_records)
                    db.commit()
                return False

            # 5. Normalize and Generate Hashed Keys
            normalized_records = self.normalize_and_hash_records(valid_records)

            # 6. Deduplicate using Spark SQL window functions
            # Convert normalized records list to Spark DataFrame
            norm_rdd = self.spark.sparkContext.parallelize([json.dumps(r) for r in normalized_records])
            norm_df = self.spark.read.json(norm_rdd)

            # Define schema explicitly to avoid parsing errors
            norm_df = norm_df.select(
                col("schema_version"), col("scraper_version"), col("source_platform"), 
                col("extraction_status"), col("extraction_method"), col("site"), col("page_type"), 
                col("payment_type"), col("payment_name"), col("currency"), col("country"), 
                col("bonus_name"), col("support_type"), col("support_value"), col("status"), 
                col("source_url"), col("scraped_at"), col("extracted_data"), col("row_hash")
            )

            # Spark Deduplication window partition by row_hash, select latest scraped_at
            from pyspark.sql.window import Window
            from pyspark.sql.functions import row_number
            
            windowSpec = Window.partitionBy("row_hash").orderBy(col("scraped_at").desc())
            deduped_df = norm_df.withColumn("rank", row_number().over(windowSpec)).filter(col("rank") == 1).drop("rank")
            
            duplicate_count = norm_df.count() - deduped_df.count()
            logger.info(f"Spark deduplication filtered {duplicate_count} duplicate records.")

            # 8. Collect deduplicated dataset from Spark
            curated_records = [row.asDict() for row in deduped_df.collect()]

            # 7. Write Silver Parquet Layer (Transformed & Cleaned)
            silver_target_path = Path(settings.SILVER_DATA_DIR) / run_path_key
            silver_target_path.mkdir(parents=True, exist_ok=True)
            silver_file = silver_target_path / "clean_records.parquet"
            curated_pdf = pd.DataFrame(curated_records)
            curated_pdf.to_parquet(str(silver_file), index=False)
            logger.info(f"Saved Silver Parquet dataset to: {silver_file}")

            inserted_count = self.write_to_postgresql(curated_records)
            logger.info(f"Committed {inserted_count} curated records to PostgreSQL.")

            # 9. Calculate Quality Metrics and write report
            metrics = monitor.calculate_metrics(
                total_raw=total_raw,
                valid_count=len(valid_records),
                duplicate_count=duplicate_count,
                inserted_count=inserted_count,
                invalid_records=invalid_records
            )
            monitor.generate_report(metrics, invalid_records)

            # 10. Update Run catalog status in DB
            with get_db() as db:
                run_log = db.query(ETLRun).filter(ETLRun.run_path == run_path_key).first()
                if run_log:
                    run_log.status = "SUCCESS"
                    run_log.records_scraped = total_raw
                    run_log.records_processed = inserted_count
                    run_log.records_failed = len(invalid_records)
                    db.commit()
                
                # Trigger Gold Layer Aggregation automatically
                try:
                    logger.info("Automatically triggering Gold Layer Aggregation pipeline...")
                    gold_pipeline = GoldPipeline(db)
                    gold_metrics = gold_pipeline.run_aggregation(run_path_key)
                    logger.info(f"Gold Layer Aggregation completed: {gold_metrics}")
                except Exception as ex:
                    logger.error(f"Failed to auto-trigger Gold Layer Aggregation: {str(ex)}", exc_info=True)
            
            logger.info(f"=== ETL process for run {run_path_key} completed successfully ===")
            return True

        except Exception as err:
            logger.error(f"Fatal error in ETL pipeline for run {run_path_key}: {str(err)}", exc_info=True)
            with get_db() as db:
                run_log = db.query(ETLRun).filter(ETLRun.run_path == run_path_key).first()
                if run_log:
                    run_log.status = "FAILED"
                    db.commit()
            return False


def run_pipeline() -> None:
    """Entry point for triggering incremental pipeline runs."""
    pipeline = SparkETLPipeline()
    try:
        unprocessed = pipeline.find_unprocessed_runs()
        if not unprocessed:
            logger.info("All raw snapshots have already been successfully processed.")
            return

        success_count = 0
        for run_path in unprocessed:
            success = pipeline.process_run(run_path)
            if success:
                success_count += 1
        
        logger.info(f"ETL Execution finished. Processed {success_count}/{len(unprocessed)} successfully.")
    finally:
        pipeline.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    run_pipeline()
