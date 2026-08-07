"""
File: seed_db.py
Purpose:
    Seeds the PostgreSQL database with realistic sample payment records,
    ETL runs, and Gold Layer analytics so that the platform is ready for demonstration.
Author: Niraj Kadam & Niraj Kadam
Project: SentinelX Trust AI
"""

import os
import sys
import uuid
import hashlib
from datetime import datetime, timedelta

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import SessionLocal
from database.init_db import init_database
from database.models import ETLRun, PaymentRecordModel, GoldPlatformAnalytics, GoldPaymentMethodInsight

def generate_row_hash(site: str, payment_type: str, payment_name: str, country: str) -> str:
    hash_str = f"{site}_{payment_type}_{payment_name}_{country}"
    return hashlib.sha256(hash_str.encode('utf-8')).hexdigest()

def seed_database():
    print("Seeding database...")
    db = SessionLocal()
    try:
        # Clear existing data first
        db.query(GoldPlatformAnalytics).delete()
        db.query(GoldPaymentMethodInsight).delete()
        db.query(PaymentRecordModel).delete()
        db.query(ETLRun).delete()
        db.commit()
        print("Cleared old database records.")

        # 1. Seed ETL Runs
        etl_runs = [
            ETLRun(
                run_path="data/raw/20260729_100000",
                records_scraped=50,
                records_processed=48,
                records_failed=2,
                status="COMPLETED",
                processed_at=datetime.utcnow() - timedelta(hours=24)
            ),
            ETLRun(
                run_path="data/raw/20260730_120000",
                records_scraped=65,
                records_processed=65,
                records_failed=0,
                status="COMPLETED",
                processed_at=datetime.utcnow() - timedelta(hours=12)
            ),
            ETLRun(
                run_path="data/raw/20260731_140000",
                records_scraped=40,
                records_processed=39,
                records_failed=1,
                status="COMPLETED",
                processed_at=datetime.utcnow() - timedelta(hours=2)
            ),
        ]
        for run in etl_runs:
            db.add(run)
        db.commit()
        print("Seeded etl_runs.")

        # 2. Seed Payment Records
        sample_records = [
            # OneXBet
            {
                "site": "onexbet", "payment_type": "UPI", "payment_name": "UPI Instant",
                "currency": "INR", "country": "IN", "status": "active",
                "source_url": "https://1xlite-12947.pro/en", "bonus_name": "100% First Deposit Bonus"
            },
            {
                "site": "onexbet", "payment_type": "UPI", "payment_name": "Paytm Wallet",
                "currency": "INR", "country": "IN", "status": "active",
                "source_url": "https://1xlite-12947.pro/en", "bonus_name": None
            },
            {
                "site": "onexbet", "payment_type": "Crypto", "payment_name": "Tether USDT (TRC20)",
                "currency": "USDT", "country": "IN", "status": "active",
                "source_url": "https://1xlite-12947.pro/en", "bonus_name": None
            },
            # Melbet
            {
                "site": "melbet", "payment_type": "UPI", "payment_name": "UPI Fast Pay",
                "currency": "INR", "country": "IN", "status": "active",
                "source_url": "https://melbet.com", "bonus_name": "Welcome Package"
            },
            {
                "site": "melbet", "payment_type": "Crypto", "payment_name": "Bitcoin (BTC)",
                "currency": "BTC", "country": "IN", "status": "active",
                "source_url": "https://melbet.com", "bonus_name": None
            },
            # 10Cric
            {
                "site": "tencric", "payment_type": "UPI", "payment_name": "PhonePe Direct",
                "currency": "INR", "country": "IN", "status": "active",
                "source_url": "https://10cric247.com", "bonus_name": "IPL Deposit Bonus"
            },
            {
                "site": "tencric", "payment_type": "Card", "payment_name": "VISA Credit Card",
                "currency": "INR", "country": "IN", "status": "active",
                "source_url": "https://10cric247.com", "bonus_name": None
            },
            # 22Play
            {
                "site": "twentytwoxbet", "payment_type": "Crypto", "payment_name": "Ethereum (ETH)",
                "currency": "ETH", "country": "IN", "status": "active",
                "source_url": "https://22play.com", "bonus_name": None
            }
        ]

        scraped_records = []
        for r in sample_records:
            row_hash = generate_row_hash(r["site"], r["payment_type"], r["payment_name"], r["country"])
            record = PaymentRecordModel(
                id=uuid.uuid4(),
                source_platform=r["site"],
                extraction_status="success",
                extraction_method="playwright_scrape",
                site=r["site"],
                payment_type=r["payment_type"],
                payment_name=r["payment_name"],
                currency=r["currency"],
                country=r["country"],
                bonus_name=r.get("bonus_name"),
                status=r["status"],
                source_url=r["source_url"],
                scraped_at=datetime.utcnow() - timedelta(hours=3),
                extracted_data={"min_deposit": 500, "max_deposit": 50000, "processing_time": "instant"},
                row_hash=row_hash
            )
            scraped_records.append(record)
            db.add(record)
        db.commit()
        print(f"Seeded {len(scraped_records)} payment_records.")

        # 3. Seed Gold Platform Analytics
        gold_analytics = [
            GoldPlatformAnalytics(
                site="onexbet",
                trust_score=78.2,
                trust_level="MEDIUM",
                confidence_score=0.88,
                total_payment_methods=14,
                active_payment_methods=12,
                supported_countries=["IN", "BD", "PK"],
                top_payment_methods=["UPI Instant", "Paytm Wallet", "USDT"],
                risk_summary="High-volume UPI transaction channel recycling detected. Multiple proxy receipt endpoints identified.",
                risk_flags=["UPI_RECYCLING_ANOMALY", "PROXY_PAYEE_FOOTPRINT"],
                last_scraped_at=datetime.utcnow() - timedelta(hours=2)
            ),
            GoldPlatformAnalytics(
                site="melbet",
                trust_score=85.6,
                trust_level="HIGH",
                confidence_score=0.91,
                total_payment_methods=10,
                active_payment_methods=10,
                supported_countries=["IN", "BD"],
                top_payment_methods=["UPI Fast Pay", "Bitcoin"],
                risk_summary="Stable transactional routing observed. Scraper parameters compliant with platform structure.",
                risk_flags=[],
                last_scraped_at=datetime.utcnow() - timedelta(hours=2)
            ),
            GoldPlatformAnalytics(
                site="tencric",
                trust_score=91.4,
                trust_level="HIGH",
                confidence_score=0.95,
                total_payment_methods=8,
                active_payment_methods=8,
                supported_countries=["IN"],
                top_payment_methods=["PhonePe Direct", "VISA Card"],
                risk_summary="Valid bank settlement nodes observed. No significant anomalies found.",
                risk_flags=[],
                last_scraped_at=datetime.utcnow() - timedelta(hours=3)
            ),
            GoldPlatformAnalytics(
                site="twentytwoxbet",
                trust_score=42.5,
                trust_level="LOW",
                confidence_score=0.82,
                total_payment_methods=6,
                active_payment_methods=4,
                supported_countries=["IN", "BR"],
                top_payment_methods=["Ethereum"],
                risk_summary="Frequent crypto wallet redirection detected. Potential KYC bypass proxy detected.",
                risk_flags=["CRYPTO_REDIRECT", "PROXY_WALLET_TRANSFER"],
                last_scraped_at=datetime.utcnow() - timedelta(hours=3)
            )
        ]
        for analytic in gold_analytics:
            db.add(analytic)
        db.commit()
        print("Seeded gold_platform_analytics.")

        # 4. Seed Gold Payment Method Insights
        gold_insights = [
            GoldPaymentMethodInsight(
                site="onexbet",
                payment_type="UPI",
                payment_name="UPI Instant",
                total_records=45,
                active_count=42,
                reliability_score=82.4,
                supported_countries=["IN"]
            ),
            GoldPaymentMethodInsight(
                site="onexbet",
                payment_type="Crypto",
                payment_name="Tether USDT (TRC20)",
                total_records=30,
                active_count=30,
                reliability_score=95.0,
                supported_countries=["IN", "BD"]
            ),
            GoldPaymentMethodInsight(
                site="melbet",
                payment_type="UPI",
                payment_name="UPI Fast Pay",
                total_records=35,
                active_count=35,
                reliability_score=88.5,
                supported_countries=["IN"]
            )
        ]
        for insight in gold_insights:
            db.add(insight)
        db.commit()
        print("Database seeding completed successfully!")

    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
