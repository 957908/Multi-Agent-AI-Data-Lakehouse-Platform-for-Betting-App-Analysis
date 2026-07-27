"""
File: gold_pipeline.py
Purpose:
    Gold Layer aggregation pipeline that processes Silver curated data,
    computes platform trust scores and insights, saves Parquet datasets,
    and updates PostgreSQL analytics tables.
Author: Priya Iyer
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from config.settings import settings
from database.models import PaymentRecordModel, GoldPlatformAnalytics, GoldPaymentMethodInsight
from services.ai.trust_engine import TrustEngine

logger = logging.getLogger("backend.services.etl.gold_pipeline")


class GoldPipeline:
    """
    Orchestrates the extraction of Silver layer payment records, aggregates them,
    computes trust profiles and risk indicators, and serializes Gold layer assets.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.trust_engine = TrustEngine(db_session=db)

    def run_aggregation(self, run_path_key: str) -> Dict[str, Any]:
        """
        Executes the Gold aggregation run for all active platforms.
        Saves local Parquet backups and populates the PostgreSQL database.
        """
        logger.info(f"Starting Gold Layer Aggregation for run path: {run_path_key}")

        # 1. Fetch all distinct sites currently present in the Silver payment_records table
        sites = [row[0] for row in self.db.query(PaymentRecordModel.site).distinct().all()]
        if not sites:
            logger.warning("No records found in payment_records. Skipping Gold layer generation.")
            return {"platform_count": 0, "status": "skipped", "message": "No curated records available."}

        platform_summaries = []
        payment_insights = []

        # 2. Compute aggregates for each site
        for site in sites:
            logger.info(f"Computing Gold analytics for site: {site}")
            # Fetch all records for this site
            records = self.db.query(PaymentRecordModel).filter(
                PaymentRecordModel.site == site
            ).all()

            if not records:
                continue

            # Convert to dictionary representation for the TrustEngine
            record_dicts = [
                {
                    "site": r.site,
                    "payment_type": r.payment_type,
                    "payment_name": r.payment_name,
                    "currency": r.currency,
                    "country": r.country,
                    "support_type": r.support_type,
                    "support_value": r.support_value,
                    "bonus_name": r.bonus_name,
                    "status": r.status,
                    "extraction_status": r.extraction_status,
                    "scraped_at": r.scraped_at
                }
                for r in records
            ]

            # Compute trust score response
            trust_resp = self.trust_engine.calculate_platform_trust(site, custom_records=record_dicts)

            # High-level metrics
            total_methods = len(records)
            active_methods = sum(1 for r in records if r.status == "active")
            countries = list(set(r.country for r in records if r.country))
            top_methods = list(set(r.payment_name for r in records if r.payment_name))[:5]
            last_scraped_at = max(r.scraped_at for r in records)

            # Build platform summary dict
            platform_summary = {
                "site": site,
                "trust_score": trust_resp.trust_score,
                "trust_level": trust_resp.trust_level,
                "confidence_score": trust_resp.confidence_score,
                "total_payment_methods": total_methods,
                "active_payment_methods": active_methods,
                "supported_countries": countries,
                "top_payment_methods": top_methods,
                "risk_summary": trust_resp.score_explanation,
                "risk_flags": trust_resp.risk_flags,
                "last_scraped_at": last_scraped_at
            }
            platform_summaries.append(platform_summary)

            # Method level insights
            # Group records by type and name
            method_groups = {}
            for r in records:
                key = (r.payment_type, r.payment_name)
                if key not in method_groups:
                    method_groups[key] = []
                method_groups[key].append(r)

            for (p_type, p_name), group_recs in method_groups.items():
                total = len(group_recs)
                active = sum(1 for r in group_recs if r.status == "active")
                rel_score = round((active / total) * 100.0, 1) if total > 0 else 0.0
                grp_countries = list(set(r.country for r in group_recs if r.country))

                insight = {
                    "site": site,
                    "payment_type": p_type,
                    "payment_name": p_name,
                    "total_records": total,
                    "active_count": active,
                    "reliability_score": rel_score,
                    "supported_countries": grp_countries
                }
                payment_insights.append(insight)

        # 3. Write Gold Parquet files to the Gold directory
        gold_root = Path(settings.SILVER_DATA_DIR).parent / "gold"
        
        analytics_dir = gold_root / "platform_analytics" / run_path_key
        analytics_dir.mkdir(parents=True, exist_ok=True)
        analytics_file = analytics_dir / "platform_analytics.parquet"
        pd.DataFrame(platform_summaries).to_parquet(str(analytics_file), index=False)
        logger.info(f"Saved Gold Platform Analytics Parquet to: {analytics_file}")

        insights_dir = gold_root / "payment_method_insights" / run_path_key
        insights_dir.mkdir(parents=True, exist_ok=True)
        insights_file = insights_dir / "payment_method_insights.parquet"
        pd.DataFrame(payment_insights).to_parquet(str(insights_file), index=False)
        logger.info(f"Saved Gold Payment Method Insights Parquet to: {insights_file}")

        # 4. Load/Upsert computed values to PostgreSQL tables
        # Platform summaries upsert
        for summary in platform_summaries:
            stmt = insert(GoldPlatformAnalytics).values(**summary)
            update_stmt = stmt.on_conflict_do_update(
                index_elements=["site"],
                set_={
                    "trust_score": stmt.excluded.trust_score,
                    "trust_level": stmt.excluded.trust_level,
                    "confidence_score": stmt.excluded.confidence_score,
                    "total_payment_methods": stmt.excluded.total_payment_methods,
                    "active_payment_methods": stmt.excluded.active_payment_methods,
                    "supported_countries": stmt.excluded.supported_countries,
                    "top_payment_methods": stmt.excluded.top_payment_methods,
                    "risk_summary": stmt.excluded.risk_summary,
                    "risk_flags": stmt.excluded.risk_flags,
                    "last_scraped_at": stmt.excluded.last_scraped_at,
                    "updated_at": datetime.utcnow()
                }
            )
            self.db.execute(update_stmt)

        # Insights upsert
        for insight in payment_insights:
            stmt = insert(GoldPaymentMethodInsight).values(**insight)
            update_stmt = stmt.on_conflict_do_update(
                index_elements=["site", "payment_type", "payment_name"],
                set_={
                    "total_records": stmt.excluded.total_records,
                    "active_count": stmt.excluded.active_count,
                    "reliability_score": stmt.excluded.reliability_score,
                    "supported_countries": stmt.excluded.supported_countries
                }
            )
            self.db.execute(update_stmt)

        self.db.commit()
        logger.info("Successfully populated Gold Layer PostgreSQL tables.")

        return {
            "platform_count": len(platform_summaries),
            "insight_count": len(payment_insights),
            "status": "success",
            "message": f"Successfully processed {len(platform_summaries)} platforms into Gold Layer."
        }
